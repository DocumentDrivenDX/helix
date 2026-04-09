# HELIX Action: Input

You are processing sparse user intent through the HELIX intake surface.

Your goal is to accept a natural language request, identify the governed work it
affects in the artifact stack, and create or update tracker beads so the rest
of the HELIX workflow can execute the intent without further user prompting.

## Action Input

You receive:

- A natural language request (the user's intent, possibly incomplete or ambiguous)
- An autonomy level: `low`, `medium`, or `high` (default: `medium`)

**Autonomy semantics (FEAT-011 / TD-011)**:

- `low`: Ask the user before proceeding at each step and before creating each
  downstream artifact. Do not infer unconfirmed scope.
- `medium`: Create deterministic non-conflict artifacts. Pause for user input
  when ambiguity or conflict blocks deterministic progress on an affected artifact.
- `high`: Create downstream artifacts without interactive prompts unless blocked
  by a physics-level constraint. Create speculative beads for assumptions rather
  than asking.

## Authority Order

When artifacts disagree, use this precedence:

1. Product Vision
2. Product Requirements
3. Feature Specs / User Stories
4. Architecture / ADRs
5. Solution Designs / Technical Designs
6. Test Plans / Tests
7. Implementation Plans
8. Source Code / Build Artifacts

## PHASE 0 — Bootstrap

1. Read AGENTS.md so project instructions are fresh in working memory.
2. Verify the built-in tracker is available (`ddx bead status`).
3. Read `docs/helix/01-frame/` if it exists to load project vision and
   declared concerns.

## PHASE 1 — Intent Parsing

Parse the request:

1. Extract the core intent (what the user wants to change, add, or fix).
2. Identify the affected artifact layer (feature, design, bug, etc.).
3. Identify any explicit constraints or references (spec IDs, bead IDs,
   feature names, area labels).
4. If autonomy=low, confirm your interpretation with the user before
   continuing. If autonomy=medium or high, proceed with best-effort
   interpretation and document it.

## PHASE 2 — Artifact Graph Traversal

Traverse the artifact stack to find affected artifacts:

1. Search for existing governing beads, features, specs, and designs that
   the request touches.
2. Determine the blast radius: which governed artifacts need to change?
3. If a matching bead already exists (same scope, same intent), prefer
   updating it over creating a duplicate.

## PHASE 3 — Bead Creation / Update

Create or update tracker beads for the identified work:

1. Use `ddx bead create` for new work items.
2. Use `ddx bead update <id>` to refine existing items.
3. Set labels: `helix`, plus `phase:build`, `kind:implementation`, and any
   relevant `area:` labels.
4. Set `spec-id` to the nearest governing artifact (feature, user story, or
   design doc ID).
5. Write concrete, locally verifiable acceptance criteria.
6. Encode blockers with `ddx bead dep add` when one bead must precede another.

**Autonomy-specific bead creation rules**:

- `low`: Create only the bead the user explicitly confirmed.
- `medium`: Create beads for deterministic downstream work. Flag ambiguous
  scope in bead descriptions rather than creating speculative beads.
- `high`: Create speculative beads for reasonable downstream assumptions;
  label them `kind:speculative` to mark them as assumed, not confirmed.

## PHASE 4 — Conflict Detection

Before finishing, check for conflicts:

1. Does this intent contradict an existing higher-authority artifact?
2. Does it duplicate an existing open bead?

If a conflict exists:
- `low` / `medium`: Report the conflict and ask the user how to resolve it.
- `high`: Create an escalation bead labeled `kind:escalation` and proceed
  with the non-conflicting portions of the request.

## PHASE 5 — Output

Report what was done:

```
INPUT_STATUS: COMPLETE | NEEDS_CLARIFICATION | BLOCKED
BEADS_CREATED: N
BEADS_UPDATED: N
AUTONOMY_LEVEL: low|medium|high
CONFLICTS: <description or "none">
NEXT_ACTION: helix run | helix check | <clarification question>
```

Be precise. If the user's intent was ambiguous and autonomy required you to
pause, state exactly what clarification is needed.
