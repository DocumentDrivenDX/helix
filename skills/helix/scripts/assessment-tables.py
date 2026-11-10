#!/usr/bin/env python3
"""Keep a document's generated tables equal to its structured front matter.

Usage:
    assessment-tables.py [--write] FILE...

A technology assessment's `assessment:` block makes its `## Criteria` table and the tables under
`## Comparison`; a position paper's `recommendations:` list makes the first table under
`## Recommendations`. Tables are found by position; prose between them is never touched. Without
--write the script reports FAIL for each file whose tables differ and exits 1 (a CI check); with
--write it rewrites them. A file without a block is skipped. Block shape: see structured_blocks.py.

Requires PyYAML.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import structured_blocks as sb  # noqa: E402

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

BLOCKS = {"technology-assessment": "assessment", "position-paper": "recommendations"}


def main(argv: list[str]) -> int:
    if yaml is None:
        print("error: PyYAML is required (python3 -m pip install pyyaml)", file=sys.stderr)
        return 2
    write = "--write" in argv
    files = [Path(a) for a in argv if not a.startswith("--")]
    if not files:
        print(__doc__, file=sys.stderr)
        return 2
    status = 0
    for path in files:
        text = path.read_text(encoding="utf-8")
        end = text.find("\n---\n", 4) if text.startswith("---\n") else -1
        if end < 0:
            print(f"skip  {path}: no front matter")
            continue
        raw, body = text[4:end], text[end + 5:]
        fm = yaml.safe_load(raw) or {}
        type_id = (fm.get("ddx") or {}).get("type")
        if BLOCKS.get(type_id) not in fm:
            print(f"skip  {path}: no structured block")
            continue
        problems = []
        sb.check(fm, type_id, path, lambda sev, chk, msg: problems.append(f"{chk}: {msg}") if sev == "blocking" else None)
        if problems:
            print(f"FAIL  {path}: its block is malformed; the tables are not generated")
            for line in problems:
                print(f"        {line}")
            status = 1
            continue
        try:
            new = sb.regenerate(fm, type_id, body, path)
        except (ValueError, KeyError) as err:
            print(f"FAIL  {path}: {err}; run validate-instance.py for the block's findings")
            status = 1
            continue
        if new == body:
            print(f"ok    {path}")
        elif write:
            path.write_text(f"---\n{raw}\n---\n{new}", encoding="utf-8")
            print(f"wrote {path}")
        else:
            print(f"FAIL  {path}: its tables differ from its front matter (run with --write)")
            status = 1
    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
