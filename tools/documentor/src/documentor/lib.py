"""What every documentor command shares: the page header, root and catalog resolution, the project's
configuration, the files git tracks, and the plan of pages the configuration implies.

The catalog is package data under `documentor/catalog/`: `helix/` is copied from the HELIX
repository's `workflows/` (the audiences and the voice profiles are HELIX's), the rest is documentor's own (traits,
themes, the CI template). A project adds to it from `.helix.yml`: `publish.traits_dir` for its own
traits, `publish.pages` for its own pages, `publish.delegate` and `publish.existing` for pages it
already has.
"""

from __future__ import annotations

import fnmatch
import posixpath
import re
import subprocess
from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path

HEADER = re.compile(r"^<!-- helix:publish ((?:\w+=\S+ ?)+)-->$", re.M)
SOURCE = re.compile(r"^<!-- helix:source (\S+?)(?: sha256:([0-9a-f]+|-))? -->$", re.M)
CREATES = re.compile(r"^<!-- helix:creates (\S+) -->$", re.M)
GAP = re.compile(r"^<!-- helix:gap (\S+) -->$", re.M)  # a HELIX artifact the page was written without
FENCE = re.compile(r"^```.*?^```", re.M | re.S)
KINDS = ("tutorial", "how-to", "reference", "explanation")  # Diátaxis
SCHEMA = 1  # the `publish.schema` this version reads
# Directories that never hold a source: build output, vendored code, tool state. (Not `resources`
# or `public`: a Databricks bundle keeps its jobs under resources/.)
SKIP = {".git", ".ddx", ".claude", "node_modules", ".venv", "venv", "dist", "build", ".helix",
        "__pycache__", ".tox", "site-packages", ".terraform"}


# --- catalog and root -----------------------------------------------------------------------------

def catalog() -> Path:
    """The package's catalog directory (audiences, voice, traits, themes, CI template)."""
    return Path(str(resources.files("documentor") / "catalog"))


_CATALOG_OVERRIDE: Path | None = None


def set_catalog(path: str | Path | None) -> None:
    """Use this directory, laid out like HELIX's `workflows/`, as the HELIX half of the catalog."""
    global _CATALOG_OVERRIDE
    _CATALOG_OVERRIDE = Path(path).resolve() if path else None


def _is_helix_catalog(path: Path) -> bool:
    return (path / "voice.yml").is_file() and (path / "publish" / "audiences").is_dir()


def helix_catalog() -> Path:
    """The HELIX half of the catalog (audiences, voice, the writing pass, deliverables), laid out like
    `workflows/`: `--catalog` or `DOCUMENTOR_CATALOG` when given; else the HELIX checkout this tool
    sits in, read live; else the copy packaged with the tool (`scripts/sync_references.py --subset
    documentor` writes it, from the same tree, at the same release)."""
    import os

    for given in (_CATALOG_OVERRIDE, os.environ.get("DOCUMENTOR_CATALOG")):
        if given:
            path = Path(given).resolve()
            if not _is_helix_catalog(path):
                raise SystemExit(f"documentor: {path} is not a HELIX catalog (no voice.yml and publish/audiences)")
            return path
    for parent in Path(__file__).resolve().parents:
        if _is_helix_catalog(parent / "workflows"):
            return parent / "workflows"
    return catalog() / "helix"


def helix_version() -> str:
    """Which HELIX catalog this run reads: a path when live or given, else the copy packaged with
    this release (documentor is released with HELIX, at the same version)."""
    from documentor import __version__

    source = helix_catalog()
    if source != catalog() / "helix":
        return f"live {source}"
    return f"packaged {__version__}"


def find_root(start: Path) -> Path:
    """The project root: the nearest directory above `start` with a `.helix.yml`, else with `.git`."""
    start = start.resolve()
    chain = [start, *start.parents]
    for parent in chain:
        if (parent / ".helix.yml").is_file():
            return parent
    for parent in chain:
        if (parent / ".git").exists():
            return parent
    return start


# --- configuration ------------------------------------------------------------------------------------

def have_yaml() -> bool:
    try:
        import yaml  # noqa: F401
    except ImportError:
        return False
    return True


def load_yaml(path: Path):
    """The file's YAML; {} when the file is missing; None when PyYAML is not installed."""
    try:
        import yaml
    except ImportError:
        return None
    if not path.is_file():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def config_of(root: Path) -> dict:
    return load_yaml(root / ".helix.yml") or {}


def helix_root(config: dict) -> str:
    return ((config.get("flows") or [{}])[0].get("root") or "docs/helix").rstrip("/")


