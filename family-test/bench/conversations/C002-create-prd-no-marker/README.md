# C002 — Create a PRD with no marker (empty workspace, guided)

**Category:** conversation-library (happy paths) (plan §1.5b)
**Phase:** P5
**Tier:** must_pass_core

## What this asserts

Empty workspace, no `.helix.yml`. Operator says "Let's create a PRD".
"PRD" is a router-anchor noun (plan §2.2). Under autonomy=guided the
skill MUST:

1. Engage via `Skill(helix)`.
2. Surface the "no marker" diagnostic — the workspace is unscoped.
3. Surface the cascade (a PRD requires a product-vision per
   `graph.yml`'s `prd informs product-vision` edge).
4. Offer to add the marker + draft the vision first.

This row covers the cascading-prerequisite case at the engagement
boundary (no marker yet).

## Negative control

`plugins_remove: [methodology-product]`. With the methodology plugin
removed, no `helix` skill exists; cascade-from-graph reasoning cannot
fire because the agent has no graph.yml to read.
