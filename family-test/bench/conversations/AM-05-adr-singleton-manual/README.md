# AM-05 — Autonomy matrix: ADR singleton @ manual

**Category:** autonomy-matrix (plan §1.5b)
**Phase:** P3
**Tier:** must_pass_core
**Fixture:** B (ADR requested, marker active, no upstream needed)
**Level:** manual

## What this asserts

Same level-discrimination contract as AM-01 but on a non-cascading fixture
(ADRs are cross-cutting). Removing the cascade variable isolates the level
as the sole driver of behavioural differences across AM-05..AM-08.

## Negative control

`autonomy_swap` to AM-07 — the confirmation prompt MUST disappear under
autonomous mode.
