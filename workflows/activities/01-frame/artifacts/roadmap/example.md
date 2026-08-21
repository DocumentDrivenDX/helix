---
ddx:
  id: example.roadmap.depositmatch
  depends_on:
    - example.prd.depositmatch
---

# Roadmap

**Scope**: DepositMatch — deposit reconciliation for community banks
**Owner**: Product Owner
**Last Revised**: 2026-05-20 — pilot go decision re-ranked reporting behind matching

## Horizon and Cadence

- **Horizon**: 3 iterations (through pilot exit decision)
- **Cadence**: 2-week iterations, review on the final Friday
- **Beyond the horizon**: multi-bank tenancy and audit export stay in the
  improvement backlog, unsequenced, until pilot evidence arrives

## Workstreams

Workstreams are the stable cross-iteration groupings of work. The alias is
the identifier: `WS-<n>`, assigned sequentially, never reused or renumbered.

| Alias | Workstream | Scope | Owner | Status |
|-------|------------|-------|-------|--------|
| WS-1 | Data Intake | CSV import, fixtures, validation; excludes matching logic | Priya | active |
| WS-2 | Matching & Review | Matching engine and exception-review queue; excludes reporting | Sam | active |
| WS-3 | Pilot Reporting | Reconciliation summaries and exports for pilot exit | Priya | active |

## Sequenced Outcomes

| Order | Outcome | Workstream | Governing Artifact | Target Iteration | Depends On | Confidence | Why This Order |
|-------|---------|------------|--------------------|------------------|------------|------------|----------------|
| 1 | CSV import validated against real pilot-bank exports | WS-1 | PRD R-1, FEAT-001 | IT-05 | None | High | Every downstream feature consumes imported data; fixture risk is the top test-plan risk |
| 2 | Matching engine reaches ≥95% auto-match on pilot data | WS-2 | PRD R-2, FEAT-002 | IT-06 | 1 | Medium | Value driver of the pilot; needs real imports first to be measurable |
| 3 | Exception-review queue usable by pilot operations staff | WS-2 | PRD R-3, FEAT-003 | IT-06 | 2 | Medium | Unmatched deposits must land somewhere reviewable before pilot exit |
| 4 | Reconciliation summary report exportable | WS-3 | PRD R-5 | IT-07 | 2 | Low | Wanted for pilot exit review; drops first if matching accuracy needs the slot |

## Revision Triggers

- Pilot-bank fixture findings contradict the import assumptions (re-sequence
  within one business day of the finding).
- Matching accuracy plateaus below 90% (reporting drops off the horizon;
  accuracy work takes IT-07).
- The active iteration's committed outcomes stay stable across revisions;
  re-sequencing applies from the next iteration forward.

## Review Checklist

- [x] Every workstream has a stable `WS-<n>` alias, a scope line, and an owner
- [x] Every outcome cites its workstream and its governing artifact
- [x] Ordering states its rationale
- [x] The horizon is explicit; nothing beyond it is committed
- [x] Current-iteration outcomes match the active iteration plan
