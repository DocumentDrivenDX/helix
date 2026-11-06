---
ddx:
  id: example.feature-registry.depositmatch
  authoring:
    home: repo
  depends_on:
    - example.prd.depositmatch
    - example.opportunity-canvas.depositmatch
---

# Feature Registry

**Last Updated**: 2026-05-12

## Active Features

| ID | Name | Description | Priority | Owner | Source | Updated |
|----|------|-------------|----------|-------|--------|---------|
| FEAT-001 | CSV Import and Column Mapping | Import bank/invoice CSVs and map columns per client. | P0 | Product / Engineering | PRD, Opportunity Canvas | 2026-05-12 |
| FEAT-002 | Evidence-Backed Match Review | Suggest deposit-to-invoice matches with visible evidence before reviewer approval. | P0 | Product / Engineering | PRD, Product Vision | 2026-05-12 |
| FEAT-003 | Client Exception Queue | Keep unresolved deposits grouped by client with owner and next action. | P0 | Product | PRD, Opportunity Canvas | 2026-05-12 |
| FEAT-004 | Review Log Export | Export accepted matches, exceptions, reviewer actions, and evidence for client review. | P1 | Product / Compliance | Compliance Requirements, PRD | 2026-05-12 |

## Product Lifecycle

Record release, product deprecation, or cancellation information only when it
changes a product decision. Implementation progress belongs in the relevant
plan, selected work item, or factual report. Do not track document stages here.

## Dependencies

| Feature | Depends On | Type | Notes |
|---------|------------|------|-------|
| FEAT-002 | FEAT-001 | Required | Match suggestions need normalized imported records. |
| FEAT-003 | FEAT-001 | Required | Exceptions originate from imported unmatched or ambiguous deposits. |
| FEAT-004 | FEAT-002, FEAT-003 | Required | Export needs accepted matches and exception history. |

## Relevant References

Link governing artifacts and evidence when useful for the scoped work. Do not
seed empty traceability matrices or report missing links as separate work.

## Feature Categories

### Pilot Foundation

- FEAT-001: CSV Import and Column Mapping

### Review Workflow

- FEAT-002: Evidence-Backed Match Review
- FEAT-003: Client Exception Queue
- FEAT-004: Review Log Export

## ID Rules

1. Sequential numbering: FEAT-XXX (zero-padded 3 digits)
2. Never reuse IDs, even for cancelled features
3. Do not encode category or priority into the ID
4. Keep full behavior in Feature Specifications, not in this registry

## Deprecated/Cancelled

| ID | Name | Status | Reason | Date |
|----|------|--------|--------|------|
| None | None | None | None | None |
