# CD-01 — Graph carries a non-standard required edge

**Category:** graph-discrimination (plan §1.5b)
**Phase:** P2 (Cascade discrimination)
**Tier:** must_pass_core

## What this asserts

The `workflows/graph.yml` in this fixture declares a project-local edge
`market-validation-brief requires prd` (`required: true`). This edge is NOT
part of canonical HELIX library knowledge — it is added by the project.

When the operator asks for a PRD, the skill (per SKILL.md §Consult The Graph
Before Authoring) must:

1. Read the methodology's `graph.yml`.
2. Enumerate incoming edges to the `prd` node.
3. Find the `requires` edge from `market-validation-brief`.
4. Surface that prerequisite (autonomy=guided → ask whether to draft the
   brief first).

The `graph_edge_observed` matcher verifies both the Read tool_use on
`graph.yml` AND the verbatim signature `market-validation-brief requires
prd` in the assistant text.

## Paired discrimination

CD-02 is the positive-control with the same workspace minus the edge — the
skill must NOT surface a market-validation prerequisite when the graph
does not declare it. The negative_control block on this row's discriminator
swaps in CD-02's graph and asserts the opposite verdict.

CD-03 covers the plugin-removed negative (skill cannot engage; no cascade
possible). CD-04 covers a different non-standard edge to defend against
phrase-memorisation.

## Status

`authored-pending-verification`. P2 lands the rows + fixtures + SKILL.md §
update. Live-driving Claude against the rows + scoring is wired in P3+
(autonomy matrix + driver harness).