def publish_out(config: dict) -> str:
    """Where pages are written: `publish.out`, else `guide` beside the HELIX root."""
    publish = config.get("publish") or {}
    if publish.get("out"):
        return str(publish["out"]).rstrip("/")
    parent = posixpath.dirname(helix_root(config))
    return posixpath.join(parent, "guide") if parent else "guide"


def audiences(config: dict) -> list[str]:
    """The readers the project publishes for (`publish.audiences`; `publish.flows` is the old name)."""
    publish = config.get("publish") or {}
    return list(publish.get("audiences") or publish.get("flows") or [])


def expand(pattern: str, config: dict) -> str:
    return pattern.replace("{helix}", helix_root(config))


# --- the repository's files ---------------------------------------------------------------------

INCIDENTAL_DIRS = {"test", "tests", "__tests__", "testdata", "test_data", "e2e", "fixture", "fixtures",
                   "example", "examples", "sample", "samples", "demo", "demos"}


def incidental(path: str) -> bool:
    """A test, fixture, or example: it shows what the repository can do, not what it is. A
    directory counts by its whole name (`tests/`, `examples/`, `e2e/`, a `*_test` or `test_*`
    package), never by a substring, so `03-test/` or `test-plan/` is not incidental."""
    for part in path.split("/")[:-1]:
        name = part.lower()
        if name in INCIDENTAL_DIRS or name.startswith(("test_", "tests_", "e2e")) or name.endswith(("_test", "_tests", "-e2e")):
            return True
    return False


def repository_files(root: Path) -> list[str]:
    """The files git tracks, else every file under the root, skipping build and vendor trees."""
    tracked = subprocess.run(["git", "-C", str(root), "ls-files"], capture_output=True, text=True)
    if tracked.returncode == 0 and tracked.stdout.strip():
        return sorted(line for line in tracked.stdout.splitlines()
                      if not SKIP & set(line.split("/")) and (root / line).is_file())
    found: list[str] = []
    stack = [root]
    while stack:
        here = stack.pop()
        for entry in here.iterdir():
            if entry.is_dir():
                if entry.name not in SKIP and not entry.is_symlink():
                    stack.append(entry)
            elif entry.is_file():
                found.append(entry.relative_to(root).as_posix())
    return sorted(found)


def matching(files: list[str], pattern: str) -> list[str]:
    """Files a glob matches; `**/` matches any depth, including none."""
    if pattern.startswith("**/"):
        tail = pattern[3:]
        return [f for f in files if fnmatch.fnmatch(f, tail) or fnmatch.fnmatch(f, "*/" + tail)]
    if "**" in pattern:
        return [f for f in files if fnmatch.fnmatch(f, pattern)]
    return [f for f in files if fnmatch.fnmatch(f, pattern) and f.count("/") == pattern.count("/")]


# --- audiences and traits ---------------------------------------------------------------------------

def load_audience(audience_id: str) -> dict:
    return load_yaml(helix_catalog() / "publish" / "audiences" / f"{audience_id}.yml") or {}


def trait_dirs(config: dict, root: Path | None) -> list[Path]:
    """The catalog's traits, then the project's own (`publish.traits_dir`, default `.helix/traits`)."""
    dirs = [catalog() / "traits"]
    if root is not None:
        local = root / ((config.get("publish") or {}).get("traits_dir") or ".helix/traits")
        if local.is_dir():
            dirs.append(local)
    return dirs


def load_traits(config: dict, root: Path | None, ids: list[str] | None = None) -> list[dict]:
    """Every trait by id, a project trait replacing a catalog trait of the same id; `ids` selects."""
    found: dict[str, dict] = {}
    for directory in trait_dirs(config, root):
        for path in sorted(directory.glob("*.yml")):
            data = load_yaml(path) or {}
            if "id" in data:
                found[data["id"]] = data
    if ids is None:
        return list(found.values())
    missing = [i for i in ids if i not in found]
    if missing:
        raise KeyError(f"unknown trait(s) in .helix.yml publish.traits: {', '.join(missing)}")
    return [found[i] for i in ids]


def significant() -> list[str]:
    return list((load_yaml(catalog() / "traits" / "significant.yml") or {}).get("files") or [])


def watches(config: dict, root: Path) -> list[tuple[str, str]]:
    """(who watches, glob) for the audiences, the traits, and the project (`publish.watch`)."""
    publish = config.get("publish") or {}
    found = []
    for audience_id in audiences(config):
        found += [(f"the {audience_id} audience", expand(p, config)) for p in load_audience(audience_id).get("watch") or []]
    for trait in load_traits(config, root, publish.get("traits") or []):
        found += [(f"the {trait['id']} trait", expand(p, config)) for p in trait.get("watch") or []]
    found += [("the project", expand(p, config)) for p in publish.get("watch") or []]
    return found


# --- the plan ------------------------------------------------------------------------------------------

