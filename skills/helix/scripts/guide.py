#!/usr/bin/env python3
"""HELIX guide: point it at a repository and get the documentation that repository needs, kept current.

Usage:
    guide.py init   [--root DIR] [--write]   detect what the repository is; propose (or write) the guide
    guide.py status [--root DIR] [--format text|json]
                                             every page of the guide, and what each needs next
    guide.py build  [--root DIR] [--site DIR] [--no-site]
                                             regenerate what is generated, check everything, build the site
    guide.py check  [--root DIR]             the CI gate: regenerate in memory, fail on anything stale
    guide.py review PAGE [--root DIR] --by NAME
                                             record that a person or an evaluating agent read the page
                                             against its sources and its task

A guide is every page the repository's readers need (workflows/references/guide.md). Its shape comes
from `.helix.yml`: the flows (readers), the traits (what the repository is, which add pages and
delegate others), and the project's own pages. Each page is one of four kinds of work:

  generated   written by publish_generate.py from the repository's structured sources; never by hand
  written     written by an agent from artifacts and code (publish mode), then evaluated (`review`)
  delegated   published by a tool the repository already has; the guide links it
  views       architecture views rendered from the model (architecture_views.py)

`build` and `check` do every deterministic step. The written pages are the agent's: `status` lists
which are missing, stale, or unreviewed, with the reader task and sources for each. Requires PyYAML.
Exit codes: 0 = ok, 1 = something needs doing (check), 2 = usage error.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import publish_check  # noqa: E402
import publish_detect  # noqa: E402
import publish_generate  # noqa: E402
import yaml  # noqa: E402


@dataclass
class GuidePage:
    flow: str
    id: str
    title: str
    kind: str
    work: str  # generated | written | delegated
    path: str
    task: str = ""
    state: str = ""  # missing | stale | unreviewed | current | delegated
    detail: str = ""
    generator: str = ""
    tool: str = ""
    sources: list = field(default_factory=list)


def catalog() -> Path:
    here = Path(__file__).resolve().parent
    for candidate in (here.parent.parent.parent / "workflows", here.parent / "references"):
        if (candidate / "publish" / "flows").is_dir():
            return candidate
    sys.exit("guide.py: could not find the HELIX catalog (workflows/publish)")


def load(path: Path) -> dict:
    return (yaml.safe_load(path.read_text(encoding="utf-8")) or {}) if path.is_file() else {}


def plan(root: Path) -> list[GuidePage]:
    """The guide's pages: each flow's pages, replaced or joined by the traits' and the project's."""
    config = load(root / ".helix.yml")
    publish = config.get("publish") or {}
    out = publish_check.publish_out(config)
    traits = [load(catalog() / "publish" / "traits" / f"{t}.yml") for t in publish.get("traits") or []]
    delegated = {d["page"]: d for t in traits for d in t.get("delegates") or []}
    pages: list[GuidePage] = []
    for flow_id in publish.get("flows") or []:
        flow = load(catalog() / "publish" / "flows" / f"{flow_id}.yml")
        extra = [p for t in traits for p in t.get("pages") or [] if p.get("flow") == flow_id]
        extra += list((publish.get("pages") or {}).get(flow_id) or [])
        replacing = {e["id"]: e for e in extra}
        entries = [replacing.pop(e["id"], e) for e in flow.get("pages") or []] + list(replacing.values())
        for entry in entries:
            key = f"{flow_id}/{entry['id']}"
            page = GuidePage(flow_id, entry["id"], entry.get("title", entry["id"]), entry.get("kind", ""),
                             "generated" if entry.get("generated") else "written",
                             f"{out}/{flow_id}/{entry['id']}.md", entry.get("task", ""),
                             generator=entry.get("generated", ""),
                             sources=[s if isinstance(s, str) else next(iter(s.values()))
                                      for s in entry.get("sources") or []])
            if key in delegated:
                page.work, page.tool = "delegated", delegated[key]["tool"]
                page.detail = f"build it with `{delegated[key]['build']}`"
            pages.append(page)
    return pages


def assess(root: Path, pages: list[GuidePage]) -> None:
    """Each page's state, from the same checks CI runs."""
    for page in pages:
        path = root / page.path
        if page.work == "delegated":
            page.state = "delegated"
            continue
        if not path.is_file():
            page.state = "missing"
            page.detail = (f"run publish_generate.py {page.generator} --page {page.path}"
                           if page.work == "generated" else "write it (publish mode), then review it")
            continue
        parsed = publish_check.parse_page(path)
        findings = publish_check.Findings()
        if parsed and page.work == "generated":
            publish_check.check_generated(parsed, root, findings)
        elif parsed:
            publish_check.check_sources(parsed, root, findings)
        stale = [f for f in findings.items if f["severity"] == "blocking"]
        if stale:
            page.state, page.detail = "stale", "; ".join(f["message"] for f in stale[:2])
        elif page.work == "written" and parsed and "reviewed" not in parsed.meta:
            page.state, page.detail = "unreviewed", "evaluate it against its task and sources, then `guide.py review`"
        elif page.work == "written" and parsed and not parsed.meta["reviewed"].endswith("/" + body_digest(path)):
            page.state, page.detail = "unreviewed", "changed after its evaluation; evaluate it again"
        else:
            page.state = "current"


