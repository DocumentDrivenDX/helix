# Reference: Report Activity

The report activity closes the feedback loop between the execution helix and the
planning helix. It analyzes measurement results, creates follow-on work items for
new work identified, and closes the governing work item with evidence.

## Per-Work-Item Report (Default)

Every action's final activity is a per-work-item report. After measure completes:

### 1. Analyze Measurement Results

Read the `<measure-results>` block from the work item's notes. Classify outcomes:

- **Clean**: All criteria passed, all gates passed. The work item's work is done.
- **Fixable**: Failures are within the action's scope to fix. Fix them, re-run
  measure, then report.
- **Follow-on**: Failures or findings require new work outside this work item's scope.

### 2. Create Follow-On Work Items

For each follow-on item, create a new work item carrying:

- type `task` and labels `helix,activity:build`
- a `spec-id` pointing at the governing artifact
- a `<context-digest>` description naming the parent work item and the work needed
- testable acceptance criteria

The runtime supplies the work-item store; for the concrete create command see
its install guide ([docs/install/ddx.md](../../docs/install/ddx.md) for DDx).

Follow-on work items enter the planning helix — they will be refined by `/helix
polish` before execution.

Categories of follow-on work:

| Category | When |
|----------|------|
| `regression` | A previously passing test or criterion now fails |
| `review-finding` | Fresh-eyes review identified a bug, security issue, or quality gap |
| `acceptance-failure` | An acceptance criterion could not be satisfied |
| `concern-gap` | A concern-declared quality gate failed or concern coverage is missing |
| `ratchet-regression` | A ratchet measurement dropped below the floor |
| `follow-on` | Execution revealed additional work outside the work item's scope |

### 3. Close the Governing Work Item

Close the governing work item through the runtime's work-item store. The close
comment should summarize:
- What was done
- Measurement status (PASS/FAIL/PARTIAL)
- Number of follow-on work items created
- References to commits, artifacts, or reports produced

If measurement status is `FAIL` and the failures are not captured as follow-on
work items, do not close the work item. Leave it open with a status note explaining what
blocks closure.

### 4. Report Output

The action's output section includes measurement results and follow-on work items:

```
REPORT_STATUS: CLOSED|OPEN|FOLLOW_ON
WORK_ITEM_ID: <id>
MEASURE_STATUS: PASS|FAIL|PARTIAL
FOLLOW_ON_CREATED: N
COMMITS: <list>
```

## Batch Report (`/helix report <scope>`)

Batch report aggregates across work items in a scope (epic, area, activity, or
time range).

### Input

```bash
/helix report <scope>          # e.g., FEAT-003, area:auth, activity:build
/helix report --since 2026-04-01
```

### Analysis

1. Collect all work items in scope that have `<measure-results>` notes.
2. Aggregate statistics:
   - Total work items measured / passed / failed / partial
   - Concern gate pass rates by concern
   - Ratchet trends (floor vs. measured over time)
   - Follow-on work item categories (how much new work did execution generate?)
3. Identify patterns:
   - Recurring failures (same gate fails across multiple work items)
   - Concern coverage gaps (work items without concern-appropriate criteria)
   - Ratchet trends approaching floor

### Output

```
REPORT_SCOPE: <scope>
WORK_ITEMS_TOTAL: N
WORK_ITEMS_PASSED: N
WORK_ITEMS_FAILED: N
WORK_ITEMS_PARTIAL: N
FOLLOW_ON_TOTAL: N
CONCERN_COVERAGE: N/M (work items with full concern threading / total)
RATCHET_STATUS: all-passing | <name> approaching floor
```

Write the batch report to:
`docs/helix/06-iterate/reports/RPT-YYYY-MM-DD[-scope].md`

## Feed-Back Into Planning Helix

Follow-on work items created during report are intentionally unrefined — they have
descriptions and acceptance criteria but may need polish before execution.
This is by design: the execution helix produces raw findings, and the planning
helix refines them into well-specified, concern-threaded, ready work items.

The next `/helix check` will detect these work items and route appropriately:
- If they need refinement → `POLISH`
- If they are already ready → `BUILD`
- If they reveal design gaps → `DESIGN`
