# C025 — "Our PRD needs a new metric we can measure" (cross-flow helix → helix-data)

**Category:** conversation-library (happy paths) (plan §1.5b + §12.8)
**Phase:** P5
**Tier:** must_pass_core
**Flow classification:** compatibility row for the flow rename. Current
contract: first public engagement is `helix`; `helix-data` is an internal flow
surface, not a separate public skill.

## What this asserts

Marker has BOTH `helix` and `helix-data` active. An approved
product-vision exists. Operator says "Our PRD needs a new metric we can
measure". The cross-flow contract per plan §14.1:

1. `helix` engages first — the prompt names PRD (a helix artifact).
2. Skill surfaces that the metric definition spans into helix-data
   territory (`metric-definition`, `data-product-brief`).
3. Offers to draft both a metric-definition (helix) and a
   data-product-brief (helix-data), linking cross-flow.

The structural floor at P5 is the FIRST-engaged-flow signal:
`Skill(helix)` MUST appear in the stream. (Cross-flow handoff to
helix-data is graded by Layer 2 at P7 wiring.)

## Negative control

`plugins_remove: [methodology-product]`. Without the helix skill, the
prompt either falls through to helix-data alone (which doesn't own
"PRD") or no skill engages. The `Skill(helix)` tool_use cannot fire.
Verdict flips.
