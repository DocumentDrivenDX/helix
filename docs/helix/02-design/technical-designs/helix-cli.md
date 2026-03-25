# HELIX Technical Design: helix-cli

**Status**: backfilled
**Backfill Date**: 2026-03-25

## Design Goal

Provide a thin Bash wrapper that keeps HELIX execution bounded, delegates deep
work to documented actions, and gives the repository a local tracker and
launcher without requiring operators to assemble prompts manually.

## Components

### 1. Wrapper Entry Script

`scripts/helix` resolves the repository root, selects the workflow library
root, sources the tracker library, opens a session log, parses CLI flags, and
dispatches commands.

### 2. Prompt Builders

Each agent-facing command builds a prompt that points at the authoritative
workflow action file and injects repository-local instructions such as tracker
usage and required output trailers.

### 3. Agent Runner

`run_agent_prompt` supports both Codex and Claude. It prints dry-run commands,
streams Claude progress when possible, and enforces an agent timeout.

### 4. Built-In Tracker Library

`scripts/tracker.sh` stores issues as JSONL in `.helix/issues.jsonl`. It
provides creation, read/update/close flows, dependency management, ready and
blocked queue queries, and tracker health summaries using `jq`.

### 5. Loop Controller

`run_loop` is the orchestration layer for `helix run`. It:

- checks ready work before implementation
- runs one bounded implementation pass at a time
- calls `check` after the queue drains
- can auto-run alignment after `ALIGN`
- can attempt one unblock pass after `WAIT`
- can trigger periodic alignment with `--review-every`

### 6. Installer

`scripts/install-local-skills.sh` links the HELIX skills into Codex and Claude
skill directories, makes `scripts/helix` executable, and installs a local
`helix` launcher under `~/.local/bin`.

### 7. Deterministic Test Harness

`tests/helix-cli.sh` creates temporary git workspaces, stubs agent binaries,
seeds tracker state, and verifies command behavior without relying on live
agent sessions.

## Data and Filesystem Surfaces

- Workflow docs root: `workflows/`
- Tracker state: `.helix/issues.jsonl`
- Session logs: `.helix-logs/helix-YYYYMMDD-HHMMSS.log`
- Installed launcher: `~/.local/bin/helix`
- Installed skill links: `${CODEX_HOME:-$HOME/.codex}/skills`,
  `${CLAUDE_HOME:-$HOME/.claude}/skills`

## External Dependencies

- Required for normal operation: `bash`, `jq`
- Required per agent choice: `codex` or `claude`
- Optional for swarm mode: `ntm`, `tmux`

## Constraints

- The wrapper is intentionally bounded; it is not allowed to replace the HELIX
  loop with an unconditional `while true`.
- Tracker readiness is dependency-aware.
- Experiment mode must refuse dirty worktrees.
- Backfill must fail if the report trailer is missing or the declared report
  file does not exist.

## Evidence

- `scripts/helix:15-37`
- `scripts/helix:109-239`
- `scripts/helix:250-359`
- `scripts/helix:381-519`
- `scripts/helix:542-570`
- `scripts/helix:677-760`
- `scripts/tracker.sh:7-49`
- `scripts/tracker.sh:52-224`
- `scripts/tracker.sh:265-420`
- `scripts/install-local-skills.sh:4-67`
- `tests/helix-cli.sh:46-176`
- `tests/helix-cli.sh:347-414`
- `tests/helix-cli.sh:571-646`
