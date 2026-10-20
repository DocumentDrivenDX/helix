"""Assemble the guide's pages into a site: the repository's own site when it has one, else a new one.

Usage:
    documentor site [--root DIR] [--site DIR] [--target mkdocs|hugo|hextra] [--no-build] [--base-url URL]

Reads the project's `.helix.yml` `publish:` block and the pages under `publish.out` (one directory
per audience), then:

  mkdocs   the repository has a `mkdocs.yml`: the pages are copied under its docs directory
           (`site.content_dir`, default `guide`), with a `nav.yml` fragment to include, and
           nothing else of the site is touched
  hugo     the repository has a Hugo site (`hugo.yaml` or `hugo.toml`, at the root or under
           `website/`): the pages become a section of its content with Hugo front matter
  hextra   the repository has no site: a Hextra project is written to `--site` (default
           `<root>/.helix/site`) with a home page, one section per audience, and the theme as a
           Hugo module (building needs hugo and go, and the network once)

`site.target` in `.helix.yml` chooses; without it the repository's files decide, as above. Each
audience becomes a section with its pages in order; links between pages become site links, links
to repository files resolve to `publish.site.repo_url` when it is set, and referenced images and
HTML files are copied in. The Markdown pages under `publish.out` stay the record; what is emitted
into a site is rebuilt from them, never edited.

Exit codes: 0 = done, 1 = a page could not be read or the build failed, 2 = usage error.
"""

from __future__ import annotations

import argparse
import posixpath
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

from documentor.check import parse_page
from documentor.lib import FENCE, audiences, config_of, find_root, load_audience, load_traits, publish_out

LINK = re.compile(r"(!?\[[^\]]*\]\()([^)\s]+)((?:\s+\"[^\"]*\")?\))")
HREF = re.compile(r'(href=")([^"]+)(")')
ASSET_SUFFIXES = {".png", ".svg", ".jpg", ".jpeg", ".gif", ".webp", ".html", ".pdf"}
HUGO_CONFIGS = ("hugo.yaml", "hugo.yml", "hugo.toml", "config.toml", "config.yaml")


# --- what the repository has ----------------------------------------------------------------------

def mkdocs_config(root: Path) -> Path | None:
    for candidate in (root / "mkdocs.yml", root / "docs" / "mkdocs.yml"):
        if candidate.is_file():
            return candidate
    return None


def hugo_dir(root: Path) -> Path | None:
    for base in (root, root / "website", root / "site", root / "docs"):
        if any((base / name).is_file() for name in HUGO_CONFIGS):
            return base
    return None


def detect_target(root: Path) -> str:
    if mkdocs_config(root):
        return "mkdocs"
    if hugo_dir(root):
        return "hugo"
    return "hextra"


# --- the pages -----------------------------------------------------------------------------------------

def ordered_pages(out: Path, audience_id: str, audience: dict, extra: list) -> list[tuple[str, Path, dict]]:
    """(page id, file, entry) in audience order, then project additions, then any other page."""
    replacing = {entry["id"]: entry for entry in extra or []}
    entries = [replacing.pop(e["id"], e) for e in audience.get("pages") or []] + list(replacing.values())
    seen: set[str] = set()
    pages: list[tuple[str, Path, dict]] = []
    for entry in entries:
        path = out / audience_id / f"{entry['id']}.md"
        if path.is_file() and entry["id"] not in seen:
            pages.append((entry["id"], path, entry))
            seen.add(entry["id"])
    for path in sorted((out / audience_id).glob("*.md")):
        if path.stem not in seen:
            pages.append((path.stem, path, {"id": path.stem}))
    return pages


def collect(root: Path, config: dict) -> list[tuple[str, dict, list[tuple[str, Path, dict]]]]:
    publish = config.get("publish") or {}
    out = root / publish_out(config)
    traits = load_traits(config, root, publish.get("traits") or [])
    sections = []
    for audience_id in audiences(config):
        audience = load_audience(audience_id)
        extra = list((publish.get("pages") or {}).get(audience_id) or [])
        for trait in traits:
            extra += [{k: v for k, v in page.items() if k not in ("audience", "flow")}
                      for page in trait.get("pages") or [] if page.get("audience", page.get("flow")) == audience_id]
        sections.append((audience_id, audience, ordered_pages(out, audience_id, audience, extra)))
    return sections


