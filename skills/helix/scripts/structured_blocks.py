"""Structured front matter for two Technology Atlas types, and the tables made from it.

A technology assessment's `assessment:` block holds its criteria and ratings as data; a position
paper's `recommendations:` list holds its stances. The Markdown tables a reader sees are generated
from them (`assessment-tables.py`), so prose and data cannot disagree, and `validate-instance.py`
checks the data's shape. Criteria come from a shared `criteria.yml` in the nearest ancestor
directory that has one (the flow root), so one criterion is one node across assessments.

    assessment:
      criteria: [licence-cost, scale-limits]        # ids in criteria.yml; the Criteria table's rows
      subjects:                                     # the Comparison table's technologies
        - {id: component-profile-postgresql-reusable, label: PostgreSQL}
      comparison: {rows: criteria, tables: [[licence-cost, scale-limits]]}   # optional layout
      ratings:
        - {criterion: licence-cost, subject: component-profile-postgresql-reusable, finding: "No fee (PG §Pricing)"}
        - {criterion: scale-limits, subject: component-profile-postgresql-reusable, gap: Not published}

    recommendations:
      - subject: component-profile-postgresql-reusable
        label: PostgreSQL                           # optional; the table's name for the subject
        context: relational-database
        stance: conditional                         # recommended | conditional | watch | avoid
        conditions: Where the team already runs it   # required for conditional
        rationale: Why, in one or two sentences
        based_on: [{assessment: TA-001, criteria: [licence-cost]}]
        since: 2026-11-08
        review_by: 2027-02-06
        approved_by: Name                           # both or neither; until then "proposed"
        approved_on: 2026-11-20

Keys: `keys.yml` in the nearest ancestor directory that has one (the flow root) maps a short name to a
document id. In the blocks, a subject, a rating's subject, a recommendation's subject, and a
`based_on` assessment may be a key. A key is only an alias, resolved before any check: the document
that cites a source still lists it by its full id in `ddx.links`, with its pinned `rev`, so a key can
never follow a moving source. A document that uses a key also records what it resolved to, in a
top-level `keys:` mapping, and the check fails when keys.yml disagrees; so repointing a key is a
visible edit to every document that uses it, never a silent change of what they cite. A key is a
lower-case slug and never the id of a document; keys.yml may not repeat a key.

    # keys.yml                                      # in the document, beside `ddx:`
    keys:                                           keys:
      pg: component-profile-postgresql-reusable       pg: component-profile-postgresql-reusable
"""
from __future__ import annotations

import datetime
import re
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover  (callers report the missing dependency)
    yaml = None

STANCES = {
    "recommended": "Recommended",
    "conditional": "Use with conditions",
    "watch": "Watch",
    "avoid": "Avoid",
}
EVIDENCE_KINDS = {"evaluates", "supported_by"}
ROW_LAYOUTS = ("criteria", "subjects")


