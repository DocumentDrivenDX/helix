# Customer Events Reconciliation Suite

## reconciliation_rules
- REC-001 amount parity: Stripe balance transaction export `gross_usd` equals `gold.customer_revenue_daily.gross_usd` by event_date, tolerance applied after refunds.
- REC-002 event count parity: Stripe events API count equals bronze distinct `event_id` count by hour; F1 duplicate webhook must not inflate sink count.
- REC-003 late-arrival correction: F2 events update the original event_date partition within 72 hours.
- REC-004 replay parity: F10 dead-letter replay count equals silver accepted replay rows for `invoice.paid` and `charge.refunded`.

## alert_thresholds
- Severity P1: amount delta greater than $25 or 0.05% for a finance-close date.
- Severity P2: event count delta greater than 10 events per hour for non-close dates.
- Severity P2: freshness lag greater than 45 minutes for ops dashboard stream.

## response_runbook_ref
Runbook: `docs/runbooks/customer-events-reconciliation.md`; primary owner: data-platform on-call; consumer contacts: finance-recon, marketing-attribution, ops-dashboard.
