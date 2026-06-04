#!/usr/bin/env python3
"""Validate the structural shape of helix-family bench fixtures.

Walks tests/fixtures/family/<TNN-slug>/ and asserts each fixture is
well-formed for the future Claude Code runner. Stdlib only.

Required for a normal fixture:
  - README.md
  - plugins-installed.txt
  - workspace/         (directory; may be empty)
  - prompts/           (directory with at least one prompt file)
  - expected/          (directory; one JSON per prompt, same stem)
  - each prompts/NN-name.txt has a matching expected/NN-name.json
  - each expected/*.json parses as valid JSON

Deferred fixtures (README.md frontmatter contains "status: deferred"):
  - only README.md is required; other dirs/files are optional.

Exits 0 if all fixtures pass; 1 otherwise (with a per-fixture failure list).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "family"


def is_deferred(fixture: Path) -> bool:
    readme = fixture / "README.md"
    if not readme.is_file():
        return False
    try:
        text = readme.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    # Look at top frontmatter block for `status: deferred`
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return False
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if line.strip().lower() == "status: deferred":
            return True
    return False


def validate_fixture(fixture: Path) -> list[str]:
    errors: list[str] = []
    name = fixture.name

    readme = fixture / "README.md"
    if not readme.is_file():
        errors.append(f"{name}: missing README.md")
        # Without README we cannot tell deferred from normal; treat as normal.

    if is_deferred(fixture):
        # Deferred fixtures: only README.md required.
        return errors

    plugins_file = fixture / "plugins-installed.txt"
    if not plugins_file.is_file():
        errors.append(f"{name}: missing plugins-installed.txt")

    workspace = fixture / "workspace"
    if not workspace.is_dir():
        errors.append(f"{name}: missing workspace/ directory")

    prompts = fixture / "prompts"
    expected = fixture / "expected"

    if not prompts.is_dir():
        errors.append(f"{name}: missing prompts/ directory")
    if not expected.is_dir():
        errors.append(f"{name}: missing expected/ directory")

    if not (prompts.is_dir() and expected.is_dir()):
        return errors

    prompt_files = sorted(p for p in prompts.iterdir() if p.is_file())
    if not prompt_files:
        errors.append(f"{name}: prompts/ has no prompt files")
        return errors

    for prompt in prompt_files:
        stem = prompt.stem
        expected_json = expected / f"{stem}.json"
        if not expected_json.is_file():
            errors.append(
                f"{name}: prompts/{prompt.name} has no matching expected/{stem}.json"
            )
            continue
        try:
            with expected_json.open("r", encoding="utf-8") as fh:
                json.load(fh)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(
                f"{name}: expected/{expected_json.name} is not valid JSON: {exc}"
            )

    return errors


def main() -> int:
    if not FIXTURE_ROOT.is_dir():
        print(f"FAIL: fixture root not found: {FIXTURE_ROOT}", file=sys.stderr)
        return 1

    fixtures = sorted(p for p in FIXTURE_ROOT.iterdir() if p.is_dir())
    if not fixtures:
        print(f"FAIL: no fixtures under {FIXTURE_ROOT}", file=sys.stderr)
        return 1

    all_errors: list[str] = []
    for fixture in fixtures:
        all_errors.extend(validate_fixture(fixture))

    if all_errors:
        print(f"FAIL: {len(all_errors)} fixture issue(s):", file=sys.stderr)
        for err in all_errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print(f"OK: {len(fixtures)} fixture(s) validated under {FIXTURE_ROOT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
