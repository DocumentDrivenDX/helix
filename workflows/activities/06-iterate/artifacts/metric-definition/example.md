---
ddx:
  id: example.metric-definition.depositmatch.csv-import-validation-seconds
  depends_on:
    - example.test-plan.depositmatch
    - example.deployment-checklist.depositmatch.csv-import
  review:
    self_hash: a1bb2128a1335ff7b306902f4bc6ab433468c93f567943535c641fa2e53d617e
    deps:
      example.deployment-checklist.depositmatch.csv-import: 02e9e7c9c29b4a335e0e2eceacaaaa6673018042db2a706f89293ab6f58abcbf
      example.test-plan.depositmatch: ba055b639a94e62d3b24f3a7ca270f78c3f17f6bae78b936d399291225d7976f
    reviewed_at: "2026-05-15T04:11:24Z"
---

# Metric Definition: csv-import-validation-seconds

> Store at `docs/helix/06-iterate/metrics/csv-import-validation-seconds.yaml`

```yaml
name: csv-import-validation-seconds
description: Time required to validate and summarize a representative DepositMatch CSV import fixture totaling 10,000 rows.
unit: seconds
direction: lower
command: pnpm metric:csv-import-validation -- --fixture fixtures/import/acme-10000-rows
output_pattern: "METRIC csv-import-validation-seconds=([0-9]+\\.?[0-9]*)"
tolerance: "5%"
interpretation: A value above 5 seconds violates the FEAT-001 performance target and should create an improvement backlog item unless the fixture changed.
labels:
  product: depositmatch
  feature: FEAT-001
  area: import
  signal: latency
```
