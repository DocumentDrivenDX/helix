# C015 — "What's next?" with vision but no PRD (guided)

**Category:** conversation-library (happy paths) (plan §1.5b)
**Phase:** P5
**Tier:** must_pass_core

## What this asserts

Marker active (`helix`), an approved vision exists, no PRD yet.
Operator asks "What's next?". The skill MUST read `graph.yml`, identify
the next downstream node from `product-vision` (the `prd` node, via the
`prd informs product-vision` edge), and surface PRD as the suggested
next artifact.

This row exercises the graph-as-source-of-truth path (plan §3.2 / §10):
the answer is a STRUCTURAL query against the graph, not a memorised
HELIX stage table.

## Negative control

`plugins_remove: [methodology-product]`. The skill cannot consult
`graph.yml` (no graph reachable, no Skill(helix) tool_use). Verdict
flips present → absent.
