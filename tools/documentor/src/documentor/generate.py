#!/usr/bin/env python3
"""Generate the pages a repository's structured sources already describe (publishing.md, Traits).

Usage:
    documentor generate <generator> --page PAGE [--root DIR]     write the page
    documentor generate --list                                   name the generators

Some pages need no judgment: a list of plug-ins built from their manifests. (Where a repository's
own tool already publishes a reference, such as tablespec's guidebook, the trait delegates the page
to it instead, and nothing here duplicates it.) A trait names such a page's generator (`generated: <name>`), and the page is
written here, deterministically, from the sources, never by an agent. Its header says
`generated=<name>`; `documentor check` regenerates it and reports it stale when the result differs,
so the page cannot drift from the specs it lists. Generators read structure only: names, keys,
dependencies, counts. Free text in a source (a spec's description) is left out, because it can hold
what `handling:` forbids.

A repository's own generator is a command: `generated: {command: ..., sources: [...]}` on a page in
`.helix.yml`; the page's header says `generated=command` and the check runs the command and compares.
Packaged generators from other distributions register in the `documentor.generators` entry-point group.

Exit codes: 0 = written, 1 = nothing to generate from, 2 = usage error.
"""

from __future__ import annotations

import argparse
import re
import sys
import tomllib
from collections.abc import Callable
from pathlib import Path

import yaml

from documentor.lib import HEADER as _HEADER, config_of, expand, incidental, matching, repository_files

GENERATORS: dict[str, Callable[[Path, dict], tuple[str, list[str]]]] = {}


def generator(name: str):
    def register(function):
        GENERATORS[name] = function
        return function

    return register


def _tracked(root: Path, pattern: str) -> list[Path]:
    """Files git tracks that match the glob, leaving out tests, their fixtures, and whatever the
    project's `publish.ignore` names (a legacy tree the guide must not describe)."""
    import fnmatch

    ignored = [expand(g, config_of(root)) for g in (config_of(root).get("publish") or {}).get("ignore") or []]
    return [root / f for f in matching(repository_files(root), pattern)
            if not incidental(f) and not any(fnmatch.fnmatch(f, g) for g in ignored)]


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



# --- openapi-api ---------------------------------------------------------------------------------

@generator("openapi-api")
def openapi_api(root: Path, page: dict) -> tuple[str, list[str]]:
    """Every operation an OpenAPI document declares: method, path, summary, by tag. Schemas are counted."""
    import json

    files = _tracked(root, "**/openapi*.json") + _tracked(root, "**/openapi*.yaml") + _tracked(root, "**/openapi*.yml")
    rows: list[tuple[str, str, str, str]] = []
    schemas = 0
    globs: set[str] = set()
    for path in files:
        text = path.read_text(encoding="utf-8")
        data = json.loads(text) if path.suffix == ".json" else yaml.safe_load(text)
        if not isinstance(data, dict) or "paths" not in data:
            continue
        globs.add(f"{path.parent.relative_to(root).as_posix()}/openapi*{path.suffix}".lstrip("./"))
        for route, operations in sorted((data.get("paths") or {}).items()):
            for method, operation in (operations or {}).items():
                if method.lower() not in ("get", "post", "put", "patch", "delete", "head", "options"):
                    continue
                tags = ", ".join((operation or {}).get("tags") or []) or "—"
                summary = _first_sentence((operation or {}).get("summary") or (operation or {}).get("description") or "")
                rows.append((tags, route, method.upper(), summary or "—"))
        schemas += len(((data.get("components") or {}).get("schemas")) or {})
    if not rows:
        return "", []
    lines = [f"Every operation the API declares: {len(rows)} in all, with {schemas} schemas, read from the "
             "OpenAPI document. Request and response shapes stay in the document.",
             "", "| Tag | Path | Method | What it does |", "|---|---|---|---|"]
    for tags, route, method, summary in sorted(rows):
        lines.append(f"| {tags} | `{route}` | {method} | {_cell(summary)} |")
    return "\n".join(lines) + "\n", sorted(globs)


# --- cli-commands --------------------------------------------------------------------------------

def _script_module(root: Path, target: str) -> tuple[Path | None, str]:
    """The file and attribute a `[project.scripts]` entry (`pkg.mod:attr`) names, from the source."""
    module, _, attr = target.partition(":")
    for base in (root / "src", root):
        candidate = base / (module.replace(".", "/") + ".py")
        if candidate.is_file():
            return candidate, attr
        candidate = base / module.replace(".", "/") / "__init__.py"
        if candidate.is_file():
            return candidate, attr
    return None, attr


