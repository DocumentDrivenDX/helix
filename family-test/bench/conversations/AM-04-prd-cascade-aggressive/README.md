# AM-04 — Autonomy matrix: PRD cascade @ aggressive

**Category:** autonomy-matrix (plan §1.5b)
**Phase:** P3
**Tier:** must_pass_core
**Fixture:** A (PRD requested, marker active, no vision)
**Level:** aggressive

## What this asserts

With `autonomy.default: aggressive` the skill marches the full methodology
graph autonomously — drafts vision then PRD in one pass, surfacing only at
stop_at or unrecoverable ambiguity. Discriminator polarity is absent
(matches AM-03). stop_at is the safety net; this fixture's workspace
already has the marker so no marker_edit trigger fires.

## Negative control

`autonomy_swap` to AM-01 (manual) — the confirmation marker MUST appear
when the level changes to manual.
