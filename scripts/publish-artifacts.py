#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""
Publish a project's artifacts into the Hugo microsite.

Reads:  <source>/**/*.md            (default: docs/helix/)
Writes: <dest>/**/*.md               (default: docs/website/content/artifacts/)

The source directory is treated as a HELIX-shaped artifact tree organised by
activity directory (00-discover/, 01-frame/, ..., 06-iterate/). The activity
prefix is dropped from destination URLs (it's metadata, not navigation), so:

    docs/helix/00-discover/product-vision.md
      -> docs/website/content/artifacts/product-vision.md

    docs/helix/02-design/adr/ADR-001-foo.md
      -> docs/website/content/artifacts/adr/ADR-001-foo.md

Each page carries `activity: <Label>` in its frontmatter so the landing page
can still group artifacts by where they live in the HELIX loop.

Design constraints:

- **Deterministic.** Same source bytes produce byte-identical destination
  bytes. Iteration order is sorted; emitted frontmatter is fixed-order; no
  timestamps appear in output.
- **Idempotent.** The destination directory is wiped and rebuilt on every run.
- **Portable.** Defaults match this repo. --source / --dest / --project
  override for any project that follows the same activity-directory shape.

Intended future home: a DDx skill that any HELIX-using project can invoke.

Usage:
  uv run scripts/publish-artifacts.py
  uv run scripts/publish-artifacts.py --source docs/helix --dest docs/website/content/artifacts
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

# Activity directory name in source -> display label.
ACTIVITIES: dict[str, str] = {
    "00-discover": "Discover",
    "01-frame":    "Frame",
    "02-design":   "Design",
    "03-test":     "Test",
    "04-build":    "Build",
    "05-deploy":   "Deploy",
    "06-iterate":  "Iterate",
}

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?\n)---\s*\n", re.DOTALL)
H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)


