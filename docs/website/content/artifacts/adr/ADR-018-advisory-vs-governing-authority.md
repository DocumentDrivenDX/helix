---
title: "ADR-018: Cross-graph references are advisory unless the consumer grants authority"
slug: ADR-018-advisory-vs-governing-authority
weight: 360
activity: "Design"
source: "02-design/adr/ADR-018-advisory-vs-governing-authority.md"
generated: true
collection: adr
---

> **Example from HELIX's own docs.** This generated page comes from `docs/helix/`. Use it to see the method in practice; start with the [artifact-type catalog](/artifact-types/) for reusable templates. Historical plans and reports may describe retired architecture.

> **Source identity** (from `02-design/adr/ADR-018-advisory-vs-governing-authority.md`):

```yaml
ddx:
  id: ADR-018
  authoring:
    home: repo
  status: accepted
  depends_on:
    - ADR-017
    - ADR-004
    - ADR-013
```

# ADR-018: Cross-graph references are advisory unless the consumer grants authority

| Date | Status | Deciders | Related | Confidence |
|------|--------|----------|---------|------------|
| 2026-11-06 | Accepted | HELIX maintainers | `ddx.links`, `external_edges`, concerns, SD-003 | Medium |

## Problem

A general technology assessment may inform a client's ADR without overruling
client requirements or approved decisions. Today authority is implicit and
positional within one flow, `external_edges` is always empty, and `ddx.links`
is used by the skill and modes but undefined in `artifact-schema.md`. Atlas
needs typed relationships and an explicit informational/governing split.

## Decision

1. Extend the existing `ddx.links` entry shape `{id, kind}` (as in `kind: informed_by`) with optional `authority` and `rev`: `{id, kind, authority?, rev?}`. `kind` reads from this document to the target.
2. Reuse existing predicates first: `depends_on`, `informs`, `supersedes`.
   Add `kind` values `addresses`, `evaluates`, `supported_by`, `contradicts`
   (alongside the existing `informed_by` and `informs`) only as link kinds,
   not new top-level fields. `rev` pins the target revision read.
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
| Neutral | Existing `ddx.links` usage stays valid: a bare id string and `{id, kind: informed_by}` both mean an upstream reference. |

## Open question

Resolved. `ddx.links` is not defined in `artifact-schema.md`, but it is in use
in two shapes: bare id strings (`docs/helix/02-design/design-desired-state-authoring.md`)
and `{id, kind: informed_by}` mappings (every deliverable). Item 1 extends
that mapping shape rather than introducing another. An earlier draft of this
ADR proposed `{rel, target}`; that was corrected to match existing usage.
