#!/usr/bin/env python3
"""Generate the pages a repository's structured sources already describe (publishing.md, Traits).

Usage:
    publish_generate.py <generator> --page PAGE [--root DIR]     write the page
    publish_generate.py --list                                   name the generators

Some pages need no judgment: a list of plug-ins built from their manifests. (Where a repository's
own tool already publishes a reference, such as tablespec's guidebook, the trait delegates the page
to it instead, and nothing here duplicates it.) A trait names such a page's generator (`generated: <name>`), and the page is
written here, deterministically, from the sources, never by an agent. Its header says
`generated=<name>`; `publish_check.py` regenerates it and reports it stale when the result differs,
so the page cannot drift from the specs it lists. Generators read structure only: names, keys,
dependencies, counts. Free text in a source (a spec's description) is left out, because it can hold
what `handling:` forbids.

Requires PyYAML. Exit codes: 0 = written, 1 = nothing to generate from, 2 = usage error.
"""

from __future__ import annotations

import argparse
import re
import sys
import tomllib
from collections.abc import Callable
from pathlib import Path

import yaml

GENERATORS: dict[str, Callable[[Path, dict], tuple[str, list[str]]]] = {}


def generator(name: str):
    def register(function):
        GENERATORS[name] = function
        return function

    return register


def _tracked(root: Path, pattern: str) -> list[Path]:
    """Files git tracks that match the glob, leaving out tests and their fixtures."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from publish_detect import incidental, matching, repository_files

    return [root / f for f in matching(repository_files(root), pattern) if not incidental(f)]


# --- plugin-workflows --------------------------------------------------------------------------

@generator("plugin-workflows")
def plugin_workflows(root: Path, page: dict) -> tuple[str, list[str]]:
    """Every workflow a plug-in manifest declares, by practice area, one row each."""
    manifests = _tracked(root, "**/plugin.toml")
    rows: list[tuple[str, dict, str]] = []
    folders: set[str] = set()
    for path in manifests:
        workflow = tomllib.loads(path.read_text(encoding="utf-8")).get("workflow") or {}
        if workflow.get("id"):
            rows.append((workflow.get("title") or workflow["id"], workflow, path.parent.parent.name))
            folders.add(path.parent.parent.relative_to(root).as_posix())
    if not rows:
        return "", []
    lines = [
        f"Every workflow the plug-in manifests declare: {len(rows)} in all, read from "
        f"{', '.join(f'`{f}/`' for f in sorted(folders))}.",
        "",
        "| Workflow | Practice areas | What it does | Model | Tools |",
        "|---|---|---|---|---:|",
    ]
    for title, workflow, _ in sorted(rows, key=lambda row: row[0].lower()):
        areas = ", ".join(workflow.get("areas") or []) or "—"
        what = " ".join((workflow.get("description") or "").split()).replace("|", "\\|")
        lines.append(f"| **{title}** | {areas} | {what} | {workflow.get('model', '—')} | "
                     f"{len(workflow.get('tools') or [])} |")
    return "\n".join(lines) + "\n", sorted(f"{folder}/*/plugin.toml" for folder in folders)


# --- shared ------------------------------------------------------------------------------------

def _first_sentence(text: str) -> str:
    flat = " ".join((text or "").split())
    end = re.search(r"(?<=[.!?])\s", flat)
    return (flat[: end.start()] if end else flat).replace("|", "\\|")


def _cell(value: str) -> str:
    return value.replace("|", "\\|").replace("<", "&lt;").replace(">", "&gt;")


# --- databricks-app-settings ---------------------------------------------------------------------

def _env_comments(text: str) -> dict[str, str]:
    """Each setting's explanation: the comment block above it, shared by the settings that follow
    it with no blank line between (one comment often explains a group)."""
    notes: dict[str, str] = {}
    block: list[str] = []
    current = ""
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            block, current = [], ""
        elif stripped.startswith("#"):
            block.append(stripped.lstrip("#").strip())
        else:
            named = re.match(r"-\s*name:\s*(\S+)", stripped)
            if named:
                if block:
                    current = _first_sentence(" ".join(block))
                    block = []
                if current and named[1] not in notes:
                    notes[named[1]] = current
            elif block:
                block = []
    return notes


def _value_kind(entry: dict) -> str:
    if "value_from" in entry:
        return f"the app resource `{entry['value_from']}`"
    value = str(entry.get("value", ""))
    if "${var." in value:
        return "a bundle variable, set per target"
    if "${" in value:
        return "the bundle, resolved at deploy"
    return "fixed in the bundle"


@generator("databricks-app-settings")
def databricks_app_settings(root: Path, page: dict) -> tuple[str, list[str]]:
    """Every setting a Databricks App's bundle gives it: which targets, where the value comes from."""
    bundle = root / "databricks.yml"
    if not bundle.is_file():
        return "", []
    text = bundle.read_text(encoding="utf-8")
    data = yaml.safe_load(text) or {}
    notes = _env_comments(text)
    settings: dict[str, dict] = {}
    for app in ((data.get("resources") or {}).get("apps") or {}).values():
        for entry in ((app.get("config") or {}).get("env")) or []:
            settings[entry["name"]] = {"targets": ["every target"], "from": _value_kind(entry)}
    for target, body in (data.get("targets") or {}).items():
        for app in (((body or {}).get("resources") or {}).get("apps") or {}).values():
            for entry in ((app.get("config") or {}).get("env")) or []:
                row = settings.setdefault(entry["name"], {"targets": [], "from": _value_kind(entry)})
                if "every target" not in row["targets"]:
                    row["targets"].append(target)
    if not settings:
        return "", []
    lines = [f"Every setting the deploy bundle gives the app: {len(settings)} in all, read from "
             "`databricks.yml`. Values are not listed here: the bundle and its variables hold them.",
             "", "| Setting | Targets | Value from | What it does |", "|---|---|---|---|"]
    for name, row in sorted(settings.items()):
        lines.append(f"| `{name}` | {', '.join(row['targets'])} | {row['from']} | {notes.get(name, '—')} |")
    return "\n".join(lines) + "\n", ["databricks.yml"]


