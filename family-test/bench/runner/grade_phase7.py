#!/usr/bin/env python3
"""Grade Phase 7 retest bench results.

Usage:
    python3 grade_phase7.py [run_dir]

Default run_dir: family-test/bench/runs/phase7-retest-20260608T015359Z
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
BENCH_ROOT = Path(__file__).resolve().parents[1]

# Add the runner dir to sys.path so we can import helix_bench
sys.path.insert(0, str(Path(__file__).parent))
from helix_bench import (
    Transcript, validate_discriminator, load_row, MATCHER_REGISTRY,
    Whitelist, BannedPatterns, is_validator_row
)

ROWS = [
    # 16 Tier-4 stable-fail rows
    "C008-manage-infrastructure-empty",
    "C011-what-methodologies-active",
    "C013-update-prd-edit-not-write",
    "C014-reject-unauthorized-flow",
    "C015-whats-next-graph",
    "C016-plan-rollout-ambiguous-guided",
    "C017-plan-rollout-ambiguous-autonomous",
    "C024-backfill-90d-manual",
    "CD-01-graph-nonstandard-edge",
    "CD-03-negative-control-plugin-removed",
    "CD-04-robustness-variant",
    "CF-02-pipeline-needs-dns",
    "CF-03-whats-blocked-multi-flow",
    "G3-artifact-canonicalization",
    "G4-orchestration-with-gates",
    "G5-upstream-discovery",
    # 5 new rows
    "CD-02-positive-control-no-edge",
    "EA-01-prd-feat-candidates-guided",
    "EA-02-prd-feat-candidates-guided-named",
    "EA-03-prd-feat-candidates-autonomous",
    "EA-04-prd-feat-candidates-autonomous-many",
]

TIER4_STABLE_FAILS = set([
    "C008-manage-infrastructure-empty",
    "C011-what-methodologies-active",
    "C013-update-prd-edit-not-write",
    "C014-reject-unauthorized-flow",
    "C015-whats-next-graph",
    "C016-plan-rollout-ambiguous-guided",
    "C017-plan-rollout-ambiguous-autonomous",
    "C024-backfill-90d-manual",
    "CD-01-graph-nonstandard-edge",
    "CD-03-negative-control-plugin-removed",
    "CD-04-robustness-variant",
    "CF-02-pipeline-needs-dns",
    "CF-03-whats-blocked-multi-flow",
    "G3-artifact-canonicalization",
    "G4-orchestration-with-gates",
    "G5-upstream-discovery",
])


def grade_pass(row_id: str, pass_file: Path, disc: dict) -> dict:
    """Grade a single pass. Returns dict with pass/fail verdict and details."""
    if not pass_file.exists() or pass_file.stat().st_size == 0:
        return {"pass": False, "verdict": "absent", "error": "empty or missing transcript"}

    try:
        transcript = Transcript.parse(pass_file)
    except Exception as e:
        return {"pass": False, "verdict": "absent", "error": f"parse error: {e}"}

    assertion_id = disc["assertion_id"]
    params = disc["params"]
    expected_verdict = disc["expected_in_positive_run"]

    matcher = MATCHER_REGISTRY.get(assertion_id)
    if not matcher:
        return {"pass": False, "verdict": "absent", "error": f"no matcher for {assertion_id}"}

    try:
        result = matcher(params, transcript)
    except Exception as e:
        return {"pass": False, "verdict": "absent", "error": f"matcher error: {e}"}

    passed = result.verdict == expected_verdict
    return {
        "pass": passed,
        "verdict": result.verdict,
        "expected": expected_verdict,
        "details": result.details,
    }


def grade_row(row_id: str, run_dir: Path) -> dict:
    """Grade all 3 passes for a row."""
    row_dir = BENCH_ROOT / "conversations" / row_id
    expected_yml = row_dir / "expected.yml"

    if not expected_yml.exists():
        return {"row_id": row_id, "status": "error", "error": "expected.yml missing"}

    raw_expected = load_row(row_dir)

    if is_validator_row(raw_expected):
        return {"row_id": row_id, "status": "error", "error": "validator-row, not gradable here"}

    try:
        whitelist = Whitelist.load()
        banned = BannedPatterns.load()
        disc = validate_discriminator(raw_expected, whitelist, banned)
    except Exception as e:
        return {"row_id": row_id, "status": "error", "error": f"discriminator validation failed: {e}"}

    pass_results = []
    for pass_idx in range(3):
        pass_file = run_dir / f"{row_id}.pass{pass_idx}.stream.jsonl"
        pass_result = grade_pass(row_id, pass_file, disc)
        pass_results.append(pass_result)

    all_pass = all(r["pass"] for r in pass_results)
    any_pass = any(r["pass"] for r in pass_results)

    if all_pass:
        status = "stable_pass"
    elif not any_pass:
        # Check for empty/missing transcripts
        all_empty = all(r.get("error") for r in pass_results)
        status = "broken" if all_empty else "stable_fail"
    else:
        status = "flake"

    return {
        "row_id": row_id,
        "status": status,
        "assertion_id": disc["assertion_id"],
        "passes": pass_results,
        "in_tier4_stable_fail": row_id in TIER4_STABLE_FAILS,
    }


def main():
    run_dir_arg = sys.argv[1] if len(sys.argv) > 1 else None
    if run_dir_arg:
        run_dir = Path(run_dir_arg)
    else:
        run_dir = BENCH_ROOT / "runs" / "phase7-retest-20260608T015359Z"

    if not run_dir.exists():
        print(f"ERROR: run_dir not found: {run_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Grading from: {run_dir}")
    print()

    results = []
    for row_id in ROWS:
        result = grade_row(row_id, run_dir)
        results.append(result)

    # Summary
    stable_pass = [r for r in results if r["status"] == "stable_pass"]
    stable_fail = [r for r in results if r["status"] == "stable_fail"]
    flake = [r for r in results if r["status"] == "flake"]
    broken = [r for r in results if r["status"] == "broken"]
    error = [r for r in results if r["status"] == "error"]

    # Tier4 recovery (only among the 16 Tier-4 stable-fails)
    tier4_recovered = [r for r in stable_pass if r.get("in_tier4_stable_fail")]
    new_rows_pass = [r for r in stable_pass if not r.get("in_tier4_stable_fail")]

    print(f"=== Phase 7 Re-bench Results ===")
    print(f"Total rows: {len(results)}")
    print(f"stable_pass: {len(stable_pass)}")
    print(f"  - Tier-4 recoveries: {len(tier4_recovered)}")
    print(f"  - New rows pass: {len(new_rows_pass)}")
    print(f"flake: {len(flake)}")
    print(f"stable_fail: {len(stable_fail)}")
    print(f"broken: {len(broken)}")
    print(f"error: {len(error)}")
    print(f"Delta vs Tier-4 baseline: +{len(tier4_recovered)} (of 16 Tier-4 stable-fails)")
    print()

    print("=== Per-row breakdown ===")
    for r in results:
        status = r["status"]
        row_id = r["row_id"]
        marker = "*" if r.get("in_tier4_stable_fail") else " "
        if status == "stable_pass":
            emoji = "PASS"
        elif status == "flake":
            emoji = "FLAKE"
        elif status == "broken":
            emoji = "BROKEN"
        elif status == "error":
            emoji = "ERROR"
        else:
            emoji = "FAIL"

        pass_summary = ""
        if "passes" in r:
            pass_summary = " [" + "/".join("P" if p["pass"] else "F" for p in r["passes"]) + "]"
        print(f"  {emoji} {marker} {row_id}{pass_summary}")
        if r.get("error"):
            print(f"       error: {r['error']}")

    print()
    print(f"Recommendation: ", end="")
    n = len(tier4_recovered)
    if n >= 8:
        print(f"YES stage 5b ({n}/16 >= 50% recovery)")
    elif n >= 4:
        print(f"MAYBE stage 5b ({n}/16 recovery — 4-7 range)")
    else:
        print(f"NO stage 5b ({n}/16 < 4 recovery)")

    # Write JSON results
    output = {
        "run_dir": str(run_dir),
        "total_rows": len(results),
        "stable_pass_count": len(stable_pass),
        "tier4_recovered": len(tier4_recovered),
        "new_rows_pass": len(new_rows_pass),
        "flake_count": len(flake),
        "stable_fail_count": len(stable_fail),
        "broken_count": len(broken),
        "stable_pass_rows": [r["row_id"] for r in stable_pass],
        "fail_rows": [r["row_id"] for r in stable_fail + flake + broken + error],
        "rows": results,
    }

    out_path = run_dir / "grade_phase7_results.json"
    out_path.write_text(json.dumps(output, indent=2))
    print(f"\nFull results written to: {out_path}")

    return output


if __name__ == "__main__":
    main()
