"""Draft an architecture model from what the repository already declares.

A repository with no `architecture-model.toml` gets no views. Most of a first model is in files the
repository already has: the services a compose file runs and what each depends on, the apps and
jobs a Databricks bundle deploys, the database its migrations build, the web frontend its package
manifest names, the command line or API its Python project installs. Each becomes an element or a
relation citing the file and the string that shows it, so the draft passes `documentor views
--check` as written and fails the moment the code stops saying so. The draft is a start: a person
or the agent names things better, adds what no file declares, and removes what does not matter.

    documentor model draft [--root DIR] [--write] [--force]

Without `--write` the draft is printed. `--write` writes it to the project's model path
(`<HELIX root>/02-design/architecture-model.toml`) and refuses to replace an existing model
without `--force`.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from documentor.lib import find_root, incidental, repository_files

STORES = re.compile(r"(postgres|mysql|mariadb|redis|mongo|elasticsearch|opensearch|rabbitmq|kafka|minio|clickhouse|memcached|valkey)", re.I)
FRONTENDS = ("react", "vue", "svelte", "next", "@angular/core", "solid-js")
APIS = ("fastapi", "flask", "django", "starlette", "litestar")
NAMES = {"fastapi": "FastAPI", "flask": "Flask", "django": "Django", "starlette": "Starlette", "litestar": "Litestar",
         "react": "React", "vue": "Vue", "svelte": "Svelte", "next": "Next.js", "core": "Angular", "solid-js": "Solid"}
MAX_VIEW = 15


@dataclass
class Element:
    id: str
    name: str
    kind: str
    path: str
    contains: str
    detail: str = ""
    tier: int = 2
    zone: str = "Apps"


@dataclass
class Relation:
    source: str
    target: str
    label: str
    path: str
    contains: str


@dataclass
class Draft:
    system: str
    name: str
    elements: dict[str, Element] = field(default_factory=dict)
    relations: list[Relation] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)

    def add(self, element: Element) -> str:
        """Add an element; one with the same id and kind is the same part, seen from another file
        (a Databricks App and the Python project it runs), so their details merge."""
        base, n = element.id, 2
        while element.id in self.elements:
            known = self.elements[element.id]
            if known.kind == element.kind:
                if element.detail and element.detail not in known.detail:
                    known.detail = "; ".join(d for d in (known.detail, element.detail) if d)
                return known.id
            element.id, n = f"{base}-{n}", n + 1
        self.elements[element.id] = element
        if element.path not in self.sources:
            self.sources.append(element.path)
        return element.id

    def relate(self, relation: Relation) -> None:
        key = (relation.source, relation.target)
        if relation.source != relation.target and key not in {(r.source, r.target) for r in self.relations}:
            self.relations.append(relation)


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "part"


def title(text: str) -> str:
    words = re.split(r"[-_ ]+", text)
    return " ".join(w[:1].upper() + w[1:] for w in words if w)


def _read(root: Path, path: str) -> str:
    try:
        return (root / path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def _line(text: str, pattern: str) -> str:
    """The first line of `text` matching `pattern`, stripped: a string the file certainly contains."""
    for line in text.splitlines():
        if re.search(pattern, line):
            return line.strip()
    return ""


def _owner_of(draft: Draft, path: str) -> str:
    """The element whose source directory holds `path`, else the first container."""
    best, depth = "", -1
    for element in draft.elements.values():
        if element.kind != "container":
            continue
        folder = str(Path(element.path).parent)
        folder = "" if folder == "." else folder
        if (not folder or path.startswith(folder + "/")) and len(folder) > depth:
            best, depth = element.id, len(folder)
    return best


# --- what each kind of file declares ---------------------------------------------------------------

def compose(draft: Draft, root: Path, path: str, files: list[str]) -> None:
    text = _read(root, path)
    data = yaml.safe_load(text) or {}
    services = data.get("services") or {}
    ids = {}
    for name, spec in services.items():
        spec = spec or {}
        image = str(spec.get("image", ""))
        store = bool(STORES.search(image) or STORES.search(name))
        ports = ", ".join(str(p).split(":")[-1] for p in spec.get("ports") or [])
        ids[name] = draft.add(Element(
            id=slug(name), name=title(name), kind="store" if store else "container", path=path,
            contains=f"{name}:", detail=image.split(":")[0] if image else (f"port {ports}" if ports else ""),
            tier=3 if store else 2, zone="Data" if store else "Apps"))
    for name, spec in services.items():
        needs = (spec or {}).get("depends_on") or []
        for dep in (needs if isinstance(needs, list) else list(needs)):
            if dep in ids:
                draft.relate(Relation(ids[name], ids[dep], "depends on", path, str(dep)))


def dockerfile(draft: Draft, root: Path, path: str, files: list[str]) -> None:
    if any(e.path.startswith(str(Path(path).parent)) and "compose" in e.path for e in draft.elements.values()):
        return
    base = _line(_read(root, path), r"^\s*FROM\s")
    if not base:
        return
    folder = Path(path).parent.name if Path(path).parent != Path(".") else draft.system
    draft.add(Element(id=slug(folder), name=title(folder), kind="container", path=path, contains=base,
                      detail="container image"))


COLLAPSE = 5  # a bundle with more jobs (or pipelines, apps, dashboards) than this draws them as one part


def databricks(draft: Draft, root: Path, path: str, files: list[str]) -> None:
    import fnmatch

    text = _read(root, path)
    data = yaml.safe_load(text) or {}
    folder = str(Path(path).parent)
    folder = "" if folder == "." else folder + "/"
    declared: dict[str, list[tuple[str, str, str]]] = {}  # kind -> [(key, file, the include line)]

    def collect(resources: dict, file: str, line: str) -> None:
        for kind, entries in (resources or {}).items():
            for key in (entries or {}):
                declared.setdefault(kind, []).append((key, file, line))

    collect(data.get("resources"), path, "")
    for target in (data.get("targets") or {}).values():
        collect((target or {}).get("resources"), path, "")
    for pattern in data.get("include") or []:
        line = _line(text, re.escape(pattern))
        for file in files:
            if file.startswith(folder) and fnmatch.fnmatch(file[len(folder):], pattern) and file.endswith((".yml", ".yaml")):
                collect((yaml.safe_load(_read(root, file)) or {}).get("resources"), file, line)
    labels = {"apps": "Databricks App", "jobs": "Databricks job", "pipelines": "Lakeflow pipeline",
              "dashboards": "Databricks dashboard"}
    ZONES = {"apps": "Apps", "jobs": "Jobs", "pipelines": "Jobs", "dashboards": "Apps"}
    if not any(declared.get(k) for k in labels):
        return
    platform = draft.add(Element(id="databricks", name="Databricks workspace", kind="external", path=path,
                                 contains=_line(text, r"^bundle:") or "bundle", tier=3, zone="Platform"))
    bundle = (data.get("bundle") or {}).get("name") or Path(path).parent.name or draft.system
    for kind, label in labels.items():
        entries = [(k, f, line) for k, f, line in declared.get(kind) or [] if f"{k}:" in _read(root, f)]
        if len(entries) > COLLAPSE:
            _, file, line = entries[0]
            evidence = (path, line) if line else (file, f"{entries[0][0]}:")
            element = draft.add(Element(id=slug(f"{bundle}-{kind}"), name=f"{title(bundle)} {kind}",
                                        kind="container", path=evidence[0], contains=evidence[1],
                                        detail=f"{len(entries)} {label.split()[-1].lower()}s", zone=ZONES[kind]))
            draft.relate(Relation(element, platform, "runs on", *evidence))
            continue
        for key, file, _ in entries:
            element = draft.add(Element(id=slug(key), name=title(key), kind="container", path=file,
                                        contains=f"{key}:", detail=label, zone=ZONES[kind]))
            draft.relate(Relation(element, platform, "runs on", file, f"{key}:"))


def alembic(draft: Draft, root: Path, path: str, files: list[str]) -> None:
    text = _read(root, path)
    line = _line(text, r"^script_location")
    if not line:
        return
    store = draft.add(Element(id="database", name="Database", kind="store", path=path, contains=line,
                              detail="schema by Alembic migrations", tier=3, zone="Data"))
    owner = _owner_of(draft, path)
    if owner:
        draft.relate(Relation(owner, store, "reads and writes", path, line))


def package_json(draft: Draft, root: Path, path: str, files: list[str]) -> None:
    text = _read(root, path)
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return
    deps = {**(data.get("dependencies") or {}), **(data.get("devDependencies") or {})}
    framework = next((f for f in FRONTENDS if f in deps), "")
    if not framework:
        return
    name = data.get("name") or Path(path).parent.name or "web"
    web = draft.add(Element(id=slug(Path(path).parent.name or "web"), name=title(Path(path).parent.name or "web"),
                            kind="container", path=path, contains=f'"{framework}"',
                            detail=f"{NAMES.get(framework.split('/')[-1], title(framework))} frontend"))
    person = draft.add(Element(id="user", name="User", kind="person", path=path, contains=f'"{name}"',
                               tier=1, zone="People"))
    draft.relate(Relation(person, web, "uses", path, f'"{name}"'))


def pyproject(draft: Draft, root: Path, path: str, files: list[str]) -> None:
    text = _read(root, path)
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError:
        return
    project = data.get("project") or {}
    name = project.get("name")
    if not name:
        return
    deps = " ".join(project.get("dependencies") or []).lower()
    api = next((a for a in APIS if re.search(rf"\b{a}\b", deps)), "")
    scripts = project.get("scripts") or {}
    if not (api or scripts):
        return
    detail = f"{NAMES.get(api, title(api))} API" if api else f"command line `{next(iter(scripts))}`"
    contains = _line(text, rf"^\s*\"?{re.escape(api)}") if api else _line(text, rf"^\s*\"?{re.escape(next(iter(scripts)))}\"?\s*=")
    draft.add(Element(id=slug(name), name=title(name), kind="container", path=path,
                      contains=contains or f'name = "{name}"', detail=detail))


def frontend_calls(draft: Draft, root: Path, files: list[str]) -> None:
    """A frontend that fetches `/api/...` calls the project's API, when there is one."""
    webs = [e for e in draft.elements.values() if e.detail.endswith("frontend")]
    apis = [e for e in draft.elements.values() if e.detail.endswith("API")]
    if not (webs and apis):
        return
    for web in webs:
        folder = str(Path(web.path).parent)
        for path in files:
            if path.startswith(folder + "/") and path.endswith((".ts", ".tsx", ".js", ".jsx")) and "/api/" in _read(root, path):
                draft.relate(Relation(web.id, apis[0].id, "calls the API", path, "/api/"))
                break


