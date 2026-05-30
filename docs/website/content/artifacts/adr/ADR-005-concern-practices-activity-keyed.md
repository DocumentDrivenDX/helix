---
title: "ADR-005: Concern practices.md is HELIX-activity-keyed"
slug: ADR-005-concern-practices-activity-keyed
weight: 200
activity: "Design"
source: "02-design/adr/ADR-005-concern-practices-activity-keyed.md"
generated: true
collection: adr
---

> **Source identity** (from `02-design/adr/ADR-005-concern-practices-activity-keyed.md`):

```yaml
ddx:
  id: ADR-005
  depends_on:
    - helix.prd
```

# ADR-005: Concern practices.md is HELIX-activity-keyed

| Date | Status | Deciders | Related | Confidence |
|------|--------|----------|---------|------------|
| 2026-05-30 | Accepted | HELIX maintainers | concerns library, context-digest assembly | High |

## Context

| Aspect | Description |
|--------|-------------|
| Problem | Concern `practices.md` files use two incompatible organizing principles. Some are keyed by HELIX activity (Discover / Frame / Design / Test / Build / Deploy / Iterate), so per-activity context-digest assembly is a mechanical lookup. Others are keyed by topic (Implementation / Quality Gates / etc.), forcing the context assembler to guess which heading belongs to which activity. |
| Current State | Ten concerns are topic-keyed: `auth-local-sessions`, `caching-strategy`, `classic-layered`, `cqrs`, `domain-driven-design`, `enterprise-application-patterns`, `hexagonal-architecture`, `mcp-server`, `onion-architecture`, `sample-data`. The remaining concerns already organize practices by HELIX activity. |
| Requirements | Per-activity context-digest assembly must be a deterministic lookup, not a heuristic. The concerns library must use one consistent organizing principle so that any consumer — context assembler, alignment review, methodology docs — extracts the practices for a given activity by reading the corresponding heading. |

## Decision

Every concern's `practices.md` organizes its per-activity content under HELIX
activity headings: **Discover**, **Frame**, **Design**, **Test**, **Build**,
**Deploy**, **Iterate**. Topic-keyed or quality-gates-keyed organization is no
longer acceptable for `practices.md`.

Activity-keying makes per-activity context-digest assembly a mechanical lookup:
the assembler reads the heading whose name matches the current activity and
pulls the bullets underneath. No guessing, no mapping table, no per-concern
schema.

The ten topic-keyed concerns named above convert to activity-keying in Phase 3
of the artifact-types-and-concerns audit. New concerns ship activity-keyed from
day one.

**Key Points**: HELIX activity headings are the only acceptable top-level
structure in `practices.md` | mechanical per-activity lookup | ten existing
topic-keyed concerns convert in Phase 3

## Alternatives

| Option | Pros | Cons | Evaluation |
|--------|------|------|------------|
| Keep both styles (activity-keyed and topic-keyed) | No conversion work | Context-digest assembly must implement per-concern mapping logic and stay in sync as concerns evolve | Rejected: pushes guesswork into every consumer |
| Topic-keyed everywhere (Implementation / Quality Gates / ...) | Matches a few existing concerns | Forces the assembler to guess which topic applies to which activity; topics differ by concern | Rejected: not mechanically extractable |
| Add a frontmatter mapping table from topic → activity in each `practices.md` | Preserves topic prose | Introduces a per-concern schema to maintain; the heading and the mapping can drift | Rejected: heading is already the natural index |
| **Activity-keyed everywhere; convert the ten topic-keyed concerns in Phase 3** | One consistent structure; mechanical lookup; matches the majority of existing concerns | Requires per-concern restructuring for ten concerns | **Selected: smallest sufficient unification** |

## Consequences

| Type | Impact |
|------|--------|
| Positive | Per-activity context-digest assembly becomes a mechanical heading lookup across every concern. |
| Positive | Downstream consumers (alignment review, methodology docs, the website mirror) get a uniform structure to render and reason about. |
| Positive | New concerns have one obvious shape to follow; no per-concern bikeshed about structure. |
| Negative | The ten topic-keyed concerns require restructuring; some topic prose (e.g. cross-cutting Quality Gates) has to be reseated under the activity it applies to. |
| Neutral | The bullet content of each concern is preserved; only the organizing headings change. |

## Risks

| Risk | Prob | Impact | Mitigation |
|------|------|--------|------------|
| Conversion silently drops practice content during restructuring | M | M | Phase 3 conversion reviews the diff per concern; bullets must land under exactly one activity heading |
| Cross-cutting content (e.g. Quality Gates) has no natural single activity home | M | M | Allow the same bullet to appear under more than one activity heading when it genuinely applies across activities; prefer the closest activity otherwise |
| New concerns drift back to topic-keying | L | M | Lint or review check rejects `practices.md` whose top-level headings are not from the HELIX activity vocabulary |

## Validation

| Success Metric | Review Trigger |
|----------------|----------------|
| Every `practices.md` uses HELIX activity headings as its top-level structure | A `practices.md` lands or merges with topic-keyed headings |
| The ten named concerns are converted in Phase 3 with no lost content | Phase 3 closes with any of the ten still topic-keyed |
| Context-digest assembly extracts per-activity practices by heading lookup, with no per-concern mapping | The assembler grows per-concern conditional logic |

## References

- [PRD](/artifacts/prd/)
- Phase 1A plan: `docs/helix/02-design/plan-2026-05-30-artifact-types-and-concerns-audit.md`
- Concerns library: `workflows/concerns/`
