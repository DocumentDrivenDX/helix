# AM-06 — Autonomy matrix: ADR singleton @ guided

**Category:** autonomy-matrix (plan §1.5b)
**Phase:** P3
**Tier:** must_pass_core
**Fixture:** B (ADR requested, marker active, no upstream needed)
**Level:** guided

## What this asserts

Skill reads freely, asks before first Write/Edit. Same level-discrimination
contract as AM-02 but on a non-cascading fixture.

## Negative control

`autonomy_swap` to AM-07 — confirmation prompt MUST disappear under
autonomous mode.
