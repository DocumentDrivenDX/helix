---
ddx:
  id: DA-001
  type: data-architecture
  methodology: helix-data
  library_type_version: 1.0.0
  links:
    - {kind: informs, to: DD-001}
    - {kind: informs, to: ADR-001}
    - {kind: informs, to: MS-001}
    - {kind: informs, to: MD-001}
---

# Data Architecture: Customer Events Pipeline

## Overview
A medallion (Bronze / Silver / Gold) topology on AWS, sized for ~2.4M
events/day with bursts to 1.8M events/hour.

```
Stripe webhook
   │
   ▼
API Gateway ── Lambda (validate + sign-check)
   │
   ▼
Kinesis Firehose ── S3 BRONZE (parquet, hourly partition by event_ts_utc)
   │
   ▼
Glue ETL  (every 10 min trigger)
   │   ├─ schema-fingerprint check (F3)
   │   ├─ PII tokenize/drop      (F4)
   │   ├─ dedup on event_id      (F1)
   │   └─ DLQ on reject          (F10)
   ▼
S3 SILVER (parquet, hourly partition by event_ts_utc, sub-partition by event_type)
   │
   ▼
Glue job → Redshift COPY (hourly)
   │
   ▼
Redshift GOLD (charge_fact, invoice_fact, customer_dim)
   │
   ├─ Analytics dashboards (BI tool, 1h refresh)
   ├─ Ops Slack alerts (Lambda subscriber, ≤5min)
   └─ Looker (overnight rebuild)
```

## Topology Choices

### Bronze landing
- Kinesis Firehose buffers 5min OR 5MB → S3 parquet.
- Choice rationale: Firehose handles burst absorption (F9 hot-key
  protection at ingress); cheaper than Kinesis Data Streams at our scale.

### Silver curation
- AWS Glue (Spark) over the bronze partitions.
- 10-minute trigger to meet the silver freshness SLA (DC-001 says ≤10min p99).
- Bookmark on `ingestion_ts_utc` so we never re-read processed bronze
  partitions (the **F10** replay path bypasses the bookmark deliberately).
- Choice rationale: detailed in **`adr/ADR-001-glue-vs-spark.md`** — Glue
  vs. self-managed EMR Spark.

### Gold mart
- Redshift COPY from silver parquet hourly.
- Late-arriving events (**F2**) are MERGE-upserted into the fact tables;
  partitions are NOT immutable.

## Partitioning Strategy

- **Bronze**: `event_ts_utc / year=YYYY / month=MM / day=DD / hour=HH /`.
  Hourly granularity chosen because:
  - hourly aligns with the silver job cadence.
  - daily was rejected because a hot-key day (**F9**) would re-process the
    entire day on partial failure.
- **Silver**: `event_ts_utc/hour=HH/event_type=X/`. Sub-partition on
  `event_type` because the 12 in-scope types have a ~1000:1 volume ratio
  (`charge.succeeded` vs. `customer.deleted`); without sub-partition,
  small queries scan the same files as large queries (**F8** cost driver).
- **Gold (Redshift)**: distkey on `customer_token` (most common join key);
  sortkey on `event_ts_utc` (time-range scans dominate).

## Idempotency
- Dedup on `event_id` at silver. The dedup window is **7 days** (Stripe's
  retry policy ceiling is 3 days; 7 gives safety margin).
- The dedup state is a small Glue-managed table keyed by `event_id` with a
  TTL prune job nightly. This is the **F1** primary defense.
- Bronze stores duplicates by design (they're the raw stream); silver
  dedup is the first idempotent layer.

## Late-Arrival Handling (F2)
- **Watermark**: silver job processes the rolling 24h window, not just the
  most recent 10min. Late events up to 24h are folded in automatically.
- Events older than 24h trigger the **late-event replay path**
  (`runbook.md` §"late-event replay"), which is the bounded escape valve
  for the Stripe 3-day retry tail.
- Events with `event_ts_utc > now()` (future-dated by source clock skew)
  are quarantined to DLQ with reason `future_timestamp`.

## Hot-Key / Skew (F9)
- Detection: silver expectation S-06 flags any hourly partition where a
  single `customer_token` exceeds 5% of rows.
- Mitigation: a **salted-key Spark optimization** is wired into the Glue
  job for joins with the customer dimension; salting is enabled when S-06
  fires and disabled when it clears.
- Long-term fix: customers driving > 5% are flagged for product review
  (often an integration bug on the customer's side).

## Cost Posture (F8)
- Baseline Glue spend modeled at ~$280/mo on 2.4M events/day.
- Budget envelope: **$400/mo** (SLA target in DPB-001). Exceedance triggers
  the F8 review gate documented in `monitoring-setup.md` (MS-001) and
  `metrics-dashboard.md` (MD-001).
- The two known cost-amplifiers are partition explosion (mitigated above)
  and unbounded `LIKE '%...%'` scans from analytics consumers (governed by
  Redshift workload management rules).

## Dead-Letter Queue (F10)
- All bronze + silver rejects land in `s3://.../dlq/<reason>/...`.
- Reason-coded subpaths: `dedup_key_missing`, `schema_drift`,
  `future_timestamp`, `pii_metadata`, `signature_failed`.
- Bounded replay procedure: see `backfill-plan.md` (BP-001) §"DLQ replay
  after schema fix". Replay is NEVER unconditional; it requires:
  1. Root-cause documented.
  2. Schema/code fix shipped.
  3. Replay scope explicitly limited to the affected reason-code subpath.

## Lineage (F7)
- OpenLineage events emitted from the Glue job at silver and gold writes.
- Upstream anchor: a synthetic `stripe-webhook` namespace with
  `dataset=event_id` (because Stripe doesn't emit lineage; we have to
  manufacture the upstream node). See `lineage-spec.md` (LS-001) for the
  full emitter strategy.
