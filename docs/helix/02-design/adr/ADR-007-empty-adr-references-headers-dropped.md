---
ddx:
  id: ADR-007
  depends_on:
    - helix.prd
---
# ADR-007: Empty ADR References Headers Are Dropped; Required Only When a Concern Cites a Specific ADR

| Date | Status | Deciders | Related | Confidence |
|------|--------|----------|---------|------------|
| 2026-05-30 | Accepted | HELIX maintainers | concerns library, schema validator | High |

## Context

| Aspect | Description |
|--------|-------------|
| Problem | Many concerns ship an `ADR References` section header with no entries beneath it. The empty header creates a false promise of governing decisions that do not exist, and pads the artifact with structure that carries no information. |
| Current State | 14 concerns currently ship an empty `ADR References` header: `a11y-wcag-aa`, `demo-asciinema`, `demo-playwright`, `design-patterns-gof`, `e2e-kind`, `e2e-playwright`, `go-std`, `hugo-hextra`, `i18n-icu`, `k8s-kind`, `o11y-otel`, `python-uv`, `rust-cargo`, `scala-sbt`. The schema validator does not require the section to be present. |
| Requirements | The concerns library must not advertise references that do not exist. The section should appear only when it carries real ADR citations, and should be omitted when it would otherwise be empty. The schema validator must continue to treat the section as optional. |

## Decision

An `ADR References` section header in a concern is included **only when the
concern actually cites one or more ADRs**. Empty headers are removed by Phase 3
mechanical edits across the 14 concerns enumerated above. The schema validator
does not require this section; presence is driven by content, not by template
shape.

Concerns that genuinely govern decisions via ADRs keep the section and list the
ADRs they cite. Concerns with no real ADR citations omit the header entirely.

**Key Points**: header presence follows content | empty headers removed in
Phase 3 | schema validator keeps the section optional

## Alternatives

| Option | Pros | Cons | Evaluation |
|--------|------|------|------------|
| Keep empty `ADR References` headers as a template slot | Uniform structure across concerns | False promise of citations; padding without information; invites cargo-cult copy of the empty section into new concerns | Rejected: structure without content is noise |
| Require every concern to cite at least one ADR | Forces explicit governance | Most concerns are not governed by an ADR; would manufacture spurious references | Rejected: not all concerns need ADR backing |
| **Drop empty headers; require the section only when ADRs are cited** | Removes false promise; keeps real citations visible; matches existing validator behavior | Requires a one-time mechanical edit pass across 14 concerns | **Selected: smallest change that aligns shape with content** |

## Consequences

| Type | Impact |
|------|--------|
| Positive | Concerns no longer advertise references that do not exist. |
| Positive | Real ADR citations remain visible and unambiguous in the concerns that have them. |
| Positive | New concerns inherit a "populate or omit" rule that prevents the empty header from reappearing. |
| Negative | Phase 3 must touch 14 concern files to remove the empty headers. |
| Neutral | The schema validator is unchanged; the section stays optional. |

## Risks

| Risk | Prob | Impact | Mitigation |
|------|------|--------|------------|
| Future concerns reintroduce the empty header by copy-paste | M | L | Phase 3 edits remove existing instances; reviewers reject empty headers on new concerns |
| A real ADR citation is accidentally removed alongside the empty headers | L | M | Phase 3 mechanical edits target only the enumerated 14 concerns where the section is empty |

## Validation

| Success Metric | Review Trigger |
|----------------|----------------|
| None of the 14 enumerated concerns ships an empty `ADR References` header after Phase 3 | An empty `ADR References` header appears in any concern |
| Concerns that cite ADRs retain the section with the citations intact | A real ADR citation is dropped by the Phase 3 edits |

## References

- [PRD](../../01-frame/prd.md)
- [Plan: 2026-05-30 Artifact Types and Concerns Audit](../plan-2026-05-30-artifact-types-and-concerns-audit.md)
