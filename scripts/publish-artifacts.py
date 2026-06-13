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
from pathlib import Path, PurePosixPath

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
# Inline markdown links and images: [text](target) / ![alt](target).
LINK_RE = re.compile(r"(!?\[[^\]]*\])\(([^)\s]+)\)")
GITHUB_BLOB = "https://github.com/DocumentDrivenDX/helix/blob/main"
EXTERNAL_PREFIXES = ("http://", "https://", "//", "mailto:", "tel:", "data:", "javascript:")


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
            if any(part.startswith(".") for part in md.relative_to(activity_dir).parts):
                continue  # skip scratch/dotfiles (e.g. .plan-codex-review.md)
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


def build_url_map(records: list[dict], source_root: Path) -> dict[Path, str]:
    """Map each published source file (and collection dir) to its site URL."""
    url_map: dict[Path, str] = {}
    for rec in records:
        url = "/artifacts/" + rec["dest_rel"].with_suffix("").as_posix().lower() + "/"
        url_map[rec["src"].resolve()] = url
        if rec["collection"]:
            # A bare directory link (e.g. `adr/`) lands on the collection index.
            url_map[rec["src"].resolve().parent] = f"/artifacts/{rec['collection'].lower()}/"
    return url_map


def rewrite_links(body: str, src_path: Path, repo_root: Path, url_map: dict[Path, str]) -> str:
    """Rewrite intra-repo .md cross-links to site URLs (published) or GitHub blobs.

    Source artifacts cross-reference each other and the wider repo with relative
    `.md` paths that are meaningless on the site. Resolve each against the source
    file: if it points at a published artifact, link to its site URL; if it points
    at any other file that exists in the repo, link to the GitHub source; otherwise
    leave it untouched.
    """
    def repl(m: re.Match) -> str:
        prefix, target = m.group(1), m.group(2)
        frag = ""
        if "#" in target:
            target, _, rest = target.partition("#")
            frag = "#" + rest
        low = target.strip().lower()
        if not target or low.startswith(EXTERNAL_PREFIXES):
            return m.group(0)
        if target.startswith("/"):
            # Absolute filesystem path that leaked into a source doc.
            idx = target.find("docs/helix/")
            if idx == -1:
                return m.group(0)  # genuine site-absolute link
            resolved = (repo_root / target[idx:]).resolve()
        else:
            resolved = (src_path.parent / target).resolve()
        if resolved in url_map:
            return f"{prefix}({url_map[resolved]}{frag})"
        in_repo: Path | None = None
        try:
            if resolved.exists():
                in_repo = resolved.relative_to(repo_root)
        except ValueError:
            in_repo = None  # outside the repo
        if in_repo is None:
            # Many source docs reference repo files with the wrong `../` depth
            # (broken on the site and in the raw repo). Re-anchor the tail at a
            # repo top-level dir if that names a file that actually exists.
            tail = [p for p in PurePosixPath(target).parts if p not in ("..", ".", "/")]
            for base in (repo_root, repo_root / "docs"):
                cand = base.joinpath(*tail) if tail else None
                if cand and cand.exists():
                    in_repo = cand.relative_to(repo_root)
                    break
        if in_repo is not None:
            return f"{prefix}({GITHUB_BLOB}/{in_repo.as_posix()}{frag})"
        return m.group(0)

    return LINK_RE.sub(repl, body)


def render_page(rec: dict, source_root: Path, weight: int,
                repo_root: Path, url_map: dict[Path, str]) -> str:
    text = rec["src"].read_text(encoding="utf-8")
    src_fm, body = split_frontmatter(text)
    body = rewrite_links(body, rec["src"].resolve(), repo_root, url_map)
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
    preamble = (
        "\n> **Example from HELIX's own docs.** This generated page comes from "
        "`docs/helix/`. Use it to see the method in practice; start with the "
        "[artifact-type catalog](/artifact-types/) for reusable templates. "
        "Historical plans and reports may describe retired architecture.\n\n"
    )
    if src_fm.strip():
        preamble += (
            "> **Source identity** (from "
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
    lines = [
        fm,
        f"# {title}",
        "",
        "> **Examples from HELIX's own docs.** These generated pages come from "
        "`docs/helix/`. Use them to see the method in practice; start with the "
        "[artifact-type catalog](/artifact-types/) for reusable templates.",
        "",
    ]
    for it in sorted(items, key=lambda r: r["slug"]):
        # Hugo lowercases page URLs; the link must match or it 404s on a
        # case-sensitive host (it did in production: caps stems vs lowercase dirs).
        lines.append(f"- [{it['title']}]({it['slug'].lower()}/)")
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
        f"Generated examples from the {project} project's own HELIX documents. "
        "Use this section to see how the method looks in practice. To create "
        "documents for your project, start with the "
        "[artifact-type catalog](/artifact-types/). Historical plans and reports "
        "may describe retired architecture.",
        "",
        "Each page is the live content of the corresponding source document; "
        "edits should be made in the source, not here.",
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
            lines.append(f"- [{r['title']}](/artifacts/{r['slug'].lower()}/)")
        for coll_name in sorted(collections.keys()):
            count = len(collections[coll_name])
            lines.append(
                f"- [{coll_name.replace('-', ' ').replace('_', ' ')}](/artifacts/{coll_name.lower()}/) "
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

    repo_root = source.parent.parent  # docs/helix -> repo root
    url_map = build_url_map(records, source)

    # Emit each page.
    for i, rec in enumerate(records):
        out_path = dest / rec["dest_rel"]
        out_path.parent.mkdir(parents=True, exist_ok=True)
        # Weight ordering: by activity number, then by collection, then by slug.
        # i is the sorted-walk index, so it already encodes the right order.
        page = render_page(rec, source, weight=(i + 1) * 10,
                           repo_root=repo_root, url_map=url_map)
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