def split_frontmatter(text: str) -> tuple[str, str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return "", text
    return m.group(1), text[m.end():]


def extract_title(body: str, fallback_stem: str) -> str:
    m = H1_RE.search(body)
    if m:
        return m.group(1).strip()
    return fallback_stem.replace("-", " ").replace("_", " ")


def yaml_dq(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def render_frontmatter(fields: list[tuple[str, str]]) -> str:
    out = ["---"]
    for k, v in fields:
        out.append(f"{k}: {v}")
    out.append("---")
    return "\n".join(out) + "\n"


def collect_artifacts(source: Path) -> list[dict]:
    """Walk source tree and return a sorted list of artifact records.

    Each record:
        {
          "src": Path,                   # absolute source path
          "dest_rel": Path,              # path relative to dest root (no activity prefix)
          "activity_key": str,           # "01-frame"
          "activity_label": str,         # "Frame"
          "collection": str | None,      # "features", "adr", ... or None for top-level
          "slug": str,                   # file stem
          "title": str,                  # H1 or derived from stem
        }
    """
    records: list[dict] = []
    for activity_key, activity_label in ACTIVITIES.items():
        activity_dir = source / activity_key
        if not activity_dir.is_dir():
            continue
        for md in sorted(activity_dir.rglob("*.md")):
            rel = md.relative_to(activity_dir)
            parts = list(rel.parts)
            slug = md.stem
            if len(parts) == 1:
                collection = None
                dest_rel = Path(parts[0])
            else:
                collection = parts[0]
                dest_rel = Path(*parts)

            text = md.read_text(encoding="utf-8")
            _, body = split_frontmatter(text)
            title = extract_title(body, slug)

            records.append({
                "src": md,
                "dest_rel": dest_rel,
                "activity_key": activity_key,
                "activity_label": activity_label,
                "collection": collection,
                "slug": slug,
                "title": title,
            })
    return records


def render_page(rec: dict, source_root: Path, weight: int) -> str:
    text = rec["src"].read_text(encoding="utf-8")
    src_fm, body = split_frontmatter(text)
    rel_source = rec["src"].relative_to(source_root).as_posix()

    fields: list[tuple[str, str]] = [
        ("title", yaml_dq(rec["title"])),
        ("slug", rec["slug"]),
        ("weight", str(weight)),
        ("activity", yaml_dq(rec["activity_label"])),
        ("source", yaml_dq(rel_source)),
        ("generated", "true"),
    ]
    if rec["collection"]:
        fields.append(("collection", rec["collection"]))

    fm = render_frontmatter(fields)
    preamble = ""
    if src_fm.strip():
        preamble = (
            "\n> **Source identity** (from "
            f"`{rel_source}`):\n\n```yaml\n{src_fm.rstrip()}\n```\n\n"
        )
    return fm + preamble + body.lstrip("\n")


def render_collection_index(name: str, items: list[dict], weight: int) -> str:
    title = name.replace("-", " ").replace("_", " ")
    fm = render_frontmatter([
        ("title", yaml_dq(title)),
        ("slug", name),
        ("weight", str(weight)),
        ("generated", "true"),
    ])
    lines = [fm, f"# {title}", ""]
    for it in sorted(items, key=lambda r: r["slug"]):
        lines.append(f"- [{it['title']}]({it['slug']}/)")
    lines.append("")
    return "\n".join(lines)


def render_top_index(records: list[dict], project: str, source: Path) -> str:
    fm = render_frontmatter([
        ("title", yaml_dq("Artifacts")),
        ("weight", "2"),
        ("generated", "true"),
    ])
    lines = [
        fm,
        f"# {project} — Artifacts",
        "",
        f"The actual governing artifacts of the {project} project, organised by "
        "the HELIX activity they belong to. Each page is the live content of the "
        "corresponding source document; edits should be made in the source, not here.",
        "",
        f"_Auto-generated from `{source.name}/` by `scripts/publish-artifacts.py`._",
        "",
    ]
    # Group records by activity. Within each activity, list top-level pages and
    # collection indexes.
    for activity_key, activity_label in ACTIVITIES.items():
        members = [r for r in records if r["activity_key"] == activity_key]
        if not members:
            continue
        lines.append(f"## {activity_label}")
        lines.append("")
        # Top-level singletons first (no collection), then collections.
        singletons = [r for r in members if r["collection"] is None]
        collections: dict[str, list[dict]] = {}
        for r in members:
            if r["collection"]:
                collections.setdefault(r["collection"], []).append(r)

        for r in sorted(singletons, key=lambda r: r["slug"]):
            lines.append(f"- [{r['title']}](/artifacts/{r['slug']}/)")
        for coll_name in sorted(collections.keys()):
            count = len(collections[coll_name])
            lines.append(
                f"- [{coll_name.replace('-', ' ').replace('_', ' ')}](/artifacts/{coll_name}/) "
                f"_({count} {'item' if count == 1 else 'items'})_"
            )
        lines.append("")
    return "\n".join(lines)


def publish(source: Path, dest: Path, project: str) -> int:
    if not source.is_dir():
        print(f"FAIL: source not found: {source}", file=sys.stderr)
        return 1

    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)

    records = collect_artifacts(source)
    if not records:
        print(f"WARN: no markdown files found under {source}", file=sys.stderr)

    # Emit each page.
    for i, rec in enumerate(records):
        out_path = dest / rec["dest_rel"]
        out_path.parent.mkdir(parents=True, exist_ok=True)
        # Weight ordering: by activity number, then by collection, then by slug.
        # i is the sorted-walk index, so it already encodes the right order.
        page = render_page(rec, source, weight=(i + 1) * 10)
        out_path.write_text(page, encoding="utf-8")

    # Emit collection indexes for each subdirectory that holds files.
    collections: dict[str, list[dict]] = {}
    for r in records:
        if r["collection"]:
            collections.setdefault(r["collection"], []).append(r)
    for coll_name in sorted(collections.keys()):
        idx = render_collection_index(coll_name, collections[coll_name], weight=5)
        (dest / coll_name / "_index.md").write_text(idx, encoding="utf-8")

    # Emit top-level index.
    (dest / "_index.md").write_text(
        render_top_index(records, project, source),
        encoding="utf-8",
    )

    print(f"published {len(records)} artifacts from {source} to {dest}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--source", type=Path, default=Path("docs/helix"))
    ap.add_argument("--dest", type=Path, default=Path("docs/website/content/artifacts"))
    ap.add_argument("--project", default="HELIX")
    args = ap.parse_args()
    return publish(args.source.resolve(), args.dest.resolve(), args.project)


if __name__ == "__main__":
    raise SystemExit(main())
