# HELIX Action: Report

You are analyzing measurement results and closing the feedback loop between
the execution cycle and the planning cycle.

This action operates in two modes: per-item (closing one cycle) and batch
(aggregating across a scope).

## Action Input

You may receive:

- an explicit work item ID (per-item mode)
- a scope selector such as `FEAT-003`, `area:auth`, or `activity:build` (batch mode)
- `--since YYYY-MM-DD` to limit batch scope by time

## STEP 0 - Bootstrap

0. **Context Recovery**: Re-read AGENTS.md so project instructions are fresh
   in your working memory.
1. Verify the runtime-provided work-item source is available.
2. Load active concerns following the concern-resolution reference for this
   runtime.

## Per-Item Mode

### STEP 1 - Load Measurement Results

1. Load the target work item from the tracker.
2. Parse the measurement results block from the item's notes.
3. If no measurement results exist, recommend running the measure action first
   and stop.

### STEP 2 - Analyze Results

Classify the measurement outcome:

- **Clean**: All criteria passed, all gates passed. The work item is done.
- **Fixable**: Failures are within the action's scope to fix. Recommend
  fixing and re-measuring rather than creating follow-on items.
- **Follow-on**: Failures or findings require new work outside this item's
  scope.

### STEP 3 - Create Follow-On Work Items

For each follow-on item, create a work item with a category prefix in the
title, labels including `helix` and `activity:build`, a `spec-id` pointing to the
nearest governing artifact, a context digest, a reference to the parent item in
the description, and deterministic acceptance criteria.

Follow-on categories:

| Category | When |
|----------|------|
| `regression` | A previously passing test or criterion now fails |
| `review-finding` | Fresh-eyes review identified a quality gap |
| `acceptance-failure` | An acceptance criterion could not be satisfied |
| `concern-gap` | A concern-declared quality gate failed or coverage is missing |
| `ratchet-regression` | A ratchet measurement dropped below the floor |
| `phantom-claim` | A claims-vs-reality check classified an artifact assertion as `ASSERTED_UNBACKED` (zero-floor; see `workflows/ratchets.md` and FEAT-016) |
| `follow-on` | Execution revealed additional work outside scope |

Follow-on work items enter the planning cycle — they will be refined by the
polish action before execution.

### STEP 4 - Close the Governing Work Item

If measurement status is PASS or all failures are captured as follow-on items,
close the governing work item. The close comment should summarize:

- What was done
- Measurement status
- Number of follow-on items created
- References to commits or artifacts produced

If measurement status is FAIL and failures are not captured as follow-on items,
do not close. Leave the item open with a status note.

### Per-Item Output

```
REPORT_STATUS: CLOSED|OPEN|FOLLOW_ON
ITEM_ID: <id>
MEASURE_STATUS: PASS|FAIL|PARTIAL
FOLLOW_ON_CREATED: N
```

## Batch Mode

### STEP 1 - Collect Work Items

1. Load all work items in scope that have measurement result notes.
2. If `--since` is specified, filter by the measurement timestamp.
3. Load each item's measurement results.

### STEP 2 - Aggregate Statistics

Compute:

- Total items measured / passed / failed / partial
- Concern gate pass rates by concern
- Ratchet trends (floor vs. measured over time)
- Follow-on item categories (how much new work did execution generate?)
- Acceptance criteria satisfaction rate

### STEP 3 - Identify Patterns

Look for:

- **Recurring failures**: Same gate fails across multiple items. May indicate
  a systemic issue rather than per-item bugs.
- **Concern coverage gaps**: Items without concern-appropriate criteria. May
  indicate a polish gap.
- **Ratchet trends**: Metrics approaching the floor. May indicate quality
  erosion that needs attention before it becomes a regression.
- **Follow-on volume**: High follow-on creation rate may indicate that items
  are under-specified or that the planning cycle needs more polish passes.

### STEP 4 - Write Batch Report

Write the report to:
`docs/helix/06-iterate/reports/RPT-YYYY-MM-DD[-scope].md`

The report should include:

1. Scope and time range
2. Summary statistics
3. Pattern analysis
4. Concern coverage assessment
5. Ratchet trend analysis
6. Recommendations (more polish, concern updates, ratchet floor adjustments)

### Batch Output

```
REPORT_SCOPE: <scope>
ITEMS_TOTAL: N
ITEMS_PASSED: N
ITEMS_FAILED: N
ITEMS_PARTIAL: N
FOLLOW_ON_TOTAL: N
CONCERN_COVERAGE: N/M
RATCHET_STATUS: all-passing | <name> approaching floor
REPORT_FILE: docs/helix/06-iterate/reports/RPT-YYYY-MM-DD[-scope].md
```

## Feed-Back Into Planning Cycle

Follow-on work items created during report are intentionally unrefined. The
execution cycle produces raw findings; the planning cycle refines them.

The next check action will detect these items and route appropriately:
- If they need refinement → polish action
- If they are already ready → build action
- If they reveal design gaps → design action

Be precise, quantitative, and evidence-driven.

## Runtime Integration Appendix

This appendix covers how a runtime realizes the report action. The reference
paths and work-item acquisition below are runtime-neutral; for the concrete
commands of a specific runtime, see its install guide (DDx:
[docs/install/ddx.md](../../docs/install/ddx.md)).

### STEP 0 — Reference resolution

Verify the runtime-provided work-item source is reachable; stop immediately if
it is not.

Load active concerns following `workflows/references/concern-resolution.md`.

### Per-item mode — runtime specifics

Load the target work item from the runtime-provided work-item source.

If no measurement results exist, recommend running `/helix measure <id>` first.

Create follow-on work items with labels `helix,activity:build`, `spec-id` set to
the governing artifact, a `<context-digest>` description naming the parent item
and the work needed, and testable acceptance criteria. The runtime supplies the
work-item store; for the concrete commands see its install guide
([docs/install/ddx.md](../../docs/install/ddx.md) for DDx).

Follow-on items enter the planning helix and will be refined by `/helix
polish` before execution.

Close the governing work item once the report is complete.

Per-item trailer:
```
REPORT_STATUS: CLOSED|OPEN|FOLLOW_ON
ITEM_ID: <id>
MEASURE_STATUS: PASS|FAIL|PARTIAL
FOLLOW_ON_CREATED: N
```

### Batch mode — trailer

```
REPORT_SCOPE: <scope>
WORK_ITEMS_TOTAL: N
WORK_ITEMS_PASSED: N
WORK_ITEMS_FAILED: N
WORK_ITEMS_PARTIAL: N
FOLLOW_ON_TOTAL: N
CONCERN_COVERAGE: N/M
RATCHET_STATUS: all-passing | <name> approaching floor
REPORT_FILE: docs/helix/06-iterate/reports/RPT-YYYY-MM-DD[-scope].md
```

The next `/helix check` will detect follow-on work items and route appropriately:
`POLISH` for refinement, `BUILD` if already ready, `DESIGN` if design gaps
are revealed.
