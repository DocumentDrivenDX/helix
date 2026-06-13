#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

python3 - <<'PY'
from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(".")
STRICT_ROOTS = [
    pathlib.Path("docs/website/content/_index.md"),
    pathlib.Path("docs/website/content/install"),
    pathlib.Path("docs/website/content/platforms"),
    pathlib.Path("docs/website/content/reference"),
    pathlib.Path("docs/website/content/skills"),
    pathlib.Path("docs/website/content/use"),
    pathlib.Path("docs/website/content/why"),
    pathlib.Path("docs/demos"),
]

EXCLUDED_STRICT_PARTS: set[tuple[str, ...]] = set()

PATTERNS = [
    (re.compile(r"/helix-(?:input|frame|align|plan|evolve|review|implement|worker|backfill)\b"), "legacy slash command"),
    (re.compile(r"\balignment[-/ ]and[-/ ]planning skill\b", re.I), "alignment-and-planning skill"),
    (re.compile(r"\balignment skill\b", re.I), "alignment skill"),
    (re.compile(r"\bHELIX_(?:FLOW|METHODOLOGY)\b"), "HELIX env-var routing"),
    (re.compile(r"\bhelix-(?:infra|data|web)\b"), "public sibling flow"),
    (re.compile(r"\bHELIX build mode\b"), "HELIX build mode"),
    (re.compile(r"\bFZO\b"), "Fizeau shorthand in public demos"),
    (re.compile(r"built-in tracker is HELIX's execution layer", re.I), "HELIX-owned tracker wording"),
]


def strict_files() -> list[pathlib.Path]:
    files: set[pathlib.Path] = set()
    for root in STRICT_ROOTS:
        if root.is_file():
            files.add(root)
        elif root.is_dir():
            for suffix in ("*.md", "*.jsonl", "*.yml", "*.yaml"):
                files.update(root.rglob(suffix))
    return sorted(p for p in files if not is_excluded(p))


def is_excluded(path: pathlib.Path) -> bool:
    parts = path.parts
    if parts[:4] == ("docs", "website", "content", "artifacts"):
        return True
    if parts[:4] == ("docs", "website", "content", "research"):
        return True
    return any(parts[: len(ex)] == ex for ex in EXCLUDED_STRICT_PARTS)


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


errors: list[str] = []
for path in strict_files():
    text = path.read_text(encoding="utf-8")
    for pattern, label in PATTERNS:
        for match in pattern.finditer(text):
            line_start = text.rfind("\n", 0, match.start()) + 1
            line_end = text.find("\n", match.end())
            if line_end == -1:
                line_end = len(text)
            line = text[line_start:line_end]
            # Demo directory slugs are stable source paths, not public slash
            # commands. Keep this allowlist narrow so `/helix-align` prose still
            # fails.
            if label == "legacy slash command" and (
                "docs/demos/" in line or "/demos/helix-" in line
            ):
                continue
            # This page must name retired sibling terms only inside the explicit
            # negation that tells readers they are not public skills.
            if (
                label == "public sibling flow"
                and path == pathlib.Path("docs/website/content/use/multiple-flows.md")
                and "not separate public" in line
            ):
                continue
            errors.append(f"{path}:{line_number(text, match.start())}: {label}: {match.group(0)!r}")

demo_dirs = sorted(p for p in pathlib.Path("docs/demos").iterdir() if (p / "session.jsonl").is_file())
for demo_dir in demo_dirs:
    if not (demo_dir / "assertions.yml").is_file():
        errors.append(f"{demo_dir}: missing assertions.yml for displayed demo session")

artifact_files = sorted(pathlib.Path("docs/website/content/artifacts").rglob("*.md"))
for path in artifact_files:
    text = path.read_text(encoding="utf-8")
    if "Dogfood" not in text and "dogfood" not in text:
        errors.append(f"{path}: generated dogfood page lacks dogfood warning")

if errors:
    print("microsite doctrine validation failed:", file=sys.stderr)
    for err in errors:
        print(f"  {err}", file=sys.stderr)
    raise SystemExit(1)

print(f"OK: checked {len(strict_files())} strict files and {len(artifact_files)} dogfood files")
PY
