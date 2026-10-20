"""documentor: point it at a repository and get the documentation that repository needs, kept current.

Usage:
    documentor init    [--root DIR] [--write]      detect what the repository is; propose (or write) the guide
    documentor status  [--root DIR] [--format text|json]
                                                  every page of the guide, and what each needs next
    documentor build   [--root DIR] [--site DIR] [--no-site] [--write]
                                                  regenerate what is generated, check everything, build the site;
                                                  with --write, write the written pages first (as `write`)
    documentor write   [PAGE] [--root DIR] [--model M] [--reviewer-model M] [--agent CMD] [--dry-run]
                                                  write the missing and stale pages with an agent, and evaluate
                                                  them with a second one on another model (ADR-003)
    documentor check   [--root DIR]                the CI gate: regenerate in memory, fail on anything behind
    documentor review  PAGE --by NAME [--root DIR] record that a person or an evaluating agent read the page
                                                  against its sources and its task
    documentor adopt   PAGE --audience ID [--kind KIND] [--source SPEC ...] [--root DIR]
                                                  bring a hand-written page under the guide, unchanged
    documentor check-pages | stamp | detect | generate | site | views | present | estate ...
                                                  the tools, each with its own --help
    documentor --version

A guide is every page the repository's readers need (HELIX's `publishing.md`). Its shape comes from
`.helix.yml`: the audiences (readers), the traits (what the repository is, which add pages and
delegate others), and the project's own pages. Each page is one of five kinds of work:

  generated   written by a generator (packaged, or the project's own command); never by hand
  views       architecture views rendered from the model
  written     written by an agent from artifacts and code (HELIX guide mode), then evaluated (`review`)
  existing    a hand-written page the project already had, adopted with its header (`adopt`)
  delegated   published by a tool the repository already has; the guide links it

`build` and `check` do every deterministic step. The written pages are the agent's: `status` lists
which are missing, stale, or unreviewed, with the reader task and sources for each.
Exit codes: 0 = ok, 1 = something needs doing (check), 2 = usage error.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from dataclasses import asdict
from pathlib import Path

import yaml

from documentor import __version__, check, detect, generate
from documentor.lib import (
    GAP,
    HEADER,
    SCHEMA,
    PagePlan,
    audiences,
    config_of,
    helix_version,
    incidental,
    load_traits,
    plan,
    publish_out,
    repository_files,
)

TOOLS = ("check-pages", "stamp", "detect", "generate", "site", "views", "present", "estate")
PHASES = ("00-discover", "01-frame", "02-design", "03-test", "04-build", "05-deploy", "06-iterate")


# --- state ----------------------------------------------------------------------------------------

def assess(root: Path, config: dict, pages: list[PagePlan]) -> None:
    """Each page's state, from the same checks CI runs."""
    generate.load_plugins()
    for page in pages:
        if page.work == "generated" and not (root / page.path).is_file() and "empty" not in page.entry:
            if page.generator in generate.GENERATORS and not generate.GENERATORS[page.generator](root, {})[0]:
                page.entry["empty"] = True
        path = root / page.path
        if page.work == "delegated":
            page.entry["state"] = "delegated"
            page.entry["detail"] = f"build it with `{page.build}`" if page.build else page.tool
            continue
        if not path.is_file():
            if page.work == "generated" and page.entry.get("empty"):
                page.entry["state"] = "empty"
                page.entry["detail"] = "nothing to generate from; add the source or skip the page in .helix.yml"
                continue
            page.entry["state"] = "missing"
            page.entry["detail"] = ("run `documentor build`" if page.work == "generated"
                                    else "write it (`documentor write`, or HELIX guide mode), then review it")
            continue
        parsed = check.parse_page(path)
        findings = check.Findings()
        if parsed is None:
            page.entry["state"] = "unadopted" if page.work == "existing" else "missing"
            page.entry["detail"] = (f"run `documentor adopt {page.path} --audience {page.audience}`"
                                    if page.work == "existing" else "it has no helix:publish header")
            continue
        if page.work == "generated":
            check.check_generated(parsed, root, config, findings)
        else:
            check.check_sources(parsed, root, findings)
        stale = [f for f in findings.items if f["severity"] == "blocking"]
        if stale:
            page.entry["state"], page.entry["detail"] = "stale", "; ".join(f["message"] for f in stale[:2])
        elif page.work != "generated" and "reviewed" not in parsed.meta:
            page.entry["state"], page.entry["detail"] = "unreviewed", "evaluate it against its task and sources, then `documentor review`"
        elif page.work != "generated" and not parsed.meta["reviewed"].endswith("/" + check.body_digest(path)):
            page.entry["state"], page.entry["detail"] = "unreviewed", "changed after its evaluation; evaluate it again"
        else:
            page.entry["state"], page.entry["detail"] = "current", ""
        gaps = GAP.findall(path.read_text(encoding="utf-8"))
        if gaps:
            page.entry["gaps"] = gaps
            page.entry["detail"] = "; ".join(filter(None, [page.entry["detail"], f"written without {', '.join(gaps)}"]))