def views(root: Path) -> tuple[str, list[str]]:
    """The architecture model's state: none, current, or the problems --check reports."""
    import architecture_model
    import architecture_views

    model = architecture_model.default_model(root)
    if not model.is_file():
        return "none", []
    problems = architecture_views.run(check=True, directory=model.parent, model_path=model)
    return ("current" if not problems else "stale"), problems


def regenerate(root: Path, pages: list[GuidePage]) -> list[str]:
    written = []
    for page in pages:
        if page.work != "generated" or page.generator not in publish_generate.GENERATORS:
            continue
        header = (f"<!-- helix:publish flow={page.flow} page={page.id} kind={page.kind or 'reference'} "
                  f"voice=onboarding generated={page.generator} -->")
        text = publish_generate.render(page.generator, root, header, page.title)
        if text is None:
            continue
        target = root / page.path
        if not target.is_file() or target.read_text(encoding="utf-8") != text:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
            written.append(page.path)
    return written


def report(root: Path, pages: list[GuidePage], view_state: tuple[str, list[str]]) -> str:
    mark = {"current": "ok", "missing": "MISSING", "stale": "STALE", "unreviewed": "REVIEW",
            "delegated": "->"}
    lines = [f"Guide for {root.name}: {len(pages)} pages", ""]
    for flow in dict.fromkeys(p.flow for p in pages):
        lines.append(f"  {flow}")
        for p in (p for p in pages if p.flow == flow):
            what = p.tool if p.work == "delegated" else p.work
            lines.append(f"    {mark[p.state]:8} {p.id:22} {p.kind:12} {what:10} {p.detail}")
    state, problems = view_state
    lines += ["", f"  architecture views: {state}"] + [f"    {x}" for x in problems[:5]]
    todo = [p for p in pages if p.state in ("missing", "stale", "unreviewed") and p.work == "written"]
    if todo:
        lines += ["", "For the agent (publish mode), in this order:"]
        for p in sorted(todo, key=lambda p: ("missing", "stale", "unreviewed").index(p.state)):
            lines.append(f"  - {p.state} {p.path}: {p.task or p.title}")
    return "\n".join(lines)


def init(root: Path, write: bool) -> int:
    files = [f for f in publish_detect.repository_files(root) if not publish_detect.incidental(f)]
    directory = catalog() / "publish" / "traits"
    scores = [s for s in (publish_detect.score(root, files, t) for t in publish_detect.load_traits(directory)) if s.matches]
    proposed = [s for s in scores if s.confidence >= 0.5]
    print(publish_detect.report(root, scores, 0.5, publish_detect.unmapped(root, files, directory, proposed)))
    config_path = root / ".helix.yml"
    config = load(config_path)
    if (config.get("publish") or {}).get("traits"):
        print("\n.helix.yml already records traits; compare them with the proposal above.")
        return 0
    block = publish_detect.proposal(proposed)
    block.pop("_views", None)
    block["publish"] = {k: v for k, v in block["publish"].items() if k != "delegated"}
    snippet = "\n# HELIX guide (guide.py init): what this repository is, and who reads its documentation.\n"
    snippet += yaml.safe_dump(block, sort_keys=False)
    if write and not config.get("publish"):
        config_path.write_text(config_path.read_text(encoding="utf-8") + snippet if config_path.is_file() else snippet,
                               encoding="utf-8")
        print(f"\nwrote the proposal to {config_path}")
    else:
        print("\nAdd to .helix.yml (or rerun with --write):\n" + snippet)
    return 0


