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
- tracker status summary

### Wrapper Help and Dry-Run Output

- `help` lists supported commands and key options
- `check --dry-run` prints the expected agent invocation and action reference
- `backfill --dry-run` includes writable-session and trailer requirements
- `plan`, `polish`, `review`, and `experiment` dry-runs include their scoped
  prompt details

### Loop, Queue, and Cycle Control

- `run` stops after the queue drains
- `run --review-every N` triggers periodic alignment
- `run` auto-aligns once after `NEXT_ACTION: ALIGN`
- `run` surfaces alignment failures
- `run` treats `NEXT_ACTION: WAIT` as terminal and does not attempt an unblock implementation pass
- `run` surfaces `NEXT_ACTION: BACKFILL` as a distinct terminal branch rather than collapsing it into `WAIT` or `STOP`
- `run --max-cycles N` counts successful implementation completions, not failed attempts
- failed implementation attempts do not advance completed-cycle counters or periodic alignment timing

### Backfill Contract

- `backfill` fails when `BACKFILL_REPORT` is missing
- `backfill` succeeds only when the declared report file exists

### Recovery and Review

- orphan recovery does not destroy unrelated worktree changes
- orphan recovery does not unclaim legitimately active work without sufficient evidence
- recovery is issue-scoped and non-destructive by default
- `run` invokes post-implementation review when enabled
- `REVIEW_STATUS: CLEAN` allows the loop to continue
- review findings are surfaced and redirect or stop the loop rather than being ignored

### Utility Commands

- `next` returns the first ready issue or `no ready issues`
- `experiment` requires a clean worktree
- `experiment --close` includes close-session guidance
- installer creates the local `helix` launcher

## Test Method

- Create isolated temporary git workspaces
- Inject mock `codex` and `claude` binaries
- Seed `.helix/issues.jsonl` with known issue graphs
- Assert exact stdout or stderr fragments and filesystem side effects

## Known Gaps

- The current harness validates prompt shape and loop behavior, not live remote
  agent correctness.
- The harness does not validate tmux or `ntm` success paths; it only checks the
  no-`ntm` fallback.
- The harness should be extended if claim leases or heartbeat-based ownership
  are added to the tracker data model.

## Evidence

- `tests/helix-cli.sh:347-447`
- `tests/helix-cli.sh:451-646`
- `tests/helix-cli.sh:650-775`
- `tests/helix-cli.sh:808-937`
- `tests/helix-cli.sh:978-1010`
- `workflows/EXECUTION.md:185-203`
- `workflows/REFERENCE.md:149-154`
