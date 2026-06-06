# C012 — Create an ADR with no upstream artifacts (guided)

**Category:** conversation-library (happy paths) (plan §1.5b)
**Phase:** P5
**Tier:** must_pass_core

## What this asserts

Marker is active (`helix`). No vision or PRD exist yet. Operator says
"Create an ADR for choosing Postgres". The graph declares `adr` with
`scope: cross-cutting` — ADRs are NOT gated by upstream vision/PRD per
plan §1.5 (row C012) and graph-fixture conventions.

The skill MUST engage and produce an ADR draft with an empty (or
deliberation-noted) `depends_on` chain, WITHOUT inventing fake upstream
links.

## Negative control

`plugins_remove: [methodology-product]`. Skill cannot engage; verdict
flips.
