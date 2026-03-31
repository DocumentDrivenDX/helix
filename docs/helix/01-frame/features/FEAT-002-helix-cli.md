# Feature Specification: FEAT-002 - HELIX CLI

**Feature ID**: FEAT-002
**Status**: backfilled
**Backfill Date**: 2026-03-25
**Scope**: wrapper CLI, built-in tracker, local installer, and deterministic harness

## Summary

`helix-cli` is the repository's operator-facing wrapper around HELIX actions.
It provides one command surface for bounded execution (`run`, `build`,
`check`, `align`, `backfill`), supervisory steering (`status`, `evolve`,
`design`, `polish`, `review`, `triage`, `experiment`), tracker access
(`tracker`), and helper navigation (`next`). The wrapper must preserve the
HELIX authority stack, keep execution bounded, and make queue-control
semantics explicit, observable, and safe.

## Users

- Repository operators running HELIX actions from a local checkout
- AI-assisted sessions that need a stable shell entrypoint
- Maintainers who need deterministic wrapper tests before changing CLI behavior

## Required Behavior

### Command Surface

The CLI must expose these top-level commands:

- `run`
- `status`
- `build`
- `check`
- `align`
- `backfill`
- `evolve`
- `design`
- `polish`
- `next`
- `review`
- `experiment`
- `triage`
- `tracker`
- `help`

### Execution Model

- `run` must continue only while true ready work exists, then call `check` when
  the queue drains.
- `build` must execute one bounded build pass.
- `status` must report a structured lifecycle snapshot sourced from persisted
  run-controller state.
- `check` must return a `NEXT_ACTION` code used to decide whether to build,
  design, polish, align, backfill, wait, ask for guidance, or stop.
- `run` must treat `NEXT_ACTION` as authoritative:
  - `BUILD`: continue with the next bounded build pass.
  - `DESIGN`: run one bounded design pass, then re-evaluate queue state.
  - `POLISH`: run one bounded issue-refinement pass, then re-evaluate queue
    state.
  - `ALIGN`: run the alignment workflow once, then re-evaluate queue state.
  - `BACKFILL`: stop and surface the explicit `helix backfill <scope>` command
    before execution resumes.
  - `WAIT`: stop without attempting implementation.
  - `GUIDANCE`: stop and surface the required decision.
  - `STOP`: stop because no actionable work remains.
- `run` must support epic focus mode: when an epic is selected, remain on that
  epic's children until it is complete or explicitly blocked.
- `run` must retry difficult work with bounded exponential backoff before
  declaring it blocked.
- `run` must absorb small adjacent work into the current slice when the change
  is clearly part of satisfying the same governing acceptance.
- Only successfully completed build passes count as completed cycles.
- Failed implementation attempts, reviews, alignment, backfill, and recovery
  retries must not be counted as completed cycles.
- After each successful build pass, `run` must perform a fresh-eyes review
  before advancing to the next cycle.
- When `--review-agent` is configured, post-build review must switch to the
  alternate agent for cross-model verification.
- When an epic closes, `run` must perform a scoped post-epic review against
  the epic's governing spec before leaving that scope.
- A review with findings must be surfaced as actionable follow-up before the
  loop advances.
- When the loop stops with skipped work, `run` must emit a blocker report and
  persist enough state for `helix status` to explain the stop condition.

### Tracker Model

- The CLI must expose a built-in tracker at `helix tracker`.
- Tracker data must live in `.helix/issues.jsonl`.
- Ready work must be determined from open issues whose dependencies are all
  closed.
- Tracker creation paths must enforce the required issue fields at creation
  time: `helix` label, one phase label, `--spec-id` for tasks, and
  deterministic `--acceptance` for tasks and epics.
- Tracker ownership must distinguish active claims from stale or orphaned
  claims.
- The wrapper may only reclaim or recover stale work when the tracker's
  ownership rules indicate that the issue is no longer actively owned.
- Recovery must preserve unrelated worktree changes and may only act on work
  that can be attributed to the stale issue.
- If the wrapper cannot safely attribute the partial work to the issue, it must
  stop and require guidance rather than discard changes.

### Operator Safeguards

- The experiment flow must require a clean worktree before continuing.
- Backfill output must include machine-readable `BACKFILL_STATUS`,
  `BACKFILL_REPORT`, and `RESEARCH_EPIC` trailers, and the declared report file
  must exist.

### Local Installation

- `scripts/install-local-skills.sh` must install the HELIX skill entrypoints
  into the canonical `~/.agents/skills` location and mirror them into
  `~/.claude/skills` for Claude compatibility.
- The installed skill links must preserve package-relative access back to the
  shared `workflows/` resource library in the HELIX repo.
- The installer must create `~/.local/bin/helix` as a launcher that invokes the
  repository's `scripts/helix`.

## Acceptance Criteria

- Running `helix help` shows the command surface and key options.
- Running `helix status` reports a structured lifecycle snapshot derived from
  persisted run-controller state.
- Running `helix tracker` subcommands supports create/show/update/close/list,
  ready/blocked queries, dependency management, and status summaries.
- Running `helix triage` produces tracker-valid issues with required labels,
  governing artifact reference, and deterministic acceptance criteria.
- Running `helix run` follows the explicit `NEXT_ACTION` contract for
  `BUILD`, `DESIGN`, `POLISH`, `ALIGN`, `BACKFILL`, `WAIT`, `GUIDANCE`, and
  `STOP`.
- Running `helix run` does not attempt implementation after `WAIT`.
- Running `helix run` stops and surfaces the exact backfill command after
  `BACKFILL`.
- Running `helix run` counts only completed build passes as completed
  cycles.
- Running `helix run` surfaces review findings before the loop advances.
- Running `helix run` stays focused on a chosen epic until the epic finishes
  or an explicit blocker forces release.
- Running `helix run` emits blocker-report output and observability metadata
  for cycle timing and token accounting.
- Running `helix run` does not discard unrelated worktree changes during
  recovery.
- Running `helix backfill <scope>` enforces the required trailers and durable
  report creation contract.
- Running `bash tests/helix-cli.sh` remains the required deterministic
  verification path for wrapper behavior changes.

## Evidence

- `docs/helix/01-frame/prd.md`
- `docs/helix/02-design/solution-designs/SD-001-helix-supervisory-control.md`
- `docs/helix/02-design/technical-designs/TD-002-helix-cli.md`
- `docs/helix/03-test/test-plans/TP-002-helix-cli.md`
- `workflows/README.md`
- `workflows/EXECUTION.md`
- `workflows/TRACKER.md`
