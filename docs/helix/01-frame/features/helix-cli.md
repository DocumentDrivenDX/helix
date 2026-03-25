# HELIX Feature Spec: helix-cli

**Status**: backfilled
**Backfill Date**: 2026-03-25
**Scope**: wrapper CLI, built-in tracker, local installer, and deterministic harness

## Summary

`helix-cli` is the repository's operator-facing wrapper around HELIX actions. It
provides one command surface for bounded execution (`run`, `implement`,
`check`, `align`, `backfill`), planning and quality workflows (`plan`,
`polish`, `review`, `experiment`), tracker access (`tracker`), and optional
swarm orchestration (`spawn`).

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
- `spawn`
- `tracker`
- `help`

### Execution Model

- `run` must loop only while true ready work exists, then call `check` when the
  queue drains.
- `implement` must execute one bounded implementation pass.
- `check` must return a `NEXT_ACTION` code used to decide whether to implement,
  align, backfill, wait, ask for guidance, or stop.
- `align` and `backfill` must delegate to their corresponding workflow actions.

### Tracker Model

- The CLI must expose a built-in tracker at `helix tracker`.
- Tracker data must live in `.helix/issues.jsonl`.
- Ready work must be determined from open issues whose dependencies are all
  closed.

### Operator Safeguards

- The experiment flow must require a clean worktree before continuing.
- `spawn` must require `ntm`; when `ntm` is unavailable it must fall back to a
  single-agent `helix run`.
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