def delegated_pages(config: dict, root: Path, audience_id: str, audience: dict) -> list[tuple[str, str, str]]:
    """(page id, title, body) for each page a trait or the project delegates to a tool the repository already has."""
    publish = config.get("publish") or {}
    titles = {page["id"]: page.get("title", page["id"]) for page in audience.get("pages") or []}
    delegates = [d for t in load_traits(config, root, publish.get("traits") or []) for d in t.get("delegates") or []]
    delegates += [{"page": k, **v} for k, v in (publish.get("delegate") or {}).items()]
    found = []
    for delegate in delegates:
        part, _, page_id = delegate["page"].partition("/")
        if part != audience_id:
            continue
        body = f"This reference is published by **{delegate['tool']}**"
        body += f", which covers {delegate['covers']}." if delegate.get("covers") else "."
        if delegate.get("url"):
            body += f" [Open it]({delegate['url']})."
        if delegate.get("build"):
            body += f" Build it from the repository with:\n\n```sh\n{delegate['build']}\n```\n"
        found.append((page_id, titles.get(page_id, page_id.replace("-", " ").capitalize()), body + "\n"))
    return found


def page_title(body: str, fallback: str) -> tuple[str, str]:
    """The page's H1 as its title, and the body without it (the site prints the title)."""
    match = re.search(r"^# (.+)$", body, re.M)
    if not match:
        return fallback, body
    return match.group(1).strip(), body[: match.start()] + body[match.end():]


def relative_to(here: str, url: str) -> str:
    """A site-absolute URL made relative to the directory `here`, so a static file works offline."""
    if not url.startswith("/"):
        return url
    path, hash_, anchor = url.partition("#")
    rel = posixpath.relpath(path, here) + ("/" if path.endswith("/") else "")
    return rel + (hash_ + anchor if hash_ else "")


class Linker:
    """Rewrites a page's relative links for the site. `published` maps a page file to its site URL;
    assets are copied under `static_dir` and linked at `/files/...` (prefixed with `prefix`)."""

    def __init__(self, root: Path, static_dir: Path, published: dict[Path, str], repo_url: str, branch: str,
                 prefix: str = "") -> None:
        self.root, self.static_dir, self.published = root, static_dir, published
        self.repo_url, self.branch, self.prefix = repo_url.rstrip("/"), branch, prefix.rstrip("/")

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
            destination = self.static_dir / "files" / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            url = f"{self.prefix}/files/{relative.as_posix()}"
            if resolved.suffix.lower() == ".html":
                html = resolved.read_text(encoding="utf-8")
                here = f"{self.prefix}/files/{relative.parent.as_posix()}/"
                html = HREF.sub(lambda m: m.group(1) + relative_to(here, self.target(resolved, m.group(2))) + m.group(3), html)
                destination.write_text(html, encoding="utf-8")
            else:
                shutil.copy2(resolved, destination)
            return url + suffix
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


def front_matter(data: dict) -> str:
    return "---\n" + yaml.safe_dump(data, sort_keys=False, allow_unicode=True) + "---\n\n"


def sources_block(sources: list[str]) -> str:
    if not sources:
        return ""
    items = "".join(f"<li><code>{s}</code></li>" for s in sources)
    return f'\n\n<details class="guide-sources"><summary>Built from {len(sources)} sources</summary><ul>{items}</ul></details>\n'


# --- Hugo (an existing site, or a new Hextra one) --------------------------------------------------

