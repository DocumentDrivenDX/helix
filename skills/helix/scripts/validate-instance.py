#!/usr/bin/env python3
"""Validate a HELIX artifact instance against its catalog type's `validation:` block.

Usage:
    validate-instance.py <instance.md> [--catalog DIR] [--type TYPE] [--format text|json]

Checks run, in order:
  frontmatter        ddx.id, ddx.type/ddx.activity, ddx.authoring.home
  required_sections  each catalog section id must be an H2 in the instance
  pattern_checks     regex entries {pattern, expected, message[, severity]}
                     where expected is 0 (must not match) or >=N
  automated_checks   rule entries {check, type, field[, severity, message]}
                     with type unique_constraint, or not_equals plus `value`;
                     other rule types are reported as unsupported without failing
  placeholder        leftover template markers ([TODO], TBD, [Fill in], ...)

Exit codes: 0 = no blocking findings, 1 = blocking findings, 2 = usage or
resolution error (instance unreadable, type or catalog unresolvable).

Requires PyYAML (`python3 -c 'import yaml'`); fails with a clear message otherwise.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

# Uppercase ID prefixes that identify a type when the frontmatter has no
# `ddx.type`. Catalog `id_format.prefix` entries are merged over this table.
PREFIX_TYPES = {
    "PRD": "prd",
    "FEAT": "feature-specification",
    "US": "user-stories",
    "ADR": "adr",
    "SD": "solution-design",
    "TD": "technical-design",
    "TP": "test-plan",
    "STP": "story-test-plan",
    "CONTRACT": "contract",
    "RISK": "risk-register",
    "SPIKE": "tech-spike",
    "POC": "proof-of-concept",
}

# Explicit leftover markers (blocking) and generic template bracket tokens
# such as `[Name]` or `[Stakeholder Name/Role]` (warning). Wiki-links `[[..]]`,
# markdown links `[text](url)`, checkboxes and IDs like `[ADR-003]` do not match.
PLACEHOLDER_RE = re.compile(r"\[TODO\]|\bTBD\b|<placeholder>|\[Fill in\]|\[NEEDS CLARIFICATION")
BRACKET_TOKEN_RE = re.compile(r"(?<!\[)\[(?:[A-Z][a-z]+)(?:[ /][A-Za-z]+)*\](?!\()")
H2_RE = re.compile(r"^##\s+(?!#)(.+?)\s*$")
KNOWN_SEVERITIES = {"blocking": "blocking", "warning": "warning", "informational": "info", "info": "info"}


class Report:
    def __init__(self) -> None:
        self.findings: list[dict] = []

    def add(self, severity: str, check: str, message: str, line: int | None = None) -> None:
        self.findings.append({"severity": severity, "check": check, "message": message, "line": line})

    def summary(self) -> dict:
        counts = {"blocking": 0, "warning": 0, "info": 0}
        for f in self.findings:
            counts[f["severity"]] += 1
        return counts


def die(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    sys.exit(2)


def slugify(heading: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", heading.lower()).strip("_")


def normalize_severity(raw: object, report: Report, check: str) -> str:
    if raw is None:
        return "blocking"
    key = str(raw).strip().lower()
    if key in KNOWN_SEVERITIES:
        return KNOWN_SEVERITIES[key]
    report.add("info", check, f"unknown severity '{raw}' in catalog; treated as warning")
    return "warning"


# --- instance parsing --------------------------------------------------------

def split_frontmatter(text: str) -> tuple[dict | None, str, int]:
    """Return (frontmatter mapping or None, body, 1-based line where body starts)."""
    if not text.startswith("---\n"):
        return None, text, 1
    end = text.find("\n---\n", 4)
    if end < 0:
        return None, text, 1
    raw = text[4:end]
    body = text[end + 5:]
    data = yaml.safe_load(raw) or {}
    return (data if isinstance(data, dict) else {}), body, raw.count("\n") + 3


def strip_fences(body: str) -> str:
    """Blank out fenced code blocks (keeping line count) so scans skip diagrams/code."""
    out, in_fence = [], False
    for line in body.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            out.append("")
        else:
            out.append("" if in_fence else line)
    return "\n".join(out)


def line_of(body: str, offset: int, base: int) -> int:
    return base + body.count("\n", 0, offset)


# --- catalog ------------------------------------------------------------------

def resolve_catalog(explicit: str | None, instance: Path) -> Path:
    """Return the `activities` directory, following the skill's fall-through order."""
    candidates: list[Path] = []
    if explicit:
        p = Path(explicit).expanduser().resolve()
        candidates += [p, p / "activities", p / "workflows" / "activities"]
    else:
        for parent in [instance.resolve().parent, *instance.resolve().parents]:
            candidates.append(parent / "workflows" / "activities")
        skill_dir = Path(__file__).resolve().parent.parent
        candidates.append(skill_dir / "references" / "activities")
        candidates.append(skill_dir.parent.parent / "workflows" / "activities")
    for c in candidates:
        if c.is_dir() and any(c.glob("*/artifacts/*/meta.yml")):
            return c
    tried = "\n  ".join(str(c) for c in candidates)
    die(f"could not resolve an artifact catalog; tried:\n  {tried}")


