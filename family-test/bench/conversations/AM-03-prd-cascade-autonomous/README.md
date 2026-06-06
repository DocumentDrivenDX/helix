# AM-03 — Autonomy matrix: PRD cascade @ autonomous

**Category:** autonomy-matrix (plan §1.5b)
**Phase:** P3
**Tier:** must_pass_core
**Fixture:** A (PRD requested, marker active, no vision)
**Level:** autonomous

## What this asserts

With `autonomy.default: autonomous` the skill proceeds directly to Read +
Write without confirmation. The cascade (vision before PRD) is executed
silently as commentary, not as a question. Pair-row contract: discriminator
polarity inverted vs AM-01/AM-02 — the confirmation marker MUST NOT appear
in the positive run.

## Negative control

`autonomy_swap` to AM-01 (manual) — the confirmation marker MUST appear
when the level changes back to manual.
