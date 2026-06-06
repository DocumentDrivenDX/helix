---
ddx:
  id: DD-001
  type: data-design
  methodology: helix-data
  library_type_version: 1.0.0
  links:
    - {kind: informs, to: IP-001}
    - {kind: informs, to: LS-001}
    - {kind: informs, to: DQT-001}
---

# Data Design: Customer Events Pipeline

Concrete schemas, transformations, and per-layer behaviour. Pairs with
`data-architecture.md` (DA-001).

## Bronze Schema (parquet)

```
event_id                string      not null
event_received_ts_utc   timestamp   not null  -- when API GW saw it
raw_payload             string      not null  -- full JSON, including PII
api_version_seen        string      not null
signature_verified      bool        not null
landing_partition_hour  string      partition key
```

PII is present in `raw_payload` by design — bronze is the audit-trail layer.
Access controls are in `governance-classification.md` (GC-001).

## Silver Schema (parquet)

```
event_id                string      not null  -- unique (post-dedup, F1)
event_type              string      not null
event_ts_utc            timestamp   not null  -- source-of-truth (F2 anchor)
customer_token          string      not null  -- sha256, no raw email (F4)
payload_silver          struct      typed projection per event_type (F3)
api_version_seen        string      not null
ingestion_ts_utc        timestamp   not null
lineage_ref             string      not null  -- OpenLineage dataset URN (F7)
silver_partition_hour   string      partition key
event_type              string      sub-partition key
```

### Transformations (Bronze → Silver)

1. **Signature gate**: drop rows where `signature_verified = false` to
   `dlq/signature_failed/`.
2. **Schema fingerprint**: hash the row's `payload_silver` shape;
   compare to the contract's published fingerprint. On mismatch:
   - Additive (new field) → passthrough + W-01 alert (F3, non-breaking).
   - Subtractive/narrowing → DLQ to `dlq/schema_drift/` + S2 alert (F3,
     breaking — the contract was violated).
3. **PII tokenize/drop** (F4):
   - Hash `customer.id` → `customer_token` (sha256 + salt).
   - Drop `customer.email`, `customer.name`, `billing_details.*`.
   - Quarantine row to `dlq/pii_metadata/` if any `metadata.*` value
     matches the PII regex (email, phone, SSN canaries).
4. **Dedup** (F1):
   - Join against the 7-day dedup table on `event_id`.
   - Existing row → drop silently (idempotent retry success).
   - New row → insert into dedup table + write to silver.
5. **Late-arrival check** (F2):
   - `event_ts_utc > now()` → DLQ `future_timestamp/`.
   - `event_ts_utc < now() - 24h` AND not in replay mode → DLQ
     `late_event/` (bounded escape valve in runbook).
   - Otherwise → fold into the appropriate hourly partition (out-of-order
     OK because Redshift gold MERGE handles it).
6. **Lineage emit** (F7):
   - Build the OpenLineage event before the silver write.
   - `inputs=[stripe-webhook:event_id]`, `outputs=[silver:event_type:hour]`.
   - Emit synchronously; failure to emit halts the silver write (lineage
     completeness is a hard contract).

## Gold Schema (Redshift)

### `charge_fact`
```sql
event_id            VARCHAR(255)  NOT NULL,
charge_id           VARCHAR(255)  NOT NULL,
customer_token      VARCHAR(64)   NOT NULL,  -- DISTKEY
event_ts_utc        TIMESTAMP     NOT NULL,  -- SORTKEY
event_type          VARCHAR(50)   NOT NULL,  -- charge.{succeeded,failed,refunded,dispute.created}
amount_cents        BIGINT,
currency            CHAR(3),
livemode            BOOLEAN       NOT NULL,
api_version_seen    VARCHAR(20)   NOT NULL,
lineage_ref         VARCHAR(512)  NOT NULL,
loaded_ts_utc       TIMESTAMP     NOT NULL,
PRIMARY KEY (event_id)
```

### `invoice_fact` (analogous structure)

### `customer_dim` (slowly-changing-type-2)
- `customer_token` PK; `effective_from` / `effective_to` for SCD2.
- **F5 redaction path**: `customer.deleted` events trigger a tombstone row
  with `effective_to=now()` AND a downstream prune job that removes prior
  rows after the audit window.

### Silver → Gold load
- Redshift `COPY` from silver parquet hourly.
- MERGE on `event_id` PK so late arrivals (F2) upsert idempotently.
- Schema fingerprint check at MERGE time (G-06): if silver's published
  schema version doesn't match what gold expects, the load aborts and an
  **F11** alert fires.

## Storage Layout Summary

| Layer | Store | Format | Partitioning | Retention |
|---|---|---|---|---|
| Bronze | S3 | parquet | hour | 90d |
| Silver | S3 | parquet | hour × event_type | 13mo |
| Gold | Redshift | columnar | distkey customer_token, sortkey event_ts | 7y |
| DLQ | S3 | parquet | reason × hour | 30d |

## Skew Detection Internals (F9)
- A Spark accumulator counts per-`customer_token` rows in the silver batch.
- After the batch, the top 10 tokens are emitted to CloudWatch.
- If any token's share > 5%, S-06 fires and the next batch runs in
  salted-join mode (configurable via Glue job parameter).
- The skew incident is logged with the token (hashed) so product can chase
  the upstream cause.
