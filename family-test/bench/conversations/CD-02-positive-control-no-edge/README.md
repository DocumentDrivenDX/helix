# CD-02 — Positive control: no non-standard edge

**Category:** graph-discrimination (plan §1.5b)
**Phase:** P2
**Tier:** must_pass_core

## What this asserts

Same prompt and workspace shape as CD-01 — but the graph.yml here is the
canonical HELIX shape WITHOUT the project-local
`market-validation-brief requires prd` edge.

The skill must engage, read the graph, and proceed with the PRD WITHOUT
surfacing a market-validation-brief prerequisite. A surfaced prerequisite
in this configuration would mean the skill was answering from training
rather than from the graph — exactly the failure mode the discrimination
fixture exists to catch.

This is the *positive control* for CD-01: together they confirm graph
content drives surfacing.
