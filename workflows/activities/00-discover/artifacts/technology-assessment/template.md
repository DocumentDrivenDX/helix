---
ddx:
  id: TA-[number]
  type: technology-assessment
  status: draft
  authoring:
    home: repo
  links:
    # - {id: <technology brief id>, kind: evaluates, rev: <pinned revision>}
    # - {id: <source id>, kind: supported_by, rev: <pinned revision>}
    # - {id: <other assessment id>, kind: contradicts}
---

# TA-[number]: [Subject: what is compared]

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
