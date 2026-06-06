# C005 — Create a PRD: marker active, NO vision (guided)

**Category:** conversation-library (happy paths) (plan §1.5b)
**Phase:** P5
**Tier:** must_pass_core

## What this asserts

Marker is active (`helix`), but no `product-vision.md` exists. Operator
asks for a PRD. Under autonomy=guided the skill MUST consult `graph.yml`,
observe the `prd informs product-vision` cascade prerequisite, and
SURFACE the prerequisite — offering to draft the vision first — rather
than silently fabricating one or skipping the cascade.

Pair-row: C006 (same workspace, autonomy=autonomous) where the skill
just does both writes. The contrast is the autonomy slider; the cascade
itself is autonomy-invariant per §2.7 / §4.

## Negative control

`plugins_remove: [methodology-product]`. Without the skill the agent
cannot consult `graph.yml`; the cascade language vanishes; `Skill(helix)`
absent.
