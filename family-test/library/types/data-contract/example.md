---
ddx:
  id: DC-EX-001
  type: data-contract
  methodology: helix
  library_type_version: 1.0.0
  links: []
---

# Stripe Charge Events Data Contract

## Producer
The data-platform team produces `stripe_charge_events` in Snowflake across
bronze, silver, and gold layers. Payments engineering supplies Stripe webhook
events for `charge.succeeded`, `charge.failed`, and `charge.refunded`.

## Consumer
Contracted consumers are `finance-reporting` for daily aggregates,
`fraud-ML` for streaming features, and `customer-success-dashboard` for
interactive account support views.

## Schema Versioning Policy
The contract version is `stripe-charge-events/v1`. Additive nullable fields
may ship as minor changes. Renames, removals, type changes, and semantic
changes require a new major version and 30 days of dual publishing.

## Semantic Field Definitions
`charge_id` is the stable Stripe charge identifier. `event_created` is the
Stripe event timestamp, not warehouse load time. `amount` is integer minor
currency units. `refunded` means Stripe reports a refund against the charge.
`last4` is masked card metadata and must never be joined to full PAN data.

## Freshness SLA
Bronze tables must be fresh within <= 5 min of Stripe delivery. Gold finance
tables must refresh within <= 1h. Fraud streaming outputs target p95 <= 2 min
after bronze arrival.

## Evolution Policy
Data-platform announces proposed schema changes in the contract review channel
and updates compatibility tests before release. Consumers have 10 business
days to certify additive fields and 30 days for major-version migrations.

## Termination Clauses
A consumer can be removed after 60 days of no reads and written owner approval.
Producer support for `v1` can end only after all named consumers migrate or
explicitly waive their dependency.
