---
name: helix-input
description: 'Accept sparse user intent and create governed tracker beads. Use when the user provides a natural language request that should be converted to HELIX work items. Public command surface: helix input.'
argument-hint: '"<natural language request>" [--autonomy low|medium|high]'
disable-model-invocation: true
---

# Input

Accept sparse user intent, traverse the artifact stack to identify affected
governed work, and create or update tracker beads so the rest of the HELIX
workflow can execute the intent.

If a specific request or autonomy level is given, use: $ARGUMENTS

## Use This Skill When

- the user provides a natural language request that should be converted to work items
- the user wants `helix input` behavior from inside the agent
- intent is sparse or incomplete and needs to be mapped to governed artifacts
- the user specifies an autonomy level (`low`, `medium`, or `high`)

## Autonomy Levels

- `low`: ask the user before proceeding at each step; do not infer unconfirmed scope
- `medium` (default): create deterministic non-conflict artifacts; pause when ambiguity blocks progress
- `high`: create downstream artifacts without prompts unless blocked by physics-level constraints; use `kind:speculative` beads for assumptions

## Steps

1. **Parse the intent** — extract the core request, affected artifact layer, and
   any explicit constraints or references.

2. **Traverse the artifact stack** — search for existing governing beads,
   features, specs, and designs the request touches. Identify the blast radius.

3. **Create or update beads** — use `ddx bead create` for new work and
   `ddx bead update <id>` to refine existing items. Set appropriate labels
   (`helix`, `phase:build`, `kind:implementation`, `area:*`) and `spec-id`.
   For `high` autonomy, label speculative beads `kind:speculative`.

4. **Detect conflicts** — check for contradictions with higher-authority
   artifacts or duplicate open beads. Report conflicts; on `high` autonomy,
   create a `kind:escalation` bead instead of blocking.

5. **Output a structured report** — emit the machine-readable trailer:

   ```
   INPUT_STATUS: COMPLETE | NEEDS_CLARIFICATION | BLOCKED
   BEADS_CREATED: N
   BEADS_UPDATED: N
   AUTONOMY_LEVEL: low|medium|high
   CONFLICTS: <description or "none">
   NEXT_ACTION: helix run | helix check | <clarification question>
   ```

## Authority Order

When artifacts disagree, prefer:

1. Product Vision
2. Product Requirements
3. Feature Specs / User Stories
4. Architecture / ADRs
5. Solution / Technical Designs
6. Test Plans / Tests
7. Implementation Plans
8. Source Code / Build Artifacts

## Governing Action

Full action detail is in `.ddx/plugins/helix/workflows/actions/input.md`.
