# C023 — "Add quality checks for the orders pipeline" (helix-data engages)

**Category:** conversation-library (happy paths) (plan §1.5b + §12.8)
**Phase:** P5
**Tier:** must_pass_core

## What this asserts

Marker has `helix-data` active. Operator says "Add quality checks for
the orders pipeline". Quality checks are the canonical 03-validate
artifacts (`data-quality-expectations` and executable
`data-quality-tests`). The skill MUST engage and draft them, suggesting
testable EXPECT rules.

## Negative control

`plugins_remove: [methodology-data]`. Skill unregistered; verdict flips.