READERS = (
    (re.compile(r"(^|/)(docker-)?compose(\.[\w-]+)?\.ya?ml$"), compose),
    (re.compile(r"(^|/)Dockerfile$"), dockerfile),
    (re.compile(r"(^|/)databricks\.yml$"), databricks),
    (re.compile(r"(^|/)pyproject\.toml$"), pyproject),
    (re.compile(r"(^|/)package\.json$"), package_json),
    (re.compile(r"(^|/)alembic\.ini$"), alembic),
)


def draft_model(root: Path) -> Draft:
    files = [f for f in repository_files(root) if not incidental(f)]
    draft = Draft(system=slug(root.name), name=title(root.name))
    for pattern, read in READERS:  # in this order: containers before what attaches to them
        for path in files:
            if pattern.search(path):
                read(draft, root, path, files)
    frontend_calls(draft, root, files)
    return draft


# --- the TOML ------------------------------------------------------------------------------------

def _q(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _evidence(path: str, contains: str) -> str:
    return f"[{{ path = {_q(path)}, contains = {_q(contains)} }}]"


def to_toml(draft: Draft) -> str:
    elements = list(draft.elements.values())
    lines = [
        "# Drafted by `documentor model draft` from the files cited below. Rename, describe, add what no",
        "# file declares, and remove what a reader does not need; `documentor views --check` holds every",
        "# element and relation to its evidence (workflows/references/architecture-model.md).",
        "",
        "[system]",
        f"id = {_q(draft.system)}",
        "",
    ]
    for e in elements:
        lines += ["[[element]]", f"id = {_q(e.id)}", f"name = {_q(e.name)}"]
        if e.detail:
            lines.append(f"detail = {_q(e.detail)}")
        lines += [f"kind = {_q(e.kind)}", 'status = "built"', f"tier = {e.tier}", f"zone = {_q(e.zone)}",
                  f"evidence = {_evidence(e.path, e.contains)}", ""]
    for r in draft.relations:
        lines += ["[[relation]]", f"from = {_q(r.source)}", f"to = {_q(r.target)}", f"label = {_q(r.label)}",
                  'status = "built"', f"evidence = {_evidence(r.path, r.contains)}", ""]
    shown = [e.id for e in elements][:MAX_VIEW]
    lines += ["[[view]]", 'id = "containers"', f"title = {_q(draft.name + ': its parts')}",
              f"elements = {json.dumps(shown)}", "",
              "[[view]]", 'id = "deployment"', 'type = "deployment"', f"title = {_q('Where ' + draft.name + ' runs')}",
              f"elements = {json.dumps(shown)}", ""]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="documentor model draft", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--write", action="store_true", help="write the draft to the project's model path")
    parser.add_argument("--force", action="store_true", help="replace an existing model")
    args = parser.parse_args(argv)
    root = find_root(args.root or Path.cwd())
    draft = draft_model(root)
    if len(draft.elements) < 2:
        print("documentor model draft: nothing in the repository declares two or more parts "
              "(compose services, a Databricks bundle, a frontend, an API, migrations); write the model by hand",
              file=sys.stderr)
        return 1
    text = to_toml(draft)
    if not args.write:
        print(text, end="")
        return 0
    from documentor.architecture.model import default_model

    path = default_model(root)
    if path.exists() and not args.force:
        print(f"documentor model draft: {path} exists; --force replaces it", file=sys.stderr)
        return 2
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path} ({len(draft.elements)} elements, {len(draft.relations)} relations, from {len(draft.sources)} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
