---
ddx:
  id: DQ-EX-001
  type: data-quality-expectations
  methodology: helix
  library_type_version: 1.0.0
  links: []
---

# Stripe Charge Events Data Quality Expectations

## Bronze Expectations
Bronze must accept only signed Stripe webhook payloads for `charge.succeeded`,
`charge.failed`, and `charge.refunded`. `event_id`, `event_type`,
`event_created`, `charge_id`, and raw payload are required. Duplicate
`event_id` records are quarantined after the first accepted load.

## Silver Expectations
Silver must deduplicate by `event_id`, normalize `amount` as integer minor
currency units, and require `charge_id`, `currency`, and `event_created`.
PII fields `customer_email`, `billing_address`, and `last4` must be classified
and masked in non-privileged views.

## Gold Expectations
Gold finance tables must reconcile daily gross charge amount, failed charge
count, and refunded amount to Stripe dashboard exports with variance < 0.1%.
Customer success views must expose only masked `last4` and must answer p95
queries under 2 sec for 90-day account history.

## Escalation When Failed
Freshness failures above 5 min for bronze page data-platform during business
hours and open an incident after 15 min. Gold SLA misses above 1h notify
finance-reporting. Fraud feature completeness below 99.5% notifies risk
science and data-platform.

## Override Policy
Only the data-platform on-call can override blocking checks, and each override
requires an incident or change ticket. Overrides expire after 24h and must
state the affected layer, fields, consumers, and planned backfill.
