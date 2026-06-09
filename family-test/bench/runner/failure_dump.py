"""Failure observability scaffold (Phase 0b).

On a row failure, the runner writes a dump under
`family-test/bench/failures/<row-id>-<utc>/` containing:

  - transcript.stream.jsonl       (the raw stream-json as emitted by CC)
  - matcher-trace.txt             (per-matcher params + verdict + details)
  - expected-vs-actual.diff       (yaml diff of expected vs observed verdict)
  - negative-control.diff         (the workspace mutation we applied)

The dump path is also echoed to stderr so a CI viewer can deep-link to it.
"""

from __future__ import annotations

import difflib
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

BENCH_ROOT = Path(__file__).resolve().parents[1]
FAILURES_ROOT = BENCH_ROOT / "failures"


@dataclass
class FailureContext:
    row_id: str
    transcript_events: list[dict[str, Any]]
    matcher_name: str
    matcher_params: dict[str, Any]
    matcher_verdict: str
    matcher_details: dict[str, Any]
    expected_verdict: str
    negative_control: dict[str, Any]
    extra_notes: dict[str, Any]


def _slugify(s: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "-_." else "-" for ch in s)


def dump(ctx: FailureContext, root: Path = FAILURES_ROOT) -> Path:
    """Write the four artifacts and return the dump dir path."""
    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    dir_name = f"{_slugify(ctx.row_id)}-{ts}"
    out = root / dir_name
    out.mkdir(parents=True, exist_ok=True)

    # 1. transcript.stream.jsonl — raw events, one per line
    (out / "transcript.stream.jsonl").write_text(
        "\n".join(json.dumps(ev) for ev in ctx.transcript_events) + "\n"
    )

    # 2. matcher-trace.txt — human-readable per-matcher trace
    trace_lines = [
        f"row_id: {ctx.row_id}",
        f"matcher: {ctx.matcher_name}",
        f"params: {json.dumps(ctx.matcher_params, indent=2)}",
        f"verdict: {ctx.matcher_verdict}",
        f"details: {json.dumps(ctx.matcher_details, indent=2)}",
        f"timeline_event_count: {len(ctx.transcript_events)}",
    ]
    if ctx.extra_notes:
        trace_lines.append(f"notes: {json.dumps(ctx.extra_notes, indent=2)}")
    (out / "matcher-trace.txt").write_text("\n".join(trace_lines) + "\n")

    # 3. expected-vs-actual.diff — unified diff of yaml-ish snapshots
    expected_snap = f"verdict: {ctx.expected_verdict}\n"
    actual_snap = f"verdict: {ctx.matcher_verdict}\n"
    diff = difflib.unified_diff(
        expected_snap.splitlines(keepends=True),
        actual_snap.splitlines(keepends=True),
        fromfile="expected",
        tofile="actual",
        n=2,
    )
    (out / "expected-vs-actual.diff").write_text("".join(diff))

    # 4. negative-control.diff — yaml dump of the modification we applied
    (out / "negative-control.diff").write_text(
        json.dumps(ctx.negative_control, indent=2) + "\n"
    )

    return out


def scaffold_self_test() -> int:
    """Smoke: simulate a failure dump and assert all 4 artifacts exist."""
    ctx = FailureContext(
        row_id="selftest-row",
        transcript_events=[
            {"type": "text", "text": "synthetic"},
            {"type": "tool_use", "name": "Write", "input": {"file_path": "/tmp/x"}},
        ],
        matcher_name="scope_write_path",
        matcher_params={"allowed_root": "^/repo/"},
        matcher_verdict="absent",
        matcher_details={"violations": [{"path": "/tmp/x"}]},
        expected_verdict="present",
        negative_control={"plugins_remove": ["methodology-product"]},
        extra_notes={"reason": "self-test scaffold smoke"},
    )
    root = FAILURES_ROOT / "_selftest"
    if root.exists():
        for child in root.iterdir():
            if child.is_dir():
                for f in child.iterdir():
                    f.unlink()
                child.rmdir()
            else:
                child.unlink()
    out = dump(ctx, root=root)
    required = [
        "transcript.stream.jsonl",
        "matcher-trace.txt",
        "expected-vs-actual.diff",
        "negative-control.diff",
    ]
    missing = [name for name in required if not (out / name).exists()]
    if missing:
        print(f"failure_dump self-test FAIL: missing {missing}")
        return 1
    print(f"failure_dump self-test PASS: artifacts under {out}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(scaffold_self_test())
