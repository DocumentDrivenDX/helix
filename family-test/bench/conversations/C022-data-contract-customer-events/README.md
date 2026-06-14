# C022 — "Define a data contract for the customer events" (helix-data engages)

**Category:** conversation-library (happy paths) (plan §1.5b + §12.8)
**Phase:** P5
**Tier:** must_pass_core
**Flow classification:** legacy sibling-flow research row. Retained as an
expected-failing data-flow probe for the retired public `helix-data` skill
design; current HELIX routes data work through the single public `helix` skill.

## What this asserts

Marker has `helix-data` active. Operator says "Define a data contract
for the customer events". "Data contract" is the canonical helix-data
01-contract artifact. The skill MUST engage and draft a `data-contract`;
if producer/consumer aren't identified in the workspace it asks.

## Negative control

`plugins_remove: [methodology-data]`. Skill unregistered; verdict flips.
