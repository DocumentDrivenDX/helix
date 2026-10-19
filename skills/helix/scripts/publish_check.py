#!/usr/bin/env python3
"""Check and stamp the pages `publish` generates (workflows/references/publishing.md).

Usage:
    publish_check.py check <page-or-dir>... [--root DIR] [--strict-prose] [--format text|json]
    publish_check.py stamp <page>... [--root DIR]

`check` reads each page's provenance header and reports:
  stale            a source's text changed after the page was stamped        (blocking)
  missing-source   a source path or `#section` no longer exists              (blocking)
  broken-link      a relative link resolves to no file                        (blocking)
  missing-path     a backticked repository path does not exist                (blocking)
  unmapped         a file a flow watches is cited by no page                  (warning)
  kind             the header names no page kind, or one that is not Diátaxis's (warning)
  handling         the page matches a pattern the project's `handling:` forbids  (blocking)
  outside-scope    the pages are written outside `publish.scope`               (blocking)
  prose.*          a breach of the page's voice limits or budget              (warning;
                   blocking with --strict-prose)
`stamp` records the current digest of every source a page names.

The root is the nearest directory above the page with a `.helix.yml`, else with `.git`. The
staleness, link, and path checks use only the standard library, so a project can run them in CI
without HELIX's dependencies; the prose and unmapped checks also need PyYAML and the catalog's
`voice.yml` and flows, and are skipped (with a note) when either is missing.

Exit codes: 0 = no blocking findings, 1 = blocking findings, 2 = usage error.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import posixpath
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

HEADER = re.compile(r"^<!-- helix:publish ((?:\w+=\S+ ?)+)-->$", re.M)
SOURCE = re.compile(r"^<!-- helix:source (\S+?)(?: sha256:([0-9a-f]+|-))? -->$", re.M)
LINK = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
CODE_PATH = re.compile(r"`([\w.-]+(?:/[\w.-]+)+\.\w+)(?:::[\w:]+)?`|`([\w.-]+(?:/[\w.-]+)+/)`")
FENCE = re.compile(r"^```.*?^```", re.M | re.S)
DIGEST_CHARS = 16
KINDS = ("tutorial", "how-to", "reference", "explanation")  # Diátaxis; publishing.md, Page kinds


@dataclass
class Page:
    path: Path
    meta: dict[str, str]
    sources: list[tuple[str, str]]  # (spec, digest or "-")
    body: str
    body_line: int


@dataclass
class Findings:
    items: list[dict] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def add(self, severity: str, check: str, page: Path, message: str, line: int = 0) -> None:
        self.items.append({"severity": severity, "check": check, "page": str(page), "message": message, "line": line})

    @property
    def blocking(self) -> int:
        return sum(1 for f in self.items if f["severity"] == "blocking")


# --- sources and digests ----------------------------------------------------------------------

def slugify(heading: str) -> str:
    """The anchor GitHub and Hugo give a heading: lowercase, punctuation dropped, spaces to hyphens."""
    text = re.sub(r"[^\w\s-]", "", heading.strip().lower())
    return re.sub(r"\s", "-", text)


def section(text: str, slug: str) -> str | None:
    """The section whose heading (H2 or deeper) has anchor `slug`: the heading through the line
    before the next heading of the same or a higher level. Headings inside code do not count."""
    lines, start, level, fenced = text.splitlines(), None, 0, False
    for index, line in enumerate(lines):
        if line.startswith("```"):
            fenced = not fenced
            continue
        heading = None if fenced else re.match(r"^(#{2,6}) (.+)$", line)
        if start is not None and heading and len(heading.group(1)) <= level:
            return "\n".join(lines[start:index])
        if start is None and heading and slugify(heading.group(2)) == slug:
            start, level = index, len(heading.group(1))
    return "\n".join(lines[start:]) if start is not None else None


def digest(text: str) -> str:
    normalized = "\n".join(line.rstrip() for line in text.strip().splitlines())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:DIGEST_CHARS]


def read_glob(root: Path, pattern: str) -> str | None:
    """Every file a glob source matches, named and in order, as one text; None when none match."""
    files = sorted(p for p in root.glob(pattern) if p.is_file())
    if not files:
        return None
    parts = [f"--- {p.relative_to(root).as_posix()}\n{p.read_text(encoding='utf-8', errors='replace')}"
             for p in files]
    return "\n".join(parts)


def read_source(root: Path, spec: str) -> str | None:
    path_part, _, slug = spec.partition("#")
    if any(c in path_part for c in "*?["):
        return read_glob(root, path_part)
    target = root / path_part
    if not target.is_file():
        return None
    text = target.read_text(encoding="utf-8", errors="replace")
    return section(text, slug) if slug else text


# --- pages ------------------------------------------------------------------------------------

def parse_page(path: Path) -> Page | None:
    text = path.read_text(encoding="utf-8")
    header = HEADER.search(text)
    if not header:
        return None
    meta = dict(pair.split("=", 1) for pair in header.group(1).split())
    sources = [(m.group(1), m.group(2) or "-") for m in SOURCE.finditer(text)]
    last = max([header.end()] + [m.end() for m in SOURCE.finditer(text)])
    return Page(path, meta, sources, text[last:], text.count("\n", 0, last) + 1)


def pages_under(paths: list[Path]) -> list[Path]:
    found: list[Path] = []
    for path in paths:
        found += sorted(path.rglob("*.md")) if path.is_dir() else [path]
    return found


def find_root(start: Path) -> Path:
    for parent in [start.resolve(), *start.resolve().parents]:
        if (parent / ".helix.yml").is_file() or (parent / ".git").exists():
            return parent
    return start.resolve()


# --- checks -----------------------------------------------------------------------------------

def check_generated(page: Page, root: Path, findings: Findings) -> bool:
    """A generated page is current when regenerating it writes the same text; True if generated."""
    name = page.meta.get("generated")
    if not name:
        return False
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import publish_generate

    if name not in publish_generate.GENERATORS:
        findings.add("blocking", "missing-source", page.path, f"no generator named {name}")
    elif publish_generate.regenerated(page.path, root) != page.path.read_text(encoding="utf-8"):
        findings.add("blocking", "stale", page.path,
                     f"its sources changed; run publish_generate.py {name} --page {page.path}")
    return True


def check_sources(page: Page, root: Path, findings: Findings) -> None:
    if not page.sources:
        findings.add("blocking", "missing-source", page.path, "the page names no sources")
    for spec, recorded in page.sources:
        text = read_source(root, spec)
        if text is None:
            findings.add("blocking", "missing-source", page.path, f"{spec} does not exist")
        elif recorded == "-":
            findings.add("blocking", "stale", page.path, f"{spec} was never stamped; run publish_check.py stamp")
        elif digest(text) != recorded:
            findings.add("blocking", "stale", page.path, f"{spec} changed after the page was generated")


def check_kind(page: Page, findings: Findings) -> None:
    kind = page.meta.get("kind")
    if kind not in KINDS:
        found = f"kind={kind}" if kind else "no kind"
        findings.add("warning", "kind", page.path, f"the header has {found}; one of {', '.join(KINDS)}", 1)


CREATES = re.compile(r"^<!-- helix:creates (\S+) -->$", re.M)


def check_links(page: Page, root: Path, findings: Findings) -> None:
    creates = set(CREATES.findall(page.path.read_text(encoding="utf-8")))
    body = FENCE.sub("", page.body)
    for match in LINK.finditer(body):
        target = match.group(1).split("#", 1)[0]
        if not target or re.match(r"^[a-z]+:", target) or target.startswith("/"):
            continue
        if not (page.path.parent / target).exists():
            line = page.body_line + body.count("\n", 0, match.start())
            findings.add("blocking", "broken-link", page.path, f"{match.group(1)} resolves to no file", line)
    for match in CODE_PATH.finditer(body):
        candidate = match.group(1) or match.group(2)
        if any(ch in candidate for ch in "<>*{}") or candidate.startswith(("http", "~", "../")):
            continue
        if not (root / candidate).exists() and candidate not in creates:
            line = page.body_line + body.count("\n", 0, match.start())
            findings.add("blocking", "missing-path", page.path,
                         f"`{candidate}` does not exist (a file the reader creates is named in the header: "
                         f"<!-- helix:creates {candidate} -->)", line)


# --- optional checks (PyYAML and the catalog) -------------------------------------------------

def catalog_dir() -> Path | None:
    here = Path(__file__).resolve().parent
    for candidate in (here.parent.parent.parent / "workflows", here.parent / "references"):
        if (candidate / "voice.yml").is_file():
            return candidate
    return None


def load_yaml(path: Path):
    try:
        import yaml
    except ImportError:
        return None
    return yaml.safe_load(path.read_text(encoding="utf-8")) if path.is_file() else None


def check_prose(page: Page, catalog: Path, strict: bool, findings: Findings) -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import prose_audit

    voice = load_yaml(catalog / "voice.yml") or {}
    limits = prose_audit.limits_for(voice, page.meta.get("voice", "onboarding"), int(page.meta.get("budget", 0)))
    if limits is None:
        return
    severity = "blocking" if strict else "warning"
    for check, message, line in prose_audit.audit(page.body, page.body_line, limits, prose_audit.phrases(voice)):
        findings.add(severity, check, page.path, message, line)


def helix_root(config: dict) -> str:
    return ((config.get("flows") or [{}])[0].get("root") or "docs/helix").rstrip("/")


def publish_out(config: dict) -> str:
    """Where pages are written: `publish.out`, else `guide` beside the HELIX root."""
    publish = config.get("publish") or {}
    if publish.get("out"):
        return str(publish["out"]).rstrip("/")
    parent = posixpath.dirname(helix_root(config))
    return posixpath.join(parent, "guide") if parent else "guide"


def check_scope(config: dict, root: Path, findings: Findings) -> None:
    """`publish.scope` is the one directory the project allows `publish` to write under."""
    scope = ((config.get("publish") or {}).get("scope") or "").rstrip("/")
    out = publish_out(config)
    if scope and not (out == scope or out.startswith(scope + "/")):
        findings.add("blocking", "outside-scope", root / out,
                     f"pages are written to {out}, outside publish.scope {scope}")


def check_handling(pages: list[Page], config: dict, findings: Findings) -> None:
    """No page may match a pattern the project's `handling:` forbids (a sample value, an id)."""
    for pattern in (config.get("handling") or {}).get("patterns") or []:
        expression = re.compile(pattern)
        for page in pages:
            for match in expression.finditer(page.body):
                line = page.body_line + page.body.count("\n", 0, match.start())
                findings.add("blocking", "handling", page.path,
                             f"matches the handling pattern {pattern!r}; remove it", line)


