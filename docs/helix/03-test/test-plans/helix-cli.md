# HELIX Test Plan: helix-cli

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
- tracker status summary

### Wrapper Help and Dry-Run Output

- `help` lists supported commands and key options
- `check --dry-run` prints the expected agent invocation and action reference
- `backfill --dry-run` includes writable-session and trailer requirements
- `plan`, `polish`, `review`, and `experiment` dry-runs include their scoped
  prompt details

### Loop and Queue Control

- `run` stops after the queue drains
- `run --review-every N` triggers periodic alignment
- `run` auto-aligns once after `NEXT_ACTION: ALIGN`
- `run` surfaces alignment failures
- `run` attempts one unblock implementation pass after `NEXT_ACTION: WAIT`
- `run --no-auto-unblock` suppresses the unblock attempt

### Backfill Contract

- `backfill` fails when `BACKFILL_REPORT` is missing
- `backfill` succeeds only when the declared report file exists

### Utility Commands

- `next` returns the first ready issue or `no ready issues`
- `spawn` reports missing `ntm`
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

## Evidence

- `tests/helix-cli.sh:347-447`
- `tests/helix-cli.sh:451-646`
- `tests/helix-cli.sh:650-775`
- `tests/helix-cli.sh:808-937`
- `tests/helix-cli.sh:978-1010`
- `workflows/EXECUTION.md:185-203`
- `workflows/REFERENCE.md:149-154`
