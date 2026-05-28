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
    for resource in sorted(SOURCE.glob("*.md")):
        text = resource.read_text(encoding="utf-8")
        source_frontmatter, body = split_frontmatter(text)
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
