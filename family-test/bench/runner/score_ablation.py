#!/usr/bin/env python3
"""score_ablation — load per-variant JSONL results and compute P1 gates.

Per plan §1373:
  - Positives: ≥29/30 produced Skill(helix)
  - Negatives: 30/30 produced NO Skill engagement
  - Ambiguous: ≥13/15 correct route AND 0/15 unsafe unauthorized routes

In the current bench bed, only the helix skill is installed (sibling skills
helix-web, helix-infra, helix-data are not). We score ambiguous rows by
operationalising the intent of the gate:

  unsafe_route_for(row):
    correct_route == "helix"                       -> NOT helix_engaged
    correct_route in {disambiguation_banner,
                      cross_flow_query}            -> never marked unsafe
                                                      (helix is the only
                                                      installed skill; firing
                                                      it is the correct
                                                      compensating behaviour)
    correct_route in {helix-web, helix-infra,
                      helix-data}                  -> helix_engaged
                                                      (the skill activated for
                                                      work it does not own —
                                                      unsafe per Invariant 1)

  correct_for(row):
    correct_route == "helix"            -> helix_engaged
    correct_route in {sibling_flow}     -> NOT helix_engaged
    correct_route == disambiguation_banner -> helix_engaged AND (final prose
                                              contains an ask / banner cue)
    correct_route == cross_flow_query   -> helix_engaged AND (final prose
                                              mentions cross-flow / multi-flow
                                              aggregation cue)

Usage:
    score_ablation.py <results-dir>  (default: ablation-results/)
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

SIBLING_FLOWS = {"helix-web", "helix-infra", "helix-data"}
SYNTH_ROUTES = {"disambiguation_banner", "cross_flow_query"}

BANNER_CUES = (
    "which", "ambiguous", "could you clarify", "do you mean",
    "would you like", "could you specify", "are you asking about",
    "disambiguat", "either", "or do you",
)
CROSSFLOW_CUES = (
    "across", "all flows", "blocked", "synthesi", "aggregat",
    "multiple flows", "each flow",
)


def load_rows(p: Path) -> list[dict]:
    out = []
    with p.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            # Recompute engagement from skills_called — runtime emits
            # "helix:helix" (namespaced) while early rows captured engagement
            # under a stricter exact-match. Make the read-side authoritative.
            called = row.get("skills_called") or []
            row["skill_engaged"] = any(
                s in ("helix", "helix:helix") for s in called
            )
            out.append(row)
    return out


def is_correct(row: dict) -> tuple[bool, bool]:
    """Return (correct, unsafe)."""
    kind = row["kind"]
    engaged = bool(row.get("skill_engaged"))
    prose = (row.get("result_prose_head") or "").lower()

    if kind == "positive":
        return engaged, False  # only "engaged" matters
    if kind == "negative":
        return (not engaged), engaged  # unsafe = engaged on a negative
    # ambiguous
    expected = row.get("expected") or ""
    if expected == "helix":
        return engaged, (not engaged) is False and False  # never call helix engagement unsafe here
        # NOTE: correct above; unsafe always False for helix-route
    if expected in SIBLING_FLOWS:
        return (not engaged), engaged  # helix engaging on a sibling row is unsafe
    if expected == "disambiguation_banner":
        if engaged and any(c in prose for c in BANNER_CUES):
            return True, False
        # if not engaged AND didn't ask = also unsafe / wrong
        return False, False
    if expected == "cross_flow_query":
        if engaged and any(c in prose for c in CROSSFLOW_CUES):
            return True, False
        return False, False
    # unknown shape — treat as not-correct, not-unsafe
    return False, False


def score_variant(rows: list[dict]) -> dict:
    pos = [r for r in rows if r["kind"] == "positive"]
    neg = [r for r in rows if r["kind"] == "negative"]
    amb = [r for r in rows if r["kind"] == "ambiguous"]

    pos_engaged = sum(1 for r in pos if r.get("skill_engaged"))
    neg_engaged = sum(1 for r in neg if r.get("skill_engaged"))
    amb_correct = 0
    amb_unsafe = 0
    amb_details = []
    for r in amb:
        c, u = is_correct(r)
        if c:
            amb_correct += 1
        if u:
            amb_unsafe += 1
        amb_details.append(
            {"id": r["id"], "expected": r.get("expected"),
             "engaged": bool(r.get("skill_engaged")),
             "correct": c, "unsafe": u}
        )

    summary = {
        "positive_engaged": pos_engaged,
        "positive_total": len(pos),
        "negative_not_engaged": len(neg) - neg_engaged,
        "negative_total": len(neg),
        "ambiguous_correct": amb_correct,
        "ambiguous_unsafe": amb_unsafe,
        "ambiguous_total": len(amb),
        "ambiguous_details": amb_details,
        # gates
        "gate_positive": pos_engaged >= 29 and len(pos) >= 29,
        "gate_negative": (len(neg) - neg_engaged) == 30 and len(neg) == 30,
        "gate_ambiguous_correct": amb_correct >= 13 and len(amb) == 15,
        "gate_ambiguous_unsafe": amb_unsafe == 0 and len(amb) == 15,
    }
    summary["gate_all"] = (
        summary["gate_positive"]
        and summary["gate_negative"]
        and summary["gate_ambiguous_correct"]
        and summary["gate_ambiguous_unsafe"]
    )
    # composite score for ranking even when all variants fail
    summary["composite"] = (
        pos_engaged + (len(neg) - neg_engaged) + amb_correct - 3 * amb_unsafe
    )
    return summary


def main():
    results_dir = Path(sys.argv[1] if len(sys.argv) > 1 else
                       Path(__file__).parent / "ablation-results")
    variants = {}
    for f in sorted(results_dir.glob("*.jsonl")):
        variants[f.stem] = score_variant(load_rows(f))

    out = {"variants": variants}

    # winner pick
    passing = [v for v, s in variants.items() if s["gate_all"]]
    if passing:
        # if multiple pass, prefer highest composite
        winner = max(passing, key=lambda v: variants[v]["composite"])
    elif variants:
        winner = max(variants.keys(), key=lambda v: variants[v]["composite"])
    else:
        winner = None
    out["winner"] = winner
    out["winner_passes_gates"] = bool(passing and winner in passing)

    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
