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


def find_catalogue(instance: Path) -> Path | None:
    """criteria.yml in the nearest ancestor directory that has one, stopping at the project marker."""
    for parent in instance.resolve().parents:
        if (parent / "criteria.yml").is_file():
            return parent / "criteria.yml"
        if (parent / ".helix.yml").is_file():
            return None
    return None


def load_catalogue(path: Path | None) -> dict[str, dict]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) if path else None
    return {c["id"]: c for c in (data or {}).get("criteria") or [] if isinstance(c, dict) and c.get("id")}


def _date(value: object) -> datetime.date | None:
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    try:
        return datetime.date.fromisoformat(str(value))
    except ValueError:
        return None


def _evidence_ids(fm: dict) -> dict[str, str]:
    """ddx.links id -> kind, for the links an assessment or paper may rest on."""
    out = {}
    for link in (fm.get("ddx") or {}).get("links") or []:
        if isinstance(link, dict) and link.get("kind") in EVIDENCE_KINDS and not link.get("graph"):
            out[str(link["id"])] = link["kind"]
    return out


def check(fm: dict | None, type_id: str, instance: Path, add) -> None:
    """Report structured-block findings through add(severity, check, message)."""
    fm = fm or {}
    for key, owner in (("assessment", "technology-assessment"), ("recommendations", "position-paper")):
        if key in fm and type_id != owner:
            add("blocking", f"{key}.placement", f"`{key}:` belongs on a {owner}, not a {type_id}; "
                "knowledge and advice are kept apart")
    if type_id == "technology-assessment" and "assessment" in fm:
        _check_assessment(fm, instance, add)
    if type_id == "position-paper" and "recommendations" in fm:
        _check_recommendations(fm, instance, add)


def _check_assessment(fm: dict, instance: Path, add) -> None:
    block = fm["assessment"]
    if not isinstance(block, dict):
        add("blocking", "assessment.shape", "`assessment:` must be a mapping")
        return
    path = find_catalogue(instance)
    cat = load_catalogue(path)
    if path is None:
        add("blocking", "assessment.catalogue", "no criteria.yml in this graph; criteria are ids from it")
    criteria = [str(c) for c in block.get("criteria") or []]
    for cid in criteria:
        if path and cid not in cat:
            add("blocking", "assessment.criteria", f"criterion '{cid}' is not in {path.name}")
    if len(set(criteria)) != len(criteria):
        add("blocking", "assessment.criteria", "a criterion is listed twice")
    if not criteria:
        add("blocking", "assessment.criteria", "`assessment.criteria` lists no criteria")

    linked = _evidence_ids(fm)
    subjects = [s for s in block.get("subjects") or [] if isinstance(s, dict)]
    ids = [str(s.get("id")) for s in subjects]
    if len(subjects) < 2:
        add("blocking", "assessment.subjects", "an assessment compares at least two subjects")
    for s in subjects:
        if not s.get("label"):
            add("blocking", "assessment.subjects", f"subject '{s.get('id')}' needs a label")
        if str(s.get("id")) not in linked:
            add("blocking", "assessment.subjects",
                f"subject '{s.get('id')}' is not linked as evaluates or supported_by in ddx.links")

    seen = set()
    for i, r in enumerate(block.get("ratings") or []):
        if not isinstance(r, dict):
            add("blocking", f"assessment.ratings.{i}", "a rating must be a mapping")
            continue
        crit, subj = str(r.get("criterion")), str(r.get("subject"))
        if crit not in criteria:
            add("blocking", f"assessment.ratings.{i}", f"rating names criterion '{crit}', which this assessment does not list")
        if subj not in ids:
            add("blocking", f"assessment.ratings.{i}", f"rating names subject '{subj}', which this assessment does not list")
        if bool(str(r.get("finding") or "").strip()) == bool(str(r.get("gap") or "").strip()):
            add("blocking", f"assessment.ratings.{i}", "a rating has exactly one of `finding` or `gap`")
        if (crit, subj) in seen:
            add("blocking", f"assessment.ratings.{i}", f"'{crit}' is rated twice for '{subj}'")
        seen.add((crit, subj))
    for crit in criteria:
        for subj in ids:
            if (crit, subj) not in seen:
                add("blocking", "assessment.ratings", f"'{subj}' has no rating or gap for '{crit}'")

    layout = block.get("comparison") or {}
    if layout.get("rows", "criteria") not in ROW_LAYOUTS:
        add("blocking", "assessment.comparison", f"`comparison.rows` is one of {', '.join(ROW_LAYOUTS)}")
    tables = layout.get("tables")
    if tables is not None:
        flat = [str(c) for t in tables for c in t]
        if sorted(flat) != sorted(criteria):
            add("blocking", "assessment.comparison", "`comparison.tables` must place every criterion in exactly one table")


