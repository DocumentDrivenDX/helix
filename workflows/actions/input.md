# HELIX Action: Input

You are processing sparse user intent through the HELIX intake surface.

Your goal is to accept a natural language request, identify the governed work it
affects in the artifact stack, and create or update work items so the rest of
the HELIX workflow can execute the intent without further user prompting.

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
  by a hard-stop constraint. Create speculative work items for assumptions
  rather than asking. When no `concerns.md` exists, infer the concern selection
  from the product nature and record it as an assumption (FEAT-011 FR-3).

**Resolution precedence (FEAT-011 FR-2)**: resolve the active level first-match
wins — (1) per-invocation override (the level passed with the request) →
(2) governing artifact frontmatter / project policy (`autonomy:` value) →
(3) runtime default (`medium`). `CLAUDE.md` and runtime-specific instruction
files are not part of this chain; the autonomy signal lives only in
runtime-neutral artifacts.

**Invariants (all levels)**: autonomy changes *checkpoint density*, never the
*stop floor*. A hard stop — a true higher/equal-authority contradiction, an
unauthorized destructive action, or a human-only decision — stops the workflow
at every level. Autonomy never collapses the seven-activity loop or skips an
activity the work requires.

## Authority Hierarchy

When artifacts disagree, use this precedence:

1. Product Vision
2. Product Requirements
3. Feature Specs / User Stories
4. Architecture / ADRs
5. Solution Designs / Technical Designs
6. Test Plans / Tests
7. Implementation Plans
8. Source Code / Build Artifacts

## STEP 0 — Bootstrap

1. Read AGENTS.md so project instructions are fresh in working memory.
2. Verify the runtime-provided work-item source is available.
3. Read `docs/helix/01-frame/` if it exists to load project vision and
   declared concerns.

## STEP 1 — Intent Parsing

Parse the request:

1. Extract the core intent (what the user wants to change, add, or fix).
2. Identify the affected artifact layer (feature, design, bug, etc.).
3. Identify any explicit constraints or references (spec IDs, work item IDs,
   feature names, area labels).
4. If autonomy=low, confirm your interpretation with the user before
   continuing. If autonomy=medium or high, proceed with best-effort
   interpretation and document it.

## STEP 2 — Artifact Graph Traversal

Traverse the artifact stack to find affected artifacts:

1. Search for existing governing work items, features, specs, and designs that
   the request touches.
2. Determine the blast radius: which governed artifacts need to change?
3. If a matching work item already exists (same scope, same intent), prefer
   updating it over creating a duplicate.

## STEP 3 — Work Item Creation / Update

Create or update work items for the identified work:

1. Create new work items for new scope.
2. Refine existing work items when the same scope already has an open item.
3. Assign labels: `helix`, plus `activity:build`, `kind:implementation`, and any
   relevant `area:` labels.
4. Set `spec-id` to the nearest governing artifact (feature, user story, or
   design doc ID).
5. Write concrete, locally verifiable acceptance criteria.
6. Encode blockers when one work item must precede another.
7. After creating a new work item, assemble its context digest per the
   runtime's context-digest reference. Do not leave HELIX-created open work
   items without either a digest or an explicit omission rationale when the
   contract allows omission.

**Autonomy-specific work item creation rules**:

- `low`: Create only the work item the user explicitly confirmed.
- `medium`: Create work items for deterministic downstream work. Flag ambiguous
  scope in descriptions rather than creating speculative items.
- `high`: Create speculative work items for reasonable downstream assumptions;
  label them `kind:speculative` to mark them as assumed, not confirmed.

## STEP 4 — Conflict Detection

Before finishing, check for conflicts:

1. Does this intent contradict an existing higher-authority artifact?
2. Does it duplicate an existing open work item?

If a conflict exists:
- `low` / `medium`: Report the conflict and ask the user how to resolve it.
- `high`: Create an escalation work item labeled `kind:escalation` and proceed
  with the non-conflicting portions of the request.

## STEP 5 — Output

Report what was done:

```
INPUT_STATUS: COMPLETE | NEEDS_CLARIFICATION | BLOCKED
ITEMS_CREATED: N
ITEMS_UPDATED: N
AUTONOMY_LEVEL: low|medium|high
CONFLICTS: <description or "none">
NEXT_ACTION: run implementation loop | check queue | <clarification question>
```

Be precise. If the user's intent was ambiguous and autonomy required you to
pause, state exactly what clarification is needed.

## Runtime Integration Appendix

This appendix covers how a runtime realizes the input action. The reference
paths and work-item acquisition below are runtime-neutral; for the concrete
commands of a specific runtime, see its install guide (DDx:
[docs/install/ddx.md](../../docs/install/ddx.md)).

### Bootstrap

Verify the runtime-provided work-item source is reachable. If it fails, stop
immediately.

### STEP 1 reference

Explicit constraints or references include work-item IDs.

### STEP 2 reference

Search for existing governing work items via the runtime-provided work-item
source.

### STEP 3 — Work-item operations

Create a new work item with labels `helix,activity:build,kind:implementation`,
`spec-id` set to the governing artifact, and testable acceptance criteria. To
refine an existing item, update it in place. To encode a blocker, declare a
dependency from the blocked item to the blocking item. The runtime supplies the
work-item store; for the concrete commands see its install guide
([docs/install/ddx.md](../../docs/install/ddx.md) for DDx).

After creating a new work item, assemble its `<context-digest>` per
`workflows/references/context-digest.md`. If the repo ships
`scripts/refresh_context_digests.py`, use it after item creation so digest
assembly and area labels stay deterministic.

Omission path: if the this action cannot assemble a digest (legacy work item,
incomplete concern mapping), use the exact prefix
`Explicit omission rationale: <reason>`, add label `digest:omission-authorized`,
and set `digest-omission-path=helix-input:legacy-migration`.

**Autonomy-specific work-item creation rules** mirror the normative rules above,
with speculative items labeled `kind:speculative` and escalation items labeled
`kind:escalation`.

### STEP 5 — Output trailer

```
INPUT_STATUS: COMPLETE | NEEDS_CLARIFICATION | BLOCKED
WORK_ITEMS_CREATED: N
WORK_ITEMS_UPDATED: N
AUTONOMY_LEVEL: low|medium|high
CONFLICTS: <description or "none">
NEXT_ACTION: build | /helix check | <clarification question>
```
