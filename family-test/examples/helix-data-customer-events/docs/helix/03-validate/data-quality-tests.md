---
ddx:
  id: DQT-001
  type: data-quality-tests
  methodology: helix-data
  library_type_version: 1.0.0
  links:
    - {kind: informs, to: IP-001}
    - {kind: informs, to: RB-001}
---

# Data Quality Tests: Customer Events

Executable contracts derived from `data-quality-expectations.md` (DQE-001).
Each test has an `expectation_id` traceable to a DQE-001 row and a
run_frequency. Tests run in CI on a synthetic golden corpus AND in
production against live data.

## Test Inventory

| ID | Name | expectation_id | Run frequency | Fixture |
|---|---|---|---|---|
| T-B01 | bronze_event_id_present | B-01 | every batch | — |
| T-B02 | bronze_event_id_dedup_window | B-02 | every batch | **F1** |
| T-B04 | bronze_event_ts_in_bounds | B-04 | every batch | **F2** |
| T-B06 | bronze_api_version_known | B-06 | every batch | **F3** |
| T-S01 | silver_customer_token_shape | S-01 | every batch | **F4** |
| T-S02 | silver_no_email_canary | S-02 | every batch (BLOCKING) | **F4** |
| T-S03 | silver_payload_matches_typed_projection | S-03 | every batch | **F3** |
| T-S04 | silver_lineage_ref_resolves | S-04 | every batch | **F7** |
| T-S05 | silver_partition_row_count_within_3sigma | S-05 | hourly | **F9** |
| T-S06 | silver_no_hot_key_above_5pct | S-06 | hourly | **F9** |
| T-S07 | silver_dlq_size_under_threshold | S-07 | hourly | **F10** |
| T-G01 | gold_reconciliation_drift_within_001pct | G-01 | hourly | **F6** |
| T-G02 | gold_customer_deletion_propagation_24h | G-02 | daily | **F5** |
| T-G03 | gold_all_rows_have_lineage_ref | G-03 | daily | **F7** |
| T-G06 | gold_schema_fingerprint_matches_contract | G-06 | every load | **F11** |

## Fixtures

CI runs each test against a curated synthetic corpus in
`fixtures/golden-events/`. Each scenario maps to a published F-fixture:

| Golden file | Adversarial scenario | Tests exercised |
|---|---|---|
| `golden-events/F1-duplicate.json` | webhook delivered 3x with same `event.id` | T-B02 must dedup; only 1 silver row written |
| `golden-events/F2-late.json` | event with `event_ts_utc` 6h behind landing | T-B04 must accept; folded into the correct partition |
| `golden-events/F3-additive.json` | producer adds a new optional field | T-B06 warns; T-S03 passes (passthrough) |
| `golden-events/F3-narrowing.json` | producer narrows a type | T-S03 fails; DLQ write; alert |
| `golden-events/F4-email-leak.json` | row with email in `metadata.{}` | T-S02 BLOCKS; DLQ to pii_metadata |
| `golden-events/F6-reconciliation.json` | 1000 events with 7 missing in Redshift | T-G01 fires Sev2 |
| `golden-events/F7-lineage-gap.json` | silver row written without OpenLineage event | T-S04 + T-G03 fail |
| `golden-events/F9-hot-key.json` | 10k rows with one customer_token at 12% | T-S06 fires; salted-join enabled next batch |
| `golden-events/F10-dlq-replay.json` | malformed rows in DLQ; replay after schema fix | T-S07 stays green during bounded replay |
| `golden-events/F11-schema-fingerprint.json` | silver bumps fingerprint; gold expects old | T-G06 aborts load; F11 alert |

These golden files are committed under `fixtures/` alongside the F1-F11
scenario YAMLs (`fixtures/F<n>-<slug>.yml`). When a new failure mode is
discovered in production, the runbook (RB-001) §"capture as golden" step
takes the offending event payload and adds it to the corpus.

## Known Failures (acknowledged drift)

These are accepted gaps with explicit owners and expiry dates:

| Test | Drift | Owner | Expires |
|---|---|---|---|
| T-G01 | Up to 0.005% drift during Stripe-side outages outside our control | data-eng | indefinite (external) |
| T-S05 | Higher-than-3σ variance accepted during marketing campaign weeks (preregistered) | data-eng + marketing | per-campaign |

Anything not in this table is a defect, not drift.
