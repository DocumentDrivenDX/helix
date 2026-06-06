---
ddx:
  id: EP-001
  type: evolution-plan
  methodology: helix-data
  library_type_version: 1.0.0
  links:
    - {kind: informs, to: DN-001}
    - {kind: informs, to: IB-001}
---

# Evolution Plan: Customer Events Schema v2

Worked example of a breaking-change rollout. Versions:
- **v1.0** — current production schema (per DC-001).
- **v2.0** — proposed: rename `customer_token` → `subject_token` (to
  cover the new merchant-events stream that will reuse this pipeline);
  add `event_outcome` enum to `charge_*` events; drop the deprecated
  `legacy_amount_cents_int` Redshift column.

This is illustrative of the workflow; whether v2 actually ships is
governed by product priority.

## Breaking Changes

| Change | Affected layer | Impact |
|---|---|---|
| Rename `customer_token` → `subject_token` | silver, gold | F11 risk: deprecated Finance consumer hard-codes the old name |
| Add `event_outcome` enum to charge_fact | gold | additive — non-breaking for tolerant consumers |
| Drop `legacy_amount_cents_int` from charge_fact | gold | breaking for any consumer still reading it |

(The middle change is additive and listed for completeness; only the
first and third are breaking.)

## Migration Window
- **Phase 1 (T+0 → T+14d)**: ship v2 silver alongside v1 silver (parallel
  write). v1 gold continues to receive v1 silver. v2 gold is built in a
  separate Redshift schema (`customer_events_v2`) and validated.
- **Phase 2 (T+14d → T+45d)**: consumers migrate to `customer_events_v2`.
  Hard consumers receive direct outreach; soft consumers see the
  changelog. The deprecated Finance consumer is the F11 study; it stays
  on v1 until the DN-001 sunset (2026-07-01).
- **Phase 3 (T+45d → T+60d)**: v1 silver write is disabled. v1 gold tables
  remain readable but frozen.
- **Phase 4 (T+60d)**: v1 gold tables dropped. Storage reclaimed.

## Consumer Notification Plan

### Hard consumers (CONS-001 Analytics, Ops)
- T-14d: written notice with v2 schema diff + migration guide.
- T-7d: 1:1 meeting with each consumer team.
- T-0 (Phase 1 start): channel announcement.
- T+45d: deprecation warning.
- T+60d: cutoff confirmation.
- ACK required before Phase 3.

### Soft consumer (CONS-001 Product Looker)
- T-14d: channel announcement.
- T+45d: deprecation warning.
- T+60d: cutoff confirmation.
- No ACK required, but a no-response is logged.

### Deprecated consumer (CONS-001 Finance, DN-001)
- This is the F11 worst-case rehearsal: Finance hard-codes the v1
  column names with no version check. Strategy: keep v1 gold tables
  alive AND keep v1 silver→gold loads running for the
  `customer_events_v1.charge_fact` view ONLY through the Finance sunset
  date (2026-07-01). After that, both v1 silver AND the Finance consumer
  are decommissioned in lockstep.
- Without this carve-out, ship-day for v2 = silent corruption day for
  Finance. The plan exists specifically to prevent that.

## Rollback Plan

- **Up to Phase 2 end**: re-enable v1-only write; consumers fall back.
  No data loss (we kept the parallel writes).
- **Phase 3 onwards**: re-creating v1 from v2 requires a backfill from
  bronze, which is bounded by the 90-day bronze retention. This is the
  hard rollback floor; after Phase 3, rollback is expensive.
- **Trigger conditions**: any of {
  R-01 drift > 0.1% sustained 24h after a phase advance;
  Sev1 incident attributable to v2;
  > 1 hard consumer fails to migrate by T+45d
  } triggers automatic phase-rollback.

## Success Criteria

- Phase 1 exits when both v1 and v2 reconciliation rules (R-01..R-06)
  are green for 7 consecutive days.
- Phase 2 exits when all hard consumers have ACKed AND queried v2 in
  production for ≥ 24h.
- Phase 3 exits when 7 consecutive days of v2-only operation are green
  AND the deprecated-consumer carve-out is confirmed isolated.
- Phase 4 exits when v1 storage is dropped and reclaimed.

## F-fixture coverage rehearsed pre-migration

Before Phase 1 ships, all 11 fixtures (F1..F11) are re-exercised against
v2 in the staging environment. The new schema is allowed to FAIL
fixtures we explicitly retire (e.g. `legacy_amount_cents_int`), but no
in-scope fixture may regress. **F3 (schema drift)** and **F11
(consumer-side mismatch)** get extra adversarial runs because they are
this evolution's primary risk vectors.