def check_handling_drawings(paths: list[Path], config: dict, findings: Findings) -> None:
    """Generated drawings beside the pages (architecture-views/*.svg) obey handling too."""
    patterns = [re.compile(p) for p in (config.get("handling") or {}).get("patterns") or []]
    for path in paths:
        for drawing in sorted(path.rglob("*.svg")) if path.is_dir() else []:
            text = drawing.read_text(encoding="utf-8", errors="replace")
            for expression in patterns:
                if expression.search(text):
                    findings.add("blocking", "handling", drawing,
                                 f"matches the handling pattern {expression.pattern!r}; fix the "
                                 "model it was drawn from and regenerate")


def have_yaml_now() -> bool:
    try:
        import yaml  # noqa: F401
    except ImportError:
        return False
    return True


def generated_roots(pages: list[Page], root: Path) -> tuple[str, ...]:
    """The glob sources pages cite (a generated page's inputs): every file they match is cited."""
    return tuple(spec for page in pages for spec, _ in page.sources if any(c in spec for c in "*?["))


def check_unmapped(pages: list[Page], root: Path, catalog: Path, findings: Findings) -> None:
    config = (load_yaml(root / ".helix.yml") or {})
    publish = config.get("publish") or {}
    helix = helix_root(config)
    cited = {spec.partition("#")[0] for page in pages for spec, _ in page.sources}
    covered = generated_roots(pages, root)
    watches = []
    for flow_id in publish.get("flows") or []:
        flow = load_yaml(catalog / "publish" / "flows" / f"{flow_id}.yml") or {}
        watches += [(f"the {flow_id} flow", p) for p in flow.get("watch") or []]
    for trait_id in publish.get("traits") or []:
        trait = load_yaml(catalog / "publish" / "traits" / f"{trait_id}.yml") or {}
        watches += [(f"the {trait_id} trait", p) for p in trait.get("watch") or []]
    ignored = [g.replace("{helix}", helix) for g in publish.get("ignore") or []]
    for watcher, pattern in watches:
        pattern = pattern.replace("{helix}", helix)
        for path in sorted(root.glob(pattern.replace("**/", "**/"))):
            relative = path.relative_to(root).as_posix()
            if any(fnmatch.fnmatch(relative, g) for g in (*covered, *ignored)):
                continue
            if path.is_file() and relative not in cited and fnmatch.fnmatch(relative, pattern):
                findings.add("warning", "unmapped", root / publish_out(config),
                             f"{relative} is watched by {watcher} and cited by no page")


