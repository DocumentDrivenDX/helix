# HELIX Action: Report

You are analyzing measurement results and feeding the findings back into
planning.

This action operates in two modes: per-item (one measured cycle) and batch
(aggregating across a scope). It reads measurement results wherever they were
recorded: a runtime work item's notes, a measure action's output, or the
conversation. It creates or closes tracker items only when a runtime work item
governs the run.

## Action Input

You may receive:

- a runtime work item ID (per-item mode)
- a named scope such as `FEAT-003`, `area:auth`, or `activity:build` (batch mode)
- `--since YYYY-MM-DD` to limit batch scope by time

## STEP 0 - Bootstrap

0. **Context Recovery**: Re-read AGENTS.md so project instructions are fresh
   in your working memory.
1. Load active concerns following the concern-resolution reference for this
   runtime.
2. When a runtime work item governs the run, verify the runtime-provided
   work-item source is available.

## Per-Item Mode

### STEP 1 - Load Measurement Results

1. Load the measurement results for the target: from the governing work item's
   notes when one applies, otherwise from the measure output the user supplies
   or the current conversation.
2. If no measurement results exist, recommend running the measure action first
   and stop.

### STEP 2 - Analyze Results

Classify the measurement outcome:

- **Clean**: All criteria passed, all gates passed. The work is done.
- **Fixable**: Failures are within the action's scope to fix. Recommend
  fixing and re-measuring rather than opening new work.
- **Follow-on**: Failures or findings require new work outside this scope.

### STEP 3 - Follow-On Recommendations

Classify each follow-on finding by category and report it with its evidence and
a suggested next step. Create tracker items only when the user requests them or
the runtime requires them; follow the runtime's rules for fields and digests.

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

### STEP 4 - Governing Work Item (when required)

When a runtime work item governs the run, record the report on it and follow the
runtime's closure rules. If measurement status is FAIL and the failures are not
captured as follow-on work, leave the item open with a status note.

Without a governing work item, state the measurement status, the evidence, and
the recommended next step in the response.

### Per-Item Output

Report the measurement status, the classification from Step 2, and any
follow-on recommendations. Name the governing item ID when one applies.

## Batch Mode

### STEP 1 - Collect Measurement Results

1. Load the measurement results in scope: from work item notes when a tracker
   is in use, otherwise from existing reports and measure output.
2. If `--since` is specified, filter by the measurement timestamp.

### STEP 2 - Aggregate Statistics

Compute:

- Total measured / passed / failed / partial
- Concern gate pass rates by concern
- Ratchet trends (floor vs. measured over time)
- Follow-on categories (how much new work did execution generate?)
- Acceptance criteria satisfaction rate

### STEP 3 - Identify Patterns

Look for:

- **Recurring failures**: Same gate fails across multiple items. May indicate
  a systemic issue rather than per-item bugs.
- **Concern coverage gaps**: Items without concern-appropriate criteria. May
  indicate a polish gap.
- **Ratchet trends**: Metrics approaching the floor. May indicate quality
  erosion that needs attention before it becomes a regression.
- **Follow-on volume**: A high follow-on rate may indicate that scope is
  under-specified or that the planning cycle needs more polish passes.

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

## Feed-Back Into Planning

Follow-on findings are raw. When they become tracker items, they are
intentionally unrefined: the planning cycle refines them.

The next check action routes them:
- If they need refinement → polish action
- If they are already ready → build action
- If they reveal design gaps → design action

Be precise, quantitative, and evidence-driven.

## Runtime Integration Appendix

This appendix covers how a runtime realizes the report action when a runtime
work item governs the run. The reference paths below are runtime-neutral; for
the concrete commands of a specific runtime, see its install guide.

### STEP 0 — Reference resolution

Load active concerns following `workflows/references/concern-resolution.md`.
When a runtime work item governs the run, verify the runtime-provided work-item
source is reachable; stop if it is not.

### Per-item mode — runtime specifics

Load the target work item and its `<measure-results>` block from the
runtime-provided work-item source. If no measurement results exist, recommend
running `/helix measure <id>` first.

Follow `workflows/references/work-item-first.md` for any follow-on items the
user requested or the runtime requires. Follow-on items are refined by
`/helix polish` before execution. Close the governing work item per the
runtime's rules once the report is complete.

### Optional trailers

Emit these only when a runtime consumer requires them.

Per-item:
```
REPORT_STATUS: CLOSED|OPEN|FOLLOW_ON
ITEM_ID: <id>
MEASURE_STATUS: PASS|FAIL|PARTIAL
FOLLOW_ON_CREATED: N
```

Batch:
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
