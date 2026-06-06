"""Property-based tests for 4 matchers (Phase 0b).

Each property generates 100 synthetic transcript cases with a known
ground-truth verdict, runs the matcher, and asserts the matcher's verdict
matches ground truth. Generators are seeded (random.Random(seed)) so a
failing case can be reproduced from (property_name, seed, case_index).

On failure, the runner dumps:
  - the offending transcript JSONL
  - the matcher params
  - the expected verdict + the matcher's verdict

Properties cover the four programmatic matchers most prone to subtle
ordering / scoping bugs (per plan §1.4b prioritisation):
  P1: read_before_write     — ordering + presence
  P2: scope_write_path      — allowlist-with-forbidden
  P3: skill_tool_use        — name + skill_id alias forms
  P4: graph_edge_observed   — read AND surface conjunction
"""

from __future__ import annotations

import json
import random
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# helix_bench.py imports under runner/
from helix_bench import (  # noqa: E402
    MATCHER_REGISTRY,
    Transcript,
)


CASES_PER_PROPERTY = 100
SEED = 0xC0FFEE  # deterministic; bump only on intentional generator change


@dataclass
class PropertyCase:
    name: str
    index: int
    transcript: Transcript
    params: dict[str, Any]
    expected_verdict: str
    annotation: str  # human-readable description of this case's intent


# ---------------------------------------------------------------------------
# Generators
# ---------------------------------------------------------------------------


_HELIX_PATHS_IN_SCOPE = [
    "/repo/docs/helix/00-discover/product-vision.md",
    "/repo/docs/helix/01-frame/prd.md",
    "/repo/docs/helix/01-frame/feature-specification.md",
    "/repo/docs/helix/02-design/architecture.md",
]
_HELIX_PATHS_OUT_OF_SCOPE = [
    "/repo/README.md",
    "/repo/src/main.py",
    "/repo/.env",
    "/repo/package.json",
]


def _events_to_transcript(events: list[dict[str, Any]]) -> Transcript:
    return Transcript.from_events(events)


def gen_read_before_write(rng: random.Random, i: int) -> PropertyCase:
    """Generate either an ordered, reversed, or absent case."""
    flavor = rng.choice(["ordered", "reversed", "absent", "no_read", "no_write"])
    target = rng.choice([".helix.yml", "marker.yml", ".helix.yml"])
    target_path = f"/repo/{target}"
    write_path = rng.choice(_HELIX_PATHS_IN_SCOPE)
    params = {
        "first_tool": "Read",
        "second_tool": "Write",
        "target_pattern": r"\.helix\.yml$|marker\.yml$",
    }
    if flavor == "ordered":
        events = [
            {"type": "tool_use", "name": "Read", "input": {"file_path": target_path}},
            {"type": "tool_use", "name": "Write", "input": {"file_path": write_path}},
        ]
        expected = "ordered"
    elif flavor == "reversed":
        events = [
            {"type": "tool_use", "name": "Write", "input": {"file_path": write_path}},
            {"type": "tool_use", "name": "Read", "input": {"file_path": target_path}},
        ]
        expected = "reversed"
    elif flavor == "absent":
        events = [{"type": "text", "text": f"case {i}: agent emitted no tool_use"}]
        expected = "absent"
    elif flavor == "no_read":
        # Write only — second_idx set, first_idx None → matcher returns 'reversed'
        events = [
            {"type": "tool_use", "name": "Write", "input": {"file_path": write_path}}
        ]
        expected = "reversed"
    else:  # no_write
        events = [
            {"type": "tool_use", "name": "Read", "input": {"file_path": target_path}}
        ]
        expected = "ordered"  # first found, second absent → ordered (per matcher)
    return PropertyCase(
        name="read_before_write",
        index=i,
        transcript=_events_to_transcript(events),
        params=params,
        expected_verdict=expected,
        annotation=flavor,
    )


def gen_scope_write_path(rng: random.Random, i: int) -> PropertyCase:
    """Generate writes that are either all-in-scope or contain a violation."""
    params = {
        "allowed_root": r"^/repo/docs/helix/",
        "forbidden_pattern": r"\.env$",
    }
    flavor = rng.choice(["in_scope", "out_of_scope", "forbidden", "mixed", "no_writes"])
    if flavor == "in_scope":
        events = [
            {"type": "tool_use", "name": "Write", "input": {"file_path": p}}
            for p in rng.sample(_HELIX_PATHS_IN_SCOPE, k=rng.randint(1, 3))
        ]
        expected = "present"
    elif flavor == "out_of_scope":
        bad = rng.choice([p for p in _HELIX_PATHS_OUT_OF_SCOPE if not p.endswith(".env")])
        events = [{"type": "tool_use", "name": "Write", "input": {"file_path": bad}}]
        expected = "absent"
    elif flavor == "forbidden":
        # path under allowed_root that matches forbidden_pattern
        events = [
            {
                "type": "tool_use",
                "name": "Write",
                "input": {"file_path": "/repo/docs/helix/.env"},
            }
        ]
        expected = "absent"
    elif flavor == "mixed":
        events = [
            {"type": "tool_use", "name": "Write", "input": {"file_path": _HELIX_PATHS_IN_SCOPE[0]}},
            {"type": "tool_use", "name": "Write", "input": {"file_path": _HELIX_PATHS_OUT_OF_SCOPE[0]}},
        ]
        expected = "absent"
    else:  # no_writes
        events = [{"type": "text", "text": f"case {i}: zero mutations"}]
        # matcher treats "no writes" as trivially in-scope → present
        expected = "present"
    return PropertyCase(
        name="scope_write_path",
        index=i,
        transcript=_events_to_transcript(events),
        params=params,
        expected_verdict=expected,
        annotation=flavor,
    )


