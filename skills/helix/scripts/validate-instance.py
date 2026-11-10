#!/usr/bin/env python3
"""Validate a HELIX artifact instance against its catalog type's `validation:` block.

Usage:
    validate-instance.py <instance.md> [--catalog DIR] [--type TYPE] [--format text|json] [--strict-prose]

Checks run, in order:
  frontmatter        ddx.id, ddx.type/ddx.activity, ddx.authoring.home
  required_sections  each catalog section id must be an H2 in the instance
  pattern_checks     regex entries {pattern, expected, message[, severity]}
                     where expected is 0 (must not match) or >=N
  automated_checks   rule entries {check, type, field[, severity, message]}
                     with type unique_constraint, module_boundaries, ux_coverage, findings_sources,
                     or not_equals plus `value`;
                     other rule types are reported as unsupported without failing
  placeholder        leftover template markers ([TODO], TBD, [Fill in], ...)
  structured blocks  a technology assessment's `assessment:` and a position paper's `recommendations:`
                     front matter: criteria from the graph's criteria.yml, a rating or gap for every
                     criterion and subject, stances, rationale, pinned assessments, review dates, and
                     approval given whole (structured_blocks.py); `assessment-tables.py` keeps the
                     Markdown tables equal to them
  figures            `{basis=... accessed=... source=...}` attribute lists on figures: basis is
                     published, third-party, or not-published; the first two need source and a
                     YYYY-MM-DD accessed date (figure_attributes.py)
  visuals            each fenced `visual` block (and each Mermaid block naming `%% id:`): an id that
                     is present, well formed, and unique; a body naming a `source`, or a `kind`,
                     `form`, and `question`; a form of its kind (umf.visual 1.0). A kind and form
                     the type's meta.yml `visuals:` does not list is a warning
                     (workflows/references/visuals.md)
  prose              for a type people read (meta.yml prose.audience: human), the voice
                     profile's limits and phrase lists in workflows/voice.yml:
                     long sentences, crowded paragraphs, overfull cells, avoided phrases, and a
                     word budget when meta.yml sets prose.budget_words. Warnings unless
                     --strict-prose or the project's .helix.yml sets `prose: {strict: true}`.
                     Other types, agent context and history, are not audited, nor is a path
                     the project lists in `.helix.yml` prose.exempt. Resolve findings with
                     workflows/references/writing-pass.md

Document lifecycle labels, review stamps and graph completeness are not checked.
Content diagnostics do not establish implementation readiness: assess their
effect on the scoped user outcome before blocking authorized work. Explicit
source and identity metadata still protect authoring correctness when a ddx
block is supplied.

Scope variants: when the instance sets `ddx.scope` and the type's
`validation.by_scope.<scope>` exists, its `required_sections` and
`pattern_checks` replace the type-level lists.

Pinned links: under `--tier publish`, when the type declares
`validation.pin_links: {kinds: [...]}`, every `ddx.links` mapping whose `kind`
is listed must carry `rev` (a `git:<commit>` or `sha256:<hex>` revision), so an
issued document is reproducible from pinned sources. `pin-sources.py` fills
and verifies pins. The flow profile's `validation.default` tier softens content
findings to warnings until `--tier publish` is requested; lifecycle status
selects nothing. `pin-sources.py` fills and verifies pins.

Validation tiers (graph profiles, ADR-017): when the instance sets
`ddx.status: draft` and its flow's profile (`.helix.yml` `flows[].profile`,
default software-delivery) does not run `all` checks at draft, content checks
(required_sections, pattern_checks, automated_checks, placeholder) are reported
as warnings; frontmatter checks stay blocking. Any other status runs every check.

Exit codes: 0 = no blocking findings, 1 = blocking findings, 2 = usage or
resolution error (instance unreadable, type or catalog unresolvable).

Requires PyYAML (`python3 -c 'import yaml'`); fails with a clear message otherwise.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import prose_audit  # noqa: E402  (sibling module, found beside this script)
import figure_attributes  # noqa: E402  (sibling module: {basis=... accessed=... source=...} on figures)
import structured_blocks  # noqa: E402  (sibling module: assessment and recommendations blocks)

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

# The visual vocabulary: umf.visual 1.0 (DocumentDrivenDX/umf-visual CONTRACT-083, `visualForms`).
# workflows/references/visuals.md says which kind answers which question.
VISUAL_FORMS = {
    "flow": ("network", "pipeline", "zoned", "lanes"),
    "sequence": ("lifelines", "ladder"),
    "structure": ("stack", "tree", "nested", "entities"),
    "state": ("machine", "lifecycle"),
    "timeline": ("milestones", "roadmap", "history"),
    "comparison": ("matrix", "quadrant", "before-after"),
    "metric": ("stat", "bar", "line", "meter"),
}
VISUAL_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FENCE_OPEN_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})\s*([^\n]*)$")
MERMAID_ID_RE = re.compile(r"^\s*%%\s*id:\s*(\S+)")
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


def fenced_blocks(body: str):
    """Yield (line index, info string, content) for each top-level fenced block.

    A block closes only on a fence of its own character at least as long as the one that opened
    it, so a ```visual sample inside a ````markdown block stays text, not a visual.
    """
    lines = body.split("\n")
    i = 0
    while i < len(lines):
        opened = FENCE_OPEN_RE.match(lines[i])
        if not opened or (opened.group(1)[0] == "`" and "`" in opened.group(2)):
            i += 1
            continue
        fence, start = opened.group(1), i
        close = re.compile(rf"^ {{0,3}}{re.escape(fence[0])}{{{len(fence)},}}\s*$")
        i += 1
        while i < len(lines) and not close.match(lines[i]):
            i += 1
        yield start, opened.group(2).strip(), "\n".join(lines[start + 1:i])
        i += 1


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


def find_profile(instance: Path, activities: Path) -> dict:
    """Profile of the flow whose root contains the instance (default software-delivery)."""
    profile_id = "software-delivery"
    for parent in instance.resolve().parents:
        marker = parent / ".helix.yml"
        if not marker.is_file():
            continue
        try:
            flows = (yaml.safe_load(marker.read_text(encoding="utf-8")) or {}).get("flows") or []
        except yaml.YAMLError:
            flows = []
        best = None
        for flow in flows:
            root = (parent / str(flow.get("root", ""))).resolve()
            if root == instance.resolve() or root in instance.resolve().parents:
                if best is None or len(str(root)) > len(str(best[0])):
                    best = (root, flow)
        if best:
            profile_id = best[1].get("profile") or profile_id
        break
    path = activities.parent / "profiles" / f"{profile_id}.yml"
    if not path.is_file():
        return {"validation": {"draft": ["all"]}}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


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
    # Prose and unrelated frontmatter remain valid; graph addressability is
    # optional, not a housekeeping warning. Explicit ddx blocks still obey the
    # identity and authoring-home contract so edits cannot silently fork sources.
    if fm is None or "ddx" not in fm:
        return
    ddx = fm.get("ddx")
    if not isinstance(ddx, dict):
        report.add("blocking", "frontmatter.ddx", "frontmatter has no `ddx:` block", 1)
        return
    if not ddx.get("id"):
        report.add("blocking", "frontmatter.id", "ddx.id is missing", 1)
    home = (ddx.get("authoring") or {}).get("home") if isinstance(ddx.get("authoring"), dict) else None
    if home not in ("repo", "external-tool"):
        report.add("blocking", "frontmatter.authoring_home", "ddx.authoring.home must be `repo` or `external-tool`", 1)


LINK_KINDS = {"informed_by", "informs", "addresses", "evaluates", "supported_by", "contradicts"}


def check_links(fm: dict | None, profile: dict, report: Report) -> None:
    """ddx.links shape, vocabulary, and the profile's authority grant (ADR-018)."""
    ddx = (fm or {}).get("ddx") or {}
    authority = profile.get("authority") or {}
    for i, link in enumerate(ddx.get("links") or []):
        if isinstance(link, str):
            continue  # bare id: an upstream reference
        if not isinstance(link, dict) or not link.get("id"):
            report.add("blocking", f"links.{i}", "a ddx.links entry must be an id string or a mapping with `id`")
            continue
        kind = link.get("kind")
        if kind is not None and kind not in LINK_KINDS:
            report.add("warning", f"links.{i}.kind", f"link '{link['id']}' has unknown kind '{kind}'")
        allowed = profile.get("edge_kinds")
        if allowed and kind and kind not in {"informed_by", "informs", *allowed}:
            report.add("warning", f"links.{i}.kind", f"link kind '{kind}' is not allowed by this flow's profile")
        grant = link.get("authority")
        if grant is not None and grant not in ("advisory", "governing"):
            report.add("blocking", f"links.{i}.authority", f"link '{link['id']}' authority must be advisory or governing")
        if grant == "governing":
            scope = "cross_graph" if link.get("graph") else "within_graph"
            if authority.get(scope, "advisory" if scope == "cross_graph" else "positional") == "advisory":
                report.add("blocking", f"links.{i}.authority",
                           f"link '{link['id']}' claims governing authority but this flow's profile grants {scope.replace('_', '-')} references advisory only; the consuming graph must grant it")
        if kind == "contradicts":
            report.add("info", f"links.{i}.contradicts", f"contradicts '{link['id']}': surfaced for review, never a validation failure")


def check_pinned_links(fm: dict | None, pin: dict, report: Report) -> None:
    ddx = (fm or {}).get("ddx") or {}
    if not pin:
        return
    kinds = set(pin.get("kinds") or [])
    for i, link in enumerate(ddx.get("links") or []):
        if not isinstance(link, dict) or link.get("kind") not in kinds:
            continue
        rev = str(link.get("rev") or "")
        if not structured_blocks.PIN_RE.match(rev):
            report.add("blocking", f"pin_links.{i}", f"link '{link.get('id')}' ({link.get('kind')}) needs a pinned rev (git:<commit> or sha256:<hex>) at the publish tier")


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


def check_module_boundaries(body: str, base: int, severity: str, report: Report) -> None:
    """Check populated boundary evidence, not import semantics or execution readiness.

    Omission is valid for legacy instances. Workflows own adoption/readiness.
    Source-free instances explicitly explain applicability, without invented modules.
    """
    scan = strip_fences(body)
    headings = list(re.finditer(r"(?m)^##[ \t]+(?!#)(.+?)[ \t]*$", scan))
    matches = [h for h in headings if slugify(h.group(1)) == "module_boundaries"]
    if not matches:
        return
    match = matches[0]
    line = line_of(scan, match.start(), base)
    if len(matches) != 1:
        report.add(severity, "module_boundaries", "Use exactly one Module Boundaries section", line)
        return
    next_heading = next((h for h in headings if h.start() > match.start()), None)
    section = scan[match.end():next_heading.start() if next_heading else len(scan)]

    def fail(message: str) -> None:
        report.add(severity, "module_boundaries", message, line)

    def value(label: str) -> str:
        found = re.search(r"(?m)^\*\*" + re.escape(label) + r"\*\*:[ \t]*([^\n]*)$", section)
        return found.group(1).strip() if found else ""

    applicability = value("Source Applicability")
    kind, separator, reason = applicability.partition(";")
    if kind.strip() not in {"source", "source-free"} or not separator or not reason.strip():
        fail("Source Applicability must be source or source-free followed by '; reason'")
        return
    if kind.strip() == "source-free":
        return
    for label in ("Integration Owners", "Construction Policy", "Boundary Check"):
        if not value(label):
            fail(f"Source projects must populate **{label}**")
    columns = ("module", "responsibility_owned_types", "public_api", "allowed_dependencies", "forbidden_dependencies")
    headers = None
    rows = 0
    for text in section.splitlines():
        if not text.startswith("|"):
            headers = None
            continue
        cells = [cell.strip() for cell in text.strip().strip("|").split("|")]
        names = [slugify(cell) for cell in cells]
        if headers is None:
            headers = names if all(name in names for name in columns) else None
            continue
        if all(re.fullmatch(r":?-+:?", cell) for cell in cells):
            continue
        rows += 1
        if len(cells) != len(headers) or any(not cells[headers.index(name)] for name in columns if headers.index(name) < len(cells)):
            fail("Each boundary-map row must populate all five required columns")
    if not rows:
        fail("Source projects need a populated module table with Module, Responsibility / Owned Types, Public API, Allowed Dependencies and Forbidden Dependencies")


UX_PATTERNS = {"navigation", "keyboard-overlays", "async-actions", "forms",
               "data-states", "destructive-actions"}


def check_ux_coverage(body: str, base: int, severity: str, report: Report) -> None:
    """Validate declared STP coverage, not test execution or UX semantics.

    Legacy absence passes; workflow readiness requires adoption for affected UI.
    """
    scan = strip_fences(body)
    headings = list(re.finditer(r"(?m)^##[ \t]+(?!#)(.+?)[ \t]*$", scan))
    sections = [h for h in headings if slugify(h.group(1)) == "ux_coverage"]
    if not sections:
        return
    line = line_of(scan, sections[0].start(), base)

    def fail(message: str) -> None:
        report.add(severity, "ux_coverage", message, line)

    if len(sections) != 1:
        fail("Use exactly one UX Coverage section")
        return

    def section(heading):
        end = next((h.start() for h in headings if h.start() > heading.start()), len(scan))
        return scan[heading.end():end]

    def table_rows(text, columns):
        header = None
        rows = []
        for text_line in text.splitlines():
            if not text_line.lstrip().startswith("|"):
                header = None
                continue
            cells = [c.strip() for c in text_line.strip().strip("|").split("|")]
            if all(re.fullmatch(r":?-+:?", c or "-") for c in cells):
                continue
            names = [slugify(c) for c in cells]
            names = ["test_s_to_create_or_run" if n in (
                "failing_test_s_to_create_or_run", "new_or_existing_test_s_to_create_or_run"
            ) else n for n in names]
            if all(c in names for c in columns):
                header = names
                continue
            if header is not None:
                rows.append({c: cells[header.index(c)] if header.index(c) < len(cells) else ""
                             for c in columns})
        return rows

    mapping_heads = [h for h in headings if slugify(h.group(1)) == "acceptance_criteria_test_mapping"]
    columns = ("ac_id", "test_s_to_create_or_run", "asserted_behavior_what_the_test_verifies", "file_or_command")
    mapped = {}
    for heading in mapping_heads:
        for row in table_rows(section(heading), columns):
            ac = row["ac_id"].strip("` ")
            if ac in mapped:
                fail(f"Duplicate mapped AC ID: {ac}")
            mapped[ac] = row
    rows = table_rows(section(sections[0]), ("pattern", "disposition", "ac_ids_or_reason"))
    seen = set()
    for row in rows:
        pattern, disposition, value = (row[c].strip("` ") for c in ("pattern", "disposition", "ac_ids_or_reason"))
        if pattern not in UX_PATTERNS or pattern in seen:
            fail(f"Unknown or duplicate UX pattern: {pattern}")
        seen.add(pattern)
        if disposition == "not-applicable":
            if not value or value.lower() in {"n/a", "none", "not applicable", "-"}:
                fail(f"{pattern}: non-applicability needs a concrete reason")
        elif disposition == "covered":
            ids = [ac.strip("` ") for ac in value.split(",")]
            if not ids or any(not re.fullmatch(r"US-\d+-AC\d+", ac) for ac in ids) or len(ids) != len(set(ids)):
                fail(f"{pattern}: covered rows need unique stable US numeric AC IDs")
                continue
            for ac in ids:
                mapping = mapped.get(ac)
                if not mapping:
                    fail(f"{pattern}: unresolved AC ID {ac}")
                elif any(not mapping[c].strip("` \t") or mapping[c].strip("` \t").lower() in {"n/a", "none", "-"} for c in columns[1:]):
                    fail(f"{pattern}: {ac} needs populated test, assertion and file/command")
        else:
            fail(f"{pattern}: disposition must be covered or not-applicable")
    missing = UX_PATTERNS - seen
    if missing:
        fail("Missing UX patterns: " + ", ".join(sorted(missing)))


