#!/usr/bin/env python3
"""Pin, check, and materialize the sources a HELIX document cites.

Usage:
    pin-sources.py pin <doc.md>                 write git:<commit> rev on unpinned links
    pin-sources.py check <doc.md>               verify every pinned rev resolves; report drift
    pin-sources.py materialize <doc.md> <dir>   write each pinned source as it was at its rev

Pinned links are `ddx.links` mappings `{id, kind, rev}` whose kind is
informed_by, evaluates, or supported_by. A link resolves locally when some
tracked Markdown file in the document's git repository has that `ddx.id`; a
link with a `graph:` key belongs to another graph and is resolved by the
runtime (reported, never failed). Revisions are `git:<commit>` (content is
recoverable) or `sha256:<hex>` (content is verifiable only).

Exit codes: 0 ok, 1 a pinned source is missing or unresolvable, 2 usage error.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print("error: PyYAML required", file=sys.stderr); sys.exit(2)

PIN_KINDS = {"informed_by", "evaluates", "supported_by"}
FM = re.compile(r"\A---\n(.*?)\n---\n", re.S)


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True).stdout


def frontmatter(text: str) -> dict:
    m = FM.match(text)
    return (yaml.safe_load(m.group(1)) or {}) if m else {}


def repo_of(doc: Path) -> Path:
    return Path(git(doc.parent, "rev-parse", "--show-toplevel").strip())


def index(repo: Path) -> dict[str, str]:
    """ddx.id -> repo-relative path for tracked Markdown files."""
    ids: dict[str, str] = {}
    for rel in git(repo, "ls-files", "*.md").splitlines():
        try:
            fm = frontmatter((repo / rel).read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError):
            continue
        ident = (fm.get("ddx") or {}).get("id") if isinstance(fm, dict) else None
        if ident:
            ids.setdefault(str(ident), rel)
    return ids


def links(doc: Path) -> list[dict]:
    ddx = frontmatter(doc.read_text(encoding="utf-8")).get("ddx") or {}
    return [l for l in ddx.get("links") or [] if isinstance(l, dict) and l.get("kind") in PIN_KINDS]


def pinned_content(repo: Path, rev: str, rel: str) -> bytes | None:
    if rev.startswith("git:"):
        r = subprocess.run(["git", "-C", str(repo), "show", f"{rev[4:]}:{rel}"], capture_output=True)
        return r.stdout if r.returncode == 0 else None
    return None


def main(argv: list[str]) -> int:
    if len(argv) < 3 or argv[1] not in ("pin", "check", "materialize") or (argv[1] == "materialize" and len(argv) != 4):
        print(__doc__, file=sys.stderr); return 2
    cmd, doc = argv[1], Path(argv[2]).resolve()
    repo = repo_of(doc)
    ids = index(repo)
    status = 0
    text = doc.read_text(encoding="utf-8")
    for link in links(doc):
        ident, rev = str(link.get("id")), str(link.get("rev") or "")
        rel = ids.get(ident)
        if link.get("graph") or rel is None:
            where = f"graph {link['graph']}" if link.get("graph") else "not in this repository"
            print(f"external  {ident}: {where}; resolved by the runtime")
            continue
        if cmd == "pin":
            if rev:
                print(f"pinned    {ident} {rev}"); continue
            commit = git(repo, "log", "-1", "--format=%H", "--", rel).strip()
            if not commit:
                print(f"MISSING   {ident}: {rel} has no commit; commit it before pinning"); status = 1; continue
            pat = re.compile(rf"(^\s*-\s*id:\s*{re.escape(ident)}\s*\n(?:\s+\w+:.*\n)*?\s+kind:\s*\S+)", re.M)
            if not pat.search(text):
                print(f"MISSING   {ident}: link not in multi-line form; add rev by hand"); status = 1; continue
            indent = re.search(rf"^(\s*)-\s*id:\s*{re.escape(ident)}", text, re.M).group(1) + "  "
            text = pat.sub(lambda m: m.group(1) + f"\n{indent}rev: git:{commit}", text, count=1)
            print(f"pinned    {ident} git:{commit}")
        else:
            if not rev:
                print(f"UNPINNED  {ident}"); status = 1; continue
            blob = pinned_content(repo, rev, rel)
            if rev.startswith("git:") and blob is None:
                print(f"MISSING   {ident}: {rel} not found at {rev}"); status = 1; continue
            current = (repo / rel).read_bytes() if (repo / rel).exists() else None
            drift = "source has changed since the pin (this document keeps its pinned content)" if blob is not None and current != blob else "unchanged"
            print(f"ok        {ident} {rev}: {drift}")
            if cmd == "materialize" and blob is not None:
                out = Path(argv[3]) / rel
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(blob)
    if cmd == "pin":
        doc.write_text(text, encoding="utf-8")
    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv))
