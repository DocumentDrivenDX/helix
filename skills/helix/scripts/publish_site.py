#!/usr/bin/env python3
"""Build a static site from the pages `publish` generated (workflows/references/publishing.md).

Usage:
    publish_site.py [--root DIR] [--site DIR] [--no-build] [--base-url URL]

Reads the project's `.helix.yml` `publish:` block, takes the pages under `publish.out` (one
directory per flow), and writes a Hugo project to `--site` (default `<root>/.helix/site`) using the
self-contained layout in `workflows/publish/site/`: no theme download and no external fonts;
Mermaid diagrams render in the browser. Each flow becomes a section with its pages in flow order.
Links between pages become site links, links to repository files resolve to `publish.site.repo_url`
when set, and referenced images and HTML files are copied in. Runs `hugo` to build `<site>/public`
unless --no-build. The Markdown pages stay the record; the site is rebuilt from them, never edited.

Requires PyYAML. Exit codes: 0 = built, 1 = a page or flow could not be read, 2 = usage error.
"""

from __future__ import annotations

import argparse
import posixpath
import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

sys.path.insert(0, str(Path(__file__).resolve().parent))
from publish_check import FENCE, find_root, parse_page, publish_out  # noqa: E402

LINK = re.compile(r"(!?\[[^\]]*\]\()([^)\s]+)((?:\s+\"[^\"]*\")?\))")
HREF = re.compile(r'(href=")([^"]+)(")')
ASSET_SUFFIXES = {".png", ".svg", ".jpg", ".jpeg", ".gif", ".webp", ".html", ".pdf"}


def catalog_dir() -> Path:
    here = Path(__file__).resolve().parent
    for candidate in (here.parent.parent.parent / "workflows", here.parent / "references"):
        if (candidate / "publish" / "site").is_dir():
            return candidate
    sys.exit("publish_site.py: could not find workflows/publish/site in the HELIX catalog")


def ordered_pages(root: Path, out: Path, flow_id: str, flow: dict, extra: list) -> list[tuple[str, Path, dict]]:
    """(page id, file, flow entry) in flow order, then project additions, then any other page."""
    # A trait's or project's page with a flow page's id replaces it in place (a generated table
    # reference for the flow's written one); the rest follow the flow's pages.
    replacing = {entry["id"]: entry for entry in extra or []}
    entries = [replacing.pop(e["id"], e) for e in flow.get("pages") or []] + list(replacing.values())
    seen: set[str] = set()
    pages: list[tuple[str, Path, dict]] = []
    for entry in entries:
        path = out / flow_id / f"{entry['id']}.md"
        if path.is_file() and entry["id"] not in seen:
            pages.append((entry["id"], path, entry))
            seen.add(entry["id"])
    for path in sorted((out / flow_id).glob("*.md")):
        if path.stem not in seen:
            pages.append((path.stem, path, {"id": path.stem}))
    return pages


def site_url(flow_id: str, page_id: str) -> str:
    return f"/{flow_id}/" if page_id == "index" else f"/{flow_id}/{page_id}/"


def relative_to(here: str, url: str) -> str:
    """A site-absolute URL made relative to the directory `here`, so a static file works offline."""
    if not url.startswith("/"):
        return url
    path, hash_, anchor = url.partition("#")
    rel = posixpath.relpath(path, here) + ("/" if path.endswith("/") else "")
    return rel + (hash_ + anchor if hash_ else "")


