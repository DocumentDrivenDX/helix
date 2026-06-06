---
ddx:
  id: SRC-EX-001
  type: source-profile
  methodology: helix
  library_type_version: 1.0.0
  links: []
---

# Stripe Webhook Source Profile

## Source System
Stripe webhooks from the payments platform, limited to `charge.succeeded`,
`charge.failed`, and `charge.refunded`. Events are delivered to the
data-platform ingestion endpoint and persisted to Snowflake bronze tables.

## Schema Snapshot
Representative fields: `event_id`, `event_type`, `event_created`,
`charge_id`, `amount`, `currency`, `paid`, `refunded`, `refund_id`,
`failure_code`, `failure_message`, `customer_id`, `customer_email`,
`billing_address`, and card `last4`.

## Volume Estimates
Current volume is ~2M events/day with weekday peaks near 140k events/hour.
Refund events account for ~4% of volume. Expected annual growth is 35% based
on transaction forecasts from finance.

## Freshness Observed
p50 webhook delivery is under 20 sec, p95 is 90 sec, and rare retries can
arrive up to 24h later. Bronze Snowflake load currently lands p95 within
3 min during normal traffic.

## PII Classification
PII fields include `customer_email`, `billing_address`, and `last4`.
`customer_id` is treated as pseudonymous personal data. Full card number and
CVV are not present.

## Producers Contacted
Payments engineering owns the webhook configuration. Data-platform owns the
ingestion endpoint and bronze table. Finance operations confirmed event
coverage for charge settlement reporting.

## Risks And Unknowns
Stripe retries can duplicate `event_id`; dedupe must be idempotent. Partial
refund payloads need validation against finance expectations. Webhook signing
secret rotation procedures are not yet documented for the data endpoint.