def body_digest(page: Path) -> str:
    """The page's text below its header: what an evaluation vouches for."""
    parsed = publish_check.parse_page(page)
    return publish_check.digest(parsed.body) if parsed else ""


def review(root: Path, page: Path, by: str) -> int:
    """Record an evaluation, only of a page that passes every check; it lapses when the page changes."""
    parsed = publish_check.parse_page(page)
    if parsed is None:
        print(f"{page}: no helix:publish header", file=sys.stderr)
        return 2
    findings = publish_check.run_check([page], root, False)
    open_items = [f for f in findings.items if f["severity"] == "blocking" or f["check"].startswith("prose.")]
    if open_items:
        for f in open_items:
            print(f"{page}: {f['severity']} {f['check']}: {f['message']}", file=sys.stderr)
        print(f"{page}: not reviewed; fix the findings above first", file=sys.stderr)
        return 1
    text = page.read_text(encoding="utf-8")
    header = publish_check.HEADER.search(text)
    who = re.sub(r"[^A-Za-z0-9_.-]", "-", by)
    stamp = f"reviewed={dt.date.today().isoformat()}/{who}/{body_digest(page)}"
    line = re.sub(r"\s*reviewed=\S+", "", header[0]).replace(" -->", f" {stamp} -->")
    page.write_text(text.replace(header[0], line, 1), encoding="utf-8")
    print(f"{page}: {stamp}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=("init", "status", "build", "check", "review"))
    parser.add_argument("page", nargs="?", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--by", default="")
    parser.add_argument("--site", type=Path)
    parser.add_argument("--no-site", action="store_true")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()
    root = args.root.resolve()
    if args.command == "init":
        return init(root, args.write)
    if args.command == "review":
        if not args.page or not args.by:
            parser.error("review needs PAGE and --by")
        return review(root, args.page.resolve(), args.by)
    pages = plan(root)
    if not pages:
        print("No guide yet: run `guide.py init` first.", file=sys.stderr)
        return 2
    if args.command == "build":
        for path in regenerate(root, pages):
            print(f"regenerated {path}")
        import architecture_model
        import architecture_views

        model = architecture_model.default_model(root)
        if model.is_file():
            problems = architecture_views.run(check=False, directory=model.parent, model_path=model)
            print("architecture views written" if not problems else "\n".join(problems))
    assess(root, pages)
    view_state = views(root)
    if args.format == "json":
        print(json.dumps({"pages": [asdict(p) for p in pages], "views": view_state[0]}, indent=2))
    else:
        print(report(root, pages, view_state))
    out = root / publish_check.publish_out(load(root / ".helix.yml"))
    findings = publish_check.run_check([out], root, False) if out.is_dir() else publish_check.Findings()
    blocking = [f for f in findings.items if f["severity"] == "blocking"]
    if args.command in ("build", "check"):
        print(f"\nchecks: {len(blocking)} blocking, {len(findings.items) - len(blocking)} warnings")
        for f in blocking[:10]:
            print(f"  BLOCKING {f['check']} {Path(f['page']).name}: {f['message']}")
    if args.command == "build" and not args.no_site:
        import publish_site

        site = args.site or root / ".helix" / "site"
        publish_site.build(root, site, True, None)
    if args.command == "check":
        unfinished = [p for p in pages if p.state in ("missing", "stale")]
        return 1 if blocking or unfinished or view_state[0] == "stale" else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