def views_dir(root: Path, config: dict, model: Path) -> Path:
    """Where `build` writes the architecture views: a generated page under the guide (default), or,
    when `publish.views: artifact`, between the markers in the model's own documents (a project that
    keeps its views inside its architecture record, as its own decision)."""
    if (config.get("publish") or {}).get("views") == "artifact":
        return model.parent
    return root / publish_out(config) / "architecture-views"


def views(root: Path, config: dict, write: bool) -> tuple[str, list[str]]:
    """The architecture model's state: none, current, or the problems the check reports."""
    from documentor.architecture import model as architecture_model
    from documentor.architecture import views as architecture_views

    model = architecture_model.default_model(root)
    if not model.is_file():
        return "none", []
    directory = views_dir(root, config, model)
    create = directory != model.parent
    problems = architecture_views.run(check=not write, directory=directory, model_path=model, create=create)
    if write and not problems:
        problems = architecture_views.run(check=True, directory=directory, model_path=model, create=create)
    return ("current" if not problems else "stale"), problems


def regenerate(root: Path, config: dict, pages: list[PagePlan]) -> list[str]:
    written = []
    generate.load_plugins()
    for page in pages:
        if page.work != "generated":
            continue
        header = (f"<!-- helix:publish audience={page.audience} page={page.id} kind={page.kind or 'reference'} "
                  f"voice=onboarding generated={'command' if page.command else page.generator} -->")
        if page.command:
            text = generate.render_command(page.command, page.sources, root, header, page.title)
        elif page.generator in generate.GENERATORS:
            text = generate.render(page.generator, root, header, page.title)
        else:
            print(f"{page.path}: no generator named {page.generator}", file=sys.stderr)
            continue
        if text is None:
            page.entry["empty"] = True  # nothing to generate from: the trait's source is absent here
            continue
        target = root / page.path
        if not target.is_file() or target.read_text(encoding="utf-8") != text:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
            written.append(page.path)
    return written


def report(root: Path, pages: list[PagePlan], view_state: tuple[str, list[str]]) -> str:
    mark = {"current": "ok", "missing": "MISSING", "stale": "STALE", "unreviewed": "REVIEW",
            "unadopted": "ADOPT", "delegated": "->", "empty": "EMPTY"}
    lines = [f"Guide for {root.name}: {len(pages)} pages", ""]
    for audience in dict.fromkeys(p.audience for p in pages):
        lines.append(f"  {audience}")
        for p in (p for p in pages if p.audience == audience):
            what = p.tool if p.work == "delegated" else p.work
            lines.append(f"    {mark[p.entry['state']]:8} {p.id:22} {p.kind:12} {what:10} {p.entry['detail']}")
    state, problems = view_state
    lines += ["", f"  architecture views: {state}"] + [f"    {x}" for x in problems[:5]]
    todo = [p for p in pages if p.entry["state"] in ("missing", "stale", "unreviewed", "unadopted")
            and p.work in ("written", "existing")]
    if todo:
        order = ("unadopted", "missing", "stale", "unreviewed")
        lines += ["", "For the agent (`documentor write`, or HELIX guide mode), in this order:"]
        for p in sorted(todo, key=lambda p: order.index(p.entry["state"])):
            lines.append(f"  - {p.entry['state']} {p.path}: {p.task or p.title}")
    return "\n".join(lines)


# --- init ---------------------------------------------------------------------------------------------

