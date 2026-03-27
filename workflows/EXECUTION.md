---
dun:
  id: helix.workflow.execution
  depends_on:
    - helix.workflow
    - helix.workflow.tracker
---
# HELIX Execution Guide

This guide covers operator-facing HELIX execution flow: how to run bounded work
passes, how to decide whether more work remains, and how to automate the queue
for Codex or Claude Code.

For tracker integration, labels, `spec-id`, and `helix tracker` conventions,
see [TRACKER.md](TRACKER.md).

## Scope

This document owns HELIX execution behavior.

- Follow this file for queue guards, loop shape, and `NEXT_ACTION` handling.
- Follow the bounded action prompts under `workflows/actions/` for
  action-specific behavior.
- Treat examples elsewhere in `workflows/` as supportive summaries, not
  alternate execution contracts.

## Core Actions

HELIX uses four top-level execution actions:

- `helix implement`
  Executes one ready execution issue end-to-end, then exits.
- `helix check`
  Determines whether the next step is implementation, alignment, backfill,
  waiting, guidance, or stopping.
- `helix align <scope>`
  Runs a top-down reconciliation review and can emit follow-up execution issues.
- `helix backfill <scope>`
  Reconstructs missing HELIX docs conservatively from current evidence.

## Execution Model

Use a two-stage control loop:

1. Guard on true ready work with `helix tracker ready`, not `helix tracker list --ready`
2. Run the bounded `implementation` action while ready work exists
3. When the queue drains, run the bounded `check` action once
4. Follow `check` exactly, without inventing a new state:
   - `IMPLEMENT`: continue the implementation loop
   - `ALIGN`: run reconciliation once if enabled, then re-check
   - `BACKFILL`: stop and hand off to `helix backfill <scope>`
   - `WAIT`: stop; do not attempt an unblock implementation pass
   - `GUIDANCE`: stop and ask for user or stakeholder input
   - `STOP`: stop because no actionable work remains

`helix tracker ready` is blocker-aware. `helix tracker list --ready` is not equivalent and should not
control an autonomous execution loop.

## Queue Guard

These examples assume `jq` is available.

```bash
helix_ready_count() {
  helix tracker ready --json | jq 'length'
}
```

## Manual Loop

This is the minimal safe operator loop:

```bash
while [ "$(helix_ready_count)" -gt 0 ]; do
  helix implement
done

helix check
```

Interpret `check` as follows:

- `NEXT_ACTION: IMPLEMENT`
  More safe ready work exists; continue.
- `NEXT_ACTION: ALIGN`
  Run `reconcile-alignment` once for the indicated scope if auto-alignment is
  enabled, then re-run `check`.
- `NEXT_ACTION: BACKFILL`
  Stop and hand off to `backfill-helix-docs` for the indicated scope.
- `NEXT_ACTION: WAIT`
  Stop. Do not attempt to implement around the blocker or auto-unblock it.
- `NEXT_ACTION: GUIDANCE`
  Stop and get user or stakeholder input.
- `NEXT_ACTION: STOP`
  No actionable work remains for the current scope.

`helix run` is a bounded controller, not a repair loop.

- It counts only completed implementation passes toward `--max-cycles`.
- It may run fresh-eyes review after a successful implementation when review
  automation is enabled; `--no-auto-review` disables that post-implementation
  review.
- It may run `reconcile-alignment` every `N` completed implementation passes
  when `--review-every N` is set; `--no-auto-align` disables that post-drain
  alignment step.
- It must not auto-dispatch backfill.
- It must not attempt an unblock implementation pass after `WAIT`.
- If a run is interrupted, recovery must be issue-scoped and non-destructive:
  do not clear a claim, revert files, or touch unrelated work without tracker
  evidence that the abandoned work belongs to that issue.

## Agent Loops

The examples below assume a trusted local repository.

- Codex is intentionally run with `--dangerously-bypass-approvals-and-sandbox`
  and `--progress-cursor`.

### Codex

```bash
while [ "$(helix_ready_count)" -gt 0 ]; do
  codex --dangerously-bypass-approvals-and-sandbox exec --progress-cursor -C "$PWD" --ephemeral <<'EOF'
Use the HELIX implementation action at workflows/actions/implementation.md.
Execute one ready HELIX execution issue end-to-end.
Follow the action exactly.
EOF
done

codex --dangerously-bypass-approvals-and-sandbox exec --progress-cursor -C "$PWD" --ephemeral <<'EOF'
Use the HELIX check action at workflows/actions/check.md.
Return the required NEXT_ACTION line and the exact next command.
Follow the action exactly.
EOF
```

### Claude Code

```bash
while [ "$(helix_ready_count)" -gt 0 ]; do
  claude -p \
    --permission-mode bypassPermissions \
    --dangerously-skip-permissions \
    --no-session-persistence <<'EOF'
Use the HELIX implementation action at workflows/actions/implementation.md.
Execute one ready HELIX execution issue end-to-end.
Follow the action exactly.
EOF
done

claude -p \
  --permission-mode bypassPermissions \
  --dangerously-skip-permissions \
  --no-session-persistence <<'EOF'
Use the HELIX check action at workflows/actions/check.md.
Return the required NEXT_ACTION line and the exact next command.
Follow the action exactly.
EOF
```