def _check_recommendations(fm: dict, instance: Path, add) -> None:
    recs = fm["recommendations"]
    if not isinstance(recs, list) or not recs:
        add("blocking", "recommendations.shape", "`recommendations:` must be a non-empty list")
        return
    linked = _evidence_ids(fm)
    path = find_catalogue(instance)
    cat = load_catalogue(path)
    seen = set()
    for i, r in enumerate(recs):
        where = f"recommendations.{i}"
        if not isinstance(r, dict):
            add("blocking", where, "a recommendation must be a mapping")
            continue
        subject, context, stance = r.get("subject"), r.get("context"), r.get("stance")
        if not subject or not context:
            add("blocking", where, "a recommendation names a `subject` and a `context`")
        elif (subject, context) in seen:
            add("blocking", where, f"'{subject}' is recommended twice for context '{context}'")
        seen.add((subject, context))
        if subject and str(subject) not in linked:
            add("blocking", where, f"subject '{subject}' is not linked as evaluates or supported_by in ddx.links")
        if stance not in STANCES:
            add("blocking", where, f"stance must be one of {', '.join(STANCES)}")
        if not str(r.get("rationale") or "").strip():
            add("blocking", where, "a recommendation states its rationale")
        if stance == "conditional" and not str(r.get("conditions") or "").strip():
            add("blocking", where, "a conditional stance states its conditions")
        based_on = r.get("based_on")
        if not isinstance(based_on, list) or not based_on:
            add("blocking", where, "a recommendation rests on `based_on` assessments, never on assertion")
        for b in based_on if isinstance(based_on, list) else []:
            if not isinstance(b, dict) or linked.get(str(b.get("assessment"))) != "supported_by":
                add("blocking", where, f"based_on '{b.get('assessment') if isinstance(b, dict) else b}' "
                    "must be linked as supported_by in ddx.links, so the paper pins what it rests on")
                continue
            for cid in b.get("criteria") or []:
                if path and str(cid) not in cat:
                    add("blocking", where, f"cited criterion '{cid}' is not in {path.name}")
        since, review_by = _date(r.get("since")), _date(r.get("review_by"))
        if not since or not review_by:
            add("blocking", where, "`since` and `review_by` are ISO dates")
        elif review_by <= since:
            add("blocking", where, "`review_by` is after `since`")
        approver, approved_on = r.get("approved_by"), r.get("approved_on")
        if bool(approver) != bool(approved_on):
            add("blocking", where, "`approved_by` and `approved_on` are given together or not at all")
        elif approved_on and not _date(approved_on):
            add("blocking", where, "`approved_on` is an ISO date")


# --- tables made from the blocks ---------------------------------------------------------------

def render_table(head: list[str], rows: list[list[str]]) -> str:
    out = ["| " + " | ".join(head) + " |", "|" + "|".join("-" * (len(h) + 2) for h in head) + "|"]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join(out) + "\n"


def render_assessment(block: dict, cat: dict[str, dict]) -> tuple[str, list[str]]:
    """The Criteria table and the Comparison tables an `assessment:` block makes."""
    def label(cid: str) -> str:
        return cat[cid]["label"]
    crit = render_table(["Criterion", "Definition", "Concern"],
                        [[label(c), str(cat[c].get("definition", "")).strip(), str(cat[c].get("concern") or "none")]
                         for c in block["criteria"]])
    cell = {(r["criterion"], r["subject"]): str(r.get("finding") or r.get("gap")).strip() for r in block["ratings"]}
    subjects = block["subjects"]
    layout = block.get("comparison") or {}
    by_criteria = layout.get("rows", "criteria") == "criteria"
    tables = layout.get("tables") or [block["criteria"]]
    comp = []
    for cols in tables:
        if by_criteria:
            comp.append(render_table(["Criterion"] + [s["label"] for s in subjects],
                                     [[label(c)] + [cell[(c, s["id"])] for s in subjects] for c in cols]))
        else:
            comp.append(render_table(["Option"] + [label(c) for c in cols],
                                     [[s["label"]] + [cell[(c, s["id"])] for c in cols] for s in subjects]))
    return crit, comp


def render_recommendations(recs: list[dict]) -> str:
    rows = []
    for r in recs:
        status = "Approved" if r.get("approved_by") else "Proposed"
        rows.append([str(r.get("label") or r["subject"]), f"{STANCES[r['stance']]} ({status})", str(r["context"]),
                     str(r.get("conditions") or "").strip(),
                     ", ".join(str(b["assessment"]) for b in r["based_on"])])
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