def check_findings_sources(body: str, base: int, severity: str, report: Report) -> None:
    """A present Findings section's Claims table has a Source column, filled for every claim.

    Only the table under `### Claims` is read; other tables beneath Findings are not claims.
    """
    lines = strip_fences(body).splitlines()
    start = next((i for i, l in enumerate(lines) if re.fullmatch(r"##[ \t]+Findings[ \t]*", l)), None)
    if start is None:
        return

    def fail(message: str, i: int) -> None:
        report.add(severity, "findings_sources", message, base + i)

    end = next((i for i in range(start + 1, len(lines)) if re.match(r"##[ \t]", lines[i])), len(lines))
    claims = next((i for i in range(start + 1, end) if re.fullmatch(r"###[ \t]+Claims[ \t]*", lines[i])), None)
    rows = []
    for i in range(claims + 1, end) if claims is not None else ():
        if re.match(r"#{1,3}[ \t]", lines[i]) or (rows and not lines[i].lstrip().startswith("|")):
            break  # the first table under Claims only
        if lines[i].lstrip().startswith("|"):
            cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
            rows.append((i, cells))
    rows = [(i, cells) for i, cells in rows if not all(re.fullmatch(r":?-+:?", c) for c in cells)]
    if not rows:
        fail("Findings needs a Claims table", start if claims is None else claims)
        return
    header = [slugify(c) for c in rows[0][1]]
    if "source" not in header:
        fail("The Claims table needs a Source column", rows[0][0])
        return
    source = header.index("source")
    claim = header.index("claim") if "claim" in header else 0
    for i, cells in rows[1:]:
        if not any(cells):
            continue
        value = cells[source] if source < len(cells) else ""
        if value.lower() in {"", "-", "n/a", "none"}:
            fail(f"Claim has no Source: {cells[claim] if claim < len(cells) else ''}", i)


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
        if rule == "ux_coverage":
            check_ux_coverage(body, base, severity, report)
        elif rule == "module_boundaries":
            check_module_boundaries(body, base, severity, report)
        elif rule == "findings_sources":
            check_findings_sources(body, base, severity, report)
        elif rule == "unique_constraint" and field:
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


