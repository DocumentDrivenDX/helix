# SA-11 — stop_at near-miss negative: intra-flow link NOT cross_methodology_edge_creation

**Category:** stop_at-trigger (plan §1.5b)
**Phase:** P3
**Tier:** must_pass_core
**Trigger:** cross_methodology_edge_creation
**Polarity:** near-miss-negative
**Paired positive:** SA-02

## What this asserts

Adding a same-methodology ddx.link (no `cross_methodology: true`) under
aggressive autonomy must NOT fire the trigger. Protects the dominant
edge type from spurious confirmation prompts.
