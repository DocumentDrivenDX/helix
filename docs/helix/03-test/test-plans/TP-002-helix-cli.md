# Test Plan: TP-002-helix-cli

**Status**: backfilled
**Backfill Date**: 2026-03-25

## Test Objective

Protect the wrapper CLI contract with deterministic shell tests that exercise
queue control, tracker semantics, prompt construction, installer behavior, and
command-specific safety rules.

## Primary Verification Command

```bash
bash tests/helix-cli.sh
```

## Covered Behaviors

### Tracker

- issue creation and display
- dependency-aware ready and blocked queries
- claim flow setting `in_progress` and assignee
- claimed work remains owned until it is explicitly released or closed
- tracker update coverage for execution metadata fields including
  `execution-eligible`, `superseded-by`, and `replaces`
- tracker status summary
- lock timeout reports the recorded owner and fails closed
- execution-safe ready queries exclude refinement and superseded work

### Wrapper Help and Dry-Run Output

- `help` lists supported commands and key options
- `check --dry-run` prints the expected agent invocation and action reference
- `backfill --dry-run` includes writable-session and trailer requirements
- `design`, `polish`, `review`, and `experiment` dry-runs include their scoped
  prompt details
- `build --dry-run` and `triage` surfaces reflect the converged command and
  tracker-validation contract

### Loop, Queue, and Cycle Control

- `run` stops after the queue drains
- `check` can emit `DESIGN` and `POLISH` when design or issue refinement must happen before execution resumes
- `run` dispatches bounded `design` and `polish` passes from queue-drain `NEXT_ACTION` results, then re-checks before build resumes
- `run --review-every N` triggers periodic alignment
- `run` auto-aligns once after `NEXT_ACTION: ALIGN`
- `run` surfaces alignment failures
- `run` treats `NEXT_ACTION: WAIT` as terminal and does not attempt an unblock build pass
- `run` surfaces `NEXT_ACTION: BACKFILL` as a distinct terminal branch rather than collapsing it into `WAIT` or `STOP`
- `run --max-cycles N` counts successful build completions, not failed attempts
- failed implementation attempts do not advance completed-cycle counters or periodic alignment timing
- `run` revalidates selected work before claim and before close when queue
  drift is possible
- interactive refinement during a live run is surfaced as queue drift rather
  than stale claim/close behavior
- supersession detected during a live run is surfaced as queue drift and blocks
  a stale close
- `run` stays focused on an active epic until its child work finishes or a
  blocker releases focus
- `run` retries difficult issues with bounded exponential backoff before
  reporting them as blocked
- `run` emits blocker reports, cycle timing, and token-usage observability
  data for `helix status`

### Backfill Contract

- `backfill` fails when `BACKFILL_REPORT` is missing
- `backfill` succeeds only when the declared report file exists

### Recovery and Review

- orphan recovery does not destroy unrelated worktree changes
- orphan recovery does not unclaim legitimately active work without sufficient evidence
- recovery is issue-scoped and non-destructive by default
- `run` invokes post-implementation review when enabled
- `run --review-agent <other-agent>` switches review to a second model for
  cross-model verification
- `REVIEW_STATUS: CLEAN` allows the loop to continue
- review findings are surfaced and redirect or stop the loop rather than being ignored
- epic closure triggers a scoped post-epic review

### Utility Commands

- `next` returns the first ready issue or `no ready issues`
- `experiment` requires a clean worktree
- `experiment --close` includes close-session guidance
- `status` reports persisted run-controller state and blocker summaries
- `triage` enforces required create fields instead of allowing partially
  specified HELIX issues
- installer creates the local `helix` launcher

## Test Method

- Create isolated temporary git workspaces
- Inject mock `codex` and `claude` binaries
- Seed `.helix/issues.jsonl` with known issue graphs
- Assert exact stdout or stderr fragments and filesystem side effects

## Known Gaps

- The current harness validates prompt shape and loop behavior, not live remote
  agent correctness.
- The harness should be extended if claim leases or heartbeat-based ownership
  are added to the tracker data model.
- The harness should be extended if `check` grows additional machine-readable
  trailers beyond `NEXT_ACTION` that affect loop control.
- The harness should be extended when `helix status` begins exposing richer
  lifecycle history than the initial run-controller snapshot contract.

## Evidence

- `docs/helix/01-frame/features/FEAT-002-helix-cli.md`
- `docs/helix/02-design/technical-designs/TD-002-helix-cli.md`
- `workflows/EXECUTION.md`
- `workflows/TRACKER.md`
- `tests/helix-cli.sh`
