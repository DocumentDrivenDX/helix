#!/usr/bin/env python3
"""Find near-duplicate paragraph pairs across hand-authored site content.

Vale catches token-level slop but not "the same idea said in three places."
This script tokenizes hand-authored .md files into paragraphs, shingles each
into normalized word trigrams, and reports the top N cross-file paragraph
pairs whose Jaccard similarity is above a threshold. Use it to consolidate
restated content into one canonical place + cross-link.

Usage:
    python3 scripts/check-prose-redundancy.py [--threshold 0.25] [--top 25]

Exit codes:
    0  no cross-file pairs above the threshold
    1  one or more pairs above the threshold (printed in descending order)
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

CONTENT_ROOT = Path("docs/website/content")
EXCLUDE_DIRS = {"artifacts", "concerns", "artifact-types", "research"}
MIN_WORDS = 15  # paragraphs shorter than this are skipped (headers, short callouts)
SHINGLE_N = 3   # trigram shingles


def normalize(text: str) -> list[str]:
    text = re.sub(r"`[^`]+`", " ", text)               # code spans
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)  # markdown links → label
    text = re.sub(r"<[^>]+>", " ", text)               # raw HTML
    text = re.sub(r"\W+", " ", text.lower())
    return [w for w in text.split() if len(w) > 2]


def shingles(words: list[str], n: int = SHINGLE_N) -> set[tuple[str, ...]]:
    if len(words) < n:
        return set()
    return {tuple(words[i:i + n]) for i in range(len(words) - n + 1)}


def paragraphs(path: Path) -> list[tuple[str, set[tuple[str, ...]]]]:
    text = path.read_text(encoding="utf-8")
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4:]
    out: list[tuple[str, set[tuple[str, ...]]]] = []
    for block in re.split(r"\n\s*\n", text):
        block = block.strip()
        if not block or block.startswith(("#", "|", "-", "*", ">", "```", "{{")):
            continue
        words = normalize(block)
        if len(words) < MIN_WORDS:
            continue
        sh = shingles(words)
        if sh:
            preview = " ".join(block.split())[:100]
            out.append((preview, sh))
    return out


def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--threshold", type=float, default=0.25)
    ap.add_argument("--top", type=int, default=25)
    args = ap.parse_args()

    if not CONTENT_ROOT.is_dir():
        print(f"FAIL: {CONTENT_ROOT} not found")
        return 1

    items: list[tuple[Path, str, set[tuple[str, ...]]]] = []
    for md in sorted(CONTENT_ROOT.rglob("*.md")):
        rel = md.relative_to(CONTENT_ROOT).parts
        if rel and rel[0] in EXCLUDE_DIRS:
            continue
        for preview, sh in paragraphs(md):
            items.append((md, preview, sh))

    pairs: list[tuple[float, Path, str, Path, str]] = []
    for i, (fa, pa, sa) in enumerate(items):
        for fb, pb, sb in items[i + 1:]:
            if fa == fb:
                continue
            j = jaccard(sa, sb)
            if j >= args.threshold:
                pairs.append((j, fa, pa, fb, pb))
    pairs.sort(reverse=True, key=lambda x: x[0])

    if not pairs:
        print(f"OK: no cross-file paragraph pairs >= {args.threshold} similarity "
              f"({len(items)} paragraphs scanned)")
        return 0

    print(f"FAIL: {len(pairs)} cross-file paragraph pair(s) >= {args.threshold} "
          f"similarity (top {args.top}):")
    for score, fa, pa, fb, pb in pairs[:args.top]:
        print(f"\n  similarity={score:.2f}")
        print(f"  {fa}")
        print(f"    {pa}")
        print(f"  {fb}")
        print(f"    {pb}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