def check_visuals(meta: dict, body: str, base: int, report: Report) -> None:
    """Every visual block names a stable id and a form of its kind (workflows/references/visuals.md)."""
    listed = {(v.get("kind"), v.get("form")) for v in meta.get("visuals") or [] if isinstance(v, dict)}
    seen: dict[str, int] = {}

    def claim(raw: str, line: int) -> None:
        if not VISUAL_ID_RE.match(raw):
            report.add("blocking", "visual.id", f"visual id {raw!r} must be lowercase letters, digits, and hyphens", line)
        elif raw in seen:
            report.add("blocking", "visual.id", f"visual id {raw!r} is used twice (first at line {seen[raw]})", line)
        else:
            seen[raw] = line

    for index, info, content in fenced_blocks(body):
        line = base + index
        word = info.split(maxsplit=1)[0] if info else ""
        if word == "mermaid":
            named = MERMAID_ID_RE.match(content)
            if named:
                claim(named.group(1), line)
            continue
        if word != "visual":
            continue
        found = re.search(r"\bid=(\S+)", info)
        if not found:
            report.add("blocking", "visual.id", "a visual block needs `id=<stable-id>` after ```visual", line)
        else:
            claim(found.group(1), line)
        try:
            spec = yaml.safe_load(content) or {}
        except yaml.YAMLError as error:
            report.add("blocking", "visual.body", f"the visual block is not YAML: {error}", line)
            continue
        if not isinstance(spec, dict):
            report.add("blocking", "visual.body", "the visual block must be a YAML mapping", line)
            continue
        if spec.get("source") and not spec.get("kind"):
            continue
        kind, form = spec.get("kind"), spec.get("form")
        if kind not in VISUAL_FORMS:
            report.add("blocking", "visual.kind", f"a visual block needs a `source`, or a kind of {', '.join(VISUAL_FORMS)}; got {kind!r}", line)
            continue
        if form not in VISUAL_FORMS[kind]:
            report.add("blocking", "visual.form", f"{kind} has the forms {', '.join(VISUAL_FORMS[kind])}; got {form!r}", line)
            continue
        if not spec.get("question"):
            report.add("blocking", "visual.question", "a visual block names the one question it answers (`question:`)", line)
        if listed and (kind, form) not in listed:
            report.add("warning", "visual.unlisted",
                       f"{kind}/{form} is not among this type's visuals ({', '.join(f'{k}/{f}' for k, f in sorted(listed))}); "
                       "list it in meta.yml or draw it in another artifact", line)


