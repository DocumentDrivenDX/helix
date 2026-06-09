# AM-07 — Autonomy matrix: ADR singleton @ autonomous

**Category:** autonomy-matrix (plan §1.5b)
**Phase:** P3
**Tier:** must_pass_core
**Fixture:** B (ADR requested, marker active, no upstream needed)
**Level:** autonomous

## What this asserts

Skill proceeds directly to Read + Write without confirmation. Discriminator
polarity inverted (absent in positive run).

## Negative control

`autonomy_swap` to AM-05 (manual) — confirmation prompt MUST appear when
the level changes back to manual.
