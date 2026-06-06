---
ddx:
  id: DC-001
  type: data-contract
  methodology: helix-data
  library_type_version: 1.0.0
  links:
    - {kind: informs, to: DQE-001}
    - {kind: informs, to: DQT-001}
    - {kind: informs, to: EP-001}
---

# Data Contract: Stripe Events → Curated Customer Events

## Producer
Stripe (external SaaS). No reverse-contract leverage; the contract is
**consumer-side enforced** at the bronze→silver boundary.

## Consumers
All qualified consumers from CONS-001:
- Analytics (Redshift dashboards) — hard, v1.0
- Ops Slack alerts — hard, v1.0
- Product Looker — soft, v1.0
- Finance reconciliation — DEPRECATED, frozen at v0.9

## Schema Versioning Policy
- Curated schema is **independent of Stripe's `api_version`**.
- Additive fields at the source → silent passthrough into bronze; surfaced
  as schema-drift alerts at silver if not in the contract (this is the
  enforcement seam for **F3 — schema-version drift**).
- Field-type narrowing or removal at the source → silver rejects the row to
  DLQ; alert fires; pipeline does **not** silently lose data (F3 mitigation).
- Curated breaking changes require:
  1. ADR or `evolution-plan.md` (EP-001 form).
  2. Hard-consumer ACK per CONS-001.
  3. 14-day advisory window for soft consumers.
  4. Updated `data-quality-tests.md` (DQT-001) covering the new shape.

## Semantic Field Definitions
| Field | Semantic | Required? |
|---|---|---|
| `event_id` | `event.id` from Stripe; dedup key | yes (F1 dedup pivot) |
| `event_type` | normalised, snake_cased | yes |
| `event_ts_utc` | `event.created` converted to UTC ISO-8601 | yes (F2 watermark anchor) |
| `customer_token` | sha256(`customer.id` + salt); never raw email | yes (F4 PII control) |
| `payload_silver` | typed, projected per `event_type` | yes |
| `api_version_seen` | passthrough of source `api_version` | yes (F3 audit trail) |
| `ingestion_ts_utc` | bronze landing time | yes |
| `lineage_ref` | `event.id` + source-id; emitted to OpenLineage | yes (F7 anchor) |

## Freshness SLA
Per DPB-001:
- bronze p99 ≤ 60s
- silver p99 ≤ 10min
- gold p99 ≤ 1h (analytics), ≤ 5min (ops)

SLA breach surfaces via monitoring-setup (MS-001) and is wired into the
runbook (RB-001) **F2** and **F6** response paths.

## Evolution Policy (breaking / non-breaking surface)
- **Non-breaking**: new optional fields, new event_type enum values, new
  consumers added. No version bump.
- **Breaking**: any required field added/removed, type narrowed, semantic
  changed, event_type renamed, dedup-key altered. Bumps curated schema
  major version; triggers full EP-001 evolution-plan workflow.
- The **F3 fixture** rehearses both shapes: producer adds optional field
  (non-breaking, must passthrough); producer narrows existing type
  (breaking, must DLQ + alert).
- The **F11 fixture** rehearses what happens when a deprecated consumer is
  still hard-coded to v0.9 at the moment we ship v2.

## Termination Clauses
- Either side may terminate with 90 days' written notice.
- Stripe-side termination is hypothetical (vendor switch); 90 days is what
  we'd need to swap to a different processor.
- Consumer-side termination: tracked via `deprecation-notice.md` (DN-001).
  The Finance consumer is the live example — formally deprecated 2026-04,
  sunset 2026-07-01.
