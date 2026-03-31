# Technical Design: TD-002-helix-cli

**Status**: backfilled
**Backfill Date**: 2026-03-25

## Story Reference

**User Story**: [HELIX CLI wrapper execution] | **Feature**: [FEAT-002-helix-cli] | **Solution Design**: [SD-001-helix-supervisory-control]

## Acceptance Criteria Review

- The wrapper keeps HELIX execution bounded.
- Queue-drain decisions follow the documented control contract.
- Tracker-backed execution remains deterministic and testable.
- Local installation exposes the mirrored HELIX command surface safely.

## Technical Approach
Provide a thin Bash wrapper that keeps HELIX execution bounded, delegates deep
work to documented actions, and gives the repository a local tracker and
launcher without requiring operators to assemble prompts manually.

This design defines the orchestration contract for `helix run`. The wrapper is
not allowed to invent its own workflow policy; it must execute the HELIX
decision model exactly as specified by the authority stack.

## Orchestration Contract

`helix run` is a bounded supervisor around HELIX queue state.

- It always starts from tracker-backed ready work, not from assumptions about
  in-progress work.
- It executes at most one build issue per pass.
- It treats `check` as the source of next-step guidance after the ready queue
  drains.
- It revalidates selected issue state at safe boundaries so concurrent local
  refinement does not lead to stale claim or close behavior.
- It keeps alignment and backfill as distinct follow-up actions.
- It does not auto-build blocked work on `WAIT`.
- It does not silently continue after a review failure.
- It persists run-controller state so `helix status` can report lifecycle
  progress, cycle timing, focused epic, blocked work, and token usage.
- It prefers cross-model verification when `--review-agent` is configured.
- It stays focused on a chosen epic until the epic completes or a blocker is
  recorded.

## Component Changes

### Modified: Wrapper entry and run loop
- **Current State**: Bash wrapper around HELIX actions.
- **Changes**: Enforce bounded execution, queue-drain checks, and review-aware
  cycle control.

### Modified: Tracker integration
- **Current State**: Local JSONL issue tracker.
- **Changes**: Dependency-aware ready/blocked selection, ownership, and
  recovery-aware orchestration.

### Modified: Installer and harness
- **Current State**: Local launcher and deterministic wrapper tests.
- **Changes**: Keep mirrored command install and deterministic verification in
  sync with the wrapper contract.

## State Machine

### Ready Work

When `helix tracker ready --json` reports one or more ready execution issues:

1. Select the best ready execution issue using the tracker ranking rules.
2. Re-read the issue and verify it is still a safe execution target.
3. Claim the issue.
4. Run one bounded build pass for that issue.
5. Re-read the issue before close and verify no material queue drift or
   supersession invalidates the close.
6. Verify, commit, and close it when the issue is complete.
7. Count the pass as a completed cycle only if the issue actually closes.

### Queue Drain

When the ready queue is empty, `helix run` must execute `check` once and obey
the first `NEXT_ACTION` result exactly:

- `NEXT_ACTION: BUILD`
  Re-enter ready-work selection and continue only if the tracker now reports
  ready execution work.
- `NEXT_ACTION: DESIGN`
  Run one bounded design pass, then re-check queue state before any
  build resumes.
- `NEXT_ACTION: POLISH`
  Run one bounded issue-refinement pass, then re-check queue state before any
  build resumes.
- `NEXT_ACTION: ALIGN`
  Run one alignment pass if auto-alignment is enabled. If the follow-up check
  still returns `ALIGN`, stop and surface the alignment command rather than
  looping forever.
- `NEXT_ACTION: BACKFILL`
  Stop and surface the explicit `helix backfill <scope>` command. Backfill is a
  separate cross-phase action and is not auto-run by `helix run`.
- `NEXT_ACTION: WAIT`
  Stop immediately. `WAIT` means execution is blocked by claimed work or a
  truly external dependency; `helix run` must not attempt an unblock build
  pass.
- `NEXT_ACTION: GUIDANCE`
  Stop immediately and surface the required user or stakeholder decision.
- `NEXT_ACTION: STOP`
  Stop cleanly because no actionable work remains for the scope.

### Cycle Accounting

The loop must distinguish between attempted work and completed work.

- `attempted_cycles`: increment when the wrapper starts a build
  attempt.
- `completed_cycles`: increment only after build succeeds, the issue
  is closed, and post-implementation review passes when review is enabled.
- `--review-every N` and `--max-cycles N` must use `completed_cycles`, not
  attempted cycles.
- Failed build attempts do not count toward the cycle limit.
- `cycle_start`, `cycle_end`, `cycle_duration`, and `total_tokens` belong in
  persisted run-controller state and in the loop's progress output.

## Recovery and Ownership

`helix run` needs a safe recovery model for crashed or orphaned sessions.

### Ownership Model

Claimed work is advisory state in the tracker, not a license to rewrite the
worktree blindly.

- A claimed execution issue is represented by `status: in_progress` and
  `assignee: helix`.
- The recommended tracker model should also record claim freshness metadata:
  `claimed_at`, `session_id`, and `lease_expires_at`.
