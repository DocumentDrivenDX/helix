#!/usr/bin/env python3
"""Acceptance tests for diff-to-category.py (plan §15c P14).

Run: `python3 family-test/bench/runner/test_diff_to_category.py`
Exit 0 = all pass; non-zero with diagnostic on any failure.

Coverage (per plan §15c P14 "acceptance tests"):
  - 3 positive cases:
      P1. SKILL.md edit       → conversation + routing
      P2. stop-at-triggers.yml → stop_at (and stop_at ONLY of the bench cats)
      P3. marker schema edit  → rename_compat
  - 1 negative case:
      N1. unrelated file edit (docs/) → self_test only

Plus a handful of integrity checks so a future config edit can't silently
break the mapper invariants (config validates, fallback escalates to full,
multi-rule PR unions correctly, etc.).
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "family-test" / "bench" / "runner" / "diff-to-category.py"
CONFIG = ROOT / "family-test" / "bench" / "bench-categories.yml"

# Load the script as a module so we can test internal helpers directly.
spec = importlib.util.spec_from_file_location("d2c", SCRIPT)
d2c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d2c)


FAILURES: list[str] = []


def check(label: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"  PASS  {label}")
    else:
        print(f"  FAIL  {label}  {detail}")
        FAILURES.append(f"{label}: {detail}")


def run_cli(*files: str) -> dict:
    """Invoke diff-to-category.py via subprocess, return parsed JSON."""
    args = [sys.executable, str(SCRIPT), "--config", str(CONFIG), "--json"]
    for f in files:
        args.extend(["--files", f])
    proc = subprocess.run(args, capture_output=True, text=True, check=True)
    return json.loads(proc.stdout)


# ---------------------------------------------------------------------------
# Positive acceptance cases (plan §15c P14)
# ---------------------------------------------------------------------------


def test_positive_skill_md() -> None:
    """P1. SKILL.md edit → conversation + routing run."""
    print("\nP1. SKILL.md edit → conversation + routing")
    r = run_cli("skills/helix/SKILL.md")
    check("conversation in categories", "conversation" in r["categories"],
          f"got {r['categories']}")
    check("routing in categories", "routing" in r["categories"],
          f"got {r['categories']}")
    check("does NOT escalate to full", "full" not in r["categories"],
          f"got {r['categories']}")
    check("does NOT include stop_at", "stop_at" not in r["categories"],
          f"got {r['categories']}")

    # (the legacy family-test/methodology-* fork was removed post canonical-
    # promotion; canonical skills/helix/SKILL.md is the only skill path now)


def test_positive_stop_at() -> None:
    """P2. stop-at-triggers.yml edit → stop_at rows."""
    print("\nP2. stop-at-triggers.yml edit → stop_at")
    r = run_cli("library/skill-prompts/stop-at-triggers.yml")
    check("stop_at in categories", "stop_at" in r["categories"],
          f"got {r['categories']}")
    check("only stop_at (not full bench)", set(r["categories"]) == {"stop_at"},
          f"got {r['categories']}")


def test_positive_marker_schema() -> None:
    """P3. marker schema edit → rename / compat rows."""
    print("\nP3. marker schema edit → rename_compat")
    r = run_cli("library/scripts/helix_check.py")
    check("rename_compat in categories", "rename_compat" in r["categories"],
          f"got {r['categories']}")
    check("does NOT escalate to full", "full" not in r["categories"],
          f"got {r['categories']}")


# ---------------------------------------------------------------------------
# Negative acceptance case
# ---------------------------------------------------------------------------


def test_negative_unrelated() -> None:
    """N1. Unrelated file edit → self_test only."""
    print("\nN1. Unrelated edit (docs) → self_test only")
    r = run_cli("docs/website/content/posts/announce-2026-06-05.md")
    check("categories == ['self_test']", r["categories"] == ["self_test"],
          f"got {r['categories']}")

    print("\nN1b. Pure README edit → self_test only")
    r = run_cli("README.md")
    check("categories == ['self_test']", r["categories"] == ["self_test"],
          f"got {r['categories']}")


# ---------------------------------------------------------------------------
# Integrity checks (config validation + fallback semantics)
# ---------------------------------------------------------------------------


def test_unmatched_falls_back_to_full() -> None:
    """Any path that matches no rule must escalate to the full bench."""
    print("\nI1. Unmatched path → unmatched_fallback (full → expanded)")
    r = run_cli("some/totally/unknown/file.rs")
    # `full` is expanded to every non-full category by map_paths so the matrix
    # consumer doesn't have to special-case it.
    cats = set(r["categories"])
    check("self_test included", "self_test" in cats, f"got {sorted(cats)}")
    check("conversation included", "conversation" in cats, f"got {sorted(cats)}")
    check("stop_at included", "stop_at" in cats, f"got {sorted(cats)}")
    check("full is expanded (not literally present)", "full" not in cats,
          f"got {sorted(cats)}")
    check("unmatched_paths non-empty", r["unmatched_paths"], f"got {r['unmatched_paths']}")


def test_multi_rule_pr_unions() -> None:
    """A PR touching SKILL.md AND stop-at-triggers.yml runs BOTH category sets."""
    print("\nI2. Multi-rule PR unions category contributions")
    r = run_cli(
        "skills/helix/SKILL.md",
        "library/skill-prompts/stop-at-triggers.yml",
    )
    cats = set(r["categories"])
    check("conversation included", "conversation" in cats, f"got {sorted(cats)}")
    check("routing included", "routing" in cats, f"got {sorted(cats)}")
    check("stop_at included", "stop_at" in cats, f"got {sorted(cats)}")
    check("no full escalation", "full" not in cats, f"got {sorted(cats)}")


def test_config_validates() -> None:
    """The shipped bench-categories.yml must pass validate_config."""
    print("\nI3. Shipped config passes validate_config")
    cfg = d2c.load_yaml(CONFIG)
    try:
        d2c.validate_config(cfg)
        check("validate_config OK", True)
    except SystemExit as e:
        check("validate_config OK", False, str(e))


def test_diff_file_mode() -> None:
    """--diff <path> reads paths from a file."""
    print("\nI4. --diff file mode")
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write("skills/helix/SKILL.md\n")
        f.write("library/skill-prompts/stop-at-triggers.yml\n")
        diff_path = Path(f.name)
    try:
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--config", str(CONFIG),
             "--diff", str(diff_path), "--json"],
            capture_output=True, text=True, check=True,
        )
        r = json.loads(proc.stdout)
        cats = set(r["categories"])
        check("conversation + routing + stop_at from diff file",
              {"conversation", "routing", "stop_at"}.issubset(cats),
              f"got {sorted(cats)}")
    finally:
        diff_path.unlink()


def test_glob_double_star() -> None:
    """`**` in globs must match nested paths."""
    print("\nI5. Glob ** matches nested paths")
    # bench_runner glob: family-test/bench/runner/**
    r = run_cli("family-test/bench/runner/helix_bench.py")
    check("bench runner edit → self_test + meta",
          set(r["categories"]) == {"self_test", "meta"},
          f"got {r['categories']}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    print("=== diff-to-category acceptance tests (plan §15c P14) ===")
    test_positive_skill_md()
    test_positive_stop_at()
    test_positive_marker_schema()
    test_negative_unrelated()
    test_unmatched_falls_back_to_full()
    test_multi_rule_pr_unions()
    test_config_validates()
    test_diff_file_mode()
    test_glob_double_star()

    print()
    if FAILURES:
        print(f"FAIL: {len(FAILURES)} failure(s)")
        for f in FAILURES:
            print(f"  - {f}")
        return 1
    print("PASS: all acceptance tests green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