# --- databricks-jobs ----------------------------------------------------------------------------

def _chain(tasks: list[dict]) -> str:
    """The tasks in run order: a chain when each waits on the one before, else each with its waits."""
    order = [t.get("task_key", "?") for t in tasks]
    waits = {t.get("task_key"): [d.get("task_key") for d in t.get("depends_on") or []] for t in tasks}
    linear = all(waits[k] == ([order[i - 1]] if i else []) for i, k in enumerate(order))
    if linear:
        return " → ".join(f"`{k}`" for k in order)
    return "; ".join(f"`{k}`" + (f" after {', '.join(f'`{w}`' for w in waits[k])}" if waits[k] else "")
                     for k in order)


def _schedule(job: dict) -> str:
    schedule = job.get("schedule") or {}
    if not schedule:
        return "on demand" if not job.get("trigger") else "on a trigger"
    paused = " (paused)" if schedule.get("pause_status") == "PAUSED" else ""
    return f"`{schedule.get('quartz_cron_expression', '?')}` {schedule.get('timezone_id', '')}{paused}".strip()


@generator("databricks-jobs")
def databricks_jobs(root: Path, page: dict) -> tuple[str, list[str]]:
    """Every job a bundle deploys: its schedule, and its tasks in the order they run."""
    files = _tracked(root, "**/jobs/*.yml") + _tracked(root, "**/resources/*.yml")
    jobs: list[tuple[str, dict, str]] = []
    for path in files:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        for key, job in (((data.get("resources") or {}).get("jobs")) or {}).items():
            jobs.append((job.get("name") or key, job, path.relative_to(root).as_posix()))
    if not jobs:
        return "", []
    lines = [f"Every job the bundle deploys: {len(jobs)} in all.", "",
             "| Job | Schedule | Tasks | Defined in |", "|---|---|---:|---|"]
    for name, job, where in sorted(jobs):
        lines.append(f"| `{name}` | {_schedule(job)} | {len(job.get('tasks') or [])} | `{where}` |")
    for name, job, _ in sorted(jobs):
        lines += ["", f"## {name}", "", _chain(job.get("tasks") or []) or "No tasks."]
    folders = sorted({str(Path(w).parent) for _, _, w in jobs})
    return "\n".join(lines) + "\n", [f"{f}/*.yml" for f in folders]


# --- python-api ---------------------------------------------------------------------------------

def _definitions(module: Path) -> dict[str, tuple[str, str]]:
    """Each top-level name a module defines: its kind and its docstring's first sentence."""
    import ast

    tree = ast.parse(module.read_text(encoding="utf-8"))
    found: dict[str, tuple[str, str]] = {}
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            doc = _first_sentence(ast.get_docstring(node) or "")
            fields = [n.target.id for n in node.body
                      if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name)]
            if not doc and fields:
                doc = "Fields: " + ", ".join(f"`{f}`" for f in fields[:8]) + (", …" if len(fields) > 8 else "")
            found[node.name] = ("class", doc)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            found[node.name] = ("function", _first_sentence(ast.get_docstring(node) or ""))
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if isinstance(target, ast.Name):
                    found.setdefault(target.id, ("constant", ""))
    return found


