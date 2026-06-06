# SA-12 — stop_at near-miss negative: marker Read NOT marker_edit

**Category:** stop_at-trigger (plan §1.5b)
**Phase:** P3
**Tier:** must_pass_core
**Trigger:** marker_edit
**Polarity:** near-miss-negative
**Paired positive:** SA-01

## What this asserts

Reading `.helix.yml` (no write/edit) under aggressive autonomy must NOT
fire the marker_edit trigger. Protects the dominant marker tool_use from
spurious confirmation prompts.
