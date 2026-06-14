# C021 — "Let's set up a customer-ingest pipeline" (helix-data engages)

**Category:** conversation-library (happy paths) (plan §1.5b + §12.8)
**Phase:** P5
**Tier:** must_pass_core
**Flow classification:** legacy sibling-flow research row. Retained as an
expected-failing data-flow probe for the retired public `helix-data` skill
design; current HELIX routes data work through the single public `helix` skill.

## What this asserts

Empty workspace, no marker. Operator says "Let's set up a customer-ingest
pipeline". The helix-data flow's SKILL.md router (plan §12.4) anchors on
"pipeline" / "ingest" / "data product". The skill MUST:

1. Engage via `Skill(helix-data)`.
2. Surface the missing marker; offer to add `helix-data` to it.
3. Offer to draft a `data-product-brief` as the first artifact.

This is the data-flow analogue of C001 (start a project) — the
engagement floor for helix-data.

## Negative control

`plugins_remove: [methodology-data]`. Without the data plugin no
helix-data skill is registered; verdict flips.