@generator("python-api")
def python_api(root: Path, page: dict) -> tuple[str, list[str]]:
    """A package's public names (its `__all__`), by kind, from the source, never by importing it."""
    import ast

    inits = [p for p in _tracked(root, "src/*/__init__.py") if "__all__" in p.read_text(encoding="utf-8")]
    if not inits:
        return "", []
    init = inits[0]
    package = init.parent
    tree = ast.parse(init.read_text(encoding="utf-8"))
    exported: list[str] = []
    origin: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "__all__" for t in node.targets):
            exported = [e.value for e in getattr(node.value, "elts", []) if isinstance(e, ast.Constant)]
        if isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                origin[alias.asname or alias.name] = node.module
    rows: dict[str, list[str]] = {}
    cache: dict[str, dict] = {}
    for name in exported:
        module = origin.get(name, package.name)
        path = package.parent / (module.replace(".", "/") + ".py")
        if not path.is_file():
            path = package.parent / module.replace(".", "/") / "__init__.py"
        definitions = cache.setdefault(module, _definitions(path) if path.is_file() else {})
        kind, doc = definitions.get(name, ("name", ""))
        rows.setdefault(kind, []).append(f"| `{name}` | `{module}` | {doc or '—'} |")
    lines = [f"The public interface of `{package.name}`: the {len(exported)} names its `__all__` "
             "exports. Anything else is internal and may change."]
    for kind in ("class", "function", "constant", "name"):
        if rows.get(kind):
            lines += ["", f"## {kind.title() if kind != 'class' else 'Classes'}{'s' if kind in ('function', 'constant') else ''} ({len(rows[kind])})",
                      "", "| Name | Module | What it is |", "|---|---|---|", *rows[kind]]
    rel = package.relative_to(root).as_posix()
    return "\n".join(lines) + "\n", [f"{rel}/*.py"]


# --- npm-packages -------------------------------------------------------------------------------

@generator("npm-packages")
def npm_packages(root: Path, page: dict) -> tuple[str, list[str]]:
    """Every package in a workspace: version, whether it is published, what it gives, its entry points."""
    import json

    manifests = _tracked(root, "packages/*/package.json")
    if not manifests:
        return "", []
    lines = [f"Every package in the workspace: {len(manifests)} in all, read from `packages/*/package.json`.",
             "", "| Package | Version | Published | What it gives | Entry points | Command |",
             "|---|---|---|---|---|---|"]
    for path in manifests:
        data = json.loads(path.read_text(encoding="utf-8"))
        exports = data.get("exports") or {}
        entries = ", ".join(f"`{e}`" for e in (exports if isinstance(exports, dict) else ["."])) or "—"
        command = ", ".join(f"`{c}`" for c in (data.get("bin") or {})) if isinstance(data.get("bin"), dict) else "—"
        published = "no (private)" if data.get("private") else "yes"
        lines.append(f"| `{data.get('name', path.parent.name)}` | {data.get('version', '—')} | {published} | "
                     f"{_cell(_first_sentence(data.get('description', '')) or '—')} | {entries} | {command or '—'} |")
    return "\n".join(lines) + "\n", ["packages/*/package.json"]


# --- opentofu-resources -------------------------------------------------------------------------

@generator("opentofu-resources")
def opentofu_resources(root: Path, page: dict) -> tuple[str, list[str]]:
    """What each module declares: how many resources, from which providers. Types only, no names."""
    files = _tracked(root, "**/*.tf")
    modules: dict[str, dict[str, int]] = {}
    for path in files:
        module = path.parent.relative_to(root).as_posix()
        for kind in re.findall(r'^resource\s+"([a-z0-9_]+)"', path.read_text(encoding="utf-8"), re.M):
            provider = kind.split("_", 1)[0]
            modules.setdefault(module, {}).setdefault(provider, 0)
            modules[module][provider] += 1
    if not modules:
        return "", []
    total = sum(sum(p.values()) for p in modules.values())
    lines = [f"What the infrastructure declares: {total} resources in {len(modules)} modules. Only "
             "resource types are counted here; names, ids, and state stay in the code.",
             "", "| Module | Resources | By provider |", "|---|---:|---|"]
    for module, providers in sorted(modules.items()):
        spread = ", ".join(f"{p} {n}" for p, n in sorted(providers.items(), key=lambda kv: -kv[1]))
        lines.append(f"| `{module}` | {sum(providers.values())} | {spread} |")
    return "\n".join(lines) + "\n", ["**/*.tf"]