def check_delivery_history(body: str, base: int, report: Report) -> None:
    """Flag repository-history citations, not transaction or release semantics.

    A warning, not a block: the patterns cannot tell this repository's history
    from a legitimate upstream reference. Hashes must mix letters and digits so
    numeric counts ("commit 1000000 rows") pass; bare `revision` identifiers
    (database migrations) and `PR-n` requirement IDs are not matched.
    """
    sha = r"[`\"']?(?=[0-9a-f]*[a-f])(?=[0-9a-f]*[0-9])[0-9a-f]{7,40}\b"
    pattern = re.compile(
        r"\bPR\s*#\s*[0-9]+\b"
        r"|\bpull[ -]request\s*#?\s*[0-9]+\b"
        r"|https?://[^\s)<>]+/(?:pull|pulls|merge_requests)/[0-9]+\b"
        r"|https?://[^\s)<>]+/commits?/[0-9a-f]{7,40}\b"
        r"|\bcommit\s+(?:hash\s*|SHA\s*)?" + sha +
        r"|\b(?:commit|commit_sha|source_commit)\s*[:=]\s*" + sha,
        re.IGNORECASE,
    )
    for match in pattern.finditer(body):
        report.add("warning", "delivery_history", "Keep repository-history citations in source control or the runtime tracker", line_of(body, match.start(), base))


