# HELIX Action: Polish Issues

You are performing plan decomposition and iterative issue refinement before
implementation begins.

Your goal is to decompose design plans into implementable tracker work items and then
improve relevant item quality as needed: deduplication,
coverage verification against the plan, acceptance criteria sharpening,
dependency correction, and convergence detection. This front-loaded investment
prevents agents from running off to implement work that hasn't been properly
broken down.

**Polish prepares requested work for execution.** Decompose a plan when asked or
required by the runtime, then refine the resulting scoped items.

## Action Input

You may receive:

- a task or scope named in the request
- a scope such as `auth`, `FEAT-003`, `activity:build`
- `--rounds N` as an optional upper bound on refinement passes (default: 6)

Infer scope from the named task when possible. Ask when no clear scope can be
inferred; do not expand to every open work item by default.

## STEP 0 - Load Current State

0. **Context Recovery**: Re-read AGENTS.md so project instructions are fresh
   in your working memory. After long sessions, context compaction may have
   dropped critical project rules. This step is cheap insurance against drift.
0a. **Load active design principles** following the principles-resolution
   reference for this runtime. Use them as refinement guidance — flag work
   items whose scope or criteria conflict with the active principles.
0b. **Load active concerns and practices** following the concern-resolution
   reference for this runtime. Verify item descriptions and acceptance criteria
   reference the correct concern tools and conventions.
0c. **Refresh context digests**: For each work item in scope that has an
   existing context digest, re-assemble and update if material changes exist.
   For items without a digest, assemble one and prepend it. If the runtime
   provides a digest refresh helper, use it so area-label inference and digest
   assembly stay deterministic.
1. Verify the runtime-provided work-item source is available. Stop immediately if unavailable.
2. Load open work items relevant to the scope.
3. Load the governing plan document if one exists.
   - Check `docs/helix/02-design/plan-*.md` for the scope
   - Check other planning artifacts (PRD, feature specs, architecture docs)

## STEP 0.5 - Work Item Acquisition

Before modifying any work items, acquire a governing work item for this polish
pass to record progress and govern changes. See the runtime's work-item
acquisition reference for the full pattern.

## STEP 0.75 - Evidence gate (before filing or keeping build work)

For every open or proposed `activity:build` / implement item in scope:

1. Check residual against code and tests (paths, greps, named suites).
2. If the governing AC is already exercised by a passing test (or a recorded
   exception), **close or re-scope** the item — do not leave stale implement work.
3. If only story/AC documentation lags shipped code, prefer frame/story floor
   items over new implement items.
4. Record evidence (path:line or test name) on the item when keeping it open.

## STEP 1 - Plan Decomposition

**This activity runs first when the user or runtime requests plan decomposition.**
Decompose applicable implementation slices before refinement.

1. Locate the governing plan documents for the scope:
   - `docs/helix/02-design/plan-*.md`
   - `docs/helix/02-design/solution-designs/SD-*.md`
   - Other design artifacts referenced by the scope
2. For each plan, check whether tracker work items already exist that reference it
   (via `spec-id`, description, or parent epic).
3. If the requested plan has **not been decomposed**:
   a. Read the plan's "Implementation Plan with Dependency Ordering" section
      (or equivalent work breakdown).
   b. Create one work item per implementable slice. Each item must:
      - be individually completable in one build cycle
      - carry labels `helix` and `activity:build` plus area labels
      - set `spec-id` to the governing plan or design artifact
      - have deterministic acceptance criteria derived from the plan
      - have a context digest assembled per the runtime's context-digest
        reference
   c. Group related items under an epic if the plan implies multiple
      implementation tracks.
   d. Wire dependencies based on the plan's dependency graph.
4. If the plan has been partially decomposed, create work items only for
   uncovered implementation slices; explanatory sections do not each need an
   item.

When decomposition was requested, complete or confirm it before refining the
resulting work items.

## STEP 2 through N - Refinement Passes

Each pass performs ALL of the following checks. Track changes made per pass.

### Deduplication

- Find issues with overlapping scope, description, or acceptance criteria.
- Merge duplicates into a single canonical issue that preserves the strongest
  elements of each.
- When merging, preserve all dependency relationships from both issues.
- Close the redundant issue with a note pointing to the canonical one.

### Plan Coverage Verification

- If decomposition was requested, verify each applicable implementation slice
  has a corresponding work item.
- Create an item for an uncovered slice only when it is in scope and has
  enough governing detail for verifiable acceptance criteria.
- If an issue exists but doesn't map to any plan section, flag it for review.

### Acceptance Criteria Sharpening

- Replace vague criteria with testable statements.
  - Bad: "auth should work correctly"
  - Good: "login with valid credentials returns 200 and a JWT; login with
    invalid credentials returns 401 with error code AUTH_INVALID"
- Ensure every work item has at least one concrete acceptance criterion.
- Add verification method: what command or test proves this criterion is met?
- For execution-ready items (`activity:build`, `activity:deploy`, `activity:iterate`
  implementation work), require acceptance text to name at least one explicit:
  - command to run
  - named check or execution doc
  - observable repository state, file, field, or tracker condition
- Treat "works", "correct", "complete", "aligned", or similar adjectives
  without a named check as non-measurable acceptance text.
- If the governing artifacts let you sharpen the item, rewrite the acceptance
  criteria immediately.
- If the governing artifacts do **not** let you sharpen the item into explicit
  measurement criteria, flag the work item as **not execution-ready** and route it back
  through planning/polish refinement instead of leaving hidden knowledge to
  decide success.
