"""Publish a project's governed record (its HELIX root) into the site, read-only.

    documentor record [--root DIR] [--dest DIR] [--project NAME]

Reads every Markdown file under the HELIX root, by activity (00-discover/ .. 06-iterate/), and
writes one page per file under the site's record section (`publish.site.record_dir`, default
`record`), with collection indexes and a top index grouped by activity. The activity prefix is
dropped from URLs. Each page shows its source's front matter as its "Source identity"; links to
other published documents become site links, links to other repository files go to the
repository (`publish.site.repo_url`), local images are copied under `media/`, and PDFs a
deliverable lists under `authoring.export` are copied beside it.

Deterministic and idempotent: the section is wiped and rebuilt; the same sources give the same
bytes. `build` runs it when `publish.site.record` is set. The notes on each page, collection, and
the index are `publish.site.record_notes` ({page, collection, index}; `{source}` and `{project}`
are filled in), so a project words its record as it wishes.
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
# `ddx.authoring.export` entries: rendered files a deliverable script lists.
EXPORT_BLOCK_RE = re.compile(r"^\s*export:\s*\n((?:\s*-\s*\S+\s*\n?)+)", re.MULTILINE)
EXPORT_ITEM_RE = re.compile(r"^\s*-\s*(\S+)\s*$", re.MULTILINE)
# Inline markdown links and images: [text](target) / ![alt](target).
LINK_RE = re.compile(r"(!?\[[^\]]*\])\(([^)\s]+)\)")
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


def build_url_map(records: list[dict], source_root: Path, prefix: str) -> dict[Path, str]:
    """Map each published source file (and collection dir) to its site URL."""
    url_map: dict[Path, str] = {}
    for rec in records:
        url = f"/{prefix}/" + rec["dest_rel"].with_suffix("").as_posix().lower() + "/"
        url_map[rec["src"].resolve()] = url
        if rec["collection"]:
            # A bare directory link (e.g. `adr/`) lands on the collection index.
            url_map[rec["src"].resolve().parent] = f"/{prefix}/{rec['collection'].lower()}/"
    return url_map


def publish_images(records: list[dict], source: Path, dest: Path, prefix: str) -> dict[Path, str]:
    """Publish linked local diagram assets while preserving source-relative paths.

    Only image files beneath the artifact root qualify. Mapping links and images
    to the same asset lets readers download editable SVGs alongside PNG previews.
    """
    images: dict[Path, str] = {}
    for rec in records:
        for match in LINK_RE.finditer(rec["src"].read_text(encoding="utf-8")):
            target = match.group(2).split("#", 1)[0]
            if not target or target.startswith("/") or target.lower().startswith(EXTERNAL_PREFIXES):
                continue
            image = (rec["src"].parent / target).resolve()
            if image.suffix.lower() not in {".svg", ".png", ".jpg", ".jpeg", ".webp"} or not image.is_file():
                continue
            try:
                rel = image.relative_to(source.resolve())
            except ValueError:
                continue
            out = dest / "media" / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(image, out)
            images[image] = f"/{prefix}/media/" + rel.as_posix()
    return images


def rewrite_links(body: str, src_path: Path, repo_root: Path, url_map: dict[Path, str], blob: str, helix_rel: str) -> str:
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
            idx = target.find(helix_rel + "/")
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
            return f"{prefix}({blob}/{in_repo.as_posix()}{frag})" if blob else m.group(0)
        return m.group(0)

    return LINK_RE.sub(repl, body)


def export_paths(src_fm: str) -> list[str]:
    """Repo-relative paths listed under `authoring.export` in a source frontmatter."""
    m = EXPORT_BLOCK_RE.search(src_fm)
    if not m:
        return []
    return EXPORT_ITEM_RE.findall(m.group(1))


def publish_exports(rec: dict, src_fm: str, repo_root: Path, dest: Path, prefix: str, blob: str) -> list[tuple[str, str]]:
    """Copy browser-viewable renders (PDF) beside the page; return (label, url) links.

    A PDF listed in `authoring.export` is copied into the page's collection
    directory (a Hugo branch bundle publishes it as-is) under a lowercase name
    so the link matches Hugo's lowercased URLs. Other export formats link to
    the repository. Missing files are skipped without a link.
    """
    links: list[tuple[str, str]] = []
    for rel in export_paths(src_fm):
        src = repo_root / rel
        if not src.is_file():
            continue
        if src.suffix.lower() == ".pdf" and rec["collection"]:
            name = src.name.lower()
            out = dest / rec["collection"] / name
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, out)
            links.append(("PDF", f"/{prefix}/{rec['collection'].lower()}/{name}"))
        else:
            label = src.suffix.lstrip(".").upper() or src.name
            if blob:
                links.append((label, f"{blob}/{PurePosixPath(rel).as_posix()}"))
    return links


def render_page(rec: dict, source_root: Path, weight: int,
                repo_root: Path, url_map: dict[Path, str], dest: Path, opts: dict) -> str:
    text = rec["src"].read_text(encoding="utf-8")
    src_fm, body = split_frontmatter(text)
    body = rewrite_links(body, rec["src"].resolve(), repo_root, url_map, opts["blob"], opts["helix_rel"])
    rel_source = rec["src"].relative_to(source_root).as_posix()
    exports = publish_exports(rec, src_fm, repo_root, dest, opts["prefix"], opts["blob"])

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
    preamble = "\n> " + opts["notes"]["page"] + "\n\n"
    if exports:
        rendered = ", ".join(f"[{label}]({url})" for label, url in exports)
        preamble += (
            "> **Rendered from this script.** The Markdown below is the document "
            f"of record; open the rendered file to see the finished deck: {rendered}.\n\n"
        )
    if src_fm.strip():
        preamble += (
            "> **Source identity** (from "
            f"`{rel_source}`):\n\n```yaml\n{src_fm.rstrip()}\n```\n\n"
        )
    from documentor.schemas import links as schema_links

    page_url = url_map[rec["src"].resolve()]
    preamble += schema_links(rec["src"], repo_root, page_url)
    return fm + preamble + body.lstrip("\n")


def render_collection_index(name: str, items: list[dict], weight: int, opts: dict) -> str:
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
        "> " + opts["notes"]["collection"],
        "",
    ]
    for it in sorted(items, key=lambda r: r["slug"]):
        # Hugo lowercases page URLs; the link must match or it 404s on a
        # case-sensitive host (it did in production: caps stems vs lowercase dirs).
        lines.append(f"- [{it['title']}]({it['slug'].lower()}/)")
    lines.append("")
    return "\n".join(lines)


def render_top_index(records: list[dict], project: str, source: Path, opts: dict) -> str:
    fm = render_frontmatter([
        ("title", yaml_dq(opts["title"])),
        ("weight", "2"),
        ("generated", "true"),
    ])
    lines = [
        fm,
        f"# {project} — {opts['title']}",
        "",
        opts["notes"]["index"],
        "",
        "Each page is the live content of the corresponding source document; "
        "edits should be made in the source, not here.",
        "",
        f"_Auto-generated from `{source.name}/` by `documentor record`._",
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
            lines.append(f"- [{r['title']}](/{opts['prefix']}/{r['slug'].lower()}/)")
        for coll_name in sorted(collections.keys()):
            count = len(collections[coll_name])
            lines.append(
                f"- [{coll_name.replace('-', ' ').replace('_', ' ')}](/{opts['prefix']}/{coll_name.lower()}/) "
                f"_({count} {'item' if count == 1 else 'items'})_"
            )
        lines.append("")
    return "\n".join(lines)


def publish(source: Path, dest: Path, project: str, opts: dict) -> int:
    if not source.is_dir():
        print(f"FAIL: source not found: {source}", file=sys.stderr)
        return 1

    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)

    records = collect_artifacts(source)
    if not records:
        print(f"WARN: no markdown files found under {source}", file=sys.stderr)

    repo_root = opts["repo_root"]
    url_map = build_url_map(records, source, opts["prefix"])
    url_map.update(publish_images(records, source, dest, opts["prefix"]))

    # Emit each page.
    for i, rec in enumerate(records):
        out_path = dest / rec["dest_rel"]
        out_path.parent.mkdir(parents=True, exist_ok=True)
        # Weight ordering: by activity number, then by collection, then by slug.
        # i is the sorted-walk index, so it already encodes the right order.
        page = render_page(rec, source, weight=(i + 1) * 10,
                           repo_root=repo_root, url_map=url_map, dest=dest, opts=opts)
        out_path.write_text(page, encoding="utf-8")

    # Emit collection indexes for each subdirectory that holds files.
    collections: dict[str, list[dict]] = {}
    for r in records:
        if r["collection"]:
            collections.setdefault(r["collection"], []).append(r)
    for coll_name in sorted(collections.keys()):
        idx = render_collection_index(coll_name, collections[coll_name], weight=5, opts=opts)
        (dest / coll_name / "_index.md").write_text(idx, encoding="utf-8")

    # Emit top-level index.
    (dest / "_index.md").write_text(
        render_top_index(records, project, source, opts),
        encoding="utf-8",
    )

    print(f"published {len(records)} artifacts from {source} to {dest}")
    return 0



DEFAULT_NOTES = {
    "page": "**From the governed record.** This page is generated from `{source}`; edit the source, not this page.",
    "collection": "**From the governed record.** These pages are generated from `{source}`.",
    "index": "The {project} project's governed documents (vision, requirements, designs, decisions, tests, and "
             "operations), published read-only. Historical plans and reports may describe retired designs.",
}


def options(root: Path, config: dict, dest_dir: str | None = None) -> tuple[Path, Path, str, dict]:
    """The record's source, destination, project name, and rendering options from `.helix.yml`."""
    from documentor.lib import helix_root

    publish = config.get("publish") or {}
    settings = publish.get("site") or {}
    helix = helix_root(config)
    prefix = str(settings.get("record_dir") or "record").strip("/")
    repo_url = str(settings.get("repo_url") or "").rstrip("/")
    blob = f"{repo_url}/blob/{settings.get('branch', 'main')}" if repo_url else ""
    notes = DEFAULT_NOTES | (settings.get("record_notes") or {})
    project = str(settings.get("title") or root.name)
    notes = {k: v.replace("{source}", helix + "/").replace("{project}", project) for k, v in notes.items()}
    from documentor.site import content_root_for

    dest = Path(dest_dir) if dest_dir else content_root_for(root, config) / prefix
    return root / helix, dest, project, {"prefix": prefix, "blob": blob, "notes": notes, "repo_root": root,
                                         "helix_rel": helix, "title": str(settings.get("record_title") or "Record")}


def main(argv: list[str] | None = None) -> int:
    import argparse

    from documentor.lib import config_of, find_root

    parser = argparse.ArgumentParser(prog="documentor record", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--dest", type=Path, help="the record's directory (default: the site's content root / record_dir)")
    parser.add_argument("--project", help="the project's name in the index (default: site.title, else the directory)")
    args = parser.parse_args(argv)
    root = (args.root or find_root(Path.cwd())).resolve()
    config = config_of(root)
    source, dest, project, opts = options(root, config, str(args.dest) if args.dest else None)
    try:
        return publish(source, dest.resolve(), args.project or project, opts)
    except (ValueError, OSError) as error:
        print(f"documentor record: {error}", file=sys.stderr)
        return 1