def proposal_text(root: Path) -> tuple[str, dict]:
    """The detection report and the `publish:` block it implies."""
    config = config_of(root)
    files = [f for f in repository_files(root) if not incidental(f)]
    scores = [s for s in (detect.score(root, files, t) for t in load_traits(config, root)) if s.matches]
    proposed = [s for s in scores if s.confidence >= 0.5]
    text = detect.report(root, scores, 0.5, detect.unmapped(root, files, proposed))
    block = detect.proposal(proposed)
    block.pop("_views", None)
    block["publish"] = {"schema": SCHEMA} | {k: v for k, v in block["publish"].items() if k != "delegated"}
    return text, block


def init(root: Path, write: bool) -> int:
    text, block = proposal_text(root)
    print(text)
    config_path = root / ".helix.yml"
    snippet = "\n# documentor (`documentor init`): what this repository is, and who reads its documentation.\n"
    snippet += yaml.safe_dump(block, sort_keys=False)
    if not config_path.is_file():
        # No HELIX yet: scaffold the marker and the activity directories; the agent fills them.
        marker = ("# HELIX marker: declares the flow active in this repository and the scope root it owns.\n"
                  "version: 1\nflows:\n  - id: helix\n    root: docs/helix/\n")
        config_path.write_text(marker + snippet, encoding="utf-8")
        for phase in PHASES:
            folder = root / "docs" / "helix" / phase
            folder.mkdir(parents=True, exist_ok=True)
            (folder / ".gitkeep").touch()
        print(f"\nwrote {config_path} and docs/helix/ (the HELIX activity folders). Install the HELIX skill to\n"
              "author the artifacts and the written pages: https://github.com/DocumentDrivenDX/helix "
              "(docs/install/README.md).")
        return 0
    config = config_of(root)
    if (config.get("publish") or {}).get("traits"):
        print("\n.helix.yml already records traits; compare them with the proposal above.")
        return 0
    if write and not config.get("publish"):
        config_path.write_text(config_path.read_text(encoding="utf-8") + snippet, encoding="utf-8")
        print(f"\nwrote the proposal to {config_path}")
    else:
        print("\nAdd to .helix.yml (or rerun with --write):\n" + snippet)
    return 0


# --- review and adopt ---------------------------------------------------------------------------

def review(root: Path, page: Path, by: str) -> int:
    """Record an evaluation, only of a page that passes every check, never by the page's writer; it
    lapses when the page changes."""
    parsed = check.parse_page(page)
    if parsed is None:
        print(f"{page}: no helix:publish header", file=sys.stderr)
        return 2
    who = re.sub(r"[^A-Za-z0-9_.-]", "-", by)
    if who == parsed.meta.get("written"):
        print(f"{page}: {who} wrote the page; another reader must evaluate it", file=sys.stderr)
        return 1
    findings = check.run_check([page], root, False)
    adopted = "existing" in parsed.meta  # an adopted page was not written under the writing pass
    open_items = [f for f in findings.items
                  if f["severity"] == "blocking" or (f["check"].startswith("prose.") and not adopted)]
    if open_items:
        for f in open_items:
            print(f"{page}: {f['severity']} {f['check']}: {f['message']}", file=sys.stderr)
        print(f"{page}: not reviewed; fix the findings above first", file=sys.stderr)
        return 1
    text = page.read_text(encoding="utf-8")
    header = HEADER.search(text)
    stamp = f"reviewed={dt.date.today().isoformat()}/{who}/{check.body_digest(page)}"
    line = re.sub(r"\s*reviewed=\S+", "", header[0]).replace(" -->", f" {stamp} -->")
    page.write_text(text.replace(header[0], line, 1), encoding="utf-8")
    print(f"{page}: {stamp}")
    return 0


def adopt(root: Path, page: Path, audience: str, kind: str, sources: list[str]) -> int:
    """Give a hand-written page the header that brings it under the guide; its text is untouched."""
    text = page.read_text(encoding="utf-8")
    if HEADER.search(text):
        print(f"{page}: already has a helix:publish header", file=sys.stderr)
        return 1
    header = (f"<!-- helix:publish audience={audience} page={page.stem} kind={kind or '-'} voice=onboarding "
              "existing=yes -->")
    lines = [header] + [f"<!-- helix:source {s} -->" for s in sources]
    page.write_text("\n".join(lines) + "\n" + text, encoding="utf-8")
    if sources:
        check.run_stamp([page], root)
    print(f"adopted {page} under {audience}" + ("" if kind else " (name its kind in the header)"))
    return 0


