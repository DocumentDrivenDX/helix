---
ddx:
  id: SRC-001
  type: source-profile
  methodology: helix-data
  library_type_version: 1.0.0
  links:
    - {kind: informs, to: DC-001}
    - {kind: informs, to: GC-001}
---

# Source Profile: Stripe Webhook Stream

## Source System
- Stripe webhooks delivered to `https://api.example.com/hooks/stripe`.
- Delivery: HTTP POST, JSON body, signed with `Stripe-Signature`.
- Retries on non-2xx: Stripe retries with exponential backoff up to 3 days.
  This is the root cause of **F1 — duplicate webhook ID** (we WILL see the
  same `event.id` twice; idempotency is a hard requirement, not an
  optimization).

## Schema Snapshot
Captured 2026-05-28 from `stripe-node@14.0` typings + 14 days of live samples.

| Field | Type | Cardinality | Notes |
|---|---|---|---|
| `id` | string | unique per delivery attempt | dedup key for F1 |
| `type` | enum(186) | 186 known event types | only 12 are in scope |
| `created` | int (unix) | dense | source-of-truth timestamp for F2 |
| `data.object` | object | varies by `type` | nested, evolving |
| `livemode` | bool | binary | gates routing |
| `api_version` | string | 4 distinct values seen | informs F3 schema drift |
| `request.id` | string \| null | nullable | breaks lineage tie if dropped (F7) |
| `data.object.customer.email` | string \| null | **PII** | F4 driver |

In-scope event types: `charge.{succeeded,failed,refunded,dispute.created}`,
`invoice.{created,finalized,paid,payment_failed}`, `customer.{created,updated,deleted}`.

## Volume Estimates
- Steady-state: ~2.4M events/day (~28/sec average; bursty to 800/sec around
  promo events).
- 7-day p99 hourly volume: 320k events/hour.
- Peak observed: 1.8M events/hour during 2026-04-12 promo (relevant to
  partition-skew analysis — see **F9**).

## Freshness Observed
- p50 webhook delivery latency: 0.4s from event creation.
- p99: 6.2s.
- Long tail: Stripe's 3-day retry policy means a small fraction of events
  arrive up to 72h late (addresses **F2 — late event arrival**).

## PII Classification
- `data.object.customer.email`: **restricted** — must be tokenized before
  reaching silver.
- `data.object.customer.name`: **restricted**.
- `data.object.billing_details.address.*`: **restricted**.
- `data.object.metadata.*`: **untrusted** — customer-supplied; treat as
  potentially PII-bearing (F4 driver).
- Everything else: **internal** unless overridden in
  `governance-classification.md` (GC-001).

## Producers Contacted
- Stripe is an external SaaS; no producer-side contract negotiation possible.
  Schema changes arrive via the `api_version` field with no proactive notice
  (the root of **F3 — schema-version drift**). Our only lever is consumer-side
  detection + alerting (handled in monitoring-setup and data-quality-tests).

## Risks and Unknowns
- **F3**: Stripe's "additive changes are non-breaking" promise has been
  violated twice in 2025 (type narrowing on `data.object.amount` for some
  invoice events). Treat as: trust but verify.
- **F4**: `metadata` is a freeform map; customers occasionally embed PII.
  Classification policy must default to restricted for unknown keys.
- **F7**: Stripe does not emit OpenLineage. Lineage anchoring at the
  pipeline edge must reference `event.id` as the canonical upstream node.
- **F8**: webhook bursts can drive Glue auto-scaling spend > 5x baseline if
  partitioning is wrong. See `data-architecture.md`.
