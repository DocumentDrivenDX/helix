#!/usr/bin/env python3
"""validate_actions — guard the action-prompt surface.

Every bounded action prompt under `workflows/actions/*.md` must be:

  1. well-formed   — its first H1 is `# HELIX Action: <Name>`, the shared
                     contract shape every action follows.
  2. registered    — it is referenced as the explicit path/link form
                     `actions/<stem>.md` in at least one routing/registry surface,
                     so a new action is actually reachable and is not a dangling
                     file. The path form is required (not a bare substring) so a
                     stem that merely appears inside an unrelated word — e.g.
                     `security` inside `security-requirements` — does not count as
                     registration. Registry surfaces:
                       - skills/helix/SKILL.md        (intent -> mode routing)
                       - workflows/REFERENCE.md       (canonical methodology docs)
                       - workflows/QUICKSTART.md      (bounded action prompts)
                       - workflows/workflow.yml       (activity contract_docs)

This closes the process gap where an action could be added without being wired
into any route (silently unreachable) or with a malformed contract. Run by
`just test` via tests/validate-actions.sh.

Exit 0 on success; non-zero with a per-offender report otherwise.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ACTIONS_DIR = REPO_ROOT / "workflows" / "actions"
REGISTRY_FILES = [
    REPO_ROOT / "skills" / "helix" / "SKILL.md",
    REPO_ROOT / "workflows" / "REFERENCE.md",
    REPO_ROOT / "workflows" / "QUICKSTART.md",
    REPO_ROOT / "workflows" / "workflow.yml",
]
H1_CONTRACT = re.compile(r"^#\s+HELIX Action:\s+\S")


def first_h1(text: str) -> str | None:
    for line in text.splitlines():
        if line.startswith("# "):
            return line.strip()
    return None


def main() -> int:
    if not ACTIONS_DIR.is_dir():
        print(f"FAIL: actions directory not found: {ACTIONS_DIR}", file=sys.stderr)
        return 2

    registry = "\n".join(
        f.read_text(encoding="utf-8") for f in REGISTRY_FILES if f.is_file()
    )

    actions = sorted(ACTIONS_DIR.glob("*.md"))
    if not actions:
        print(f"FAIL: no action prompts found under {ACTIONS_DIR}", file=sys.stderr)
        return 2

    malformed: list[str] = []
    unregistered: list[str] = []

    for path in actions:
        stem = path.stem
        h1 = first_h1(path.read_text(encoding="utf-8"))
        if h1 is None or not H1_CONTRACT.match(h1):
            malformed.append(f"{path.relative_to(REPO_ROOT)} — first H1 is {h1!r}, expected '# HELIX Action: <Name>'")
        # registered only via the explicit path/link form `actions/<stem>.md`,
        # never a bare substring (so `security` inside `security-requirements`
        # does not count).
        if f"actions/{stem}.md" not in registry:
            unregistered.append(
                f"{path.relative_to(REPO_ROOT)} — 'actions/{stem}.md' not referenced in any of: "
                + ", ".join(str(f.relative_to(REPO_ROOT)) for f in REGISTRY_FILES)
            )

    ok = not malformed and not unregistered
    if malformed:
        print("Malformed action prompts (bad contract heading):", file=sys.stderr)
        for m in malformed:
            print(f"  - {m}", file=sys.stderr)
    if unregistered:
        print("Unregistered action prompts (not wired into any route):", file=sys.stderr)
        for u in unregistered:
            print(f"  - {u}", file=sys.stderr)

    if ok:
        print(f"OK: {len(actions)} action prompts well-formed and registered.")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
