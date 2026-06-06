---
ddx:
  id: IP-001
  type: implementation-plan
  methodology: helix-data
  library_type_version: 1.0.0
  links:
    - {kind: informs, to: LS-001}
    - {kind: informs, to: RB-001}
---

# Implementation Plan: Customer Events Pipeline

Sequenced build order with explicit checkpoints. Each milestone gates on
the named tests + reconciliation rules being green.

## Milestone M1 — Ingest backbone (week 1)

**Scope**: API Gateway endpoint, Lambda signature verification, Firehose
to S3 bronze.

**Deliverables**
- `infra/api-gw.tf` — gateway + Lambda + WAF.
- `infra/firehose.tf` — Firehose stream + bronze bucket.
- `apps/sig-verify-lambda/` — Stripe signature check.

**Exit checks**
- 10k synthetic events flow end-to-end to bronze in < 1min.
- T-B01 (event_id present) green on synthetic corpus.
- Bronze partition layout matches DA-001.

## Milestone M2 — Silver curation (weeks 2–3)

**Scope**: Glue job implementing the 6 transformation steps from DD-001.

**Deliverables**
- `apps/glue-silver/job.py` — PySpark transformation.
- `apps/glue-silver/dedup_table.py` — 7-day dedup state.
- `apps/glue-silver/schema_fingerprint.py` — schema-drift check.
- `apps/glue-silver/pii_redact.py` — F4 tokenize/drop logic.
- `infra/glue-silver.tf` — Glue job + IAM + bookmark.

**Exit checks**
- All silver expectations T-S01..T-S07 green on the golden corpus.
- F1 fixture: 3 duplicate webhooks → 1 silver row.
- F4 fixture: row with email canary → DLQ + S-02 BLOCKING fires.
- F9 fixture: hot-key detection emits the salted-join flag.

## Milestone M3 — Gold load + Redshift schema (week 4)

**Scope**: Redshift schema, hourly COPY job, MERGE for late arrivals.

**Deliverables**
- `infra/redshift/schemas.sql` — `charge_fact`, `invoice_fact`,
  `customer_dim`.
- `apps/redshift-loader/load.py` — COPY + MERGE driver.
- `apps/redshift-loader/fingerprint_check.py` — F11 schema gate.

**Exit checks**
- T-G01 reconciliation green for 7 consecutive days on staging.
- T-G06 fingerprint check rejects a deliberately-mismatched silver file.
- F2 fixture: a 6h-late event MERGEs into the correct historical partition.

## Milestone M4 — Lineage + governance + monitoring (week 5)

**Scope**: OpenLineage emission, PII audit jobs, F5 deletion-propagation
job, monitoring dashboards.

**Deliverables**
- `apps/glue-silver/lineage_emit.py` — wired into the Glue job per LS-001.
- `apps/redaction-job/` — daily customer-deletion propagation.
- `apps/pii-canary/` — weekly email-canary scan.
- `infra/monitoring/` — CloudWatch dashboards + alerts per MS-001.

**Exit checks**
- 100% of gold rows have resolvable `lineage_ref` (T-G03 + R-06 green).
- F5 fixture: `customer.deleted` event triggers prune; 0 rows remain in
  silver/gold within 24h.
- F7 fixture: lineage gap is detected and alerts.
- All MS-001 alerts wired and exercised in staging.

## Milestone M5 — Backfill + DLQ replay tooling (week 6)

**Scope**: backfill driver, bounded DLQ replay tool.

**Deliverables**
- `apps/backfill/historic.py` — implements BP-001 Scenario 1.
- `apps/backfill/dlq-replay.py` — implements BP-001 Scenario 2; bounded
  by reason code + time window.

**Exit checks**
- Synthetic 7-day backfill runs to completion on staging.
- F10 fixture: DLQ replay after a simulated schema fix yields 100%
  reprocessing with 0 duplicates in silver.

## Milestone M6 — Production rollout (week 7)

**Scope**: cutover from existing ad-hoc consumers to the curated pipeline.

**Deliverables**
- `runbook.md` (RB-001) reviewed + sign-off by on-call.
- Consumer-migration plan executed per CONS-001 hard-consumer ACK
  procedure.
- Deprecation notice for the Finance consumer published (DN-001).

**Exit checks**
- 14 consecutive days of all reconciliation rules R-01..R-06 green in
  production.
- All 11 adversarial fixtures F1..F11 have a documented response in
  RB-001.
- F11 fixture: contract-version mismatch alert successfully exercised
  end-to-end against a deprecated-consumer rehearsal.

## Cross-cutting

- All milestones ship with corresponding `data-quality-tests.md` (DQT-001)
  updates; the test corpus grows in lockstep with the code.
- All milestones ship with corresponding lineage URNs (LS-001).
- No milestone closes until its exit checks AND the prior milestones'
  reconciliation rules remain green for 24h.
