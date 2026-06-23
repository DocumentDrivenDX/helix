---
ddx:
  id: example.feature-registry.depositmatch
  depends_on:
    - example.prd.depositmatch
    - example.opportunity-canvas.depositmatch
  review:
    self_hash: 227c7c30edf5318187982fad9b7c868365600d4ffb8f92da25b1f932769dddb8
    deps:
      example.opportunity-canvas.depositmatch: 75303097bfeeed0272bd68f90ef887f9a5e646a1272f9a57ccd0d899ae17497a
      example.prd.depositmatch: c9c24e1694af4548a6deaad8d92059e365da110148bd9adc44d8640dff9770a4
    reviewed_at: "2026-05-15T04:11:24Z"
---

# Feature Registry

**Status**: Active
**Last Updated**: 2026-05-12

## Active Features

| ID | Name | Description | Status | Priority | Owner | Source | Updated |
|----|------|-------------|--------|----------|-------|--------|---------|
| FEAT-001 | CSV Import and Column Mapping | Import bank/invoice CSVs and map columns per client. | Specified | P0 | Product / Engineering | PRD, Opportunity Canvas | 2026-05-12 |
| FEAT-002 | Evidence-Backed Match Review | Suggest deposit-to-invoice matches with visible evidence before reviewer approval. | Draft | P0 | Product / Engineering | PRD, Product Vision | 2026-05-12 |
| FEAT-003 | Client Exception Queue | Keep unresolved deposits grouped by client with owner and next action. | Draft | P0 | Product | PRD, Opportunity Canvas | 2026-05-12 |
| FEAT-004 | Review Log Export | Export accepted matches, exceptions, reviewer actions, and evidence for client review. | Draft | P1 | Product / Compliance | Compliance Requirements, PRD | 2026-05-12 |

## Status Definitions

- **Draft**: Requirements being gathered
- **Specified**: Feature spec complete (Frame done)
- **Designed**: Technical design complete (Design done)
- **In Test**: Tests being written
- **In Build**: Implementation in progress
- **Built**: Implementation complete
- **Deployed**: Released to production
- **Deprecated**: Scheduled for removal
- **Cancelled**: Will not be pursued

## Dependencies

| Feature | Depends On | Type | Notes |
|---------|------------|------|-------|
| FEAT-002 | FEAT-001 | Required | Match suggestions need normalized imported records. |
| FEAT-003 | FEAT-001 | Required | Exceptions originate from imported unmatched or ambiguous deposits. |
| FEAT-004 | FEAT-002, FEAT-003 | Required | Export needs accepted matches and exception history. |

## Trace Links

| Feature | Spec | Stories | Designs | Tests | Release |
|---------|------|---------|---------|-------|---------|
| FEAT-001 | `feature-specification/example.md` | `user-stories/example.md` | Pending | Pending | Pilot |
| FEAT-002 | Pending | Pending | Pending | Pending | Pilot |
| FEAT-003 | Pending | Pending | Pending | Pending | Pilot |
| FEAT-004 | Pending | Pending | Pending | Pending | Pilot |

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
