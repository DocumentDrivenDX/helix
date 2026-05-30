---
title: "ADR-008: data-PRD Is a Kind-Switch Variant of PRD, Not a Sibling Artifact"
slug: ADR-008-data-prd-is-prd-kind-variant
weight: 230
activity: "Design"
source: "02-design/adr/ADR-008-data-prd-is-prd-kind-variant.md"
generated: true
collection: adr
---

> **Source identity** (from `02-design/adr/ADR-008-data-prd-is-prd-kind-variant.md`):

```yaml
ddx:
  id: ADR-008
  depends_on:
    - helix.prd
```

# ADR-008: data-PRD Is a Kind-Switch Variant of PRD, Not a Sibling Artifact

| Date | Status | Deciders | Related | Confidence |
|------|--------|----------|---------|------------|
| 2026-05-30 | Accepted | HELIX maintainers | artifact-types catalog, prd, data-prd | High |

## Context

| Aspect | Description |
|--------|-------------|
| Problem | The `data-prd` artifact type is a near-duplicate of `prd` with data-product framing. Its `required_sections` drift from the `prd` template, the boundary between the two artifact types is not load-bearing, and the catalog carries an orthogonality defect: two artifact-type directories that differ only in framing, not in role. |
| Current State | `workflows/activities/01-frame/artifacts/prd/` and `workflows/activities/01-frame/artifacts/data-prd/` ship as sibling artifact-type directories. Both serve the framing role of "product requirements document"; `data-prd` only adjusts vocabulary toward data products. The two trees have diverged in required sections without a substantive reason. |
| Requirements | The catalog must represent one PRD role with explicit variant framing rather than two parallel artifact types. The variant must remain discoverable for data-product framing without forcing every PRD to carry data-product vocabulary. Downstream consumers that reference `data-prd` must continue to resolve. |

## Decision

`data-prd` collapses into `prd` as a `kind: data` variant. The PRD artifact
gains a `kind` field (default `product`); when set to `data`, the prompt and
template guidance shift to data-product framing under conditional headings.
The current `data-prd` artifact-type directory is deprecated and will be
removed in Phase 3.

The PRD artifact owns one role — framing product (or data-product)
requirements — and exposes the variant through a kind switch on its meta. The
shape of the artifact is unified; the framing is parameterized.

**Key Points**: one PRD artifact with a `kind` switch | `kind: product`
default, `kind: data` for data products | `data-prd` directory removed in
Phase 3 with alias for downstream consumers

## Alternatives

| Option | Pros | Cons | Evaluation |
|--------|------|------|------------|
| Keep `data-prd` as a sibling artifact type | No migration work; existing references unchanged | Perpetuates orthogonality defect; required-section drift continues; catalog advertises a boundary that is not load-bearing | Rejected: the boundary does not carry weight |
| Merge `data-prd` into `prd` with no variant marker | Simplest collapse | Loses data-product framing entirely; existing data-PRD consumers lose guidance | Rejected: framing variant has real value |
| **Collapse `data-prd` into `prd` as a `kind: data` variant** | Unifies the role; preserves the framing as a parameterized variant; eliminates the duplicate directory; lets the template carry conditional guidance | Phase 3 must edit `prd` meta/prompt/template and remove the `data-prd` directory; downstream references to `data-prd` must be redirected or aliased | **Selected: smallest change that resolves the defect while preserving the framing variant** |

## Consequences

| Type | Impact |
|------|--------|
| Positive | The artifact-type catalog represents one PRD role instead of two near-duplicates. |
| Positive | Required-section drift between `prd` and `data-prd` ends; one template governs both framings. |
| Positive | Data-product framing remains discoverable through an explicit `kind: data` switch rather than a parallel directory. |
| Positive | New PRD-shaped variants (if any) can be added as additional `kind` values without forking the directory. |
| Negative | Phase 3 must extend `prd` meta/prompt/template, delete the `data-prd` directory, and update or alias every reference under `docs/helix/` and `workflows/`. |
| Neutral | Existing PRDs default to `kind: product` and require no content change. |

## Risks

| Risk | Prob | Impact | Mitigation |
|------|------|--------|------------|
| Downstream consumers still resolve `data-prd` by path | M | M | Add an alias in any downstream consumer that resolves artifact-type paths; update references in the same Phase 3 pass |
| Conditional kind-specific guidance in the template becomes hard to read | M | M | Keep kind-specific guidance under clearly labeled conditional headings; avoid interleaving product and data framing line-by-line |
| New PRD variants accumulate via the kind switch without governance | L | M | Document the kind enum in `prd` meta with the supported values; new values require an ADR |

## Validation

| Success Metric | Review Trigger |
|----------------|----------------|
| `workflows/activities/01-frame/artifacts/data-prd/` is removed after Phase 3 | A `data-prd` artifact-type directory remains after Phase 3 |
| `prd` meta declares a `kind` enum with `product` (default) and `data` values | The `prd` artifact ships without a `kind` field after Phase 3 |
| `prd` prompt and template carry kind-specific guidance under conditional headings | Data-product framing is lost from the unified PRD artifact |
| All references to `data-prd` under `docs/helix/` and `workflows/` resolve to `prd` with the kind switch | A reference to `data-prd` resolves to a missing directory after Phase 3 |

## References

- [PRD](/artifacts/prd/)
- [Plan: 2026-05-30 Artifact Types and Concerns Audit](/artifacts/plan-2026-05-30-artifact-types-and-concerns-audit/)