def emit_hugo(root: Path, config: dict, site_dir: Path, content_dir: str, hextra: bool) -> list[dict]:
    """Write the sections and pages under `<site_dir>/content/<content_dir>`; return the sections."""
    publish = config.get("publish") or {}
    settings = publish.get("site") or {}
    sections = collect(root, config)
    prefix = f"/{content_dir}" if content_dir else ""
    content = site_dir / "content" / content_dir if content_dir else site_dir / "content"
    out = root / publish_out(config)
    if out.resolve().is_relative_to(content.resolve()):
        print(f"documentor site: {content} holds the guide's own pages ({out}); set site.content_dir elsewhere", file=sys.stderr)
        raise SystemExit(2)
    if content.exists():
        shutil.rmtree(content)
    content.mkdir(parents=True)
    published = {path.resolve(): (f"{prefix}/{aid}/" if pid == "index" else f"{prefix}/{aid}/{pid}/")
                 for aid, _, pages in sections for pid, path, _ in pages}
    linker = Linker(root, site_dir / "static", published, settings.get("repo_url", ""), settings.get("branch", "main"), prefix)
    docs = {"type": "docs", "sidebar": {"open": True}} if hextra else {}
    home_sections = []
    for weight, (aid, audience, pages) in enumerate(sections, start=1):
        section_dir = content / aid
        section_dir.mkdir(parents=True, exist_ok=True)
        position = {entry["id"]: i for i, entry in enumerate(audience.get("pages") or [], start=1)}
        listed = []
        for order, (pid, path, entry) in enumerate(pages, start=1):
            page = parse_page(path)
            if page is None:
                print(f"documentor site: {path} has no helix:publish header", file=sys.stderr)
                raise SystemExit(1)
            title, body = page_title(page.body, entry.get("title", pid))
            sources = [spec for spec, _ in page.sources]
            meta = {"title": title, "weight": position.get(pid, 100 + order), "sources": sources,
                    "task": entry.get("task", ""), "kind": page.meta.get("kind", entry.get("kind", ""))} | docs
            lead = ""
            if meta["kind"] and hextra:
                lead += f'<p class="guide-kind">{meta["kind"]}</p>\n\n'
            if meta["task"] and hextra:
                lead += f'<p class="guide-task">{meta["task"]}</p>\n\n'
            text = front_matter(meta) + lead + linker.rewrite(path, body) + sources_block(sources)
            (section_dir / ("_index.md" if pid == "index" else f"{pid}.md")).write_text(text, encoding="utf-8")
            listed.append({"title": title, "url": published[path.resolve()], "task": entry.get("task", "")})
        for pid, title, text in delegated_pages(config, root, aid, audience):
            meta = {"title": title, "weight": position.get(pid, 100 + len(listed)), "kind": "reference"} | docs
            (section_dir / f"{pid}.md").write_text(front_matter(meta) + text, encoding="utf-8")
            listed.append({"title": title, "url": f"{prefix}/{aid}/{pid}/", "task": ""})
        if not (section_dir / "_index.md").exists():
            meta = {"title": audience.get("title", aid), "weight": weight} | docs
            (section_dir / "_index.md").write_text(front_matter(meta) + (audience.get("reader", "") + "\n"), encoding="utf-8")
        home_sections.append({"id": aid, "title": audience.get("title", aid), "reader": audience.get("reader", ""),
                              "url": f"{prefix}/{aid}/", "pages": listed, "weight": weight})
    if content_dir:
        meta = {"title": settings.get("title", "Guide"), "weight": settings.get("weight", 10)} | docs
        (content / "_index.md").write_text(front_matter(meta) + (settings.get("description", "") + "\n"), encoding="utf-8")
    return home_sections


def hue(color: str) -> tuple[int, int]:
    """A hex color's hue and saturation, which Hextra takes as its primary color."""
    import colorsys

    r, g, b = (int(color.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4))
    h, _, s = colorsys.rgb_to_hls(r, g, b)
    return round(h * 360), round(s * 100)


