# AM-01 — Autonomy matrix: PRD cascade @ manual

**Category:** autonomy-matrix (plan §1.5b)
**Phase:** P3
**Tier:** must_pass_core
**Fixture:** A (PRD requested, marker active, no vision)
**Level:** manual

## What this asserts

With `autonomy.default: manual` the skill must surface every proposed action
and request explicit confirmation BEFORE issuing any tool_use that mutates
state. The matrix is hand-paired with AM-02 (guided), AM-03 (autonomous),
AM-04 (aggressive) — identical workspace, prompt, and plugins; only
`autonomy.default` changes. Determinism contract: confirmation count and
mutation count differ by level across N=3 runs (plan §4.6 / §15c P3 halt
condition).

## Negative control

`autonomy_swap` to AM-03 — replacing manual with autonomous MUST stop the
confirmation prompt from appearing before any tool use, proving the level
drove the pause (not the prompt).