def check_figures(body: str, base: int, report: Report) -> None:
    scan = strip_fences(body)
    for offset, check, message in figure_attributes.find(scan):
        report.add("blocking", check, message, line_of(scan, offset, base))


def check_placeholders(body: str, base: int, report: Report) -> None:
    scan = strip_fences(body)
    for m in PLACEHOLDER_RE.finditer(scan):
        report.add("blocking", "placeholder", f"leftover placeholder '{m.group(0)}'", line_of(scan, m.start(), base))
    for m in BRACKET_TOKEN_RE.finditer(scan):
        report.add("warning", "placeholder.bracket_token", f"possible template token '{m.group(0)}'", line_of(scan, m.start(), base))


def project_prose_settings(instance: Path) -> tuple[dict, Path | None]:
    """The `prose:` block of the nearest `.helix.yml` above the instance, and that file's directory.

    `strict: true` makes prose findings blocking for every instance under it; `exempt` lists glob
    patterns, relative to that directory, for records the project keeps (dated logs, reviews).
    """
    for parent in instance.resolve().parents:
        marker = parent / ".helix.yml"
        if marker.is_file():
            data = yaml.safe_load(marker.read_text(encoding="utf-8")) or {}
            return (data.get("prose") or {}), parent
    return {}, None


def prose_audited(meta: dict, instance: Path, settings: dict, root: Path | None) -> bool:
    """People read this type (meta.yml `prose.audience: human`) and the project has not exempted it.

    Every other type is context and history an agent loads; it keeps the wording it was written in.
    """
    if str((meta.get("prose") or {}).get("audience") or "").lower() != "human":
        return False
    if root is not None:
        relative = instance.resolve().relative_to(root).as_posix()
        return not any(fnmatch.fnmatch(relative, str(p)) for p in settings.get("exempt") or [])
    return True