def scaffold_hextra(root: Path, config: dict, site: Path, run_hugo: bool, base_url: str | None) -> int:
    """A new Hextra site from the pages: a home page with a card per audience, one section each."""
    settings = (config.get("publish") or {}).get("site") or {}
    if site.exists():
        shutil.rmtree(site)
    site.mkdir(parents=True)
    sections = emit_hugo(root, config, site, "", hextra=True)
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
    hugo_config = {
        "baseURL": base_url or settings.get("base_url", "/"),
        "title": title,
        "module": {"imports": [{"path": "github.com/imfing/hextra"}]},
        "markup": {"goldmark": {"renderer": {"unsafe": True}}, "highlight": {"noClasses": False}},
        "menu": {"main": menu},
        "params": {"navbar": {"displayTitle": True}, "theme": {"default": "system", "displayToggle": True},
                   "page": {"width": "wide"}, "footer": {"displayPoweredBy": False}},
    }
    (site / "hugo.yaml").write_text(yaml.safe_dump(hugo_config, sort_keys=False, allow_unicode=True), encoding="utf-8")
    (site / "go.mod").write_text("module guide\n\ngo 1.21\n", encoding="utf-8") if not (site / "go.mod").exists() else None
    print(f"wrote {site} (Hextra, {len(list((site / 'content').rglob('*.md')))} pages)")
    if not run_hugo:
        return 0
    hugo_bin = shutil.which("hugo")
    if not hugo_bin or not shutil.which("go"):
        print("documentor site: building a Hextra site needs hugo and go; the project is ready to build", file=sys.stderr)
        return 0
    done = subprocess.run([hugo_bin, "--source", str(site), "--destination", str(site / "public"), "--quiet"], check=False)
    if done.returncode:
        return 1
    print(f"built {site / 'public'}")
    return 0


def into_hugo(root: Path, config: dict, run_hugo: bool) -> int:
    """The pages as a section of the repository's own Hugo site."""
    settings = (config.get("publish") or {}).get("site") or {}
    site_dir = hugo_dir(root)
    assert site_dir is not None
    hextra = any("hextra" in (site_dir / name).read_text(encoding="utf-8", errors="replace")
                 for name in HUGO_CONFIGS if (site_dir / name).is_file())
    sections = emit_hugo(root, config, site_dir, settings.get("content_dir", "guide"), hextra)
    print(f"wrote {sum(len(s['pages']) for s in sections)} pages into {site_dir / 'content' / settings.get('content_dir', 'guide')}"
          f" ({'Hextra' if hextra else 'Hugo'} site)")
    if run_hugo and shutil.which("hugo"):
        done = subprocess.run([shutil.which("hugo"), "--source", str(site_dir), "--quiet"], check=False)
        return 1 if done.returncode else 0
    return 0


# --- mkdocs ---------------------------------------------------------------------------------------------

