# HELIX Action: Measure

You are performing standalone measurement of one or more work items against
their acceptance criteria, concern-declared quality gates, and ratchet
enforcement.

This action can be invoked standalone or runs as an embedded activity within
other actions. When standalone, it reads the work item's acceptance criteria
and runs verification without re-executing the work.

## Action Input

You may receive:

- an explicit work item ID
- a scope selector such as `FEAT-003`, `area:auth`, or `activity:build`
- `--rerun <id>` to re-measure a previously measured item

## Authority Order

When artifacts disagree, use this order:

1. Product Vision
2. Product Requirements
3. Feature Specs / User Stories
4. Architecture / ADRs
5. Solution Designs / Technical Designs
6. Test Plans / Tests
7. Implementation Plans
8. Source Code / Build Artifacts

## STEP 0 - Bootstrap

0. **Context Recovery**: Re-read AGENTS.md so project instructions are fresh
   in your working memory.
1. Verify the runtime tracker is available. Stop immediately if unavailable.
2. Load active concerns and practices following the concern-resolution
   reference for this runtime.
3. Load ratchet floor fixtures if the project has adopted quality ratchets.

## STEP 1 - Target Selection

1. If an explicit work item ID is given, load that item.
2. If a scope is given, load all items in scope that have been executed
   (status in-progress or closed with work completed).
3. For each target item, load:
   - Acceptance criteria from the item description
   - `spec-id` and governing artifacts
   - Context digest (if present)
   - Previous measurement results (if any, for comparison)

## STEP 2 - Acceptance Criteria Verification

For each target work item, verify every acceptance criterion:

1. Parse the criterion text to determine the verification method:
   - **Test command**: Run the specified test or command.
   - **File existence**: Verify the file exists at the specified path.
   - **Code inspection**: Check that the described behavior is implemented.
   - **Manual check**: Flag as requiring manual verification.
2. Run each verification and record pass/fail with evidence.
3. If the item has a `spec-id`, check for an acceptance manifest (e.g.,
   `TP-SD-010.acceptance.toml`) and verify against it.
4. If acceptance scripts exist (`scripts/check-acceptance-traceability.sh`,
   `scripts/check-acceptance-coverage.sh`), run them.

## STEP 2.5 - Claims-vs-Reality Check (self-validation mode-gate)

Verification is incomplete until artifact assertions resolve to reality. For
each target item and the artifacts it touched:

1. For every claim of a test, coverage figure, or emitted metric/signal, verify
   the referent actually exists (the named test is in the suite and runs, the
   figure was produced by a real measurement, the metric is emitted).
2. Classify any unbacked claim as `ASSERTED_UNBACKED` — a phantom claim. This is
   distinct from `UNTESTED` (honest gap); `ASSERTED_UNBACKED` asserts something
   untrue.
3. The phantom-claim floor is **zero**: any `ASSERTED_UNBACKED` claim is a
   blocking finding regardless of the acceptance-satisfaction count. Resolve it
   by making the claim true or deleting it — never by relaxing the check (see
   `.ddx/plugins/helix/workflows/ratchets.md` and FEAT-016).

This is a workflow-mode gate expressed as a measurement, not a recursive call to
the validate/align actions.

## STEP 3 - Concern-Declared Quality Gates

For each target work item:

1. Determine the item's area from its labels.
2. Filter active concerns to those matching the item's area.
3. For each matched concern, run the quality gates from its practices
   under the Quality Gates section.
4. Scope gate runs to the packages/files changed by the item's work
   (infer from commit history or item description).
5. Use project overrides from `docs/helix/01-frame/concerns.md` when they
   specify alternative commands.

## STEP 4 - Ratchet Enforcement

If the project has adopted quality ratchets:

1. For each applicable ratchet, run the enforcement command.
2. Record measured value vs. floor.
3. If auto-bump is triggered, note the updated floor value.

## STEP 5 - Concern Propagation Check

Verify that the bead's context digest includes all active concerns for its
area scope:

1. If the digest is missing or stale, flag it.
2. If acceptance criteria reference tools inconsistent with declared concerns,
   flag it.
3. Record propagation status.

## STEP 6 - Record Results

Record measurement results on the work item via the runtime tracker. The
result record should capture:

- timestamp
- overall status (PASS, FAIL, or PARTIAL)
- per-criterion pass/fail with evidence
- per-gate pass/fail (concern, command, result)
- per-ratchet measured value vs. floor
- propagation status (digest freshness, criteria consistency)

## Output

For each measured work item, report:

1. Item ID
2. Acceptance criteria results (per-criterion pass/fail)
3. Quality gate results (per-gate pass/fail)
4. Ratchet results (per-ratchet measured vs. floor)
5. Concern propagation status

Then emit the machine-readable trailer:

```
MEASURE_STATUS: PASS|FAIL|PARTIAL
ITEMS_MEASURED: N
ITEMS_PASSED: N
ITEMS_FAILED: N
ITEMS_PARTIAL: N
CRITERIA_TOTAL: N
CRITERIA_PASSED: N
GATES_RUN: N
GATES_PASSED: N
RATCHETS_CHECKED: N
RATCHETS_PASSED: N
```

### Status Definitions

- `PASS`: All acceptance criteria satisfied, all gates passed, all ratchets
  within tolerance for every measured item.
- `FAIL`: One or more items have failed criteria or gates.
- `PARTIAL`: Some criteria could not be verified (e.g., manual check required,
  external dependency unavailable).

Be precise, quantitative, and evidence-driven.

## DDx Integration Appendix

This appendix applies when DDx is the active HELIX runtime.

### STEP 0 — DDx bootstrap

```bash
ddx bead status  # stop immediately if this fails
```

Load concerns following `.ddx/plugins/helix/workflows/references/concern-resolution.md`.
Load ratchet floor fixtures from `.ddx/plugins/helix/workflows/ratchets.md` if adopted.

### STEP 1 — DDx target selection

- If an explicit bead ID is given: `ddx bead show <id> --json`
- If a scope: `ddx bead list --status in_progress --label <scope> --json`

For each target bead, load the `<measure-results>` block from its notes for
comparison.

### STEP 6 — DDx record results

```bash
ddx bead update <id> --notes "<measure-results>
  <timestamp>$(date -u +%Y-%m-%dT%H:%M:%SZ)</timestamp>
  <status>PASS|FAIL|PARTIAL</status>
  <acceptance>
    <criterion name='...' status='pass|fail' evidence='...'/>
  </acceptance>
  <gates>
    <gate concern='...' command='...' status='pass|fail'/>
  </gates>
  <ratchets>
    <ratchet name='...' floor='...' measured='...' status='pass|fail'/>
  </ratchets>
  <propagation digest='fresh|stale|missing' criteria='consistent|inconsistent'/>
</measure-results>"
```

### DDx output trailer

```
MEASURE_STATUS: PASS|FAIL|PARTIAL
BEADS_MEASURED: N
BEADS_PASSED: N
BEADS_FAILED: N
BEADS_PARTIAL: N
CRITERIA_TOTAL: N
CRITERIA_PASSED: N
GATES_RUN: N
GATES_PASSED: N
RATCHETS_CHECKED: N
RATCHETS_PASSED: N
```
