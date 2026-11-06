#!/usr/bin/env python3
"""Check or set every version shipped together in a HELIX release."""
import argparse
import json
import hashlib
from pathlib import Path
import re
import sys


def release_version(tag):
    if not re.fullmatch(r"v\d+\.\d+\.\d+", tag):
        raise ValueError("expected a stable release tag vX.Y.Z")
    return tag[1:]


def synchronize(root, tag, write=False):
    version = release_version(tag)
    paths = [".claude-plugin/plugin.json", ".codex-plugin/plugin.json",
             ".claude-plugin/marketplace.json"]
    changes = []
    for name in paths:
        path = root / name
        data = json.loads(path.read_text())
        target = (next(p for p in data["plugins"] if p["name"] == "helix")
                  if name.endswith("marketplace.json") else data)
        actual = target["version"]
        target["version"] = version
        changes.append((path, actual, json.dumps(data, indent=2, ensure_ascii=False) + "\n"))
    for name, pattern in [
        ("tools/documentor/pyproject.toml", r'^version = "([^"]+)"$'),
        ("tools/documentor/src/documentor/__init__.py", r'^__version__ = "([^"]+)"$'),
        ("tools/documentor/uv.lock", r'(?<=name = "documentor"\n)version = "([^"]+)"'),
    ]:
        path = root / name
        text = path.read_text()
        match = re.search(pattern, text, re.MULTILINE)
        if not match:
            raise ValueError(f"{name}: version field missing")
        changes.append((path, match[1], text[:match.start(1)] + version + text[match.end(1):]))
    mismatches = []
    stamps = {}
    for path, actual, content in changes:
        if actual != version:
            mismatches.append(f"{path.relative_to(root)}: {actual} != {version}")
            if write:
                # Only version metadata changed. Carry forward source evidence
                # when its old digest was current; stale evidence stays stale.
                def digest(text):
                    normalized = "\n".join(line.rstrip() for line in text.strip().splitlines())
                    return hashlib.sha256(normalized.encode()).hexdigest()[:16]
                stamps[path.resolve()] = (digest(path.read_text()), digest(content))
                path.write_text(content)
    if write:
        docroot = root / "tools/documentor"
        for page in (docroot / "docs/guide").rglob("*.md"):
            def refresh(match):
                source, recorded = match.groups()
                pair = stamps.get((docroot / source).resolve())
                if pair and recorded == pair[0]:
                    return f"<!-- helix:source {source} sha256:{pair[1]} -->"
                return match[0]
            text = page.read_text()
            updated = re.sub(r"<!-- helix:source (\S+) sha256:([a-f0-9]+) -->", refresh, text)
            if updated != text:
                page.write_text(updated)
    if mismatches and not write:
        raise ValueError("release version mismatch:\n" + "\n".join(mismatches))
    return mismatches


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tag")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    try:
        synchronize(Path.cwd(), args.tag, args.write)
    except (ValueError, KeyError, StopIteration, OSError) as error:
        print(str(error), file=sys.stderr)
        return 1
    print(f"OK: all release versions match {args.tag}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