def _commands(module: Path, app: str, prefix: str = "") -> list[tuple[str, str]]:
    """Each `@<app>.command(...)` (Typer or Click) in a module: its name and its docstring's first
    sentence, and the commands of every Typer sub-app added with `<app>.add_typer(sub, name=...)`."""
    import ast

    found = []
    tree = ast.parse(module.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "add_typer"
                and isinstance(node.func.value, ast.Name) and node.func.value.id == app and node.args
                and isinstance(node.args[0], ast.Name)):
            group = next((str(k.value.value) for k in node.keywords
                          if k.arg == "name" and isinstance(k.value, ast.Constant)), node.args[0].id)
            found += _commands(module, node.args[0].id, f"{prefix}{group} ")
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in node.decorator_list:
            call = decorator if isinstance(decorator, ast.Call) else None
            target = call.func if call else decorator
            if not (isinstance(target, ast.Attribute) and target.attr == "command"
                    and isinstance(target.value, ast.Name) and target.value.id == app):
                continue
            name = node.name.replace("_", "-")
            for keyword in (call.keywords if call else []):
                if keyword.arg == "name" and isinstance(keyword.value, ast.Constant):
                    name = str(keyword.value.value)
            for positional in (call.args if call else []):
                if isinstance(positional, ast.Constant) and isinstance(positional.value, str):
                    name = positional.value
            found.append((f"{prefix}{name}", _first_sentence(ast.get_docstring(node) or "")))
    return found


