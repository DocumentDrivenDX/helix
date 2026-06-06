---
ddx:
  id: DPB-001
  type: data-product-brief
  methodology: helix-data
  library_type_version: 1.0.0
  links:
    - {kind: informs, to: SRC-001}
    - {kind: informs, to: CONS-001}
    - {kind: informs, to: DC-001}
---

# Data Product Brief: Customer Events

## Problem
Analytics, ops, and product teams need a single, trusted stream of Stripe-derived
customer-lifecycle events. Today each team writes ad-hoc Lambda consumers against
the raw webhook, so dashboards disagree on basic counts and PII handling is
inconsistent. We need one curated event stream with documented contracts.

## Consumers
- **Analytics**: hourly Redshift refresh of charge + invoice fact tables.
- **Ops**: near-real-time Slack alerts on disputes and failed charges.
- **Product (Looker)**: daily retention + churn marts.

See `consumer-inventory.md` (CONS-001) for the full read-pattern matrix.

## Data Sources
- Stripe webhook stream (events at https://api.stripe.com/v1/events).
- Backfill API for replay (`/v1/events?created[gte]=...`) used by the
  backfill-plan (BP-001) and the F10 dead-letter replay path.

Profiled in `source-profile-stripe.md` (SRC-001).

## Freshness SLA
- Bronze (raw S3 landing): p99 ≤ 60s from webhook receipt.
- Silver (Glue-curated): p99 ≤ 10min.
- Gold (Redshift facts): p99 ≤ 1h for analytics; ≤ 5min for ops alerts.

## Success Metrics
- Reconciliation drift Stripe→Redshift ≤ 0.01% on a rolling 24h window
  (addresses **F6 — source/sink reconciliation mismatch**).
- Duplicate-event rate at gold ≤ 0 (addresses **F1 — duplicate webhook ID**).
- PII-leak audit: 0 emails written to non-restricted tables in any 30-day
  window (addresses **F4 — PII-bearing field surfaced**).
- Cost: Glue job spend ≤ $400/mo at current 2.4M events/day (addresses
  **F8 — cost overrun**).

## Non-Consumers (out of scope)
- Marketing automation (uses Segment, not this pipeline).
- Finance ledger reconciliation (Stripe's own monthly reports drive that).
- Real-time fraud scoring (latency-sensitive; goes through a separate
  Kinesis-Lambda path).

## Open Questions
- **F2 watermark policy**: how late is "too late" for an event to land in the
  same hourly partition? Tracked in `data-design.md`.
- **F3 schema evolution**: Stripe occasionally adds optional fields without
  notice; do we allow silent passthrough or require explicit contract bump?
  Decided in `data-contract-stripe-events.md`.
