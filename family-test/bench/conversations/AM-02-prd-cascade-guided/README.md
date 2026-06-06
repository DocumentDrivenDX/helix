# AM-02 — Autonomy matrix: PRD cascade @ guided

**Category:** autonomy-matrix (plan §1.5b)
**Phase:** P3
**Tier:** must_pass_core
**Fixture:** A (PRD requested, marker active, no vision)
**Level:** guided

## What this asserts

With `autonomy.default: guided` the skill reads context freely but must ask
before the FIRST state-changing tool_use. The cascade prereq (vision
precedes PRD) is surfaced in that confirmation. Paired with AM-01 (manual),
AM-03 (autonomous), AM-04 (aggressive); only `autonomy.default` differs
across the matrix.

## Negative control

`autonomy_swap` to AM-03 — autonomous mode MUST stop emitting the
confirmation prompt before mutation.