- Recovery may only reclaim work when the claim is demonstrably stale or when
  the user explicitly requests recovery.
- Absence of a currently running process is not sufficient evidence that a
  claim is orphaned.

### Recovery Rules

Recovery must be non-destructive by default.

- If the current session owns the claim, resume from the existing worktree
  state.
- If the claim is stale and the worktree changes are clearly attributable to
  the abandoned issue, the wrapper may ask the agent to finish or cleanly
  revert only the affected files.
- The wrapper must not perform a broad `git checkout -- .` or otherwise erase
  unrelated local changes.
- If ownership is ambiguous, the wrapper must stop and surface the blocker
  rather than guessing.
- Recovery results should be visible in the issue notes or a follow-on
  diagnostic issue when cleanup is required.

## Concurrent Interactive Refinement

`helix run` must support the local operating mode where one session advances
execution while another session refines specs or tracker issues.

### Material Queue Drift

Material drift includes any change that can invalidate execution authority or
completion status for the currently selected issue:

- changed `spec-id`
- changed dependencies
- changed parent or replacement relationship
- superseded execution issue
- execution-eligibility change that removes the issue from the runnable set

### Revalidation Rules

- Before claim:
  - re-read the issue and verify it is still runnable
  - if materially changed, skip claim and return to queue evaluation
- Before close:
  - re-read the issue and verify it has not been superseded or structurally
    invalidated
  - if materially changed, do not close it from stale assumptions; stop, reopen
    the decision path, or create follow-up work as appropriate

### Execution Eligibility

The wrapper must distinguish execution-safe work from general open work so
interactive refinement issues do not get treated as build targets by
accident.

## Review Handling

Post-build review is part of the orchestration contract.

- A clean review allows the loop to continue.
- Review findings must create or reopen follow-up work before the loop
  advances to the next issue.
- Review should be machine-readable enough for the wrapper to distinguish
  `CLEAN` from actionable findings.
- If review cannot be interpreted safely, the loop must stop instead of
  assuming success.
- When `--review-agent` is configured, review must run under the alternate
  model rather than the implementation model.
- When an epic closes, the loop must run a scoped post-epic review against the
  epic's governing artifact before releasing focus.

## Blockers And Work Absorption

- Small adjacent work discovered while satisfying the same governing
  acceptance, such as related manifest updates or directly coupled file edits,
  should be absorbed into the current issue instead of spawning avoidable
  tracker noise.
- Work that is adjacent but not clearly required by the current acceptance
  must still become separate follow-up issues.
- When the loop exits with skipped or intractable work, it must emit a blocker
  report that names the issue, reason, attempts, and any epic-level impact.

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
For this design, it is also the source of truth for claim ownership and claim
freshness metadata when the tracker schema is extended.

### 5. Loop Controller

`run_loop` is the orchestration layer for `helix run`. It:

- checks ready work before implementation
- persists run-controller state for status and observability
- revalidates the selected issue immediately before claim and before close
- runs one bounded build pass at a time
- calls `check` after the queue drains
- honors `DESIGN` and `POLISH` queue-drain results before build resumes
- can auto-run alignment once after `ALIGN`
- stops on `WAIT`, `GUIDANCE`, or `STOP`
- stops on `BACKFILL` and surfaces the explicit follow-up command
- can trigger periodic alignment with `--review-every` using completed cycles
- uses epic focus, bounded exponential backoff, and blocker reporting to keep
  useful work moving without losing traceability
- must not attempt an unblock build pass after `WAIT`

### 6. Installer

`scripts/install-local-skills.sh` links the HELIX skill entrypoints into
`~/.agents/skills`, mirrors them into `~/.claude/skills` for Claude
compatibility, preserves package-relative access back to the repository's
shared `workflows/` library, makes `scripts/helix` executable, and installs a
local `helix` launcher under `~/.local/bin`.

### 7. Deterministic Test Harness

`tests/helix-cli.sh` creates temporary git workspaces, stubs agent binaries,
seeds tracker state, and verifies command behavior without relying on live
agent sessions.

## Data and Filesystem Surfaces

- Workflow docs root: `workflows/`
- Tracker state: `.helix/issues.jsonl`
- Session logs: `.helix-logs/helix-YYYYMMDD-HHMMSS.log`
- Run-controller state: `.helix/run-state.json`
- Blocker reports: `.helix-logs/blockers-YYYYMMDD-HHMMSS.md`
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
- `WAIT` is a terminal orchestration result, not a cue to try another
  implementation pass.
- Recovery must preserve unrelated local changes and may not rely on process
  absence alone.

## Evidence

- `scripts/helix:15-37`
- `scripts/helix:109-239`
- `scripts/helix:250-359`
- `scripts/helix:381-519`
- `scripts/helix:542-570`
- `scripts/helix:579-784`
- `scripts/tracker.sh:7-49`
- `scripts/tracker.sh:52-224`
- `scripts/tracker.sh:265-420`
- `scripts/install-local-skills.sh:4-67`
- `tests/helix-cli.sh:46-176`
- `tests/helix-cli.sh:347-414`
- `tests/helix-cli.sh:571-646`
