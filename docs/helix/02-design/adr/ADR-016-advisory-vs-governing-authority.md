---
ddx:
  id: ADR-016
  authoring:
    home: repo
  status: proposed
  depends_on:
    - ADR-015
    - ADR-004
    - ADR-013
---
# ADR-016: Cross-graph references are advisory unless the consumer grants authority

| Date | Status | Deciders | Related | Confidence |
|------|--------|----------|---------|------------|
| 2026-11-06 | Proposed | HELIX maintainers | `ddx.links`, `external_edges`, concerns, SD-003 | Medium |

## Problem

A general technology assessment may inform a client's ADR without overruling
client requirements or approved decisions. Today authority is implicit and
positional within one flow, `external_edges` is always empty, and `ddx.links`
is used by the skill and modes but undefined in `artifact-schema.md`. Atlas
needs typed relationships and an explicit informational/governing split.

## Decision

1. Define `ddx.links` as a list of `{rel, target, authority?, ref?}`.
2. Reuse existing predicates first: `depends_on`, `informs`, `supersedes`.
   Add `rel` values `addresses`, `evaluates`, `supported_by`, `contradicts`
   only as link kinds, not new top-level fields.
3. Within a flow, positional authority is unchanged.
4. A link that crosses a flow or Atlas boundary is **advisory** by default.
   `governing` is granted only by the consuming graph's own marker or profile,
   never by the referenced graph.
5. `contradicts` is informational: reported by alignment, never a validation
   failure.
6. The concern registry is not generalized. Assessments reference concerns via
   `addresses`; they are not concerns.
7. External knowledge is referenced as `{graph, id, version}`. HELIX defines
   the shape; DDx or another runtime resolves it. Repository cloning is not
   required.

## Why we chose this

It adds one genuinely new semantic (authority class) plus one link kind
(`contradicts`), keeps edge vocabulary inside an existing frontmatter key, and
puts the grant of authority on the side that bears the consequence.

## Alternatives

| Option | Evaluation |
|--------|------------|
| Six new top-level predicates | Rejected: most map onto typed links or `depends_on`. |
| Referenced graph declares its own authority | Rejected: lets external knowledge overrule client decisions. |
| Universal knowledge/entity registry | Rejected: ontology creep; contradicts the concern-registry boundary. |

## Consequences

| Type | Impact |
|------|--------|
| Positive | Reuse of an Atlas assessment cannot silently override a client ADR. |
| Negative | `ddx.links` must be specified, and `check`/`align` must learn authority. |
| Neutral | Undefined legacy `ddx.links` usage stays valid when read as `informs`. |

## Open question

Checked: `ddx.links` is read as an untyped list of upstream references
(`modes/check.md:63`, `actions/evolve.md:13`, `modes/_authoring.md:17`) and is
not defined in `artifact-schema.md`. Item 1 therefore specifies the key rather
than changing it: a bare string entry remains valid and reads as `informs`.