PIN_RE = re.compile(r"^(git:[0-9a-f]{7,40}|sha256:[0-9a-f]{64})$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def find_catalogue(instance: Path) -> Path | None:
    """criteria.yml in the nearest ancestor directory that has one, stopping at the project marker."""
    for parent in instance.resolve().parents:
        if (parent / "criteria.yml").is_file():
            return parent / "criteria.yml"
        if (parent / ".helix.yml").is_file():
            return None
    return None


def _one_line(value: object) -> bool:
    return "\n" not in str(value).strip()


def read_catalogue(path: Path | None) -> tuple[dict[str, dict], list[str]]:
    """(valid entries by id, problems). An entry needs a string id and label; cells stay one line."""
    if path is None:
        return {}, []
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as err:
        return {}, [f"{path.name} is not valid YAML: {err}"]
    entries = data.get("criteria") if isinstance(data, dict) else None
    if not isinstance(entries, list):
        return {}, [f"{path.name} needs a `criteria:` list"]
    cat, problems = {}, []
    for i, c in enumerate(entries):
        if not isinstance(c, dict) or not isinstance(c.get("id"), str) or not isinstance(c.get("label"), str):
            problems.append(f"{path.name} entry {i} needs a string `id` and `label`")
        elif c["id"] in cat:
            problems.append(f"{path.name} lists '{c['id']}' twice")
        elif not all(_one_line(c.get(k) or "") for k in ("label", "definition", "concern")):
            problems.append(f"{path.name} entry '{c['id']}' has a multi-line label, definition or concern; table cells are one line")
        else:
            cat[c["id"]] = c
    return cat, problems


def load_catalogue(path: Path | None) -> dict[str, dict]:
    return read_catalogue(path)[0]


KEY_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


class _UniqueKeyLoader(yaml.SafeLoader if yaml else object):
    """SafeLoader that rejects a mapping key written twice, so the last one cannot win silently."""

    def construct_mapping(self, node, deep=False):
        seen = set()
        for key_node, _ in node.value:
            key = self.construct_object(key_node, deep=True)
            if key in seen:
                raise yaml.constructor.ConstructorError(None, None, f"duplicate key {key!r}", key_node.start_mark)
            seen.add(key)
        return super().construct_mapping(node, deep)


def find_keys(instance: Path) -> Path | None:
    """keys.yml in the nearest ancestor directory that has one, stopping at the project marker."""
    for parent in instance.resolve().parents:
        if (parent / "keys.yml").is_file():
            return parent / "keys.yml"
        if (parent / ".helix.yml").is_file():
            return None
    return None


def _document_ids(root: Path) -> set[str]:
    """ddx.id of every Markdown document under root: the ids a key must not shadow."""
    ids = set()
    for path in root.rglob("*.md"):
        if any(part.startswith(".") or part == "node_modules" for part in path.relative_to(root).parts):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        end = text.find("\n---\n", 4) if text.startswith("---\n") else -1
        try:
            fm = yaml.safe_load(text[4:end]) if end > 0 else None
        except yaml.YAMLError:
            continue
        ddx = fm.get("ddx") if isinstance(fm, dict) else None
        if isinstance(ddx, dict) and ddx.get("id"):
            ids.add(str(ddx["id"]))
    return ids


def read_keys(path: Path | None) -> tuple[dict[str, str], list[str]]:
    """(key -> document id, problems). A key is a lower-case slug that is not itself a document id."""
    if path is None:
        return {}, []
    try:
        data = yaml.load(path.read_text(encoding="utf-8"), Loader=_UniqueKeyLoader) or {}
    except yaml.YAMLError as err:
        return {}, [f"{path.name} is not valid YAML: {err}"]
    entries = data.get("keys") if isinstance(data, dict) else None
    if not isinstance(entries, dict):
        return {}, [f"{path.name} needs a `keys:` mapping of key to document id"]
    existing = _document_ids(path.parent)
    keys, problems = {}, []
    for k, v in entries.items():
        if not isinstance(k, str):
            problems.append(f"{path.name}: key {k!r} is not text; YAML reads a bare yes, no, on or off as a boolean, so quote it")
        elif not KEY_RE.match(k) or not isinstance(v, str) or not v:
            problems.append(f"{path.name}: '{k}' must be a lower-case slug mapped to a document id")
        elif k in existing:
            problems.append(f"{path.name}: key '{k}' is also a document id; a key never shadows a document")
        else:
            keys[k] = v
    return keys, problems


def expand_keys(fm: dict, instance: Path) -> tuple[dict, list[str]]:
    """fm with block references that name a key replaced by the document id; plus problems.

    Only the blocks' references are expanded; ddx.links keep full ids and pinned revs. The document
    records the resolution it was written against in a top-level `keys:` mapping, and any key it uses
    must match keys.yml, so editing keys.yml cannot silently change what a document cites. A name
    that is both a key and a linked id is ambiguous and reported, and left as the id."""
    keys, problems = read_keys(find_keys(instance))
    recorded = fm.get("keys") if isinstance(fm.get("keys"), dict) else {}
    if not keys:
        if recorded and not problems:
            problems.append("the document records `keys:` but no keys.yml is in this graph")
        return fm, problems
    ddx = fm.get("ddx") if isinstance(fm.get("ddx"), dict) else {}
    linked = {str(l["id"]) for l in ddx.get("links") or [] if isinstance(l, dict) and l.get("id")}
    used: set[str] = set()

    def ref(value):
        if not isinstance(value, str) or value not in keys:
            return value
        if value in linked:
            problems.append(f"'{value}' is both a key in keys.yml and a linked document id; rename the key")
            return value
        used.add(value)
        return keys[value]

    out = dict(fm)
    block = fm.get("assessment")
    if isinstance(block, dict):
        out["assessment"] = {**block,
            "subjects": [{**x, "id": ref(x.get("id"))} if isinstance(x, dict) else x for x in block.get("subjects") or []]
            if isinstance(block.get("subjects"), list) else block.get("subjects"),
            "ratings": [{**x, "subject": ref(x.get("subject"))} if isinstance(x, dict) else x for x in block.get("ratings") or []]
            if isinstance(block.get("ratings"), list) else block.get("ratings")}
    recs = fm.get("recommendations")
    if isinstance(recs, list):
        def rec(r):
            if not isinstance(r, dict):
                return r
            based = r.get("based_on")
            return {**r, "subject": ref(r.get("subject")),
                    **({"based_on": [{**b, "assessment": ref(b.get("assessment"))} if isinstance(b, dict) else b for b in based]}
                       if isinstance(based, list) else {})}
        out["recommendations"] = [rec(r) for r in recs]
    for k in sorted(used):
        if recorded.get(k) != keys[k]:
            problems.append(f"key '{k}' resolves to '{keys[k]}' in keys.yml, but this document records "
                            f"{recorded.get(k)!r}; re-read what it cites, then set `keys: {{{k}: {keys[k]}}}`")
    for k in sorted(set(recorded) - set(keys)):
        problems.append(f"the document records key '{k}', which keys.yml no longer defines")
    return out, problems


def _date(value: object) -> datetime.date | None:
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    if isinstance(value, str) and DATE_RE.match(value):
        try:
            return datetime.date.fromisoformat(value)
        except ValueError:
            return None
    return None


def _evidence(fm: dict) -> dict[str, dict]:
    """ddx.links id -> {kind, rev}, for the in-graph links an assessment or paper may rest on."""
    ddx = fm.get("ddx") if isinstance(fm.get("ddx"), dict) else {}
    out = {}
    for link in ddx.get("links") or []:
        if isinstance(link, dict) and link.get("id") and link.get("kind") in EVIDENCE_KINDS and not link.get("graph"):
            out[str(link["id"])] = {"kind": link["kind"], "rev": str(link.get("rev") or "")}
    return out


def _ids(value: object) -> list[str] | None:
    """value as a list of non-empty strings, or None when it is not one."""
    if isinstance(value, list) and all(isinstance(v, str) and v for v in value):
        return list(value)
    return None


def check(fm: dict | None, type_id: str, instance: Path, add, publish: bool = False) -> None:
    """Report structured-block findings through add(severity, check, message).

    A malformed shape is one finding and stops that block's checks; the table tool relies on it
    to run only on blocks that passed."""
    fm = fm or {}
    if "assessment" in fm or "recommendations" in fm:
        fm, key_problems = expand_keys(fm, instance)
        for problem in key_problems:
            add("blocking", "keys", problem)
    for key, owner in (("assessment", "technology-assessment"), ("recommendations", "position-paper")):
        if key in fm and type_id != owner:
            add("blocking", f"{key}.placement", f"`{key}:` belongs on a {owner}, not a {type_id}; "
                "knowledge and advice are kept apart")
    if type_id == "technology-assessment" and "assessment" in fm:
        _check_assessment(fm, instance, add)
    if type_id == "position-paper" and "recommendations" in fm:
        _check_recommendations(fm, instance, add, publish)


def _catalogue_for(instance: Path, add, check_id: str) -> tuple[Path | None, dict[str, dict]]:
    path = find_catalogue(instance)
    cat, problems = read_catalogue(path)
    for problem in problems:
        add("blocking", "catalogue", problem)
    return path, cat


def _check_assessment(fm: dict, instance: Path, add) -> None:
    block = fm["assessment"]
    if not isinstance(block, dict):
        add("blocking", "assessment.shape", "`assessment:` must be a mapping")
        return
    criteria = _ids(block.get("criteria"))
    subjects = block.get("subjects")
    ratings = block.get("ratings")
    layout = block.get("comparison") if block.get("comparison") is not None else {}
    shape = []
    if not criteria:
        shape.append("`criteria` is a non-empty list of criterion ids")
    if not (isinstance(subjects, list) and all(isinstance(s, dict) and isinstance(s.get("id"), str)
                                               and isinstance(s.get("label"), str) and s["label"] for s in subjects)):
        shape.append("`subjects` is a list of {id, label} mappings")
    if not (isinstance(ratings, list) and all(isinstance(r, dict) for r in ratings)):
        shape.append("`ratings` is a list of mappings")
    if not isinstance(layout, dict) or (layout.get("tables") is not None and not (
            isinstance(layout["tables"], list) and all(_ids(t) for t in layout["tables"]))):
        shape.append("`comparison` is a mapping whose `tables` are non-empty lists of criterion ids")
    if shape:
        for message in shape:
            add("blocking", "assessment.shape", message)
        return

    path, cat = _catalogue_for(instance, add, "assessment")
    if path is None:
        add("blocking", "assessment.catalogue", "no criteria.yml at the flow root; criteria are ids from it")
    for cid in criteria:
        if path and cid not in cat:
            add("blocking", "assessment.criteria", f"criterion '{cid}' is not in {path.name}")
    if len(set(criteria)) != len(criteria):
        add("blocking", "assessment.criteria", "a criterion is listed twice")

    linked = _evidence(fm)
    ids = [s["id"] for s in subjects]
    if len(set(ids)) != len(ids):
        add("blocking", "assessment.subjects", "a subject is listed twice")
    if len(set(ids)) < 2:
        add("blocking", "assessment.subjects", "an assessment compares at least two different subjects")
    for s in subjects:
        if s["id"] not in linked:
            add("blocking", "assessment.subjects", f"subject '{s['id']}' is not linked as evaluates or supported_by in ddx.links")
        if not _one_line(s["label"]):
            add("blocking", "assessment.subjects", f"the label of '{s['id']}' must be one line")

    seen = set()
    for i, r in enumerate(ratings):
        where = f"assessment.ratings.{i}"
        crit, subj = r.get("criterion"), r.get("subject")
        if not isinstance(crit, str) or crit not in criteria:
            add("blocking", where, f"rating names criterion '{crit}', which this assessment does not list")
        if not isinstance(subj, str) or subj not in ids:
            add("blocking", where, f"rating names subject '{subj}', which this assessment does not list")
        text = [str(r.get(k) or "").strip() for k in ("finding", "gap")]
        if bool(text[0]) == bool(text[1]):
            add("blocking", where, "a rating has exactly one of `finding` or `gap`")
        elif not _one_line(text[0] or text[1]):
            add("blocking", where, "a finding or gap is one line; it fills one table cell")
        if (crit, subj) in seen:
            add("blocking", where, f"'{crit}' is rated twice for '{subj}'")
        seen.add((crit, subj))
    for crit in criteria:
        for subj in ids:
            if (crit, subj) not in seen:
                add("blocking", "assessment.ratings", f"'{subj}' has no rating or gap for '{crit}'")

    if layout.get("rows", "criteria") not in ROW_LAYOUTS:
        add("blocking", "assessment.comparison", f"`comparison.rows` is one of {', '.join(ROW_LAYOUTS)}")
    if layout.get("tables") is not None:
        flat = [c for t in layout["tables"] for c in t]
        if sorted(flat) != sorted(criteria):
            add("blocking", "assessment.comparison", "`comparison.tables` must place every criterion in exactly one table")


def _check_recommendations(fm: dict, instance: Path, add, publish: bool) -> None:
    recs = fm["recommendations"]
    if not isinstance(recs, list) or not recs:
        add("blocking", "recommendations.shape", "`recommendations:` must be a non-empty list")
        return
    linked = _evidence(fm)
    path, cat = _catalogue_for(instance, add, "recommendations")
    seen = set()
    for i, r in enumerate(recs):
        where = f"recommendations.{i}"
        if not isinstance(r, dict):
            add("blocking", where, "a recommendation must be a mapping")
            continue
        subject, context, stance = r.get("subject"), r.get("context"), r.get("stance")
        if not (isinstance(subject, str) and subject and isinstance(context, str) and context):
            add("blocking", where, "a recommendation names a string `subject` and `context`")
        else:
            if (subject, context) in seen:
                add("blocking", where, f"'{subject}' is recommended twice for context '{context}'")
            seen.add((subject, context))
            if subject not in linked:
                add("blocking", where, f"subject '{subject}' is not linked as evaluates or supported_by in ddx.links")
        if not (isinstance(stance, str) and stance in STANCES):
            add("blocking", where, f"stance must be one of {', '.join(STANCES)}")
        if not str(r.get("rationale") or "").strip():
            add("blocking", where, "a recommendation states its rationale")
        if stance == "conditional" and not str(r.get("conditions") or "").strip():
            add("blocking", where, "a conditional stance states its conditions")
        if not all(_one_line(r.get(k) or "") for k in ("label", "context", "conditions")):
            add("blocking", where, "`label`, `context` and `conditions` are one line; they fill table cells")
        based_on = r.get("based_on")
        if not isinstance(based_on, list) or not based_on:
            add("blocking", where, "a recommendation rests on `based_on` assessments, never on assertion")
        for b in based_on if isinstance(based_on, list) else []:
            name = b.get("assessment") if isinstance(b, dict) else b
            link = linked.get(name) if isinstance(name, str) else None
            if not isinstance(b, dict) or not link or link["kind"] != "supported_by":
                add("blocking", where, f"based_on '{name}' must be an {{assessment, criteria}} mapping whose assessment "
                    "is linked as supported_by in ddx.links, so the paper pins what it rests on")
                continue
            if publish and not PIN_RE.match(link["rev"]):
                add("blocking", where, f"based_on '{name}' needs a pinned rev (git:<commit> or sha256:<hex>) at the publish tier")
            cited = _ids(b.get("criteria") if b.get("criteria") is not None else [])
            if cited is None:
                add("blocking", where, f"`criteria` under based_on '{name}' is a list of criterion ids")
                continue
            if cited and path is None:
                add("blocking", where, "cited criteria are ids from criteria.yml, which this graph does not have")
            for cid in cited if path else []:
                if cid not in cat:
                    add("blocking", where, f"cited criterion '{cid}' is not in {path.name}")
        since, review_by = _date(r.get("since")), _date(r.get("review_by"))
        if not since or not review_by:
            add("blocking", where, "`since` and `review_by` are YYYY-MM-DD dates")
        elif review_by <= since:
            add("blocking", where, "`review_by` is after `since`")
        approver, approved_on = r.get("approved_by"), r.get("approved_on")
        if bool(approver) != bool(approved_on):
            add("blocking", where, "`approved_by` and `approved_on` are given together or not at all")
        elif approved_on and not _date(approved_on):
            add("blocking", where, "`approved_on` is a YYYY-MM-DD date")


# --- tables made from the blocks ---------------------------------------------------------------

def cell(value: object) -> str:
    """A table cell: one line, with the pipe escaped. check() rejects multi-line text first."""
    return str(value).strip().replace("|", "\\|")


def render_table(head: list[str], rows: list[list[str]]) -> str:
    head = [cell(h) for h in head]
    out = ["| " + " | ".join(head) + " |", "|" + "|".join("-" * (len(h) + 2) for h in head) + "|"]
    out += ["| " + " | ".join(cell(c) for c in r) + " |" for r in rows]
    return "\n".join(out) + "\n"


def render_assessment(block: dict, cat: dict[str, dict]) -> tuple[str, list[str]]:
    """The Criteria table and the Comparison tables an `assessment:` block makes."""
    def label(cid: str) -> str:
        return cat[cid]["label"]
    crit = render_table(["Criterion", "Definition", "Concern"],
                        [[label(c), cat[c].get("definition") or "", cat[c].get("concern") or "none"]
                         for c in block["criteria"]])
    cells = {(r["criterion"], r["subject"]): r.get("finding") or r.get("gap") for r in block["ratings"]}
    subjects = block["subjects"]
    layout = block.get("comparison") or {}
    by_criteria = layout.get("rows", "criteria") == "criteria"
    tables = layout.get("tables") or [block["criteria"]]
    comp = []
    for cols in tables:
        if by_criteria:
            comp.append(render_table(["Criterion"] + [s["label"] for s in subjects],
                                     [[label(c)] + [cells[(c, s["id"])] for s in subjects] for c in cols]))
        else:
            comp.append(render_table(["Option"] + [label(c) for c in cols],
                                     [[s["label"]] + [cells[(c, s["id"])] for c in cols] for s in subjects]))
    return crit, comp


def render_recommendations(recs: list[dict]) -> str:
    rows = []
    for r in recs:
        status = "Approved" if r.get("approved_by") else "Proposed"
        rows.append([r.get("label") or r["subject"], f"{STANCES[r['stance']]} ({status})", r["context"],
                     r.get("conditions") or "", ", ".join(str(b["assessment"]) for b in r["based_on"])])
    return render_table(["Technology", "Stance", "Context", "Conditions", "Based on"], rows)


def section_span(body: str, name: str) -> tuple[int, int] | None:
    m = re.search(rf"^## {re.escape(name)}\s*\n", body, re.M)
    if not m:
        return None
    n = re.search(r"^## ", body[m.end():], re.M)
    return m.end(), (m.end() + n.start() if n else len(body))


def table_spans(body: str, span: tuple[int, int]) -> list[tuple[int, int]]:
    """(start, end) of each pipe table inside span."""
    out, start, pos = [], None, span[0]
    for line in body[span[0]:span[1]].splitlines(keepends=True):
        if line.lstrip().startswith("|"):
            if start is None:
                start = pos
        elif start is not None:
            out.append((start, pos))
            start = None
        pos += len(line)
    if start is not None:
        out.append((start, pos))
    return out


def regenerate(fm: dict, type_id: str, body: str, instance: Path) -> str:
    """body with its generated tables rewritten from the front matter's block."""
    fm, _ = expand_keys(fm, instance)
    if type_id == "position-paper":
        span = section_span(body, "Recommendations")
        tables = table_spans(body, span) if span else []
        if not tables:
            raise ValueError("no table under `## Recommendations`")
        (a, b), text = tables[0], render_recommendations(fm["recommendations"])
        return body[:a] + text + body[b:]
    cat = load_catalogue(find_catalogue(instance))
    crit, comp = render_assessment(fm["assessment"], cat)
    spans = []
    cs = section_span(body, "Criteria")
    ct = table_spans(body, cs) if cs else []
    if not ct:
        raise ValueError("no table under `## Criteria`")
    spans.append((ct[0], crit))
    ps = section_span(body, "Comparison")
    tables = table_spans(body, ps) if ps else []
    if len(tables) != len(comp):
        raise ValueError(f"{len(tables)} tables under `## Comparison`, {len(comp)} in the `assessment:` block")
    spans += list(zip(tables, comp))
    for (a, b), text in sorted(spans, key=lambda s: -s[0][0]):
        body = body[:a] + text + body[b:]
    return body
