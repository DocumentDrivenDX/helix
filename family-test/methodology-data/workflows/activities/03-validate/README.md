# 03-validate

Purpose: quality contracts as executable tests; backfill rehearsal;
reconciliation harness. This is `validate`, not `test`, because data
validation is structurally distinct from unit/integration testing —
it's invariant-checking on flowing data, not assertion-checking on
synthetic inputs.

Inputs: `data-quality-expectations` (requires), `data-contract`
(requires), `data-architecture` (informs), `data-design` (informs).

Outputs:
- `data-quality-tests` (exit-gate): test_inventory (id, name,
  expectation_id, run_frequency), fixtures, known_failures.
- `backfill-plan`: trigger, scope, safety_checks_pre_run,
  rollback_strategy, expected_runtime, communication_to_consumers.
- `reconciliation-suite`: reconciliation_rules (source vs sink
  invariants), alert_thresholds, response_runbook_ref.

Exit gate: `validate-validation` — every expectation has a test;
every contract has either a backfill-plan or an explicit "no backfill
needed" note; reconciliation rules exist for every consumer marked
`dependency_strength: hard` in the inventory.

Concerns: tests cite the specific expectation id they enforce (no
free-floating tests); backfill-plan names the contract version it
restores; reconciliation thresholds are absolute, not relative
("percent drift" thresholds hide step-changes in low-volume windows).

Authority boundary: backfill drafting is allowed at all autonomy
levels; backfill EXECUTION is `stop_at` regardless of autonomy.
