# AM-08 — Autonomy matrix: ADR singleton @ aggressive

**Category:** autonomy-matrix (plan §1.5b)
**Phase:** P3
**Tier:** must_pass_core
**Fixture:** B (ADR requested, marker active, no upstream needed)
**Level:** aggressive

## What this asserts

On a no-prereq fixture, aggressive behaves like autonomous — single Write
for the ADR, no confirmation prompt. The aggressive > autonomous gap shows
up on cascade fixtures (compare AM-04 vs AM-03).

## Negative control

`autonomy_swap` to AM-05 (manual) — confirmation prompt MUST appear.