def into_mkdocs(root: Path, config: dict, run_build: bool) -> int:
    """The pages under the mkdocs docs directory, with a nav fragment to include."""
    settings = (config.get("publish") or {}).get("site") or {}
    mk = mkdocs_config(root)
    assert mk is not None
    mk_config = yaml.load(mk.read_text(encoding="utf-8"), Loader=yaml.BaseLoader) or {}
    docs_dir = mk.parent / str(mk_config.get("docs_dir") or "docs")
    content_dir = settings.get("content_dir", "guide")
    content = docs_dir / content_dir
    out = root / publish_out(config)
    sections = collect(root, config)
    if content.resolve() == out.resolve() or out.resolve().is_relative_to(content.resolve()):
        # The guide already lives inside the mkdocs tree: nothing to copy, only the nav to write, and
        # it names every page of the plan that exists (generated, written, adopted, delegated).
        from documentor.lib import plan

        nav = []
        for aid in audiences(config):
            audience = load_audience(aid)
            entries = []
            for page in plan(config, root):
                if page.audience != aid:
                    continue
                path = root / page.path
                if page.work == "delegated":
                    if page.url and re.match(r"^[a-z]+:", page.url):
                        entries.append({page.title: page.url})
                    elif page.url:
                        # The url is written relative to where the page would sit; the nav wants it
                        # relative to the docs directory.
                        target = (root / page.path).parent / page.url
                        try:
                            entries.append({page.title: Path(posixpath.normpath(str(target))).resolve().relative_to(docs_dir.resolve()).as_posix()})
                        except ValueError:
                            pass
                    continue
                parsed = parse_page(path) if path.is_file() else None
                if parsed is None:
                    continue
                title = page_title(parsed.body, page.title)[0]
                try:
                    entries.append({title: path.resolve().relative_to(docs_dir.resolve()).as_posix()})
                except ValueError:
                    continue  # a page outside the docs directory cannot be in the nav
            nav.append({audience.get("title", aid): entries})
        (out / "nav.yml").write_text("# Include under `nav:` in mkdocs.yml (or let mkdocs-literate-nav read it).\n"
                                     + yaml.safe_dump(nav, sort_keys=False, allow_unicode=True), encoding="utf-8")
        print(f"the pages are already under {docs_dir}; wrote {out / 'nav.yml'}")
        return 0
    if content.exists():
        shutil.rmtree(content)
    content.mkdir(parents=True)
    published = {path.resolve(): f"{aid}/{'index' if pid == 'index' else pid}.md" for aid, _, pages in sections for pid, path, _ in pages}
    nav = []
    for aid, audience, pages in sections:
        section = content / aid
        section.mkdir(parents=True, exist_ok=True)
        entries = []
        for pid, path, entry in pages:
            page = parse_page(path)
            if page is None:
                print(f"documentor site: {path} has no helix:publish header", file=sys.stderr)
                return 1
            name = "index.md" if pid == "index" else f"{pid}.md"
            # Links between pages stay relative (the layout is the same); other links go through the linker.
            local = {p: posixpath.relpath(published[p], aid) for p in published}
            relinker = Linker(root, content, local, settings.get("repo_url", ""), settings.get("branch", "main"))
            text = relinker.rewrite(path, page.body).rstrip("\n") + sources_block([s for s, _ in page.sources])
            (section / name).write_text(text, encoding="utf-8")
            title, _ = page_title(page.body, entry.get("title", pid))
            entries.append({title: f"{content_dir}/{aid}/{name}"})
        for pid, title, body in delegated_pages(config, root, aid, audience):
            (section / f"{pid}.md").write_text(f"# {title}\n\n{body}", encoding="utf-8")
            entries.append({title: f"{content_dir}/{aid}/{pid}.md"})
        nav.append({audience.get("title", aid): entries})
    (content / "nav.yml").write_text(
        "# Include under `nav:` in mkdocs.yml (or let mkdocs-literate-nav read it).\n"
        + yaml.safe_dump(nav, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print(f"wrote {sum(len(p) for _, _, p in sections)} pages into {content} and {content / 'nav.yml'}")
    if run_build and shutil.which("mkdocs"):
        done = subprocess.run(["mkdocs", "build", "--quiet", "-f", str(mk)], check=False)
        return 1 if done.returncode else 0
    return 0


# --- entry -----------------------------------------------------------------------------------------------

def build(root: Path, site: Path, run_build: bool, base_url: str | None, target: str | None = None) -> int:
    config = config_of(root)
    publish = config.get("publish") or {}
    if not publish:
        print("documentor site: .helix.yml has no publish: block", file=sys.stderr)
        return 2
    target = target or (publish.get("site") or {}).get("target") or detect_target(root)
    if target == "mkdocs":
        return into_mkdocs(root, config, run_build)
    if target == "hugo":
        return into_hugo(root, config, run_build)
    return scaffold_hextra(root, config, site, run_build, base_url)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="documentor site", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--site", type=Path)
    parser.add_argument("--target", choices=("mkdocs", "hugo", "hextra"))
    parser.add_argument("--no-build", action="store_true")
    parser.add_argument("--base-url")
    args = parser.parse_args(argv)
    root = (args.root or find_root(Path.cwd())).resolve()
    site = (args.site or root / ".helix" / "site").resolve()
    return build(root, site, not args.no_build, args.base_url, args.target)


if __name__ == "__main__":
    sys.exit(main())
