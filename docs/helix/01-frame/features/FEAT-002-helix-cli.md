# Feature Specification: FEAT-002 - HELIX CLI

**Feature ID**: FEAT-002
**Status**: backfilled
**Backfill Date**: 2026-03-25
**Scope**: wrapper CLI, built-in tracker, local installer, and deterministic harness

## Summary

`helix-cli` is the repository's operator-facing wrapper around HELIX actions.
It provides one command surface for bounded execution (`run`, `implement`,
`check`, `align`, `backfill`), planning and quality workflows (`plan`,
`polish`, `review`, `experiment`), tracker access (`tracker`), and helper
navigation (`next`). The wrapper must preserve the HELIX authority stack,
keep execution bounded, and make queue-control semantics explicit and safe.

## Users

- Repository operators running HELIX actions from a local checkout
- AI-assisted sessions that need a stable shell entrypoint
- Maintainers who need deterministic wrapper tests before changing CLI behavior

## Required Behavior

### Command Surface

The CLI must expose these top-level commands:

- `run`
- `implement`
- `check`
- `align`
- `backfill`
- `plan`
- `polish`
- `next`
- `review`
- `experiment`
- `tracker`
- `help`

### Execution Model

- `run` must continue only while true ready work exists, then call `check` when
  the queue drains.
- `implement` must execute one bounded implementation pass.
- `check` must return a `NEXT_ACTION` code used to decide whether to implement,
  align, backfill, wait, ask for guidance, or stop.
- `run` must treat `NEXT_ACTION` as authoritative:
  - `IMPLEMENT`: continue with the next bounded implementation pass.
  - `ALIGN`: run the alignment workflow once, then re-evaluate queue state.
  - `BACKFILL`: stop and surface the explicit `helix backfill <scope>` command
    before execution resumes.
  - `WAIT`: stop without attempting implementation.
  - `GUIDANCE`: stop and surface the required decision.
  - `STOP`: stop because no actionable work remains.
- Only successfully completed implementation passes count as completed cycles.
- Failed implementation attempts, reviews, alignment, backfill, and recovery
  retries must not be counted as completed cycles.
- After each successful implementation pass, `run` must perform a fresh-eyes
  review before advancing to the next cycle.
- A review with findings must be surfaced as actionable follow-up before the
  loop advances.

### Tracker Model

- The CLI must expose a built-in tracker at `helix tracker`.
- Tracker data must live in `.helix/issues.jsonl`.
- Ready work must be determined from open issues whose dependencies are all
  closed.
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

- `scripts/install-local-skills.sh` must install the HELIX skills into Codex and
  Claude skill directories.
- The installer must create `~/.local/bin/helix` as a launcher that invokes the
  repository's `scripts/helix`.

## Acceptance Criteria

- Running `helix help` shows the command surface and key options.
- Running `helix tracker` subcommands supports create/show/update/close/list,
  ready/blocked queries, dependency management, and status summaries.
- Running `helix run` follows the explicit `NEXT_ACTION` contract for
  `IMPLEMENT`, `ALIGN`, `BACKFILL`, `WAIT`, `GUIDANCE`, and `STOP`.
- Running `helix run` does not attempt implementation after `WAIT`.
- Running `helix run` stops and surfaces the exact backfill command after
  `BACKFILL`.
- Running `helix run` counts only completed implementation passes as completed
  cycles.
- Running `helix run` surfaces review findings before the loop advances.
- Running `helix run` does not discard unrelated worktree changes during
  recovery.
- Running `helix backfill <scope>` enforces the required trailers and durable
  report creation contract.
- Running `bash tests/helix-cli.sh` remains the required deterministic
  verification path for wrapper behavior changes.

## Evidence

- `scripts/helix:40-94`
- `scripts/helix:250-359`
- `scripts/helix:467-519`
- `scripts/helix:542-570`
- `scripts/tracker.sh:7-18`
- `scripts/tracker.sh:52-128`
- `scripts/tracker.sh:265-420`
- `scripts/install-local-skills.sh:35-67`
- `tests/helix-cli.sh:419-447`
- `tests/helix-cli.sh:563-646`
- `tests/helix-cli.sh:744-937`