## `helix run`

This repo also provides a small wrapper CLI at `scripts/helix`.

To expose it on your `PATH` locally:

```bash
scripts/install-local-skills.sh
```

That installer now also links `~/.local/bin/helix` to this repo's wrapper.
HELIX's canonical project-level skill package surface lives at
`./.agents/skills`. The installer installs those skills to `~/.agents/skills`
and mirrors them to `~/.claude/skills` for Claude compatibility.

Main commands:

- `helix run`
- `helix implement`
- `helix check`
- `helix align`
- `helix backfill`

`helix run`:

- loops only while true ready HELIX execution work exists
- runs one bounded implementation pass at a time
- runs `check` when the queue drains
- can trigger `reconcile-alignment` every `N` completed implementation passes
  or when `check` returns `ALIGN`
- may run `helix review` after each successful implementation pass when review
  automation is enabled
- stops on `WAIT`, `BACKFILL`, `GUIDANCE`, or `STOP`
- uses `codex --dangerously-bypass-approvals-and-sandbox exec
  --progress-cursor` when `--agent codex` is selected
- uses the built-in tracker for queue state
- does not attempt an unblock implementation pass after `WAIT`
- does not auto-dispatch `helix backfill`
- treats interrupted runs as recoverable only when the abandoned work can be
  attributed safely and without reverting unrelated changes

Examples:

```bash
helix run
helix run --agent claude
helix run --review-every 5
helix check repo
helix align auth
```

## Reproducible Testing

The wrapper should be tested with deterministic command stubs rather than live
Codex or Claude sessions.

Run:

```bash
bash tests/helix-cli.sh
```

This harness:

- creates temporary git workspaces
- stubs `helix tracker`, `codex`, and `claude`
- drives exact ready-queue and `NEXT_ACTION` sequences
- verifies `helix run`, periodic alignment, auto-alignment, dry-run output, and
  installer behavior

## Pre-Execution Pipeline

Before the implementation loop, the recommended sequence for new work is:

1. `helix plan [scope]` — create a comprehensive design document through
   iterative refinement (recommended for new features or major work)
2. `helix polish [scope]` — refine issues against the plan: deduplication,
   coverage verification, acceptance criteria sharpening (recommended after
   issue creation)
3. `helix run` — execute the bounded implementation loop

These steps are optional for small changes but strongly recommended for any
scope that will produce more than a handful of issues.

## Next Issue

`helix next` prints the recommended next issue without spawning an agent:

```bash
helix next          # uses helix tracker ready ranking
```

## Fresh-Eyes Review

After implementing an issue, `helix review` performs 1-3 self-review passes
looking for bugs, integration issues, and security concerns with fresh
perspective:

```bash
helix review                  # review last commit
helix review ddx-abc123       # review changes for a specific issue
helix review src/auth/        # review specific files
```

Review findings are advisory for the loop controller unless they produce
follow-up work or a failing verification result.

## Experiment Loop

`helix experiment` runs a single iteration of a metric-optimization loop for
`phase:iterate` issues. Each invocation: hypothesize → edit → test → benchmark →
keep/discard → log → exit.

The loop is driven externally by the `helix-experiment` skill or by the
operator re-invoking the command. This preserves the bounded-action model.

Experiments are operator-invoked only — `helix check` does not produce a
`NEXT_ACTION: EXPERIMENT` code. The operator chooses `helix experiment` instead
of `helix implement` for optimization work.

The experiment action requires a clean worktree. The CLI prompts the user to
commit uncommitted changes before proceeding.

The optimization target is a HELIX metric definition at
`docs/helix/06-iterate/metrics/<name>.yaml`. If one exists, the experiment
reads it; if not, the experiment creates one during setup. This connects
experiments to ratchets and monitoring through a shared metric definition.

Session artifacts (`autoresearch.*`, `experiments/`) are untracked local files,
gitignored on the experiment branch. At session close (`helix experiment
--close`), the action squash-merges the experiment branch back to produce a
single commit and records the result in the issue close comment. Experiments
are execution-layer work tracked by issues, not canonical HELIX docs.

`--close` is unique to the experiment command — it directs the action to
execute session close (squash-merge, ratchet update, issue close) instead of
running another iteration.

Experiments validate governing artifacts at session setup and close (not
per-iteration). Per-iteration guardrails are: scoped files, mandatory test
passage, and the experiment's own constraints. All existing tests must pass
after every kept iteration.

## Practical Rules

- Keep execution bounded to one issue per implementation pass.
- Do not use an unconditional `while true` loop.
- Treat `check` as the queue-drain decision point, not `reconcile-alignment`.
- Use alignment to expose or refine the next work set, not as the default work
  picker.
- Do not auto-run backfill unless you are intentionally reconstructing missing
  canonical docs.