# --- streamlit-screens --------------------------------------------------------------------------

@generator("streamlit-screens")
def streamlit_screens(root: Path, page: dict) -> tuple[str, list[str]]:
    """Every screen of a Streamlit app, named as its sidebar names it, with its module's summary."""
    import ast

    screens = _tracked(root, "pages/*.py")
    if not screens:
        return "", []
    lines = [f"Every screen the app shows in its sidebar: {len(screens)}, from `pages/`.", "",
             "| Screen | What it does |", "|---|---|"]
    for path in screens:
        title = re.sub(r"^\d+_", "", path.stem).replace("_", " ")
        doc = ast.get_docstring(ast.parse(path.read_text(encoding="utf-8"))) or ""
        lines.append(f"| {title[:1].upper() + title[1:]} | {_first_sentence(doc) or '—'} |")
    return "\n".join(lines) + "\n", ["pages/*.py"]


# --- helix-artifact-types -----------------------------------------------------------------------

@generator("helix-artifact-types")
def helix_artifact_types(root: Path, page: dict) -> tuple[str, list[str]]:
    """Every artifact type a HELIX catalog defines, by activity."""
    metas = _tracked(root, "workflows/activities/*/artifacts/*/meta.yml")
    if not metas:
        return "", []
    by_activity: dict[str, list[str]] = {}
    for path in metas:
        meta = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        artifact = meta.get("artifact") or {}
        activity = path.parts[-4]
        by_activity.setdefault(activity, []).append(
            f"| {artifact.get('name', path.parent.name)} | `{artifact.get('id', path.parent.name)}` | "
            f"{_first_sentence(meta.get('description', '')) or '—'} |")
    lines = [f"Every artifact type the catalog defines: {len(metas)}, in {len(by_activity)} activities."]
    for activity, rows in sorted(by_activity.items()):
        lines += ["", f"## {activity}", "", "| Artifact | Id | What it is |", "|---|---|---|", *rows]
    return "\n".join(lines) + "\n", ["workflows/activities/*/artifacts/*/meta.yml"]


# --- writing and checking -----------------------------------------------------------------------

def render(name: str, root: Path, header: str, title: str) -> str | None:
    """The whole page: its header, its sources with their digests, its title, and the generator's
    body; None with nothing to read. The sources are globs, so any provenance check (one without
    the generators, too) sees the page go stale when a file they match changes or appears."""
    body, globs = GENERATORS[name](root, {})
    if not body:
        return None
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from publish_check import digest, read_source

    sources = [f"<!-- helix:source {g} sha256:{digest(read_source(root, g) or '')} -->" for g in globs]
    return "\n".join([header, *sources, f"# {title}", "", body.rstrip("\n")]) + "\n"


HEADER = re.compile(r"^<!-- helix:publish .*-->$", re.M)
TITLE = re.compile(r"^# (.+)$", re.M)


def regenerated(path: Path, root: Path) -> str | None:
    """What a generated page should hold now, from its own header and title."""
    text = path.read_text(encoding="utf-8")
    header, title = HEADER.search(text), TITLE.search(text)
    name = re.search(r"\bgenerated=(\S+)", header[0]) if header else None
    if not (header and title and name) or name[1] not in GENERATORS:
        return None
    return render(name[1], root, header[0], title[1])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("generator", nargs="?")
    parser.add_argument("--page", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--flow", default="data")
    parser.add_argument("--title", default="")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()
    if args.list:
        for name, function in GENERATORS.items():
            print(f"{name:20} {(function.__doc__ or '').strip()}")
        return 0
    if args.generator not in GENERATORS or not args.page:
        parser.error(f"name a generator ({', '.join(GENERATORS)}) and --page")
    page = args.page.resolve()
    header = (f"<!-- helix:publish flow={args.flow} page={page.stem} kind=reference voice=onboarding "
              f"generated={args.generator} -->")
    text = render(args.generator, args.root.resolve(), header, args.title or page.stem.title())
    if text is None:
        print(f"{args.generator}: nothing to generate from under {args.root}", file=sys.stderr)
        return 1
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text(text, encoding="utf-8")
    print(f"wrote {page} ({text.count(chr(10))} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