# --- main -----------------------------------------------------------------------------------------------

def guide_main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="documentor", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=("init", "status", "build", "write", "check", "review", "adopt"))
    parser.add_argument("page", nargs="?", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--by", default="")
    parser.add_argument("--audience", default="")
    parser.add_argument("--kind", default="")
    parser.add_argument("--source", action="append", default=[])
    parser.add_argument("--site", type=Path)
    parser.add_argument("--no-site", action="store_true")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--model", default="", help="write: the writer's model")
    parser.add_argument("--reviewer-model", default="", help="write: the evaluator's model")
    parser.add_argument("--agent", default="", help="write: the agent command; {model} is replaced")
    parser.add_argument("--dry-run", action="store_true", help="write: print the prompts, call nothing")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    if args.command == "init":
        return init(root, args.write)
    if args.command == "review":
        if not args.page or not args.by:
            parser.error("review needs PAGE and --by")
        return review(root, args.page.resolve(), args.by)
    if args.command == "adopt":
        if not args.page or not args.audience:
            parser.error("adopt needs PAGE and --audience")
        return adopt(root, args.page.resolve(), args.audience, args.kind, args.source)
    config = config_of(root)
    if not audiences(config):
        print("No guide yet: run `documentor init` first.", file=sys.stderr)
        return 2
    try:
        pages = plan(config, root)
    except KeyError as error:
        print(f"documentor: {error}", file=sys.stderr)
        return 2
    written = 0
    if args.command in ("build", "write"):
        from documentor import write

        agent = dict(command=args.agent, writer=args.model, reviewer=args.reviewer_model, dry_run=args.dry_run)
        if args.command == "write":
            return write.run(root, config, pages, str(args.page or ""), **agent)
        for path in regenerate(root, config, pages):
            print(f"regenerated {path}")
        state, problems = views(root, config, write=True)
        if state != "none":
            print("architecture views written" if not problems else "\n".join(problems))
        if args.write:
            written = write.run(root, config, pages, **agent)
            pages = plan(config, root)  # write assessed the pages before it wrote them
    assess(root, config, pages)
    view_state = views(root, config, write=False)
    if args.format == "json":
        print(json.dumps({"pages": [asdict(p) for p in pages], "views": view_state[0]}, indent=2))
    else:
        print(report(root, pages, view_state))
    out = root / publish_out(config)
    findings = check.run_check([out], root, False) if out.is_dir() else check.Findings()
    blocking = [f for f in findings.items if f["severity"] == "blocking"]
    if args.command in ("build", "check"):
        print(f"\nchecks: {len(blocking)} blocking, {len(findings.items) - len(blocking)} warnings")
        for f in blocking[:10]:
            print(f"  BLOCKING {f['check']} {Path(f['page']).name}: {f['message']}")
    if args.command == "build" and not args.no_site:
        from documentor import site

        site.build(root, args.site or root / ".helix" / "site", True, None)
    if args.command == "check":
        unfinished = [p for p in pages if p.entry["state"] in ("missing", "stale", "unreviewed", "unadopted")]
        for p in unfinished[:10]:
            print(f"  {p.entry['state'].upper()} {p.path}: {p.entry['detail']}")
        return 1 if blocking or unfinished or view_state[0] == "stale" else 0
    return 1 if written else 0


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] in (["--version"], ["-V"]):
        print(f"documentor {__version__} (HELIX catalog {helix_version()})")
        return 0
    if argv and argv[0] in TOOLS:
        name, rest = argv[0], argv[1:]
        if name == "stamp":
            return check.main(["stamp", *rest])
        if name == "check-pages":
            return check.main(["check", *rest])
        if name == "detect":
            return detect.main(rest)
        if name == "generate":
            return generate.main(rest)
        if name == "site":
            from documentor import site

            return site.main(rest)
        if name == "views":
            from documentor.architecture import views as architecture_views

            architecture_views.main(rest)
            return 0
        if name == "present":
            from documentor.architecture import present

            return present.main(rest)
        if name == "estate":
            from documentor.architecture import estate

            return estate.main(rest)
    return guide_main(argv)


if __name__ == "__main__":
    sys.exit(main())
