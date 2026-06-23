---
ddx:
  id: example.metric-definition.depositmatch.csv-import-validation-seconds
  depends_on:
    - example.test-plan.depositmatch
    - example.deployment-checklist.depositmatch.csv-import
  review:
    self_hash: 7889a106bd3b349d17124fe2fcd082f9f79c1b12947785617af369273603b0c8
    deps:
      example.deployment-checklist.depositmatch.csv-import: 02e9e7c9c29b4a335e0e2eceacaaaa6673018042db2a706f89293ab6f58abcbf
      example.test-plan.depositmatch: ba055b639a94e62d3b24f3a7ca270f78c3f17f6bae78b936d399291225d7976f
    reviewed_at: "2026-05-25T15:46:40Z"
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

## Example: regression-bench metric (methodology/skill change)

A regression bench validates a methodology or skill change. The metric scores a
fixed brief, the `command` re-runs it from the bare prompt with the improved
skill installed, and `baseline`/`target` carry the bare-prompt reading versus
the value that earns the change its keep.

```yaml
name: recipe-app-build-conformance
description: Intrinsic conformance score for the recipe-app bench brief run from the bare prompt with the candidate HELIX skill installed (build passes + template-conformant PRD + zero phantom claims).
unit: score
direction: higher
command: bash tests/workflows/run-all.sh --bench recipe-app --score
output_pattern: "METRIC recipe-app-build-conformance=([0-9]+\\.?[0-9]*)"
baseline: 0.62
target: 0.85
tolerance: "0.05"
last_verified: "2026-05-25"
interpretation: Below baseline means the candidate skill change regressed the bench; at or above target means the change earned its keep. A score that disagrees with the PRD it scores (template↔meta drift) is a broken instrument — fix the instrument before trusting the reading (FEAT-016).
labels:
  product: helix
  feature: FEAT-014
  area: methodology
  signal: conformance
```