class Linker:
    """Rewrites a page's relative links for the site."""

    def __init__(self, root: Path, site: Path, published: dict[Path, str], repo_url: str, branch: str) -> None:
        self.root, self.site, self.published = root, site, published
        self.repo_url, self.branch = repo_url.rstrip("/"), branch

    def target(self, page: Path, raw: str) -> str:
        if re.match(r"^[a-z]+:", raw) or raw.startswith(("/", "#")):
            return raw
        path_part, hash_, anchor = raw.partition("#")
        resolved = (page.parent / path_part).resolve()
        suffix = f"#{anchor}" if hash_ else ""
        if resolved in self.published:
            return self.published[resolved] + suffix
        if resolved.suffix.lower() in ASSET_SUFFIXES and resolved.is_file():
            relative = resolved.relative_to(self.root)
            destination = self.site / "static" / "files" / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            if resolved.suffix.lower() == ".html":
                # A copied HTML page links like a Markdown page: rewrite its relative hrefs too.
                html = resolved.read_text(encoding="utf-8")
                here = f"/files/{relative.parent.as_posix()}/"
                html = HREF.sub(lambda m: m.group(1) + relative_to(here, self.target(resolved, m.group(2))) + m.group(3), html)
                destination.write_text(html, encoding="utf-8")
            else:
                shutil.copy2(resolved, destination)
            return f"/files/{relative.as_posix()}{suffix}"
        if self.repo_url and resolved.exists():
            kind = "tree" if resolved.is_dir() else "blob"
            return f"{self.repo_url}/{kind}/{self.branch}/{resolved.relative_to(self.root).as_posix()}{suffix}"
        return raw

    def rewrite(self, page: Path, body: str) -> str:
        fences: list[str] = []

        def hold(match: re.Match) -> str:
            fences.append(match.group(0))
            return f"\0FENCE{len(fences) - 1}\0"

        held = FENCE.sub(hold, body)
        held = LINK.sub(lambda m: m.group(1) + self.target(page, m.group(2)) + m.group(3), held)
        return re.sub(r"\0FENCE(\d+)\0", lambda m: fences[int(m.group(1))], held)


def front_matter(title: str, weight: int, sources: list[str], extra: dict | None = None) -> str:
    data = {"title": title, "weight": weight, "sources": sources}
    data.update(extra or {})
    return "---\n" + yaml.safe_dump(data, sort_keys=False, allow_unicode=True) + "---\n\n"


def page_title(body: str, fallback: str) -> tuple[str, str]:
    """The page's H1 as its title, and the body without it (the layout prints the title)."""
    match = re.search(r"^# (.+)$", body, re.M)
    if not match:
        return fallback, body
    return match.group(1).strip(), body[: match.start()] + body[match.end():]


def delegated_pages(catalog: Path, publish: dict, flow_id: str, flow: dict) -> list[tuple[str, str, str]]:
    """(page id, title, body) for each page a trait delegates to a tool the repository already has."""
    found = []
    titles = {page["id"]: page.get("title", page["id"]) for page in flow.get("pages") or []}
    for trait_id in publish.get("traits") or []:
        trait = yaml.safe_load((catalog / "publish" / "traits" / f"{trait_id}.yml").read_text(encoding="utf-8")) or {}
        for delegate in trait.get("delegates") or []:
            flow_part, _, page_id = delegate["page"].partition("/")
            if flow_part == flow_id:
                body = (f"This reference is published by **{delegate['tool']}**, which covers "
                        f"{delegate['covers']}. Build it from the repository with:\n\n"
                        f"```sh\n{delegate['build']}\n```\n")
                found.append((page_id, titles.get(page_id, page_id.title()), body))
    return found


def hue(color: str) -> tuple[int, int]:
    """A hex color's hue and saturation, which Hextra takes as its primary color."""
    import colorsys

    r, g, b = (int(color.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4))
    h, _, s = colorsys.rgb_to_hls(r, g, b)
    return round(h * 360), round(s * 100)


