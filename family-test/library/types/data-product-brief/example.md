---
ddx:
  id: DPB-EX-001
  type: data-product-brief
  methodology: helix
  library_type_version: 1.0.0
  links: []
---

# Stripe Charge Events Data Product Brief

## Problem
Finance, fraud, and customer success teams need one governed view of Stripe
charge lifecycle events. Today each team replays webhooks differently, causing
daily revenue mismatches, duplicate refund handling, and inconsistent failure
reason definitions.

## Consumers
- `finance-reporting`: daily revenue, refund, and failure rollups.
- `fraud-ML`: streaming features for charge risk scoring.
- `customer-success-dashboard`: interactive charge history and refund status.

## Data Sources
Stripe webhooks for `charge.succeeded`, `charge.failed`, and
`charge.refunded`. Bronze records land as immutable webhook envelopes with
`event_id`, `charge_id`, `created`, `amount`, `currency`, `customer_email`,
`billing_address`, `last4`, and `failure_code`.

## Freshness SLA
Bronze freshness must be <= 5 min from Stripe delivery. Gold aggregate tables
must be refreshed within <= 1h for finance reporting. Streaming fraud features
target p95 availability within 2 min after bronze arrival.

## Success Metrics
- Daily finance revenue variance against Stripe dashboard is < 0.1%.
- Fraud feature completeness is >= 99.5% for required fields.
- Customer success dashboard p95 query latency is < 2 sec for 90-day history.

## Non Consumers
This product does not serve tax filing, payment authorization, or customer
identity resolution workflows. Raw card data and full PAN values are not
available from this product.

## Open Questions
- Should refund partial amounts be modeled as separate facts or charge state transitions?
- Does customer success need failed charges older than 18 months?
- Which team approves schema changes that affect `failure_code` semantics?
