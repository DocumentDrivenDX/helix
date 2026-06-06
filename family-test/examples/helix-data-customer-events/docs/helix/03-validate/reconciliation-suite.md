---
ddx:
  id: RS-001
  type: reconciliation-suite
  methodology: helix-data
  library_type_version: 1.0.0
  links:
    - {kind: informs, to: MS-001}
    - {kind: informs, to: RB-001}
---

# Reconciliation Suite: Customer Events

Source ↔ sink invariants that catch silent data loss or duplication.
This is the F6 firewall — the reason a customer can trust the gold
marts even when individual layers fail.

## Reconciliation Rules

### R-01 — Source → Bronze
- **Rule**: `count(stripe.events.where(created BETWEEN t-2h AND t-1h)) ==
  count(bronze.where(event_received_ts_utc BETWEEN t-2h+10s AND t-1h+10s))`
  (10s skew = signature verification + network).
- **Cadence**: hourly.
- **Tolerance**: ≤ 5 events absolute OR ≤ 0.001%, whichever larger.
  Stripe's events API is itself slightly eventually-consistent.
- **Alert**: Sev2 on breach.
- **Fixture**: **F6**.

### R-02 — Bronze → Silver
- **Rule**: `count(distinct event_id in bronze[hour=H]) ==
  count(silver[hour=H]) + count(dlq[reason in (signature_failed,
  schema_drift, pii_metadata, future_timestamp, late_event)][hour=H])`.
  Every bronze row must reach silver OR be in DLQ; no silent drops.
- **Cadence**: hourly.
- **Tolerance**: 0 (mass-conservation).
- **Alert**: Sev1 on breach (data loss class).

### R-03 — Silver → Gold
- **Rule**: `count(silver[hour=H]) == count(gold.{charge,invoice}_fact
  WHERE event_ts_utc.hour = H AND loaded_ts_utc < H+2h)`.
  The 2h grace window covers the COPY cadence + retry.
- **Cadence**: hourly after H+2h.
- **Tolerance**: 0 after grace window.
- **Alert**: Sev1 on breach.

### R-04 — Gold → Source (round-trip)
- **Rule**: random sample of 100 `event_id`s from gold each day; query
  Stripe events API for each; assert presence + matching `created` ts.
- **Cadence**: daily, off-peak.
- **Tolerance**: 0 missing.
- **Alert**: Sev2 on breach (likely a serious schema/transformation bug;
  but only sampling so could be statistical noise — investigate before
  paging).
- **Why this exists**: it's the only check that's resilient to a bug in
  R-01/R-02/R-03 themselves (those could all be lying in the same
  direction; R-04 is independently sourced).

### R-05 — Customer Deletion Propagation (F5)
- **Rule**: for every `customer.deleted` event in the last 30 days, no
  surviving rows in silver or gold for that `customer_token` after
  T+24h.
- **Cadence**: daily.
- **Tolerance**: 0.
- **Alert**: Sev1 on breach (GDPR exposure).
- **Recovery**: trigger redaction job for the missed `customer_token`;
  log to `audit_redaction`.

### R-06 — Lineage Completeness (F7)
- **Rule**: 100% of gold rows have a non-null `lineage_ref` that
  resolves to an OpenLineage event in DataHub.
- **Cadence**: daily.
- **Tolerance**: 0 missing.
- **Alert**: Sev2 on breach.

## Alert Thresholds

| Rule | Sev1 trigger | Sev2 trigger | Sev3 trigger |
|---|---|---|---|
| R-01 | — | drift > 0.001% for 2 consecutive hours | drift > 0.0001% trending |
| R-02 | any breach | — | — |
| R-03 | any breach | — | — |
| R-04 | — | any missing in daily sample | — |
| R-05 | any breach | — | — |
| R-06 | — | any missing | < 99.99% completeness trending |

## Response Runbook Reference
All breaches escalate via the alert manager to `#data-platform-incidents`.
Detailed response procedures are in `runbook.md` (RB-001):
- R-01 / R-04 → §"reconciliation drift response" (F6 path)
- R-02 / R-03 → §"mass-conservation breach"
- R-05 → §"customer-deletion propagation" (F5 path)
- R-06 → §"lineage gap remediation" (F7 path)