def check_prose(meta: dict, activities: Path, body: str, base: int, strict: bool, report: Report) -> None:
    """Audit the prose against the type's voice profile (workflows/voice.yml)."""
    voice_path = activities.parent / "voice.yml"
    if not voice_path.is_file():
        return
    voice = yaml.safe_load(voice_path.read_text(encoding="utf-8")) or {}
    declared = meta.get("voice")
    profile = declared.get("profile") if isinstance(declared, dict) else declared
    prose = meta.get("prose") or {}
    budget = prose.get("budget_words", 0)
    limits = prose_audit.limits_for(voice, profile or voice.get("default_profile") or "", budget)
    if limits is None:
        return
    severity = "blocking" if strict else "warning"
    found = prose_audit.audit(body, base, limits, prose_audit.phrases(voice), prose.get("skip_lines"))
    for check, message, line in found:
        report.add(severity, check, message, line)


# --- main ---------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("instance", type=Path)
    parser.add_argument("--catalog", help="workflows/ (or activities/) directory of the artifact catalog")
    parser.add_argument("--type", dest="type_id", help="artifact type id when the instance does not declare one")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--tier", choices=("default", "publish"), default="default",
                        help="publish applies the flow profile's publish tier (full validation and pinned sources); default applies its default tier")
    parser.add_argument("--strict-prose", action="store_true", help="report prose findings as blocking")
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

    ddx = (fm or {}).get("ddx") or {}
    scoped = (validation.get("by_scope") or {}).get(str(ddx.get("scope"))) or {}
    validation = {**validation, **{k: v for k, v in scoped.items() if k in ("required_sections", "pattern_checks")}}
    profile = find_profile(args.instance, activities)
    default_tier = (profile.get("validation") or {}).get("default") or ["all"]
    soften = args.tier == "default" and "all" not in default_tier
    report = Report()
    check_frontmatter(fm, report)
    check_links(fm, profile, report)
    structured_blocks.check(fm, type_id, args.instance, report.add, publish=args.tier == "publish")
    structural = len(report.findings)
    markdown = str((entry["meta"].get("output") or {}).get("format") or "markdown").lower() == "markdown"
    check_required_sections(validation.get("required_sections") or [], template, body, markdown, report)
    check_rule_entries("pattern_checks", validation.get("pattern_checks") or [], body, base, report)
    check_rule_entries("automated_checks", validation.get("automated_checks") or [], body, base, report)
    check_placeholders(body, base, report)
    check_delivery_history(text, 1, report)
    check_visuals(entry["meta"], body, base, report)
    check_figures(body, base, report)
    if args.tier == "publish":
        check_pinned_links(fm, validation.get("pin_links") or {}, report)
    settings, root = project_prose_settings(args.instance)
    if prose_audited(entry["meta"], args.instance, settings, root):
        strict = args.strict_prose or bool(settings.get("strict"))
        check_prose(entry["meta"], activities, body, base, strict, report)

    if soften:
        for finding in report.findings[structural:]:
            if finding["severity"] == "blocking":
                finding["severity"] = "warning"
                finding["message"] += " (enforced at the publish tier)"

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