def load_catalog(activities: Path) -> dict[str, dict]:
    types: dict[str, dict] = {}
    for meta_path in sorted(activities.glob("*/artifacts/*/meta.yml")):
        meta = yaml.safe_load(meta_path.read_text(encoding="utf-8")) or {}
        type_id = (meta.get("artifact") or {}).get("id") or meta_path.parent.name
        types[type_id] = {"dir": meta_path.parent, "meta": meta}
    return types


def resolve_type(fm: dict | None, explicit: str | None, instance: Path, catalog: dict[str, dict]) -> str:
    prefixes = dict(PREFIX_TYPES)
    for type_id, entry in catalog.items():
        prefix = (entry["meta"].get("id_format") or {}).get("prefix")
        if prefix:
            prefixes[str(prefix).upper()] = type_id

    def from_id(value: str) -> str | None:
        m = re.match(r"^([A-Z]+)-", value)
        if m and m.group(1) in prefixes:
            return prefixes[m.group(1)]
        parts = value.split(".")
        if len(parts) >= 2 and parts[0] in ("helix", "example") and parts[1] in catalog:
            return parts[1]
        return value if value in catalog else None

    ddx = (fm or {}).get("ddx") or {}
    candidates = [
        ("ddx.type", ddx.get("type")),
        ("ddx.id", from_id(str(ddx["id"])) if ddx.get("id") else None),
        ("--type", explicit),
        ("parent dir", instance.resolve().parent.name),
        ("filename", from_id(instance.stem)),
        ("filename", re.sub(r"^[\d._-]+|[\d._-]+$", "", instance.stem)),
    ]
    for source, value in candidates:
        if not value:
            continue
        if value in catalog:
            return value
        if source in ("ddx.type", "--type"):
            die(f"{source} '{value}' is not an artifact type in the catalog")
    die(f"could not resolve the artifact type for {instance}; add ddx.type to the frontmatter or pass --type")


# --- checks -------------------------------------------------------------------

def check_frontmatter(fm: dict | None, report: Report) -> None:
    if fm is None:
        report.add("warning", "frontmatter", "no YAML frontmatter; instance is not graph-addressable", 1)
        return
    ddx = fm.get("ddx")
    if not isinstance(ddx, dict):
        report.add("blocking", "frontmatter.ddx", "frontmatter has no `ddx:` block", 1)
        return
    if not ddx.get("id"):
        report.add("blocking", "frontmatter.id", "ddx.id is missing", 1)
    if not ddx.get("type") and not ddx.get("activity"):
        report.add("warning", "frontmatter.type", "neither ddx.type nor ddx.activity is set", 1)
    home = (ddx.get("authoring") or {}).get("home") if isinstance(ddx.get("authoring"), dict) else None
    if home not in ("repo", "external-tool"):
        report.add("blocking", "frontmatter.authoring_home", "ddx.authoring.home must be `repo` or `external-tool`", 1)


def check_required_sections(required: list, template: Path, body: str, markdown: bool, report: Report) -> None:
    if not markdown:  # yaml artifact types declare required_sections as top-level keys
        for section in required:
            if not re.search(rf"^\s*{re.escape(str(section))}\s*:", body, re.M):
                report.add("blocking", f"required_sections.{section}", f"required key '{section}' is not present in the instance")
        return
    template_slugs = set()
    if template.exists():
        template_slugs = {slugify(m.group(1)) for m in map(H2_RE.match, template.read_text(encoding="utf-8").splitlines()) if m}
    instance_slugs = {slugify(m.group(1)) for m in map(H2_RE.match, body.splitlines()) if m}
    for section in required:
        section = str(section)
        if template_slugs and section not in template_slugs:
            report.add("info", f"catalog.required_sections.{section}", "section id has no matching H2 in template.md")
        if section not in instance_slugs:
            report.add("blocking", f"required_sections.{section}", f"required section '{section}' is not an H2 in the instance")


def expected_ok(count: int, expected: object) -> bool:
    text = str(expected).strip().replace(" ", "")
    if text.isdigit():
        return count == int(text)
    m = re.match(r"^(>=|>|<=|<|==)(\d+)$", text)
    if not m:
        return count > 0
    op, n = m.group(1), int(m.group(2))
    return {">=": count >= n, ">": count > n, "<=": count <= n, "<": count < n, "==": count == n}[op]


