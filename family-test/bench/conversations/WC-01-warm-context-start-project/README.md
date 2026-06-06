# WC-01 — Warm-context: start a helix project

**Category:** warm-context (plan §15c P6)
**Phase:** P6
**Tier:** must_pass_core

## What this asserts

Five unrelated turns (weather, regex, Tokyo, baking, music) precede the
C001 probe at turn 6: "Let's start a helix project for a coffee-ordering
app". The HELIX skill MUST still engage despite five turns of unrelated
context.

Layer 1 floor: a `Skill(helix, ...)` tool_use event appears in the
stream. Engagement rate across WC-01..WC-05 must stay within 5pp of the
equivalent cold-start rows.

## Negative control

`plugins_remove: [methodology-product]`. With the skill unregistered,
the router cannot surface helix on turn 6 regardless of context; the
tool_use event is absent.
