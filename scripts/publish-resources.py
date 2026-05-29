#!/usr/bin/env python3
"""Publish docs/resources into the Hugo research section."""
from __future__ import annotations

import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "resources"
DEST = ROOT / "docs" / "website" / "content" / "research"
FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?\n)---\s*\n", re.DOTALL)
H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
LINK_RE = re.compile(r"(!?\[[^\]]*\])\(([^)\s]+)\)")
EXTERNAL_PREFIXES = ("http://", "https://", "//", "mailto:", "tel:", "data:", "javascript:")


def rewrite_links(body: str, stems: set[str]) -> str:
    """Rewrite sibling `*.md` cross-links to their /research/<slug>/ site URL."""
    def repl(m: re.Match) -> str:
        prefix, target = m.group(1), m.group(2)
        frag = ""
        if "#" in target:
            target, _, rest = target.partition("#")
            frag = "#" + rest
        low = target.strip().lower()
        if not target or low.startswith(EXTERNAL_PREFIXES) or target.startswith("/"):
            return m.group(0)
        name = target.rsplit("/", 1)[-1]
        if name.endswith(".md") and name[:-3] in stems:
            return f"{prefix}(/research/{name[:-3]}/{frag})"
        return m.group(0)

    return LINK_RE.sub(repl, body)


def split_frontmatter(text: str) -> tuple[str, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return "", text
    return match.group(1), text[match.end():]


def extract_title(body: str, fallback: str) -> str:
    match = H1_RE.search(body)
    if match:
        return match.group(1).strip()
    return fallback.replace("-", " ").replace("_", " ").title()


def yaml_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def main() -> int:
    DEST.mkdir(parents=True, exist_ok=True)
    for existing in DEST.glob("*.md"):
        if existing.name != "_index.md":
            existing.unlink()
    stems = {r.stem for r in SOURCE.glob("*.md")}
    for resource in sorted(SOURCE.glob("*.md")):
        text = resource.read_text(encoding="utf-8")
        source_frontmatter, body = split_frontmatter(text)
        body = rewrite_links(body, stems)
        title = extract_title(body, resource.stem)
        frontmatter = [
            "---",
            f"title: {yaml_quote(title)}",
            f"slug: {resource.stem}",
            "generated: true",
            "---",
            "",
        ]
        preamble = ""
        if source_frontmatter.strip():
            preamble = (
                "> **Source identity**:\n\n"
                f"```yaml\n{source_frontmatter.rstrip()}\n```\n\n"
            )
        (DEST / resource.name).write_text(
            "\n".join(frontmatter) + preamble + body.lstrip("\n"),
            encoding="utf-8",
        )
    print(f"Published {len(list(SOURCE.glob('*.md')))} resources -> {DEST.relative_to(ROOT)}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