# --- commands ---------------------------------------------------------------------------------

def run_check(paths: list[Path], root: Path | None, strict_prose: bool) -> Findings:
    findings = Findings()
    files = pages_under(paths)
    root = root or find_root(paths[0] if paths else Path.cwd())
    pages = [p for p in (parse_page(f) for f in files) if p]
    if not pages:
        findings.notes.append("no generated pages (no helix:publish header) under the given paths")
    for page in pages:
        if not (have_yaml_now() and check_generated(page, root, findings)):
            check_sources(page, root, findings)
        check_kind(page, findings)
        check_links(page, root, findings)
    catalog = catalog_dir()
    try:
        import yaml  # noqa: F401
        have_yaml = True
    except ImportError:
        have_yaml = False
    config_file = root / ".helix.yml"
    if have_yaml:
        config = load_yaml(config_file) or {}
        check_handling(pages, config, findings)
        check_handling_drawings(paths, config, findings)
        check_scope(config, root, findings)
    elif config_file.is_file() and re.search(r"^(handling|  scope):", config_file.read_text(encoding="utf-8"), re.M):
        findings.add("blocking", "handling", config_file,
                     "the project sets handling or publish.scope, which need PyYAML to check; install it")
    if catalog and have_yaml:
        for page in pages:
            if not page.meta.get("generated"):
                check_prose(page, catalog, strict_prose, findings)
        check_unmapped(pages, root, catalog, findings)
    else:
        findings.notes.append("prose and unmapped checks skipped: they need PyYAML and the HELIX catalog")
    return findings