def hextra(site: Path, root: Path, settings: dict, sections: list, base_url: str | None, run_hugo: bool) -> int:
    """The same content as a Hextra site: the theme HELIX's own microsite and tablespec's use.

    Hextra comes in as a Hugo module, so building needs Go and the network once; the self-contained
    layout (the default) needs neither.
    """
    for name in ("layouts", "static"):
        shutil.rmtree(site / name, ignore_errors=True)
    for page in (site / "content").rglob("*.md"):
        text = page.read_text(encoding="utf-8")
        head, _, body = text.partition("---\n\n")
        meta = yaml.safe_load(head.strip("-\n")) or {}
        lead = ""
        if meta.get("kind"):
            lead += f'<p class="guide-kind">{meta["kind"]}</p>\n\n'
        if meta.get("task"):
            lead += f'<p class="guide-task">{meta["task"]}</p>\n\n'
        sources = meta.get("sources") or []
        tail = ""
        if sources:
            items = "".join(f"<li><code>{s}</code></li>" for s in sources)
            tail = f'\n\n<details class="guide-sources"><summary>Built from {len(sources)} sources</summary><ul>{items}</ul></details>\n'
        head = head.rstrip("\n") + "\ntype: docs\nsidebar:\n  open: true\n"
        page.write_text(head + "---\n\n" + lead + body + tail, encoding="utf-8")
    title = settings.get("title", root.name)
    cards = "".join(f'  {{{{< card link="{s["url"].strip("/")}/" title="{s["title"]}" subtitle="{s["reader"]}" >}}}}\n'
                    for s in sections)
    home = (f"---\ntitle: {title}\nlayout: hextra-home\n---\n\n"
            f'<div class="hx:mt-6 hx:mb-6">\n{{{{< hextra/hero-headline >}}}}\n  {title}\n{{{{< /hextra/hero-headline >}}}}\n</div>\n\n'
            f'<div class="hx:mb-12">\n{{{{< hextra/hero-subtitle >}}}}\n  {settings.get("description", "")}\n'
            f"{{{{< /hextra/hero-subtitle >}}}}\n</div>\n\n{{{{< cards >}}}}\n{cards}{{{{< /cards >}}}}\n")
    (site / "content" / "_index.md").write_text(home, encoding="utf-8")
    h, s = hue(settings.get("accent", "#2f6f8f"))
    (site / "assets" / "css").mkdir(parents=True, exist_ok=True)
    (site / "assets" / "css" / "custom.css").write_text(
        f":root{{--primary-hue:{h}deg;--primary-saturation:{s}%;}}\n"
        ".guide-kind{text-transform:uppercase;letter-spacing:.06em;font-size:.75rem;font-weight:600;"
        "color:hsl(var(--primary-hue) var(--primary-saturation) 45%);margin:0}\n"
        ".guide-task{font-size:1.1rem;opacity:.75;margin-top:.25rem}\n"
        ".guide-sources{margin-top:2rem;font-size:.85rem;opacity:.8}\n", encoding="utf-8")
    menu = [{"name": s["title"], "pageRef": s["url"], "weight": i} for i, s in enumerate(sections, start=1)]
    if settings.get("repo_url"):
        menu.append({"name": "Repository", "url": settings["repo_url"], "weight": 99})
    config = {
        "baseURL": base_url or settings.get("base_url", "/"),
        "title": title,
        "module": {"imports": [{"path": "github.com/imfing/hextra"}]},
        "markup": {"goldmark": {"renderer": {"unsafe": True}}, "highlight": {"noClasses": False}},
        "menu": {"main": menu},
        "params": {"navbar": {"displayTitle": True}, "theme": {"default": "system", "displayToggle": True},
                   "page": {"width": "wide"}, "footer": {"displayPoweredBy": False}},
    }
    (site / "hugo.yaml").write_text(yaml.safe_dump(config, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print(f"wrote {site} (Hextra, {len(list((site / 'content').rglob('*.md')))} pages)")
    if not run_hugo:
        return 0
    hugo_bin = shutil.which("hugo")
    if not hugo_bin or not shutil.which("go"):
        print("publish_site.py: Hextra needs hugo and go; the Hugo project is ready to build", file=sys.stderr)
        return 0
    subprocess.run([hugo_bin, "mod", "init", "guide"], cwd=site, capture_output=True, check=False)
    done = subprocess.run([hugo_bin, "--source", str(site), "--destination", str(site / "public"), "--quiet"], check=False)
    if done.returncode:
        return 1
    print(f"built {site / 'public'}")
    return 0


def build(root: Path, site: Path, run_hugo: bool, base_url: str | None) -> int:
    config = yaml.safe_load((root / ".helix.yml").read_text(encoding="utf-8")) or {}
    publish = config.get("publish") or {}
    if not publish:
        print("publish_site.py: .helix.yml has no publish: block", file=sys.stderr)
        return 2
    catalog = catalog_dir()
    out = root / publish_out(config)
    settings = publish.get("site") or {}
    flows = []
    for flow_id in publish.get("flows") or []:
        flow = yaml.safe_load((catalog / "publish" / "flows" / f"{flow_id}.yml").read_text(encoding="utf-8")) or {}
        extra = (publish.get("pages") or {}).get(flow_id) or []
        for trait_id in publish.get("traits") or []:
            trait = yaml.safe_load((catalog / "publish" / "traits" / f"{trait_id}.yml").read_text(encoding="utf-8")) or {}
            extra = [*extra, *({k: v for k, v in page.items() if k != "flow"}
                               for page in trait.get("pages") or [] if page["flow"] == flow_id)]
        flows.append((flow_id, flow, ordered_pages(root, out, flow_id, flow, extra)))

    if site.exists():
        shutil.rmtree(site)
    shutil.copytree(catalog / "publish" / "site", site)
    published = {path.resolve(): site_url(fid, pid) for fid, _, pages in flows for pid, path, _ in pages}
    linker = Linker(root, site, published, settings.get("repo_url", ""), settings.get("branch", "main"))

    home_sections = []
    for weight, (flow_id, flow, pages) in enumerate(flows, start=1):
        section_dir = site / "content" / flow_id
        section_dir.mkdir(parents=True, exist_ok=True)
        listed = []
        position = {entry["id"]: i for i, entry in enumerate(flow.get("pages") or [], start=1)}
        for order, (page_id, path, entry) in enumerate(pages, start=1):
            order = position.get(page_id, 100 + order)
            page = parse_page(path)
            if page is None:
                print(f"publish_site.py: {path} has no helix:publish header", file=sys.stderr)
                return 1
            title, body = page_title(page.body, entry.get("title", page_id))
            text = front_matter(title, order, [spec for spec, _ in page.sources],
                                {"task": entry.get("task", ""), "kind": page.meta.get("kind", entry.get("kind", ""))})
            text += linker.rewrite(path, body)
            name = "_index.md" if page_id == "index" else f"{page_id}.md"
            (section_dir / name).write_text(text, encoding="utf-8")
            listed.append({"title": title, "url": site_url(flow_id, page_id), "task": entry.get("task", "")})
        for delegate in delegated_pages(catalog, publish, flow_id, flow):
            page_id, title, text = delegate
            weight = position.get(page_id, 100 + len(listed))
            (section_dir / f"{page_id}.md").write_text(front_matter(title, weight, [], {"kind": "reference"}) + text,
                                                       encoding="utf-8")
            listed.insert(min(weight - 1, len(listed)), {"title": title, "url": site_url(flow_id, page_id), "task": ""})
        if not (section_dir / "_index.md").exists():
            (section_dir / "_index.md").write_text(front_matter(flow.get("title", flow_id), weight, []), encoding="utf-8")
        home_sections.append({"id": flow_id, "title": flow.get("title", flow_id), "reader": flow.get("reader", ""),
                              "url": f"/{flow_id}/", "pages": listed, "weight": weight})

    if settings.get("theme") == "hextra":
        return hextra(site, root, settings, home_sections, base_url, run_hugo)

    hugo = {
        "baseURL": base_url or settings.get("base_url", "/"),
        "title": settings.get("title", root.name),
        "relativeURLs": True,
        "disableKinds": ["taxonomy", "term", "RSS", "sitemap"],
        "markup": {"goldmark": {"renderer": {"unsafe": True}}, "highlight": {"noClasses": False}},
        "params": {"accent": settings.get("accent", "#2f6f8f"), "repo_url": settings.get("repo_url", ""),
                   "description": settings.get("description", ""), "sections": home_sections},
    }
    (site / "hugo.yaml").write_text(yaml.safe_dump(hugo, sort_keys=False, allow_unicode=True), encoding="utf-8")
    (site / "content" / "_index.md").write_text(front_matter(hugo["title"], 0, []), encoding="utf-8")
    print(f"wrote {site} ({sum(len(p) for _, _, p in flows)} pages in {len(flows)} sections)")

    if run_hugo:
        hugo_bin = shutil.which("hugo")
        if not hugo_bin:
            print("publish_site.py: hugo is not installed; the Hugo project is ready to build", file=sys.stderr)
            return 0
        done = subprocess.run([hugo_bin, "--source", str(site), "--destination", str(site / "public"), "--quiet"], check=False)
        if done.returncode:
            return 1
        print(f"built {site / 'public'}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--site", type=Path)
    parser.add_argument("--no-build", action="store_true")
    parser.add_argument("--base-url")
    args = parser.parse_args()
    if yaml is None:
        print("publish_site.py: PyYAML is required", file=sys.stderr)
        return 2
    root = (args.root or find_root(Path.cwd())).resolve()
    site = (args.site or root / ".helix" / "site").resolve()
    return build(root, site, not args.no_build, args.base_url)


if __name__ == "__main__":
    sys.exit(main())
