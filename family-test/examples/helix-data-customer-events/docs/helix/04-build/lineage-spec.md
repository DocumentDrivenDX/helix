---
ddx:
  id: LS-001
  type: lineage-spec
  methodology: helix-data
  library_type_version: 1.0.0
  links:
    - {kind: informs, to: RB-001}
    - {kind: informs, to: MS-001}
---

# Lineage Spec: Customer Events Pipeline

OpenLineage emission strategy. F7 — lineage gap — is the failure mode this
artifact prevents.

## Emitter Strategy

**OpenLineage** is the chosen protocol. Justification:
- Vendor-neutral (OL is in the Linux Foundation).
- Native Spark integration ships with Glue 4.0.
- The org's existing DataHub backend ingests OL events.

## Nodes to Emit

### Upstream synthetic node — `stripe-webhook`
- **Namespace**: `stripe-webhook`
- **Dataset**: `events` (singular; the whole webhook stream is one
  dataset).
- **Why synthetic**: Stripe does not emit OpenLineage. We manufacture
  this node so the lineage graph has an upstream anchor; without it,
  the pipeline would appear to be a source-less producer (F7 root
  cause).
- **Per-event detail**: `event_id` is recorded in `inputFacets.eventId`
  on the silver-write event so individual events are traceable.

### Bronze node — `s3.bronze.customer_events`
- **Namespace**: `s3://customer-events-bronze`
- **Dataset**: `customer_events`
- Emitted by the Firehose pipeline via a sidecar Lambda (Firehose
  itself doesn't emit OL natively).

### Silver nodes — one per `event_type`
- **Namespace**: `s3://customer-events-silver`
- **Dataset**: `customer_events.<event_type>` (e.g.
  `customer_events.charge_succeeded`).
- Emitted by the Glue silver job.

### Gold nodes — Redshift fact + dim tables
- **Namespace**: `redshift://customer-events-prod`
- **Dataset**: `customer_events.<table_name>`.
- Emitted by the Redshift loader job.

## Consumer of Lineage

**DataHub** (self-hosted). The OL events are POSTed to the DataHub
ingestion endpoint via the OpenLineage backend connector. From there:
- Lineage graph is rendered in the DataHub UI.
- Search by `event_id` traces a single event through bronze → silver →
  gold.
- Search by `customer_token` shows all gold tables that hold rows for a
  given customer (used during the F5 redaction-propagation audit).

## Lineage Emit Failure Behaviour (F7 firewall)

OpenLineage emit is **synchronous and blocking** at silver and gold
writes. If the emit fails:
- The data write is aborted.
- The row(s) are routed to a special DLQ subpath
  `dlq/lineage_emit_failed/`.
- An alert fires immediately.

This is intentional: a silver row WITHOUT a lineage event is a worse
outcome than the row not being written at all, because downstream
consumers cannot trust their lineage graph. R-06 reconciliation enforces
this from the other side.

## Per-Event Detail Level

| Layer | Per-event lineage? | Per-batch lineage? |
|---|---|---|
| Bronze | aggregate facet (count, time range) | yes — every Firehose flush |
| Silver | yes — `event_id` recorded in facets | yes — every Glue batch |
| Gold | yes — `event_id` recorded in COPY metadata | yes — every COPY |

This granularity is required for F5 (deletion-propagation audit needs
per-event traceability) and F7 (gap detection needs per-event coverage,
not just per-batch).

## What is Explicitly NOT Emitted

- The Stripe API call by upstream consumer-facing applications (out of
  scope — that's the producer's lineage; we don't own it).
- Lambda invocation lineage for the signature-verify Lambda (handled by
  CloudWatch/X-Ray, not OL).
- Ad-hoc analyst queries against gold (handled by Redshift audit logs,
  not OL).
