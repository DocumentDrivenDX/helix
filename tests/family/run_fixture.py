#!/usr/bin/env python3
"""DRY-RUN runner for helix-family bench fixtures.

Loads tests/fixtures/family/<TNN-slug>/ and prints the command shape that
WOULD be invoked against Claude Code, plus the per-prompt expectations
parsed from expected/*.json. Does NOT execute claude — cross-skill
resource resolution is still open, so we just verify the fixture is
well-formed for a future real run.

Usage:
  python3 tests/family/run_fixture.py T01-library-only

Writes a stub report at /tmp/fixture-runner-<TNN>.txt.
Exit 0 if the fixture is well-formed; 1 otherwise.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "family"
TNN_RE = re.compile(r"^(T\d+[a-z]?)")


def fail(msg: str) -> int:
    print(f"FAIL: {msg}", file=sys.stderr)
    return 1


def is_deferred(fixture: Path) -> bool:
    readme = fixture / "README.md"
    if not readme.is_file():
        return False
    text = readme.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return False
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if line.strip().lower() == "status: deferred":
            return True
    return False


def tnn_of(name: str) -> str:
    m = TNN_RE.match(name)
    return m.group(1) if m else name


def short_expectation(payload: dict) -> str:
    if "assert" in payload:
        return f"assert={payload['assert']}"
    keys = sorted(payload.keys())
    return f"keys={keys}"


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: run_fixture.py <FIXTURE_NAME>", file=sys.stderr)
        return 1

    fixture_name = argv[1]
    fixture = FIXTURE_ROOT / fixture_name
    if not fixture.is_dir():
        return fail(f"fixture not found: {fixture}")

    tnn = tnn_of(fixture_name)
    report_path = Path("/tmp") / f"fixture-runner-{tnn}.txt"
    report_lines: list[str] = []

    def emit(line: str) -> None:
        print(line)
        report_lines.append(line)

    emit(f"# Fixture dry-run: {fixture_name}")
    emit(f"# Fixture path: {fixture}")

    if is_deferred(fixture):
        emit("status: deferred")
        emit("DRY-RUN: would skip execution (fixture marked deferred)")
        report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
        emit(f"# Report written: {report_path}")
        return 0

    plugins_file = fixture / "plugins-installed.txt"
    if not plugins_file.is_file():
        return fail(f"{fixture_name}: missing plugins-installed.txt")
    plugins = [
        line.strip()
        for line in plugins_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    if not plugins:
        return fail(f"{fixture_name}: plugins-installed.txt has no plugin entries")

    workspace = fixture / "workspace"
    if not workspace.is_dir():
        return fail(f"{fixture_name}: missing workspace/ directory")

    prompts_dir = fixture / "prompts"
    expected_dir = fixture / "expected"
    if not prompts_dir.is_dir() or not expected_dir.is_dir():
        return fail(f"{fixture_name}: prompts/ and expected/ must both exist")

    prompts = sorted(p for p in prompts_dir.iterdir() if p.is_file())
    if not prompts:
        return fail(f"{fixture_name}: prompts/ is empty")

    emit(f"plugins: {plugins}")
    emit(f"workspace: {workspace}")
    emit(f"prompts: {len(prompts)}")

    mounted_plugins = "<mounted-plugins-from-monorepo>"
    errors: list[str] = []

    for prompt in prompts:
        stem = prompt.stem
        expected_json = expected_dir / f"{stem}.json"
        if not expected_json.is_file():
            errors.append(f"prompt {prompt.name}: no matching expected/{stem}.json")
            continue
        try:
            payload = json.loads(expected_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"expected/{expected_json.name}: invalid JSON: {exc}")
            continue

        cmd = (
            f"claude --plugin-dir {mounted_plugins} "
            f"--workspace {workspace} < {prompt}"
        )
        emit("")
        emit(f"## prompt: {prompt.name}")
        emit(f"  cmd: {cmd}")
        emit(f"  expectation: {short_expectation(payload)}")
        emit(f"DRY-RUN: would assert {short_expectation(payload)}")

    if errors:
        for err in errors:
            print(f"FAIL: {fixture_name}: {err}", file=sys.stderr)
        report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
        return 1

    emit("")
    emit("DRY-RUN: fixture is well-formed for future real run")
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    emit(f"# Report written: {report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