def run_stamp(files: list[Path], root: Path | None) -> int:
    status = 0
    for path in files:
        page = parse_page(path)
        if page is None:
            print(f"{path}: no helix:publish header", file=sys.stderr)
            status = 2
            continue
        base = root or find_root(path)
        text = path.read_text(encoding="utf-8")
        for spec, _ in page.sources:
            source = read_source(base, spec)
            if source is None:
                print(f"{path}: {spec} does not exist", file=sys.stderr)
                status = 1
                continue
            text = re.sub(rf"^<!-- helix:source {re.escape(spec)}(?: sha256:\S+)? -->$",
                          f"<!-- helix:source {spec} sha256:{digest(source)} -->", text, flags=re.M)
        path.write_text(text, encoding="utf-8")
        print(f"stamped {path} ({len(page.sources)} sources)")
    return status


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=("check", "stamp"))
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--strict-prose", action="store_true")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()
    root = args.root.resolve() if args.root else None
    if args.command == "stamp":
        return run_stamp(pages_under(args.paths), root)
    findings = run_check(args.paths, root, args.strict_prose)
    if args.format == "json":
        print(json.dumps({"findings": findings.items, "notes": findings.notes, "blocking": findings.blocking}, indent=2))
    else:
        for f in findings.items:
            where = f"{f['page']}:{f['line']}" if f["line"] else f["page"]
            print(f"{f['severity'].upper():<9} {f['check']}  {where}  {f['message']}")
        for note in findings.notes:
            print(f"NOTE      {note}")
        status = "FAIL" if findings.blocking else "OK"
        print(f"{status}: {len(pages_under(args.paths))} files checked, {findings.blocking} blocking, "
              f"{len(findings.items) - findings.blocking} warnings")
    return 1 if findings.blocking else 0


if __name__ == "__main__":
    sys.exit(main())
