---
ddx:
  id: CONS-EX-001
  type: consumer-inventory
  methodology: helix
  library_type_version: 1.0.0
  links: []
---

# Fraud ML Consumer Inventory For Stripe Charge Events

## Consumer
`fraud-ML`, owned by the risk science team, consumes charge events from the
Snowflake silver stream and feature-export topic maintained by data-platform.

## Purpose
The consumer builds near-real-time risk features from `charge_id`, `amount`,
`currency`, `failure_code`, `customer_email` hash, billing country, and card
`last4` token attributes. Features support charge review prioritization and
post-authorization fraud scoring.

## Read Pattern
Streaming reads every 30 sec from silver change capture plus hourly backfill
queries against Snowflake for late retries and corrected refund states.
Peak read volume is ~80k charge feature records/hour.

## Freshness Required
Required freshness is p95 <= 2 min after bronze arrival for streaming feature
generation. Late-arriving webhook retries must be reflected in the next hourly
backfill batch.

## Contract Version
Current expected contract is `stripe-charge-events/v1`. Required fields are
`charge_id`, `event_type`, `event_created`, `amount`, `currency`,
`customer_id`, `failure_code`, `refunded`, and masked `last4`.

## Dependency Strength
Strong. Fraud model serving remains online without the feed, but detection
quality degrades within 15 min and manual review queues lose charge failure
context.