def _argparse_commands(module: Path, script: str) -> list[tuple[str, str]]:
    """The commands of an argparse CLI: each `<sub>.add_parser("name", help=...)`, or the constants of a
    positional argument's `choices=(...)`. A command's purpose is its `help`, else the docstring of a
    function of that name in the module, else its line in the module docstring's usage block."""
    import ast

    tree = ast.parse(module.read_text(encoding="utf-8"))
    functions = {n.name.replace("_", "-"): ast.get_docstring(n) or ""
                 for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    usage = {}
    lines = [line.strip() for line in (ast.get_docstring(tree) or "").splitlines()]
    for number, line in enumerate(lines):
        parts = re.split(r"\s{2,}", line)
        if not line.startswith(f"{script} ") or len(parts) < 2:
            continue
        text = parts[-1]
        if len(parts) == 2 and (text.startswith("[") or "--" in text):  # only options: the purpose is the next line
            following = lines[number + 1] if number + 1 < len(lines) else ""
            text = following if following and not following.startswith(f"{script} ") else ""
        usage.setdefault(parts[0].split()[1], text)

    def constant(node: ast.AST | None) -> str:
        return str(node.value) if isinstance(node, ast.Constant) and isinstance(node.value, str) else ""

    found: dict[str, str] = {}
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
            continue
        if node.func.attr == "add_parser" and node.args and constant(node.args[0]):
            text = next((constant(k.value) for k in node.keywords if k.arg in ("help", "description")), "")
            found.setdefault(constant(node.args[0]), text)
        elif node.func.attr == "add_argument" and node.args and not constant(node.args[0]).startswith("-"):
            choices = next((k.value for k in node.keywords if k.arg == "choices"), None)
            if isinstance(choices, (ast.Tuple, ast.List)):
                for choice in choices.elts:
                    found.setdefault(constant(choice), "")
    return [(name, _first_sentence(text or functions.get(name, "")) or usage.get(name, ""))
            for name, text in found.items() if name]


@generator("cli-commands")
def cli_commands(root: Path, page: dict) -> tuple[str, list[str]]:
    """Every command a project's console scripts offer (Typer, Click, or argparse), from the source, never by running it."""
    sections: list[str] = []
    sources: list[str] = []
    count = 0
    for pyproject in _tracked(root, "**/pyproject.toml"):
        scripts = (tomllib.loads(pyproject.read_text(encoding="utf-8")).get("project") or {}).get("scripts") or {}
        if not scripts:
            continue
        base = pyproject.parent
        sources.append(pyproject.relative_to(root).as_posix())
        for script, target in sorted(scripts.items()):
            module, app = _script_module(base, target)
            if module is None:
                continue
            commands = _commands(module, app) or _argparse_commands(module, script)
            sources.append(module.relative_to(root).as_posix())
            count += 1
            sections += ["", f"## {script}", "", f"`{script}` is `{target}` ({pyproject.relative_to(root).as_posix()}); "
                         f"{len(commands)} commands.", "", "| Command | What it does |", "|---|---|"]
            sections += [f"| `{script} {name}` | {_cell(doc) or '—'} |" for name, doc in commands]
    if not sections:
        return "", []
    lines = [f"Every command line the project installs: {count} in all, from `[project.scripts]` in its "
             "pyproject files, with each command's purpose from its docstring. Options and arguments are on "
             "each command's `--help`."] + sections
    return "\n".join(lines) + "\n", sorted(set(sources))


# --- mcp-tools -----------------------------------------------------------------------------------

@generator("mcp-tools")
def mcp_tools(root: Path, page: dict) -> tuple[str, list[str]]:
    """Every tool an MCP server exposes (`@<server>.tool()` in Python), and every server `.mcp.json` lists."""
    import ast
    import json

    rows: list[tuple[str, str, str]] = []
    sources: list[str] = []
    for path in _tracked(root, "**/*.py"):
        text = path.read_text(encoding="utf-8", errors="replace")
        if ".tool(" not in text:
            continue
        tree = ast.parse(text)
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for decorator in node.decorator_list:
                target = decorator.func if isinstance(decorator, ast.Call) else decorator
                if isinstance(target, ast.Attribute) and target.attr == "tool":
                    rows.append((path.relative_to(root).as_posix(), node.name, _first_sentence(ast.get_docstring(node) or "")))
    if rows:
        sources += sorted({str(Path(r[0]).parent) + "/*.py" for r in rows})
    servers: list[tuple[str, str]] = []
    listing = root / ".mcp.json"
    if listing.is_file():
        data = json.loads(listing.read_text(encoding="utf-8")) or {}
        for name, server in sorted((data.get("mcpServers") or {}).items()):
            if server.get("url"):
                from urllib.parse import urlsplit

                parts = urlsplit(server["url"])
                how = f"{parts.scheme}://{parts.netloc}" if parts.netloc else "a URL"  # never the path or a token
            else:
                how = " ".join([server.get("command", ""), *server.get("args", [])]).strip()
            servers.append((name, how))
        sources.append(".mcp.json")
    if not rows and not servers:
        return "", []
    lines = []
    if rows:
        lines += [f"Every tool the project's MCP servers expose: {len(rows)} in all, read from the source.", "",
                  "| Tool | What it does | Defined in |", "|---|---|---|"]
        lines += [f"| `{name}` | {_cell(doc) or '—'} | `{where}` |" for where, name, doc in sorted(rows, key=lambda r: r[1])]
    if servers:
        lines += ["", f"## Servers the repository connects to", "", f"From `.mcp.json`: {len(servers)} servers.", "",
                  "| Server | Reached by |", "|---|---|"]
        lines += [f"| `{name}` | `{_cell(how)}` |" for name, how in servers]
    return "\n".join(lines) + "\n", sorted(set(sources))

# --- ci-pipelines --------------------------------------------------------------------------------

def _mermaid_id(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "_", text)


@generator("ci-pipelines")
def ci_pipelines(root: Path, page: dict) -> tuple[str, list[str]]:
    """Each GitHub Actions workflow: what starts it, its jobs in order, and what each job waits for."""
    files = sorted(_tracked(root, ".github/workflows/*.yml") + _tracked(root, ".github/workflows/*.yaml"))
    sections = []
    for path in files:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        triggers = data.get("on", data.get(True)) or {}  # YAML 1.1 reads a bare `on:` as true
        if isinstance(triggers, str):
            triggers = {triggers: None}
        elif isinstance(triggers, list):
            triggers = {t: None for t in triggers}
        starts = []
        for event, spec in triggers.items():
            detail = ""
            if isinstance(spec, dict):
                branches = spec.get("branches") or spec.get("tags")
                if branches:
                    detail = " on " + ", ".join(f"`{b}`" for b in branches)
                elif spec.get("cron") or (isinstance(spec, list) and spec):
                    detail = ""
                if event == "schedule" or "cron" in str(spec):
                    detail = ""
            if event == "schedule" and isinstance(spec, list):
                detail = " " + ", ".join(f"`{s.get('cron')}`" for s in spec if isinstance(s, dict))
            starts.append(f"{event}{detail}")
        jobs = data.get("jobs") or {}
        if not jobs:
            continue
        rows, edges = [], []
        for job_id, job in jobs.items():
            job = job or {}
            needs = job.get("needs") or []
            needs = [needs] if isinstance(needs, str) else list(needs)
            edges += [(n, job_id) for n in needs]
            runs = job.get("runs-on", "") if not job.get("uses") else f"reuses `{job['uses']}`"
            rows.append(f"| `{job_id}` | {_cell(str(job.get('name', '')))} | {_cell(str(runs))} | "
                        + (", ".join(f"`{n}`" for n in needs) or "—") + " |")
        relative = path.relative_to(root).as_posix()
        section = [f"## {data.get('name') or path.stem}", "",
                   f"`{relative}` runs on " + ("; ".join(starts) or "no trigger") + ".", "",
                   "| Job | Name | Runs on | Waits for |", "|---|---|---|---|", *rows]
        if edges:
            section += ["", "```mermaid", "flowchart LR"]
            section += [f"  {_mermaid_id(a)}[{a}] --> {_mermaid_id(b)}[{b}]" for a, b in edges]
            section += ["```"]
        sections.append("\n".join(section))
    if not sections:
        return "", []
    intro = f"What runs on each change and release: {len(sections)} workflows, read from `.github/workflows/`."
    return intro + "\n\n" + "\n\n".join(sections) + "\n", [".github/workflows/*.yml", ".github/workflows/*.yaml"]


# --- tasks ---------------------------------------------------------------------------------------

def _first_sentence(text: str) -> str:
    match = re.match(r"(.+?[.!?])(\s|$)", text.strip())
    return match.group(1) if match else text.strip()


def _just_recipes(text: str) -> list[tuple[str, str]]:
    recipes, comment = [], []
    for line in text.splitlines():
        if line.startswith("#"):
            comment.append(line.lstrip("#").strip())
            continue
        match = re.match(r"^@?([A-Za-z0-9_-]+)(?:\s+[^:=]*)?:(?!=)", line)
        if match and not line.startswith((" ", "\t")):
            recipes.append((match.group(1), " ".join(comment)))
        if line.strip() or not line.startswith("#"):
            comment = [] if not line.startswith("#") else comment
    return recipes


def _make_targets(text: str) -> list[tuple[str, str]]:
    targets, comment = [], []
    for line in text.splitlines():
        if line.startswith("#"):
            comment.append(line.lstrip("#").strip())
            continue
        match = re.match(r"^([A-Za-z0-9_.-]+)\s*:(?!=)([^#]*)(?:##\s*(.*))?$", line)
        if match and not match.group(1).startswith("."):
            targets.append((match.group(1), (match.group(3) or " ".join(comment)).strip()))
        comment = []
    return targets


@generator("tasks")
def tasks(root: Path, page: dict) -> tuple[str, list[str]]:
    """The commands the repository's task runners define: just recipes, make targets, npm scripts,
    each with the comment above it."""
    import json

    sections, sources = [], []
    for name, reader in (("justfile", _just_recipes), ("Makefile", _make_targets)):
        for path in _tracked(root, f"**/{name}") + _tracked(root, name):
            rows = reader(path.read_text(encoding="utf-8"))
            relative = path.relative_to(root).as_posix()
            if rows and relative not in sources:
                runner = "just" if name == "justfile" else "make"
                where = "" if path.parent == root else f" (from `{path.parent.relative_to(root).as_posix()}/`)"
                sections.append("\n".join([f"## `{relative}`", "", f"Run with `{runner} <name>`{where}.", "",
                                           "| Task | What it does |", "|---|---|",
                                           *[f"| `{t}` | {_cell(_first_sentence(c)) or '—'} |" for t, c in rows]]))
                sources.append(relative)
    for path in _tracked(root, "**/package.json") + _tracked(root, "package.json"):
        relative = path.relative_to(root).as_posix()
        if relative in sources or "node_modules" in relative:
            continue
        try:
            scripts = json.loads(path.read_text(encoding="utf-8")).get("scripts") or {}
        except json.JSONDecodeError:
            continue
        if scripts:
            sections.append("\n".join([f"## `{relative}`", "", "Run with `npm run <name>`.", "",
                                       "| Script | Runs |", "|---|---|",
                                       *[f"| `{k}` | `{_cell(str(v))}` |" for k, v in scripts.items()]]))
            sources.append(relative)
    if not sections:
        return "", []
    return (f"Every task the repository defines, from {len(sources)} files.\n\n" + "\n\n".join(sections) + "\n",
            sources)


# --- database-schema -----------------------------------------------------------------------------

CREATE = re.compile(r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[\"`]?([\w.]+)[\"`]?\s*\((.*?)\n\s*\)\s*;?", re.I | re.S)
ALTER = re.compile(r"ALTER\s+TABLE\s+(?:IF\s+EXISTS\s+)?[\"`]?([\w.]+)[\"`]?\s+ADD\s+(?:COLUMN\s+)?(?:IF\s+NOT\s+EXISTS\s+)?[\"`]?(\w+)[\"`]?\s+(\w+(?:\s*\([^)]*\))?(?:\[\])?)", re.I)
CONSTRAINTS = ("primary", "foreign", "unique", "check", "constraint", "exclude", "index")


def _columns(body: str) -> list[tuple[str, str, str, str]]:
    """(name, type, flags, comment) for each column of a CREATE TABLE body."""
    columns = []
    for raw in body.splitlines():
        line, _, comment = raw.partition("--")
        line = line.strip().rstrip(",")
        match = re.match(r'^[\"`]?(\w+)[\"`]?\s+([A-Za-z][\w ]*?(?:\([^)]*\))?(?:\[\])?)(?:\s+(.*))?$', line)
        if not match or match.group(1).lower() in CONSTRAINTS:
            continue
        rest = (match.group(3) or "").lower()
        flags = []
        if "primary key" in rest:
            flags.append("PK")
        reference = re.search(r"references\s+[\"`]?([\w.]+)", rest)
        if reference:
            flags.append(f"FK {reference.group(1)}")
        if "not null" in rest and "primary key" not in rest:
            flags.append("required")
        columns.append((match.group(1), match.group(2).strip().split()[0], ", ".join(flags), comment.strip()))
    return columns


def _base_type(kind: str) -> str:
    """`numeric(10,2)` as `numeric`: an entity diagram's attribute type is one word."""
    return re.sub(r"[(\[].*", "", kind)


@generator("database-schema")
def database_schema(root: Path, page: dict) -> tuple[str, list[str]]:
    """The tables the migrations build: each table's columns, keys, and the comments beside them,
    with the references between tables drawn as an entity diagram. Read from the SQL in the
    migrations (`.sql` files and migration modules), in file order, so a later `ALTER TABLE ... ADD
    COLUMN` lands on its table. Structure only: no rows."""
    files = sorted({*_tracked(root, "**/migrations/**/*.py"), *_tracked(root, "**/migrations/**/*.sql"),
                    *_tracked(root, "**/schema/**/*.sql"), *_tracked(root, "**/schema*.sql"),
                    *_tracked(root, "**/db/**/*.sql")})
    tables: dict[str, list[tuple[str, str, str, str]]] = {}
    sources = []
    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        found = False
        for name, body in CREATE.findall(text):
            tables[name] = _columns(body)
            found = True
        for name, column, kind in ALTER.findall(text):
            if name in tables and column.lower() not in CONSTRAINTS:
                tables[name].append((column, kind.strip(), "", ""))
                found = True
        if found:
            sources.append(path.relative_to(root).as_posix())
    if not tables:
        return "", []
    lines = [f"The database the migrations build: {len(tables)} tables, read from {len(sources)} files.", "",
             "```mermaid", "erDiagram"]
    for name, columns in tables.items():
        for column, _, flags, _ in columns:
            target = next((f[3:] for f in flags.split(", ") if f.startswith("FK ")), "")
            if target in tables:
                lines.append(f"  {_mermaid_id(target)} ||--o{{ {_mermaid_id(name)} : {column}")
    for name, cols in tables.items():
        lines += [f"  {_mermaid_id(name)} {{", *[f"    {_mermaid_id(_base_type(t))} {_mermaid_id(c)}" for c, t, _, _ in cols[:12]], "  }"]
    lines += ["```"]
    for name, columns in tables.items():
        lines += ["", f"## `{name}`", "", "| Column | Type | Keys | Note |", "|---|---|---|---|"]
        lines += [f"| `{c}` | `{t}` | {k or '—'} | {_cell(n) or '—'} |" for c, t, k, n in columns]
    return "\n".join(lines) + "\n", sources


# --- compose-services ----------------------------------------------------------------------------

@generator("compose-services")
def compose_services(root: Path, page: dict) -> tuple[str, list[str]]:
    """The services each compose file runs: image or build, published ports, what each waits for."""
    files = [p for p in _tracked(root, "**/*.y*ml")
             if re.search(r"(^|/)(docker-)?compose(\.[\w-]+)?\.ya?ml$", p.relative_to(root).as_posix())]
    sections, sources = [], []
    for path in sorted(files):
        services = (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("services") or {}
        if not services:
            continue
        relative = path.relative_to(root).as_posix()
        rows, edges = [], []
        for name, spec in services.items():
            spec = spec or {}
            needs = spec.get("depends_on") or []
            needs = list(needs) if not isinstance(needs, list) else needs
            edges += [(name, n) for n in needs]
            source = spec.get("image") or ("built from `" + str((spec.get("build") or {}).get("context", spec.get("build")) if isinstance(spec.get("build"), dict) else spec.get("build")) + "`" if spec.get("build") else "—")
            ports = ", ".join(f"`{p}`" for p in spec.get("ports") or []) or "—"
            rows.append(f"| `{name}` | {_cell(str(source))} | {ports} | " + (", ".join(f"`{n}`" for n in needs) or "—") + " |")
        section = [f"## `{relative}`", "", f"Start with `docker compose -f {relative} up`.", "",
                   "| Service | Image or build | Ports | Waits for |", "|---|---|---|---|", *rows]
        if edges:
            section += ["", "```mermaid", "flowchart LR", *[f"  {_mermaid_id(a)}[{a}] --> {_mermaid_id(b)}[{b}]" for a, b in edges], "```"]
        sections.append("\n".join(section))
        sources.append(relative)
    if not sections:
        return "", []
    return f"The services the repository runs together, from {len(sources)} compose files.\n\n" + "\n\n".join(sections) + "\n", sources


# --- writing and checking -----------------------------------------------------------------------

def render(name: str, root: Path, header: str, title: str) -> str | None:
    """The whole page: its header, its sources with their digests, its title, and the generator's
    body; None with nothing to read. The sources are globs, so any provenance check (one without
    the generators, too) sees the page go stale when a file they match changes or appears."""
    body, globs = GENERATORS[name](root, {})
    if not body:
        return None
    from documentor.check import digest, read_source

    sources = [f"<!-- helix:source {g} sha256:{digest(read_source(root, g) or '')} -->" for g in globs]
    return "\n".join([header, *sources, f"# {title}", "", body.rstrip("\n")]) + "\n"


def load_plugins() -> None:
    """Generators other distributions register in the `documentor.generators` entry-point group."""
    from importlib.metadata import entry_points

    for entry in entry_points(group="documentor.generators"):
        GENERATORS.setdefault(entry.name, entry.load())


def render_command(command: str, sources: list[str], root: Path, header: str, title: str) -> str | None:
    """A page a repository's own command writes: the command's stdout is the body, the globs its
    sources. The command runs from the root with a shell; it never reads the page."""
    import subprocess

    from documentor.check import digest, read_source

    done = subprocess.run(command, shell=True, cwd=root, capture_output=True, text=True)
    if done.returncode or not done.stdout.strip():
        return None
    lines = [f"<!-- helix:source {g} sha256:{digest(read_source(root, g) or '')} -->" for g in sources]
    return "\n".join([header, *lines, f"# {title}", "", done.stdout.rstrip("\n")]) + "\n"


HEADER = re.compile(r"^<!-- helix:publish .*-->$", re.M)
TITLE = re.compile(r"^# (.+)$", re.M)


def regenerated(path: Path, root: Path, command: str = "", sources: list[str] | None = None) -> str | None:
    """What a generated page should hold now, from its own header and title. A page whose header
    says `generated=command` is regenerated with the command the plan gives for it."""
    text = path.read_text(encoding="utf-8")
    header, title = HEADER.search(text), TITLE.search(text)
    name = re.search(r"\bgenerated=(\S+)", header[0]) if header else None
    if not (header and title and name):
        return None
    if name[1] == "command":
        return render_command(command, sources or [], root, header[0], title[1]) if command else None
    load_plugins()
    if name[1] not in GENERATORS:
        return None
    return render(name[1], root, header[0], title[1])


def main(argv: list[str] | None = None) -> int:
    load_plugins()
    parser = argparse.ArgumentParser(prog="documentor generate", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("generator", nargs="?")
    parser.add_argument("--page", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--audience", "--flow", dest="audience", default="data")
    parser.add_argument("--title", default="")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args(argv)
    if args.list:
        for name, function in GENERATORS.items():
            print(f"{name:20} {(function.__doc__ or '').strip()}")
        return 0
    if args.generator not in GENERATORS or not args.page:
        parser.error(f"name a generator ({', '.join(GENERATORS)}) and --page")
    page = args.page.resolve()
    header = (f"<!-- helix:publish audience={args.audience} page={page.stem} kind=reference voice=onboarding "
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
