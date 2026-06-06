# C001 — Start a HELIX project (empty workspace, guided)

**Category:** conversation-library (happy paths) (plan §1.5b)
**Phase:** P5
**Tier:** must_pass_core

## What this asserts

Empty workspace, no `.helix.yml`, no plugins active beyond
`methodology-product`. Operator says "Let's start a helix project for a
coffee-ordering app". The HELIX skill MUST:

1. Engage via the `Skill(helix, ...)` tool — the routing description
   anchors on "start a helix project" (plan §2.2).
2. Explain HELIX briefly.
3. Offer (autonomy=guided) to add the product flow marker AND draft the
   first artifact (product-vision).

The discriminator `skill_tool_use(helix)` is non-vacuous because removing
the `methodology-product` plugin removes the skill from Claude's routing
surface entirely; the agent cannot invoke it, so the verdict flips
present → absent.

## Negative control

`plugins_remove: [methodology-product]`. With the plugin removed, Claude
has no `helix` skill to call; the agent may still write a vision-shaped
file from training but cannot emit a `Skill(helix)` tool_use.
