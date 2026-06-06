# C004 — Create a PRD: marker active, vision exists (guided)

**Category:** conversation-library (happy paths) (plan §1.5b)
**Phase:** P5
**Tier:** must_pass_core

## What this asserts

Marker is active (`helix`), an approved product-vision exists. Operator
says "Let's create a PRD". The cascade is satisfied; the skill MUST:

1. Engage via `Skill(helix)`.
2. Read the marker and vision before any write.
3. Draft a PRD with `ddx.links` populated from the vision (per the
   `prd informs product-vision` graph edge).

This row is the canonical "engagement floor" happy path — everything
works, the agent's job is simply to honour the cascade.

## Negative control

`plugins_remove: [methodology-product]`. With the plugin removed the
helix skill cannot engage; verdict flips.
