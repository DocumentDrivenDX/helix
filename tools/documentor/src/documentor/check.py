"""Check and stamp the pages of a guide (HELIX's `publishing.md`).

Usage:
    documentor check-pages <page-or-dir>... [--root DIR] [--strict-prose] [--format text|json]
    documentor stamp <page>... [--root DIR]

`check` reads each page's provenance header and reports:
  stale            a source's text changed after the page was stamped        (blocking)
  missing-source   a source path or `#section` no longer exists              (blocking)
  broken-link      a relative link resolves to no file                        (blocking)
  missing-path     a backticked repository path does not exist                (blocking)
  missing-test     a backticked test reference names a test the file does not define  (blocking)
  unmapped         a watched file is cited by no page                         (warning)
  kind             the header names no page kind, or one that is not Diátaxis's (warning)
  handling         the page matches a pattern the project's `handling:` forbids  (blocking)
  outside-scope    the pages are written outside `publish.scope`               (blocking)
  prose.*          a breach of the page's voice limits or budget              (warning;
                   blocking with --strict-prose)
`stamp` records the current digest of every source a page names.

A generated page (`generated=<id>` or `generated=command`) is regenerated in memory and compared.
An adopted page (`existing=yes`) is hand-maintained: it may name no sources, and its links, paths,
handling, and prose are checked. The root is the nearest directory above the page with a
`.helix.yml`, else with `.git`.

Exit codes: 0 = no blocking findings, 1 = blocking findings, 2 = usage error.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from documentor.lib import (
    CREATES,
    FENCE,
    HEADER,
    KINDS,
    SOURCE,
    catalog,
    config_of,
    expand,
    find_root,
    have_yaml,
    load_yaml,
    matching,
    plan,
    publish_out,
    repository_files,
    watches,
)

LINK = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
CODE_PATH = re.compile(r"`([\w.-]+(?:/[\w.-]+)+\.\w+)(?:::[\w:]+)?`|`([\w.-]+(?:/[\w.-]+)+/)`")
DIGEST_CHARS = 16


@dataclass
class Page:
    path: Path
    meta: dict[str, str]
    sources: list[tuple[str, str]]  # (spec, digest or "-")
    body: str
    body_line: int

    @property
    def audience(self) -> str:
        return self.meta.get("audience") or self.meta.get("flow") or ""


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


def body_digest(page: Path) -> str:
    """The page's text below its header: what an evaluation vouches for."""
    parsed = parse_page(page)
    return digest(parsed.body) if parsed else ""


# --- checks -----------------------------------------------------------------------------------

def check_generated(page: Page, root: Path, config: dict, findings: Findings) -> bool:
    """A generated page is current when regenerating it writes the same text; True if generated."""
    name = page.meta.get("generated")
    if not name:
        return False
    from documentor import generate

    text = page.path.read_text(encoding="utf-8")
    if name == "command":
        try:
            relative = page.path.resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            relative = ""
        planned = next((p for p in plan(config, root) if p.path == relative), None)
        if planned is None or not planned.command:
            findings.add("blocking", "missing-source", page.path,
                         "generated=command, but .helix.yml gives this page no `generated: {command: ...}`")
            return True
        fresh = generate.regenerated(page.path, root, planned.command, planned.sources)
        if fresh is None:
            findings.add("blocking", "stale", page.path, f"its command produced nothing: {planned.command}")
        elif fresh != text:
            findings.add("blocking", "stale", page.path, "its sources changed; run `documentor build`")
        return True
    generate.load_plugins()
    if name not in generate.GENERATORS:
        findings.add("blocking", "missing-source", page.path, f"no generator named {name}")
    elif generate.regenerated(page.path, root) != text:
        findings.add("blocking", "stale", page.path,
                     f"its sources changed; run `documentor generate {name} --page {page.path}`")
    return True


def check_sources(page: Page, root: Path, findings: Findings) -> None:
    if not page.sources and "existing" not in page.meta:
        findings.add("blocking", "missing-source", page.path, "the page names no sources")
    for spec, recorded in page.sources:
        text = read_source(root, spec)
        if text is None:
            findings.add("blocking", "missing-source", page.path, f"{spec} does not exist")
        elif recorded == "-":
            findings.add("blocking", "stale", page.path, f"{spec} was never stamped; run `documentor stamp`")
        elif digest(text) != recorded:
            findings.add("blocking", "stale", page.path, f"{spec} changed after the page was generated")


def check_kind(page: Page, findings: Findings) -> None:
    kind = page.meta.get("kind")
    if kind not in KINDS:
        found = f"kind={kind}" if kind else "no kind"
        findings.add("warning", "kind", page.path, f"the header has {found}; one of {', '.join(KINDS)}", 1)


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


