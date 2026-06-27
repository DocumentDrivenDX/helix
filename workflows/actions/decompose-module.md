# HELIX Action: Decompose Module

You are decomposing an oversized, poorly-encapsulated code module into focused
units, iteratively, behind a per-iteration verification gate. This is the
*code-structure* decomposition the operator otherwise drives by hand across dozens
of loop iterations — distinct from decomposing *requirements* into work items
(that is `frame` / `polish`).

The discipline that makes this safe is a **persistent target manifest** (so the
loop has durable state and the operator never re-injects "now ~9.5k") and a
**verification gate every iteration** (so a refactor never ships a regression).

## Action Input

You may receive:

- a **target**: the module(s)/file(s) to decompose, or a size threshold
  (e.g. "every source file over 800 lines")
- `--threshold <N>`: the per-file size target the manifest ratchets toward
- `--manifest <path>`: the target-manifest file (created on first run)

## Authority Hierarchy

Decomposition must not change behavior, so the governing authority is the existing
tests and the module's public contract:

1. Existing acceptance criteria / tests (behavior must be preserved)
2. Architecture / ADRs (the boundaries decomposition should respect)
3. Source Code (the thing being restructured)

## STEP 0 - Bootstrap

0. **Context Recovery**: Re-read AGENTS.md so project instructions (build, test,
   lint commands) are fresh.
1. Confirm a green baseline: the test suite passes *before* any decomposition. A
   refactor with no green baseline cannot prove it preserved behavior.
2. Load or create the target manifest (STEP 1).

## STEP 1 - Build the Target Manifest

Measure the current module sizes and record a **persistent manifest** — the
durable state this loop owns so progress is never re-typed into a prompt:

- each oversized module: its current size and the target it must reach
- the per-file threshold (the floor the manifest ratchets toward)
- a `done` list of modules already brought under threshold

The manifest is a **size ratchet** (see `workflows/ratchets.md`): the floor only
moves toward the threshold, and a later change that re-inflates a `done` module
below its recorded size is a regression. Commit the manifest.

## STEP 2 - Decompose One Module (iterate)

Pick the **largest** module still over threshold. For that one module:

1. Identify cohesive units within it — a group of functions/types that belong
   together by responsibility. Decompose along responsibility seams, not by
   arbitrary line count.
2. Extract each unit into its own module, preserving the public contract (the
   callers and tests must not change behavior). Move tests alongside the code they
   exercise.
3. Decompose by **moving** code, not by leaving a shim behind: the old oversized
   module shrinks; it does not gain a re-export layer that just forwards calls
   (that is the hollow scope the `scope-discipline` concern rejects). Update
   callers to the new path in the same change.

## STEP 3 - Verification Gate (every iteration)

Before committing the iteration, run the full gate — happy-path-green is not
enough (the `verification` concern):

- the test suite passes (behavior preserved — this is the whole point)
- lint / format clean
- the size guard: the touched module is now under threshold and no other module
  regressed past its manifest floor

If the gate fails, fix it within the iteration; do not advance the manifest over
a red gate. When it passes: update the manifest (`done` list + new sizes), and
commit the iteration as one reviewable unit.

## STEP 4 - Loop or Stop

- If any module remains over threshold: go to STEP 2 for the next-largest.
- When every module is under threshold and the suite is green: **DONE**.
- If a module cannot be brought under threshold without breaking its contract
  (a genuine cohesive unit larger than the threshold): record the exception in
  the manifest with the reason (the ratchet override protocol), and move on —
  never force a split that fractures a real responsibility.

## Output

Report:

1. The manifest: modules decomposed this run, before/after sizes, and any
   recorded over-threshold exceptions.
2. Per iteration: the module split, the units extracted, and the gate result.
3. Final disposition (all under threshold, or the recorded exceptions remaining).

Then emit the machine-readable trailer:

```
DECOMPOSE_STATUS: DONE|IN_PROGRESS|BLOCKED
MODULES_OVER_THRESHOLD_START: N
MODULES_OVER_THRESHOLD_NOW: N
ITERATIONS: N
GATE: green|red
```

- `DONE`: every module under threshold (or recorded-exception), suite green.
- `IN_PROGRESS`: modules remain; the manifest holds the durable state to resume.
- `BLOCKED`: the green baseline could not be established, or a split cannot
  preserve behavior — report and stop.

## Runtime Integration Appendix

- The manifest format and the size-guard command are project-specific; express
  the manifest as a ratchet floor fixture (`workflows/ratchets.md`) so the loop's
  durable state is versioned, not held in a prompt.
- This action composes the size ratchet (`ratchets.md`) and the `verification`
  gate; it does not restate either. It is the build-time refactoring loop that
  applies them to module structure.
