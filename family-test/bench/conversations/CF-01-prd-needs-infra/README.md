# CF-01 — "The PRD says we need new infra. Plan the change." (cross-flow helix → helix-infra)

**Category:** conversation-library (cross-flow discriminators) (plan §1.5b + §14.1)
**Phase:** P5
**Tier:** must_pass_core

## What this asserts

Marker activates BOTH `helix` (at `docs/helix/`) and `helix-infra` (at
`infra/`). An approved PRD-001 exists in `docs/helix/01-frame/` whose
prose explicitly states "deploying this requires a Cloudflare zone."
Plugins: library + methodology-product + methodology-infra.

Operator says "The PRD says we need new infra. Plan the change." The
cross-flow contract per plan §14.1:

1. `helix` engages FIRST — the prompt names PRD (a helix artifact);
   the skill MUST read PRD-001 to ground its plan.
2. The skill MUST surface `helix-infra` as a cross-flow prerequisite,
   not "plan infra in a vacuum".

The structural floor at P5 is the FIRST-engaged-flow signal:
`Skill(helix)` MUST appear in the stream. The cross-flow handoff to
`helix-infra` is graded by Layer 2/3 at P7+; we record the structural
floor here.

This is a standalone cross-flow discriminator row (codex flagged that
embedding cross-flow signal in C021/C022/C025 — which carry single-flow
floors — mixes assertions; this row isolates the helix→helix-infra
direction).

## Negative control

`plugins_remove: [methodology-product]`. Without the helix plugin no
helix skill is registered. The agent — given only `methodology-infra` —
has no flow that owns "PRD"; it cannot read PRD-001 as a helix artifact
and plans infra in a vacuum. `Skill(helix)` tool_use cannot fire.
Verdict flips present → absent, proving the helix engagement was
plugin-driven (not prompt-language driven by the word "PRD").