- A work item is not execution-ready until the runtime could determine success
  from the item's contract alone without a human inferring what "done" means.

### Dependency Verification

- Verify dependency chains are correct: if issue A depends on issue B, does B
  actually produce what A needs?
- Look for missing dependencies: does this issue assume work that hasn't been
  captured as a dependency?
- Look for circular dependencies and break them.
- Verify `spec-id` points to the correct governing artifact.

### Sizing

- Flag issues that are too large for a single bounded implementation pass.
  An issue is too large if it touches more than 3 files in different subsystems
  or requires more than one architectural decision.
- Split oversized issues into smaller, independently verifiable slices.
- Preserve the dependency ordering when splitting.

### Label Hygiene

- Ensure every issue has the `helix` label.
- Ensure every issue has exactly one activity label (`activity:build`, `activity:deploy`,
  or `activity:iterate`).
- Ensure area labels are present where applicable.
- Ensure `kind:*` labels match the issue's actual type.

### Area Label Enforcement for Concern Matching

Area labels are required for concern filtering to work. For each work item in
scope:

1. If the item has no `area:*` labels, infer the correct area from:
   - The `spec-id` and its governing artifact's scope
   - The files or subsystems referenced in the description
   - The parent epic's area labels (if the parent has them)
2. Assign the inferred `area:*` labels.
3. If the area is genuinely ambiguous, prefer the more inclusive label or
   assign multiple labels. An item touching both API and CLI should have both
   `area:api` and `area:cli`.
4. Items that touch all areas (e.g., CI config, cross-cutting refactors) may
   omit area labels — they will match only `areas: all` concerns, which is
   correct.
5. Area labels are routing metadata, not digest content. Refresh the concerns
   element from matched concern names after relabeling; do not leave stale
   area names in the digest.

### Concern-Aware Acceptance Criteria

For each work item in scope, verify acceptance criteria reference the correct
concern tools:

- An item in a `typescript-bun` project should reference `bun:test`, not
  `vitest` or `jest`, in its test-related acceptance criteria.
- An item in a `rust-cargo` project should reference `cargo clippy` and
  `cargo deny`, not ad-hoc lint approaches.
- If acceptance criteria reference tools inconsistent with declared concerns,
  update them.

### Concern Propagation Verification

For each active concern, verify end-to-end threading across all work items in
scope:

1. **Digest coverage**: Every item with a matching area label must have a
   context digest that includes the concern. If missing, assemble one.
2. **Acceptance criteria coverage**: Every item touching a concern's area must
   have at least one acceptance criterion that references the concern's quality
   gate or practice. For example:
   - A `typescript-bun` item must reference `bun:test` or `biome check`
   - A `security-owasp` item must reference input validation or dependency audit
   - A `rust-cargo` item must reference `cargo clippy` or `cargo deny`
3. **Tool consistency**: Flag any item whose acceptance criteria reference tools
   inconsistent with declared concerns (e.g., `vitest` in a `bun:test` project).
4. **New concern detection**: If concerns changed since items were created,
   propagate the change to all affected items — update both digests and
   acceptance criteria.

## Convergence Detection

Stop when requested decomposition is complete, scoped items meet applicable
readiness checks, and no material ambiguity remains. Treat `--rounds N` only as
an upper bound; stop earlier when ready. If the limit is reached first, report
what remains and why.

## ACTIVITY N+1 - Measure

Verify the polish pass against the governing work item's acceptance criteria.
See `workflows/references/measure.md` for the full pattern.

1. **Decomposition completeness**: Requested implementation slices have
   corresponding work items.
2. **Readiness**: In-scope items meet applicable readiness checks, with no
   unresolved material ambiguity, or identify what blocks readiness.
3. **Concern threading**: All work items in scope have concern-appropriate
   context digests and acceptance criteria.
4. **Dependency integrity**: No circular dependencies; all `spec-id` references
   resolve to existing artifacts.
5. **Record results** on the governing work item via the runtime-provided work-item source.

## ACTIVITY N+2 - Report

Close the polish cycle and feed back into the planning cycle. See the report
action for the full pattern.

1. If measurement passed, close the governing work item with evidence summary.
2. Create follow-on items only when requested or required by the runtime, for:
   - Items that still lack concern coverage
   - Plans that could not be fully decomposed (need guidance)
   - Dependency issues that need resolution
3. The polished work items are now ready for the build action to claim and
   execute.

## Output

Summarize modifications made across rounds. Use these fields only when the
user or runtime requests structured output:

```
POLISH_STATUS: CONVERGED|IN_PROGRESS
DECOMPOSITION: YES|NO|PARTIAL
POLISH_ROUNDS: N
ITEMS_DECOMPOSED: count (from plan decomposition)
ITEMS_MODIFIED: count
ITEMS_CREATED: count (from refinement, not decomposition)
ITEMS_MERGED: count
MEASURE_STATUS: PASS|FAIL|PARTIAL
ITEM_ID: <governing-item-id>
FOLLOW_ON_CREATED: N
```

- `CONVERGED`: requested decomposition is complete and scoped items are ready
- `IN_PROGRESS`: the upper round limit was reached before the scope was ready
- `DECOMPOSITION: YES`: plan was decomposed into work items in this run
- `DECOMPOSITION: NO`: no plan found or plan was already decomposed
- `DECOMPOSITION: PARTIAL`: plan partially decomposed, some sections could not
  be broken down without guidance

When in-scope implementation work is ready, the runtime can dispatch it under its own execution rules.
