# C020 — "Help me understand HELIX" (empty workspace, guided)

**Category:** conversation-library (happy paths) (plan §1.5b)
**Phase:** P5
**Tier:** must_pass_core

## What this asserts

Empty workspace, no marker. Operator says "Help me understand HELIX".
"HELIX" is a router-anchor noun. The skill MUST engage to explain the
methodology AND offer to set up a marker if the operator wants to use
it on this repo.

The discriminator is the standard `Skill(helix)` tool_use floor — the
explanatory content lives in Layer 2 (P7 wiring); the structural floor
proven here is that the skill IS the source of the explanation
(authoritative, not training-paraphrased).

## Negative control

`plugins_remove: [methodology-product]`. Without the skill, Claude
explains HELIX from training — accurate-ish, but the `Skill(helix)`
tool_use event is absent. Verdict flips.
