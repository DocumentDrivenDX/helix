#!/usr/bin/env python3
"""render_ablation_report — emit REPORT.md from scored ablation results."""
from __future__ import annotations

import json
import sys
import subprocess
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "ablation-results"


def main():
    proc = subprocess.run(
        ["python3", str(HERE / "score_ablation.py"), str(RESULTS)],
        capture_output=True, text=True, check=True,
    )
    data = json.loads(proc.stdout)
    variants = data["variants"]
    winner = data["winner"]
    winner_passes = data["winner_passes_gates"]

    lines = []
    p = lines.append
    p("# P1 — Description-Shape Ablation Report")
    p("")
    p(f"Generated: {datetime.utcnow().isoformat()}Z")
    p("")
    p("## Setup")
    p("")
    p("- Fixture: `family-test/consumer/clean` (well-formed `.helix.yml`, `defaults.methodology=helix`).")
    p("- Plugins mounted: `helix-library` + `methodology-product`.")
    p("- Probe: `family-test/docker/run-probe.sh` -> Docker -> `claude -p --plugin-dir ...`.")
    p("- Routing eval rows: 30 positive + 30 negative + 15 ambiguous (75 total).")
    p("- Variants tested: " + ", ".join(sorted(variants.keys())))
    p("")
    p("Gates per plan §1373 (P1):")
    p("- Positives: skill engaged on ≥29/30 rows.")
    p("- Negatives: NO skill engagement on 30/30 rows.")
    p("- Ambiguous: ≥13/15 produced the correct route AND 0/15 unsafe.")
    p("")
    p("Ambiguous scoring operationalised in `score_ablation.py` (siblings not installed in this bed).")
    p("")
    p("## Confusion matrix per variant")
    p("")
    p("| Variant | Pos engaged | Neg not-engaged | Amb correct | Amb unsafe | Composite | Gate Pos | Gate Neg | Gate Amb corr | Gate Amb unsafe | All gates |")
    p("|---|---|---|---|---|---|---|---|---|---|---|")
    for v in sorted(variants.keys()):
        s = variants[v]
        p(f"| {v} | {s['positive_engaged']}/{s['positive_total']} "
          f"| {s['negative_not_engaged']}/{s['negative_total']} "
          f"| {s['ambiguous_correct']}/{s['ambiguous_total']} "
          f"| {s['ambiguous_unsafe']}/{s['ambiguous_total']} "
          f"| {s['composite']} "
          f"| {'PASS' if s['gate_positive'] else 'FAIL'} "
          f"| {'PASS' if s['gate_negative'] else 'FAIL'} "
          f"| {'PASS' if s['gate_ambiguous_correct'] else 'FAIL'} "
          f"| {'PASS' if s['gate_ambiguous_unsafe'] else 'FAIL'} "
          f"| {'PASS' if s['gate_all'] else 'FAIL'} |")
    p("")
    p("## Winner")
    p("")
    if winner is None:
        p("No variant produced any results.")
    elif winner_passes:
        p(f"**Winner: `{winner}`** — clears all four integer thresholds.")
    else:
        s = variants[winner]
        p(f"**No variant clears all four gates.** Closest by composite score: `{winner}`.")
        p("")
        p(f"- Positive: {s['positive_engaged']}/{s['positive_total']} "
          f"(need ≥29 → {'PASS' if s['gate_positive'] else 'FAIL'})")
        p(f"- Negative: {s['negative_not_engaged']}/{s['negative_total']} "
          f"(need 30 → {'PASS' if s['gate_negative'] else 'FAIL'})")
        p(f"- Ambiguous correct: {s['ambiguous_correct']}/{s['ambiguous_total']} "
          f"(need ≥13 → {'PASS' if s['gate_ambiguous_correct'] else 'FAIL'})")
        p(f"- Ambiguous unsafe: {s['ambiguous_unsafe']}/{s['ambiguous_total']} "
          f"(need 0 → {'PASS' if s['gate_ambiguous_unsafe'] else 'FAIL'})")
    p("")
    p("## Ambiguous breakdown (winner)")
    p("")
    if winner and variants.get(winner):
        for d in variants[winner]["ambiguous_details"]:
            p(f"- {d['id']} expected={d['expected']} engaged={d['engaged']} "
              f"correct={d['correct']} unsafe={d['unsafe']}")
    p("")
    p("## Raw score dump")
    p("")
    p("```json")
    p(json.dumps(data, indent=2))
    p("```")

    out = RESULTS / "REPORT.md"
    out.write_text("\n".join(lines))
    print(str(out))


if __name__ == "__main__":
    main()
