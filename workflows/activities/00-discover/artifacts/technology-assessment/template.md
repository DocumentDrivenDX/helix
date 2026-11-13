---
ddx:
  id: TA-[number]
  type: technology-assessment
  authoring:
    home: repo
  links:
    # - {id: <technology brief id>, kind: evaluates, rev: <pinned revision>}
    # - {id: <source id>, kind: supported_by, rev: <pinned revision>}
    # - {id: <other assessment id>, kind: contradicts}
  # Optional: criteria and ratings as data. The Criteria and Comparison tables below are then
  # generated from it (`assessment-tables.py --write`) and cannot drift from it. Criteria are
  # ids from `criteria.yml` at the flow root (entries: id, label, definition, concern). A
  # `keys.yml` beside it may map short names to document ids; subjects and ratings accept a
  # key, while `ddx.links` keep the full id and pinned rev. The document records what each key
  # resolved to in a top-level `keys: {<key>: <document id>}`, so repointing a key in keys.yml
  # shows up as a finding here instead of silently changing what the assessment cites.
# assessment:
#   criteria: [<criterion id from the graph's criteria.yml>]
#   subjects: [{id: <technology brief id or a key from keys.yml>, label: <name in the table>}]
#   ratings:
#     - {criterion: <id>, subject: <brief id>, finding: "<finding, source>"}
#     - {criterion: <id>, subject: <brief id>, gap: Not published}
---

# TA-[number]: [Subject: what is compared]

**Scope kinds** (`ddx.scope`). Unset is this whole template: technologies
compared on criteria. `practice` is an assessment of a practice that no
technology assessment covers: write Scope, Findings, Contradictions and Gaps,
and Sources, and omit the `assessment:` block, Criteria, Technologies,
Comparison, and Evidence. Group its Findings by reader (cost and commitment,
security and compliance, running it, building on it). It names a product
only as an example of a kind of tool.

## Scope

What is compared and what is not. Name each technology and version line,
the kind of use the comparison speaks to, and what is excluded.

## Criteria

Each criterion, defined, with the concern it comes from when one applies.

| Criterion | Definition | Concern |
|-----------|------------|---------|
| [Criterion] | [What is measured or checked] | [Concern id, or none] |

## Technologies

One line each, with the technology brief it rests on.

- **[Technology A]**: [what it is]. Brief: [id, pinned revision]
- **[Technology B]**: [what it is]. Brief: [id, pinned revision]

## Comparison

Every technology on every criterion. Each cell cites a brief section or says
Unknown.

| Criterion | [Technology A] | [Technology B] |
|-----------|----------------|----------------|
| [Criterion] | [Finding, source] | [Finding, source] |

## Findings

What the comparison shows, one short paragraph per criterion that
separates the technologies. No recommendation for a project.

## Contradictions and Gaps

Where sources disagree (both cited), and what no brief covers.

| Item | Sources or gap | Route |
|------|----------------|-------|
| [Conflict or gap] | [Sources] | [Research, spike, or accepted] |

## Evidence

| Reference | Kind | Revision | Used for |
|-----------|------|----------|----------|
| [Technology brief or source] | [kind] | [revision or digest] | [criterion] |

## Sources

Practice scope only; an assessment of technologies cites its briefs under
Evidence. Number each source and cite it at the clause it supports.

1. [Title](https://example.org/public-page), [author or organization], [date on the page]. Read [date].