PY_TEST = re.compile(r"`([\w./-]+\.py)::([\w:\[\]-]+)`")
JS_TEST = re.compile(r'`([\w./-]+\.(?:test|spec)\.[jt]sx?)`\s+"([^"]+)"')


def _python_names(path: Path) -> set[str]:
    import ast

    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return set()
    return {n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))}


def check_tests(page: Page, root: Path, findings: Findings) -> None:
    """A page that cites a test must name one that exists: `tests/test_x.py::test_y` (each `::` part a
    function or class the file defines; a pytest parameter id in brackets is ignored), or a JavaScript
    test file followed by its quoted title. A missing file is the path check's finding."""
    body = FENCE.sub("", page.body)
    for match in PY_TEST.finditer(body):
        target = root / match.group(1)
        if not target.is_file():
            continue
        names = _python_names(target)
        parts = [part.split("[", 1)[0] for part in match.group(2).split("::") if part]
        missing = [part for part in parts if part not in names]
        if missing:
            line = page.body_line + body.count("\n", 0, match.start())
            findings.add("blocking", "missing-test", page.path,
                         f"`{match.group(1)}` defines no {', '.join(missing)}", line)
    for match in JS_TEST.finditer(body):
        target = root / match.group(1)
        if target.is_file() and match.group(2) not in target.read_text(encoding="utf-8", errors="replace"):
            line = page.body_line + body.count("\n", 0, match.start())
            findings.add("blocking", "missing-test", page.path,
                         f"`{match.group(1)}` has no test titled \"{match.group(2)}\"", line)


def check_prose(page: Page, strict: bool, findings: Findings) -> None:
    from documentor import prose

    voice = load_yaml(catalog() / "helix" / "voice.yml") or {}
    limits = prose.limits_for(voice, page.meta.get("voice", "onboarding"), int(page.meta.get("budget", 0)))
    if limits is None:
        return
    severity = "blocking" if strict else "warning"
    for check, message, line in prose.audit(page.body, page.body_line, limits, prose.phrases(voice)):
        findings.add(severity, check, page.path, message, line)


def check_scope(config: dict, root: Path, findings: Findings) -> None:
    """`publish.scope` is the one directory the project allows the guide to be written under."""
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


def check_unmapped(pages: list[Page], root: Path, config: dict, findings: Findings) -> None:
    """A file the audiences, the traits, or the project watch, cited by no page, over the files git
    tracks (never a worktree or a build tree)."""
    publish = config.get("publish") or {}
    cited = {spec.partition("#")[0] for page in pages for spec, _ in page.sources}
    covered = [spec for page in pages for spec, _ in page.sources if any(c in spec for c in "*?[")]
    ignored = [expand(g, config) for g in publish.get("ignore") or []]
    files = repository_files(root)
    for watcher, pattern in watches(config, root):
        for relative in matching(files, pattern):
            if any(fnmatch.fnmatch(relative, g) for g in (*covered, *ignored)):
                continue
            if relative not in cited:
                findings.add("warning", "unmapped", root / publish_out(config),
                             f"{relative} is watched by {watcher} and cited by no page")


# --- commands ---------------------------------------------------------------------------------

def run_check(paths: list[Path], root: Path | None, strict_prose: bool) -> Findings:
    findings = Findings()
    files = pages_under(paths)
    root = root or find_root(paths[0] if paths else Path.cwd())
    pages = [p for p in (parse_page(f) for f in files) if p]
    if not pages:
        findings.notes.append("no guide pages (no helix:publish header) under the given paths")
    config_file = root / ".helix.yml"
    config = config_of(root) if have_yaml() else {}
    for page in pages:
        if not (have_yaml() and check_generated(page, root, config, findings)):
            check_sources(page, root, findings)
        check_kind(page, findings)
        check_links(page, root, findings)
        check_tests(page, root, findings)
    if have_yaml():
        check_handling(pages, config, findings)
        check_handling_drawings(paths, config, findings)
        check_scope(config, root, findings)
        for page in pages:
            if not page.meta.get("generated"):
                check_prose(page, strict_prose, findings)
        check_unmapped(pages, root, config, findings)
    else:
        if config_file.is_file() and re.search(r"^(handling|  scope):", config_file.read_text(encoding="utf-8"), re.M):
            findings.add("blocking", "handling", config_file,
                         "the project sets handling or publish.scope, which need PyYAML to check: "
                         "`pip install pyyaml`, or run the check with `uvx documentor`")
        findings.notes.append("prose, handling, and unmapped checks skipped: they need PyYAML")
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="documentor check-pages", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=("check", "stamp"))
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--strict-prose", action="store_true")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
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
