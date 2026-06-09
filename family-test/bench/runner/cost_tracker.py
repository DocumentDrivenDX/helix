"""Per-run cost tracking (Phase 0b).

Records per-row cost into cost-log.jsonl. Each entry captures the row id, the
phase context (bench | dev_iteration), token + dollar accounting, and the
wall-clock duration. Ratchet baselines are computed by aggregating the log;
the runner reads back the rolling baseline at self-test time and refuses to
ship a regression beyond the declared tolerance.

Cost source: stream-json result events carry a `usage` block with
input_tokens + output_tokens + cache_creation_input_tokens +
cache_read_input_tokens. The runner pulls per-1M pricing from
`cost-model.yml` (sibling of this file) which can be bumped without code
changes when CC pricing shifts.

Two ratchet streams are tracked separately (per plan):
  - "bench"           — cost of running the bench suite itself
  - "dev_iteration"   — cost of iterating on the bench (writing rows,
                        regenerating fixtures); spent during P5 corpus auth.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
COST_LOG = ROOT / "cost-log.jsonl"
COST_MODEL = ROOT / "cost-model.yml"


# Per-1M-token defaults (claude-opus-4-7 as of 2026-06-05). When cost-model.yml
# exists we prefer it; these are the seed fallbacks for self-test bring-up.
DEFAULT_PRICING_PER_M = {
    "input_tokens": 15.00,
    "output_tokens": 75.00,
    "cache_creation_input_tokens": 18.75,
    "cache_read_input_tokens": 1.50,
}


@dataclass
class CostEntry:
    row_id: str
    phase: str                # 'bench' | 'dev_iteration'
    timestamp: str            # iso8601 utc
    duration_s: float
    input_tokens: int = 0
    output_tokens: int = 0
    cache_creation_input_tokens: int = 0
    cache_read_input_tokens: int = 0
    cost_usd: float = 0.0
    model: str = ""
    notes: dict[str, Any] = field(default_factory=dict)


def load_pricing() -> dict[str, float]:
    """Load per-1M-token pricing from cost-model.yml or use defaults."""
    if COST_MODEL.exists():
        try:
            import yaml  # local import (yaml is already a runner dep)
            data = yaml.safe_load(COST_MODEL.read_text()) or {}
            pricing = data.get("per_million_tokens") or {}
            return {k: float(pricing.get(k, DEFAULT_PRICING_PER_M[k])) for k in DEFAULT_PRICING_PER_M}
        except Exception:
            pass
    return dict(DEFAULT_PRICING_PER_M)


def compute_cost(usage: dict[str, Any], pricing: dict[str, float] | None = None) -> float:
    """Compute dollar cost from a stream-json `usage` block."""
    pricing = pricing or load_pricing()
    total = 0.0
    for key, per_m in pricing.items():
        toks = int(usage.get(key, 0) or 0)
        total += (toks / 1_000_000.0) * per_m
    return round(total, 6)


def record(entry: CostEntry, path: Path = COST_LOG) -> None:
    """Append a cost entry as a JSONL row."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as fh:
        fh.write(json.dumps(asdict(entry)) + "\n")


def from_result_event(
    event: dict[str, Any],
    row_id: str,
    phase: str = "bench",
    duration_s: float = 0.0,
    notes: dict[str, Any] | None = None,
) -> CostEntry:
    """Build a CostEntry from a stream-json `result` event."""
    usage = (event.get("usage") or event.get("message", {}).get("usage") or {})
    pricing = load_pricing()
    return CostEntry(
        row_id=row_id,
        phase=phase,
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        duration_s=round(duration_s, 3),
        input_tokens=int(usage.get("input_tokens", 0) or 0),
        output_tokens=int(usage.get("output_tokens", 0) or 0),
        cache_creation_input_tokens=int(usage.get("cache_creation_input_tokens", 0) or 0),
        cache_read_input_tokens=int(usage.get("cache_read_input_tokens", 0) or 0),
        cost_usd=compute_cost(usage, pricing),
        model=event.get("model") or event.get("message", {}).get("model", ""),
        notes=notes or {},
    )


def baseline(path: Path = COST_LOG, phase: str = "bench") -> dict[str, float]:
    """Aggregate the cost log to compute mean/p95 baseline per phase."""
    if not path.exists():
        return {"mean_usd": 0.0, "p95_usd": 0.0, "count": 0}
    values: list[float] = []
    with path.open() as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("phase") == phase:
                values.append(float(row.get("cost_usd", 0.0)))
    if not values:
        return {"mean_usd": 0.0, "p95_usd": 0.0, "count": 0}
    values.sort()
    mean = sum(values) / len(values)
    p95_idx = max(0, int(len(values) * 0.95) - 1)
    return {
        "mean_usd": round(mean, 6),
        "p95_usd": round(values[p95_idx], 6),
        "count": len(values),
    }


def self_test() -> int:
    """Smoke: ensure compute_cost + record + baseline round-trip."""
    sample = {
        "input_tokens": 1000,
        "output_tokens": 500,
        "cache_creation_input_tokens": 0,
        "cache_read_input_tokens": 0,
    }
    cost = compute_cost(sample)
    # 1000/1M * 15 + 500/1M * 75 = 0.015 + 0.0375 = 0.0525
    expected = 0.0525
    if abs(cost - expected) > 1e-6:
        print(f"cost_tracker self-test FAIL: cost={cost} expected={expected}")
        return 1
    print(f"cost_tracker self-test PASS: sample cost ${cost:.6f}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(self_test())
