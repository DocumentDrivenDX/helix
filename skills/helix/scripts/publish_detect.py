#!/usr/bin/env python3
"""Detect what a repository is, and propose the documentation that follows (publishing.md, Traits).

Usage:
    publish_detect.py [--root DIR] [--format text|json|yaml] [--threshold 0.5]

Scores every trait in `workflows/publish/traits/` against the repository. A trait's signals are
file globs, optionally with a pattern a matching file must contain, each with a weight; a trait's
confidence is the sum of the weights its signals matched (capped at 1). Traits at or above the
threshold are proposed, with the flows, pages, views, watched files, and handling they bring, as a
`publish:` block to confirm into `.helix.yml`. Significant files (`significant.yml`) that no
proposed trait's signals matched are reported as unmapped: the cue to add a trait.

Detection proposes; `.helix.yml` decides. Nothing here writes to the repository.
Requires PyYAML. Exit codes: 0 = ran, 2 = usage error.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

SKIP = {".git", ".ddx", ".claude", "node_modules", ".venv", "venv", "dist", "build", ".helix", "__pycache__", ".tox",
        "site-packages", ".terraform", "public", "resources"}
MAX_BYTES = 1_000_000


@dataclass
class Match:
    signal: str
    weight: float
    files: list[str]


@dataclass
class Score:
    trait: dict
    matches: list[Match] = field(default_factory=list)

    @property
    def confidence(self) -> float:
        return round(min(1.0, sum(m.weight for m in self.matches)), 2)


def catalog_dir() -> Path:
    here = Path(__file__).resolve().parent
    for candidate in (here.parent.parent.parent / "workflows", here.parent / "references"):
        if (candidate / "publish" / "traits").is_dir():
            return candidate / "publish" / "traits"
    sys.exit("publish_detect.py: could not find workflows/publish/traits in the HELIX catalog")


def incidental(path: str) -> bool:
    """A test, fixture, or example: it shows what the repository can do, not what it is."""
    return any(word in part for part in path.split("/")[:-1]
               for word in ("test", "e2e", "fixture", "example", "sample", "demo"))


def repository_files(root: Path) -> list[str]:
    """The files git tracks, else every file under the root, skipping build and vendor trees."""
    tracked = subprocess.run(["git", "-C", str(root), "ls-files"], capture_output=True, text=True)
    if tracked.returncode == 0 and tracked.stdout.strip():
        return sorted(line for line in tracked.stdout.splitlines()
                      if not SKIP & set(line.split("/")) and (root / line).is_file())
    found: list[str] = []
    stack = [root]
    while stack:
        here = stack.pop()
        for entry in here.iterdir():
            if entry.is_dir():
                if entry.name not in SKIP and not entry.is_symlink():
                    stack.append(entry)
            elif entry.is_file():
                found.append(entry.relative_to(root).as_posix())
    return sorted(found)


def matching(files: list[str], pattern: str) -> list[str]:
    """Files a glob matches; `**/` matches any depth, including none."""
    if pattern.startswith("**/"):
        tail = pattern[3:]
        return [f for f in files if fnmatch.fnmatch(f, tail) or fnmatch.fnmatch(f, "*/" + tail)]
    return [f for f in files if fnmatch.fnmatch(f, pattern) and f.count("/") == pattern.count("/")]


def contains(root: Path, path: str, expression: re.Pattern) -> bool:
    target = root / path
    if target.stat().st_size > MAX_BYTES:
        return False
    return bool(expression.search(target.read_text(encoding="utf-8", errors="replace")))


def score(root: Path, files: list[str], trait: dict) -> Score:
    result = Score(trait)
    for signal in trait.get("detect") or []:
        hits = matching(files, signal["files"])
        if signal.get("contains"):
            expression = re.compile(signal["contains"], re.M)
            hits = [f for f in hits if contains(root, f, expression)]
        if hits:
            label = signal["files"] + (f" ~ /{signal['contains']}/" if signal.get("contains") else "")
            result.matches.append(Match(label, float(signal.get("weight", 0.5)), hits))
    return result


def load_traits(directory: Path) -> list[dict]:
    traits = []
    for path in sorted(directory.glob("*.yml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if "id" in data:
            traits.append(data)
    return traits


def unmapped(root: Path, files: list[str], directory: Path, proposed: list[Score]) -> list[str]:
    significant = yaml.safe_load((directory / "significant.yml").read_text(encoding="utf-8"))
    claimed = {f for s in proposed for m in s.matches for f in m.files}
    claimed |= {f for s in proposed for g in s.trait.get("watch") or [] for f in matching(files, g)}
    loose: list[str] = []
    for pattern in significant.get("files") or []:
        hits = matching(files, pattern if "/" in pattern else "**/" + pattern)
        loose += [f for f in hits if f not in claimed]
    return sorted(set(loose))


def proposal(proposed: list[Score]) -> dict:
    """The `publish:` and `handling:` blocks the proposed traits imply."""
    flows: list[str] = []
    views: list[str] = []
    never: list[str] = []
    patterns: list[str] = []
    for s in proposed:
        flows += [f for f in s.trait.get("flows") or [] if f not in flows]
        views += [v for v in s.trait.get("views") or [] if v not in views]
        handling = s.trait.get("handling") or {}
        never += [n for n in handling.get("never_publish") or [] if n not in never]
        patterns += [p for p in handling.get("patterns") or [] if p not in patterns]
    block: dict = {"publish": {"traits": [s.trait["id"] for s in proposed], "flows": flows}}
    if never or patterns:
        block["handling"] = {k: v for k, v in (("never_publish", never), ("patterns", patterns)) if v}
    delegated = [d["page"] for s in proposed for d in s.trait.get("delegates") or []]
    if delegated:
        block["publish"]["delegated"] = delegated
    block["_views"] = views
    return block


def trait_pages(traits: list[dict]) -> dict[str, list[dict]]:
    """The pages the traits add, by flow (the site and the check read these beside the flows')."""
    pages: dict[str, list[dict]] = {}
    for trait in traits:
        for page in trait.get("pages") or []:
            pages.setdefault(page["flow"], []).append({k: v for k, v in page.items() if k != "flow"})
    return pages


def report(root: Path, scores: list[Score], threshold: float, loose: list[str]) -> str:
    lines = [f"Traits detected in {root.name}:", ""]
    for s in sorted(scores, key=lambda s: -s.confidence):
        mark = "PROPOSE" if s.confidence >= threshold else "       "
        lines.append(f"  {mark} {s.confidence:4.2f}  {s.trait['id']:20} {s.trait.get('title', '')}")
        for m in s.matches:
            sample = ", ".join(m.files[:2]) + (f" (+{len(m.files) - 2})" if len(m.files) > 2 else "")
            lines.append(f"                 +{m.weight:.1f} {m.signal}: {sample}")
    proposed = [s for s in scores if s.confidence >= threshold]
    block = proposal(proposed)
    views = block.pop("_views")
    added = trait_pages([s.trait for s in proposed])
    lines += ["", "Proposed for .helix.yml:", ""]
    lines += ["  " + line for line in yaml.safe_dump(block, sort_keys=False).splitlines()]
    lines += ["", f"Views the model should draw: {', '.join(views) or 'none'}"]
    for flow, pages in added.items():
        for page in pages:
            how = f"generated by {page['generated']}" if page.get("generated") else "written"
            lines.append(f"Page added: {flow}/{page['id']} ({page['kind']}, {how})")
    for s in proposed:
        for d in s.trait.get("delegates") or []:
            lines.append(f"Page delegated: {d['page']} to {d['tool']} ({d['covers']}); build it with `{d['build']}`")
    lines += ["", "Significant files no proposed trait claims:" if loose else "Every significant file is claimed."]
    lines += [f"  {f}" for f in loose[:20]] + ([f"  ... {len(loose) - 20} more"] if len(loose) > 20 else [])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--format", choices=("text", "json", "yaml"), default="text")
    args = parser.parse_args()
    root = args.root.resolve()
    directory = catalog_dir()
    files = [f for f in repository_files(root) if not incidental(f)]
    scores = [score(root, files, trait) for trait in load_traits(directory)]
    scores = [s for s in scores if s.matches]
    proposed = [s for s in scores if s.confidence >= args.threshold]
    loose = unmapped(root, files, directory, proposed)
    if args.format == "text":
        print(report(root, scores, args.threshold, loose))
    else:
        data = proposal(proposed) | {
            "confidence": {s.trait["id"]: s.confidence for s in scores},
            "unmapped": loose,
        }
        print(json.dumps(data, indent=2) if args.format == "json" else yaml.safe_dump(data, sort_keys=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
