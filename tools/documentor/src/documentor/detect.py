#!/usr/bin/env python3
"""Detect what a repository is, and propose the documentation that follows (publishing.md, Traits).

Usage:
    documentor detect [--root DIR] [--format text|json|yaml] [--threshold 0.5]

Scores every trait in the catalog (and the project's own, `publish.traits_dir`) against the repository. A trait's signals are
file globs, optionally with a pattern a matching file must contain, each with a weight; a trait's
confidence is the sum of the weights its signals matched (capped at 1). Traits at or above the
threshold are proposed, with the flows, pages, views, watched files, and handling they bring, as a
`publish:` block to confirm into `.helix.yml`. Significant files (`significant.yml`) that no
proposed trait's signals matched are reported as unmapped: the cue to add a trait.

Detection proposes; `.helix.yml` decides. Nothing here writes to the repository.
Exit codes: 0 = ran, 2 = usage error.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from documentor.lib import config_of, helix_root, incidental, load_traits, matching, repository_files, significant

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



def unmapped(root: Path, files: list[str], proposed: list[Score]) -> list[str]:
    claimed = {f for s in proposed for m in s.matches for f in m.files}
    claimed |= {f for s in proposed for g in s.trait.get("watch") or [] for f in matching(files, g)}
    loose: list[str] = []
    for pattern in significant():
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
        flows += [f for f in s.trait.get("audiences") or s.trait.get("flows") or [] if f not in flows]
        views += [v for v in s.trait.get("views") or [] if v not in views]
        handling = s.trait.get("handling") or {}
        never += [n for n in handling.get("never_publish") or [] if n not in never]
        patterns += [p for p in handling.get("patterns") or [] if p not in patterns]
    block: dict = {"publish": {"traits": [s.trait["id"] for s in proposed], "audiences": flows}}
    if never or patterns:
        block["handling"] = {k: v for k, v in (("never_publish", never), ("patterns", patterns)) if v}
    delegated = [d["page"] for s in proposed for d in s.trait.get("delegates") or []]
    if delegated:
        block["publish"]["delegated"] = delegated
    block["_views"] = views
    return block



def project_profile(root: Path, files: list[str], block: dict) -> None:
    """Conservative init suggestions; the operator's recorded publish block remains authoritative."""
    publish = block["publish"]
    design_root = helix_root(config_of(root)).rstrip("/") + "/"
    if any(f.startswith(design_root) and f.endswith(".md") for f in files):
        code = [f for f in files if Path(f).suffix in {".py", ".go", ".ts", ".tsx", ".js", ".rs", ".java", ".cs"}
                and not f.startswith(("docs/", "scripts/", "tests/", ".", "workflows/"))]
        if not code:
            publish["profile"] = "design-stage"
            publish.setdefault("audiences", [])
            if not publish["audiences"]:
                publish["audiences"].append("developer")
            publish["skip"] = ["developer/walkthrough", "developer/developer-guide"]
    pipeline = any(Path(f).name in {"dbt_project.yml", "pipeline.yaml", "pipeline.yml"} for f in files)
    pipeline |= any("pipeline" in t or t in {"dbt", "databricks-jobs"} for t in publish.get("traits", []))
    if "umf-tablespec" in publish.get("traits", []) and not pipeline:
        publish["data_mode"] = "operational"
        publish.setdefault("skip", []).extend(["data/lineage", "data/using", "data/metrics"])


def trait_pages(traits: list[dict]) -> dict[str, list[dict]]:
    """The pages the traits add, by audience."""
    pages: dict[str, list[dict]] = {}
    for trait in traits:
        for page in trait.get("pages") or []:
            pages.setdefault(page.get("audience", page.get("flow")), []).append(
                {k: v for k, v in page.items() if k not in ("audience", "flow")})
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="documentor detect", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--format", choices=("text", "json", "yaml"), default="text")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    files = [f for f in repository_files(root) if not incidental(f)]
    scores = [score(root, files, trait) for trait in load_traits(config_of(root), root)]
    scores = [s for s in scores if s.matches]
    proposed = [s for s in scores if s.confidence >= args.threshold]
    loose = unmapped(root, files, proposed)
    if args.format == "text":
        print(report(root, scores, args.threshold, loose))
    else:
        block = proposal(proposed)
        project_profile(root, files, block)
        data = block | {
            "confidence": {s.trait["id"]: s.confidence for s in scores},
            "unmapped": loose,
        }
        print(json.dumps(data, indent=2) if args.format == "json" else yaml.safe_dump(data, sort_keys=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