@dataclass
class PagePlan:
    audience: str
    id: str
    title: str
    kind: str
    work: str  # generated | written | delegated | existing
    path: str  # relative to the root
    task: str = ""
    generator: str = ""  # a packaged generator's id
    command: str = ""  # a repository-owned generator: a command run from the root
    sources: list = field(default_factory=list)  # source hints (written) or globs (command)
    tool: str = ""
    build: str = ""
    covers: str = ""
    url: str = ""
    entry: dict = field(default_factory=dict)

    @property
    def key(self) -> str:
        return f"{self.audience}/{self.id}"


def _strip(page: dict) -> dict:
    return {k: v for k, v in page.items() if k not in ("audience", "flow")}


def plan(config: dict, root: Path) -> list[PagePlan]:
    """The guide's pages: each audience's pages, replaced or joined by the traits' and the
    project's, with the project's delegated and existing pages marked."""
    publish = config.get("publish") or {}
    out = publish_out(config)
    traits = load_traits(config, root, publish.get("traits") or [])
    delegated = {d["page"]: d for t in traits for d in t.get("delegates") or []}
    if {"umf-tablespec", "tablespec-pipeline"} <= set(publish.get("traits") or []):
        delegated["data/pipeline-tables"] = delegated.pop("data/tables")
    delegated.update(publish.get("delegate") or {})
    existing = publish.get("existing") or {}
    skipped = set(publish.get("skip") or [])
    files = None
    pages: list[PagePlan] = []
    for audience_id in audiences(config):
        audience = load_audience(audience_id)
        if audience_id == "data" and publish.get("data_mode") == "operational":
            audience = load_yaml(helix_catalog() / "publish" / "audiences" / "data-operational.yml")
        extra = [_strip(p) for t in traits for p in t.get("pages") or []
                 if p.get("audience", p.get("flow")) == audience_id]
        extra += list((publish.get("pages") or {}).get(audience_id) or [])
        replacing = {e["id"]: e for e in extra}
        entries = [replacing.pop(e["id"], e) for e in audience.get("pages") or []] + list(replacing.values())
        own = existing.get(audience_id) or []
        mapped = own if isinstance(own, dict) else {}
        for entry in entries:
            if f"{audience_id}/{entry['id']}" in skipped:
                continue
            if entry["id"] in mapped:
                # The project's own page stands in for this audience page, adopted unchanged.
                pages.append(PagePlan(audience_id, entry["id"], entry.get("title", entry["id"]), entry.get("kind", ""),
                                      "existing", mapped[entry["id"]], entry.get("task", ""), entry=entry))
                continue
            generated = entry.get("generated")
            page = PagePlan(audience_id, entry["id"], entry.get("title", entry["id"]), entry.get("kind", ""),
                            "generated" if generated else "written", f"{out}/{audience_id}/{entry['id']}.md",
                            entry.get("task", ""), entry=entry)
            if isinstance(generated, dict):
                page.command = str(generated.get("command") or "")
                page.sources = list(generated.get("sources") or [])
            elif generated:
                page.generator = str(generated)
            else:
                page.sources = [s if isinstance(s, str) else next(iter(s.values()), "")
                                for s in entry.get("sources") or []]
            delegate = delegated.get(page.key)
            if delegate:
                page.work = "delegated"
                page.tool, page.build = delegate.get("tool", ""), delegate.get("build", "")
                page.covers, page.url = delegate.get("covers", ""), delegate.get("url", "")
            pages.append(page)
        planned = {p.id for p in pages if p.audience == audience_id}
        for key, delegate in delegated.items():
            part, _, page_id = key.partition("/")
            if part == audience_id and page_id not in planned and key not in skipped:
                # A delegated page the audience does not define: the project's own reference, linked.
                pages.append(PagePlan(audience_id, page_id, page_id.replace("-", " ").capitalize(), "reference", "delegated",
                                      f"{out}/{audience_id}/{page_id}.md", tool=delegate.get("tool", ""),
                                      build=delegate.get("build", ""), covers=delegate.get("covers", ""), url=delegate.get("url", "")))
                planned.add(page_id)
        for page_id, path in mapped.items():
            if page_id not in planned:  # a project page of its own, not standing in for an audience page
                pages.append(PagePlan(audience_id, page_id, page_id.replace("-", " ").replace("_", " ").capitalize(),
                                      "", "existing", path))
        for pattern in (own if isinstance(own, list) else []):
            files = repository_files(root) if files is None else files
            for rel in matching(files, expand(pattern, config)):
                stem = Path(rel).stem
                if any(p.audience == audience_id and p.id == stem for p in pages):
                    continue
                pages.append(PagePlan(audience_id, stem, stem.replace("-", " ").replace("_", " ").capitalize(),
                                      "", "existing", rel))
    return pages
