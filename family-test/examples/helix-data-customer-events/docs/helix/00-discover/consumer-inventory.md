---
ddx:
  id: CONS-001
  type: consumer-inventory
  methodology: helix-data
  library_type_version: 1.0.0
  links:
    - {kind: informs, to: DC-001}
    - {kind: informs, to: EP-001}
---

# Consumer Inventory: Customer Events

## Consumer 1 — Analytics (Redshift dashboards)
- **Purpose**: revenue, charge volume, dispute rate dashboards.
- **Read pattern**: batch (hourly Redshift refresh).
- **Freshness required**: ≤ 1h end-to-end.
- **Contract version**: v1.0.
- **Dependency strength**: hard. Outage > 4h triggers Sev2.
- **Schema coupling**: tolerates additive `charge.*` fields; breaks on type
  narrowing (relevant to **F3** evolution policy).

## Consumer 2 — Ops Slack alerts (`#payments-ops`)
- **Purpose**: real-time alerts on dispute_created, payment_failed.
- **Read pattern**: streaming (Glue trigger → Lambda fanout).
- **Freshness required**: ≤ 5min p99.
- **Contract version**: v1.0.
- **Dependency strength**: hard. Latency > 15min triggers Sev1 (financial
  exposure window).
- **Schema coupling**: only consumes 4 event types; immune to most schema
  drift but acutely sensitive to `type` enum changes.

## Consumer 3 — Product analytics (Looker)
- **Purpose**: daily retention, churn, LTV marts.
- **Read pattern**: batch (overnight gold rebuild).
- **Freshness required**: ≤ 24h.
- **Contract version**: v1.0.
- **Dependency strength**: soft. Tolerant of 24h outage; Sev3 only.
- **Schema coupling**: joins on `customer.id`; impacted by
  **F5 — right-to-be-forgotten deletes** (customer rows disappear).

## Consumer 4 — Finance reconciliation (DEPRECATED 2026-04)
- **Purpose**: was used for daily revenue reconciliation against Stripe's
  monthly report.
- **Read pattern**: batch (daily SQL).
- **Freshness required**: ≤ 48h.
- **Contract version**: v0.9 (frozen).
- **Dependency strength**: hard until 2026-07-01, then sunset.
- **Schema coupling**: see `06-evolve/deprecation-notice.md` (DN-001).
  Active until decommission; covered by **F11 — consumer-side breaking
  schema mismatch** risk if we ship v2 before sunset completes.

## Cross-cutting notes
- All 4 consumers receive notification via `#data-platform-changelog` when
  contract revisions land. The notification chain is the F11 mitigation.
- Hard consumers (1, 2) must ACK in writing before any breaking change ships.
  Soft consumer (3) gets advisory notice with a 14-day window.
- The deprecated consumer (4) is the F11 worst-case study: it was hard-coded
  to schema v0.9 with no version check, so any breaking change pre-sunset
  would surface as a silent gold-mart corruption.