def gen_skill_tool_use(rng: random.Random, i: int) -> PropertyCase:
    """Generate skill invocations under each of the 3 supported alias forms."""
    skill_id = rng.choice(["helix", "helix-web", "helix-data", "helix-infra"])
    params = {"skill_id": skill_id}
    flavor = rng.choice(
        ["Skill_input", "Skill_paren", "name_only", "absent", "wrong_id"]
    )
    if flavor == "Skill_input":
        events = [{"type": "tool_use", "name": "Skill", "input": {"skill_id": skill_id}}]
        expected = "present"
    elif flavor == "Skill_paren":
        events = [
            {"type": "tool_use", "name": f"Skill({skill_id})", "input": {}}
        ]
        expected = "present"
    elif flavor == "name_only":
        events = [{"type": "tool_use", "name": skill_id, "input": {}}]
        expected = "present"
    elif flavor == "absent":
        events = [{"type": "text", "text": "no skill invoked"}]
        expected = "absent"
    else:  # wrong_id
        other = "helix-other"
        events = [{"type": "tool_use", "name": "Skill", "input": {"skill_id": other}}]
        expected = "absent"
    return PropertyCase(
        name="skill_tool_use",
        index=i,
        transcript=_events_to_transcript(events),
        params=params,
        expected_verdict=expected,
        annotation=flavor,
    )


def gen_graph_edge_observed(rng: random.Random, i: int) -> PropertyCase:
    """Generate read+surface combinations; only both → present."""
    edge = "prd informs feature-specification"
    params = {
        "graph_path": r"graph\.yml$",
        "expected_edge_signature": edge,
    }
    flavor = rng.choice(["both", "read_no_surface", "surface_no_read", "neither"])
    if flavor == "both":
        events = [
            {"type": "tool_use", "name": "Read", "input": {"file_path": "/skill/graph.yml"}},
            {"type": "text", "text": f"Graph says {edge}, surfacing now."},
        ]
        expected = "present"
    elif flavor == "read_no_surface":
        events = [
            {"type": "tool_use", "name": "Read", "input": {"file_path": "/skill/graph.yml"}},
            {"type": "text", "text": "Read the graph but offering no signature."},
        ]
        expected = "absent"
    elif flavor == "surface_no_read":
        events = [{"type": "text", "text": f"From memory: {edge}"}]
        expected = "absent"
    else:  # neither
        events = [{"type": "text", "text": "nothing relevant here"}]
        expected = "absent"
    return PropertyCase(
        name="graph_edge_observed",
        index=i,
        transcript=_events_to_transcript(events),
        params=params,
        expected_verdict=expected,
        annotation=flavor,
    )


GENERATORS: dict[str, Callable[[random.Random, int], PropertyCase]] = {
    "read_before_write": gen_read_before_write,
    "scope_write_path": gen_scope_write_path,
    "skill_tool_use": gen_skill_tool_use,
    "graph_edge_observed": gen_graph_edge_observed,
}


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------


@dataclass
class PropertyFailure:
    property_name: str
    case_index: int
    annotation: str
    params: dict[str, Any]
    expected: str
    got: str
    events: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "property": self.property_name,
            "case_index": self.case_index,
            "annotation": self.annotation,
            "params": self.params,
            "expected_verdict": self.expected,
            "actual_verdict": self.got,
            "events": self.events,
        }


def run_property(name: str, dump_dir: Path | None = None) -> tuple[int, int, list[PropertyFailure]]:
    """Run 100 cases for property `name`. Return (pass, fail, failures)."""
    rng = random.Random(SEED + hash(name) & 0xFFFFFFFF)
    matcher = MATCHER_REGISTRY[name]
    failures: list[PropertyFailure] = []
    passed = 0
    for i in range(CASES_PER_PROPERTY):
        case = GENERATORS[name](rng, i)
        result = matcher(case.params, case.transcript)
        if result.verdict == case.expected_verdict:
            passed += 1
        else:
            f = PropertyFailure(
                property_name=name,
                case_index=i,
                annotation=case.annotation,
                params=case.params,
                expected=case.expected_verdict,
                got=result.verdict,
                events=case.transcript.raw_events,
            )
            failures.append(f)
            if dump_dir is not None:
                dump_dir.mkdir(parents=True, exist_ok=True)
                out = dump_dir / f"{name}-case{i:03d}-{case.annotation}.json"
                out.write_text(json.dumps(f.to_dict(), indent=2))
    return passed, CASES_PER_PROPERTY - passed, failures


def run_all(dump_dir: Path | None = None) -> dict[str, Any]:
    """Run all 4 properties. Return summary dict."""
    summary: dict[str, Any] = {
        "cases_per_property": CASES_PER_PROPERTY,
        "properties": {},
        "total_pass": 0,
        "total_fail": 0,
    }
    for name in GENERATORS:
        passed, failed, failures = run_property(name, dump_dir=dump_dir)
        summary["properties"][name] = {
            "pass": passed,
            "fail": failed,
            "failures": [f.to_dict() for f in failures[:5]],  # first 5 dumped inline
        }
        summary["total_pass"] += passed
        summary["total_fail"] += failed
    return summary


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--dump-dir", type=Path, default=None)
    args = parser.parse_args()
    s = run_all(dump_dir=args.dump_dir)
    print(json.dumps(s, indent=2))
    sys.exit(0 if s["total_fail"] == 0 else 1)
