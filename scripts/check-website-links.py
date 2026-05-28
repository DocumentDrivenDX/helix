#!/usr/bin/env python3
"""Check internal links and image sources in the built Hugo site.

Deterministic, stdlib-only. Walks the built `public/` tree, extracts every
href/src, and verifies that internal targets resolve to a file in `public/`.
External links (http/https/mailto/tel), data URIs, and pure `#fragment`
anchors are skipped. The site is built with a base path (default `/helix/`),
so root-absolute links carry that prefix and are mapped back to `public/`.

Usage:
    python3 scripts/check-website-links.py [--public DIR] [--base-path /helix/]

Exit codes:
    0  all internal links and images resolve
    1  one or more broken internal links/images
    2  public/ not found (build the site first)
"""
from __future__ import annotations

import argparse
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urldefrag


class LinkExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[tuple[str, str]] = []  # (attr_kind, url)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        d = dict(attrs)
        if tag == "a" and d.get("href"):
            self.refs.append(("href", d["href"]))
        elif tag in ("img", "source", "script") and d.get("src"):
            self.refs.append(("src", d["src"]))
        elif tag == "link" and d.get("href"):
            self.refs.append(("href", d["href"]))


def is_external(url: str) -> bool:
    lower = url.strip().lower()
    return (
        lower.startswith(("http://", "https://", "//", "mailto:", "tel:", "data:", "javascript:"))
        or lower == ""
    )


def resolve(url: str, page: Path, public: Path, base_path: str) -> Path | None:
    """Map an internal URL to the file it should resolve to in public/."""
    url, _ = urldefrag(url)
    if not url:
        return None  # pure fragment, same page
    url = unquote(url)
    if url.startswith("/"):
        rel = url[len(base_path):] if url.startswith(base_path) else url.lstrip("/")
        target = public / rel
    else:
        target = (page.parent / url).resolve()
    # Directory URLs (trailing slash or no extension) map to index.html.
    if url.endswith("/") or target.suffix == "":
        target = target / "index.html"
    return target


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--public", type=Path, default=Path("website/public"))
    ap.add_argument("--base-path", default="/helix/")
    args = ap.parse_args()

    public = args.public.resolve()
    if not public.is_dir():
        print(f"FAIL: {public} not found — build the site first (hugo).", file=sys.stderr)
        return 2

    broken: list[str] = []
    checked = 0
    for html_file in sorted(public.rglob("*.html")):
        parser = LinkExtractor()
        parser.feed(html_file.read_text(encoding="utf-8", errors="replace"))
        for _kind, url in parser.refs:
            if is_external(url):
                continue
            target = resolve(url, html_file, public, args.base_path)
            if target is None:
                continue
            checked += 1
            if not target.exists():
                page = html_file.relative_to(public)
                broken.append(f"{page} -> {url}")

    if broken:
        print(f"FAIL: {len(broken)} broken internal link(s)/image(s):", file=sys.stderr)
        for b in sorted(set(broken)):
            print(f"  {b}", file=sys.stderr)
        return 1

    print(f"OK: {checked} internal links/images resolve across {len(list(public.rglob('*.html')))} pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
