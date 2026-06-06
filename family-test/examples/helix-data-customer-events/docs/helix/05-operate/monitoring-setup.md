---
ddx:
  id: MS-001
  type: monitoring-setup
  methodology: helix-data
  library_type_version: 1.0.0
  links:
    - {kind: informs, to: MD-001}
    - {kind: informs, to: RB-001}
---

# Monitoring Setup: Customer Events Pipeline

CloudWatch + DataHub alert wiring. Every alert maps to a runbook section
(RB-001) AND to one or more adversarial fixtures.

## Alert Catalog

| Alert ID | Trigger | Sev | Runbook | Fixture |
|---|---|---|---|---|
| A-DEDUP-RATE | T-B02 dedup rate > 1% rolling 1h | 3 | RB-001 §"Duplicate-event surge" | **F1** |
| A-LATE-EVENT | `dlq/late_event/` ingress > 10k/h | 2 | RB-001 §"Late-event arrival surge" | **F2** |
| A-SCHEMA-ADDITIVE | T-B06 new api_version seen | 3 | RB-001 §"Schema drift detected" | **F3** |
| A-SCHEMA-BREAKING | T-S03 schema-fingerprint mismatch | 1 | RB-001 §"Schema drift detected" | **F3** |
| A-PII-CANARY | T-S02 email canary triggered | 1 (BLOCKING) | RB-001 §"PII canary fired" | **F4** |
| A-METADATA-PII | `dlq/pii_metadata/` ingress > 100/h | 2 | RB-001 §"PII canary fired" | **F4** |
| A-REDACTION-LAG | R-05 deletion-propagation breach | 1 | RB-001 §"Customer-deletion propagation" | **F5** |
| A-RECON-R01 | R-01 source↔bronze drift > tolerance | 2 | RB-001 §"Reconciliation drift response" | **F6** |
| A-RECON-R02 | R-02 mass-conservation breach | 1 | RB-001 §"Reconciliation drift response" | **F6** |
| A-RECON-R04 | R-04 round-trip miss in daily sample | 2 | RB-001 §"Reconciliation drift response" | **F6** |
| A-LINEAGE-GAP | R-06 lineage completeness < 100% | 2 | RB-001 §"Lineage gap remediation" | **F7** |
| A-LINEAGE-EMIT | OL emit failure rate > 0 | 2 | RB-001 §"Lineage gap remediation" | **F7** |
| A-COST-BURN | Glue spend run-rate > $400/mo | 2 | RB-001 §"Cost overrun" | **F8** |
| A-PARTITION-EXPLOSION | silver partition count > 2x baseline | 3 | RB-001 §"Cost overrun" | **F8** |
| A-HOT-KEY | T-S06 hot-key > 5% in any partition | 2 | RB-001 §"Hot-key / skew" | **F9** |
| A-DLQ-SIZE | T-S07 DLQ > 0.1% of inflow rolling 1h | 2 | RB-001 §"DLQ replay after schema fix" | **F10** |
| A-FINGERPRINT-MISMATCH | T-G06 gold fingerprint mismatch | 1 | RB-001 §"Contract-version mismatch" | **F11** |

## Routing

- Sev1: PagerDuty `data-platform-oncall` + `#data-platform-incidents`.
- Sev2: `#data-platform-incidents` + on-call best-effort.
- Sev3: `#data-platform-notices` + next-business-day handling.
- BLOCKING (A-PII-CANARY, A-SCHEMA-BREAKING, A-FINGERPRINT-MISMATCH): in
  addition to Sev1, the pipeline is auto-halted at the affected stage.

## Dashboards
- Operator overview: `metrics-dashboard.md` (MD-001) §"Operator overview".
- Cost: MD-001 §"Cost".
- Reconciliation: MD-001 §"Reconciliation status board".
- Lineage health: rendered in DataHub.

## Alert Hygiene

- Every alert must reference a runbook section (this table enforces).
- Every alert must be exercised by a fixture (this table enforces).
- A new alert without an F-fixture is a defect — add the fixture before
  shipping the alert.
- Alerts firing > 5x/week without action items → tune or remove (handled
  in monthly governance review).