def field_values(body: str, field: str) -> list[str]:
    """Collect values for a field from table columns and `**Label**: value` lines."""
    wanted = {field}
    if field.endswith("_id"):
        wanted.add("id")
    values: list[str] = []
    header: list[str] | None = None
    for line in body.splitlines():
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if header is None:
                header = [slugify(c) for c in cells]
            elif all(re.fullmatch(r":?-+:?", c or "-") for c in cells):
                continue
            else:
                values += [cells[i] for i, h in enumerate(header) if h in wanted and i < len(cells)]
            continue
        header = None
        m = re.match(r"^\s*\*\*([^*]+)\*\*\s*:\s*(.+?)\s*$", line)
        if m and slugify(m.group(1)) in wanted:
            values.append(m.group(2))
    return [v for v in values if v]


def check_rule_entries(key: str, entries: list, body: str, base: int, report: Report) -> None:
    for i, entry in enumerate(entries):
        if not isinstance(entry, dict):
            continue
        check = str(entry.get("check") or f"{key}.{i}")
        severity = normalize_severity(entry.get("severity"), report, check)
        message = str(entry.get("message") or entry.get("description") or check)
        if "pattern" in entry:
            matches = list(re.finditer(str(entry["pattern"]), body))
            expected = entry.get("expected", ">0")
            if not expected_ok(len(matches), expected):
                line = line_of(body, matches[0].start(), base) if matches else None
                report.add(severity, check, f"{message} (pattern /{entry['pattern']}/ matched {len(matches)}, expected {expected})", line)
            continue
        field = entry.get("field")
        rule = entry.get("type")
        if rule == "unique_constraint" and field:
            values = field_values(body, str(field))
            dupes = sorted({v for v in values if values.count(v) > 1})
            if dupes:
                report.add(severity, check, f"{message}: duplicate {field} values {dupes}")
            elif not values:
                report.add("info", check, f"field '{field}' not found in tables or **Label**: lines; check skipped")
        elif rule == "not_equals" and field:
            values = field_values(body, str(field))
            bad = [v for v in values if v == str(entry.get("value"))]
            if bad:
                report.add(severity, check, f"{message}: {field} is placeholder '{bad[0]}' in {len(bad)} place(s)")
            elif not values:
                report.add("info", check, f"field '{field}' not found in tables or **Label**: lines; check skipped")
        else:
            report.add("info", check, f"unsupported automated check type '{rule}'; skipped")


def check_placeholders(body: str, base: int, report: Report) -> None:
    scan = strip_fences(body)
    for m in PLACEHOLDER_RE.finditer(scan):
        report.add("blocking", "placeholder", f"leftover placeholder '{m.group(0)}'", line_of(scan, m.start(), base))
    for m in BRACKET_TOKEN_RE.finditer(scan):
        report.add("warning", "placeholder.bracket_token", f"possible template token '{m.group(0)}'", line_of(scan, m.start(), base))


# --- main ---------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("instance", type=Path)
    parser.add_argument("--catalog", help="workflows/ (or activities/) directory of the artifact catalog")
    parser.add_argument("--type", dest="type_id", help="artifact type id when the instance does not declare one")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()

    if yaml is None:
        die("PyYAML is required (python3 -m pip install pyyaml)")
    if not args.instance.is_file():
        die(f"instance not found: {args.instance}")

    text = args.instance.read_text(encoding="utf-8")
    fm, body, base = split_frontmatter(text)
    activities = resolve_catalog(args.catalog, args.instance)
    catalog = load_catalog(activities)
    type_id = resolve_type(fm, args.type_id, args.instance, catalog)
    entry = catalog[type_id]
    validation = entry["meta"].get("validation") or {}
    template = entry["dir"] / ((entry["meta"].get("template") or {}).get("file") or "template.md")

    report = Report()
    check_frontmatter(fm, report)
    markdown = str((entry["meta"].get("output") or {}).get("format") or "markdown").lower() == "markdown"
    check_required_sections(validation.get("required_sections") or [], template, body, markdown, report)
    check_rule_entries("pattern_checks", validation.get("pattern_checks") or [], body, base, report)
    check_rule_entries("automated_checks", validation.get("automated_checks") or [], body, base, report)
    check_placeholders(body, base, report)

    summary = report.summary()
    if args.format == "json":
        print(json.dumps({
            "instance": str(args.instance), "type": type_id, "catalog": str(activities),
            "findings": report.findings, "summary": summary,
        }, indent=2))
    else:
        for f in report.findings:
            suffix = f"  [line {f['line']}]" if f["line"] else ""
            print(f"{f['severity'].upper():<9} {f['check']}  {f['message']}{suffix}")
        status = "FAIL" if summary["blocking"] else "OK"
        print(f"{status}: {args.instance} type={type_id} "
              f"blocking={summary['blocking']} warning={summary['warning']} info={summary['info']}")
    return 1 if summary["blocking"] else 0


if __name__ == "__main__":
    sys.exit(main())
