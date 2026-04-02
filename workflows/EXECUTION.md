---
dun:
  id: helix.workflow.execution
  depends_on:
    - helix.workflow
    - helix.workflow.tracker
---
# HELIX Execution Guide

This guide covers operator-facing HELIX execution flow: how to run bounded work
passes, how to decide whether more work remains, and how the HELIX wrapper
controls the queue.

For tracker integration, labels, `spec-id`, and `helix tracker` conventions,
see [TRACKER.md](TRACKER.md).

## Scope

This document owns HELIX execution behavior.

- Follow this file for queue guards, loop shape, and `NEXT_ACTION` handling.
- Follow the bounded action prompts under `workflows/actions/` for
  action-specific behavior.
- Treat examples elsewhere in `workflows/` as supportive summaries, not
  alternate execution contracts.

This is the HELIX-specific layer, not the portable skill packaging layer. Skill
installation lives at `.agents/skills`; queue control and action semantics live
here.

## Core Actions

HELIX supervision is built from bounded actions with distinct roles:

- `helix build`
  Executes one ready execution issue end-to-end, then exits.
- `helix status`
  Reports the persisted run-controller snapshot: current work, blockers, cycle
  timing, token counts, and next recommended action.
- `helix check`
  Performs the queue-drain decision and returns the maintained
  `NEXT_ACTION` vocabulary: build, design, issue refinement,
  alignment, backfill, waiting, guidance, or stopping.
- `helix align <scope>`
  Runs a top-down reconciliation review and can emit follow-up execution issues.
- `helix evolve <requirement>`
  Threads a requirement change through the artifact stack and updates the
  tracker when authority shifts.
- `helix design <scope>`
  Creates or extends the design stack when supervisory routing detects missing
  design authority for the requested scope.
- `helix polish <scope>`
  Refines issue definitions and dependencies when changed specs or stale issue
  metadata would make build unsafe.
- `helix review [scope]`
  Performs fresh-eyes review after build before additional execution
  continues when review automation is enabled.
- `helix triage`
  Creates validated tracker issues with required steering metadata.
- `helix backfill <scope>`
  Reconstructs missing HELIX docs conservatively from current evidence.

## Execution Model

Use a supervisory control loop with an explicit queue-drain sub-step:

1. Guard on true ready work with `helix tracker ready`, not `helix tracker list --ready`
2. Route to the least-power bounded subroutine required by user intent and repository state:
   - `evolve` when a requirement change must propagate through canonical artifacts
   - `design` when requested work lacks sufficient design authority
   - `polish` when governing specs changed and open issues need refinement
   - `build` when safe ready execution work exists
   - `review` after successful build when review automation is enabled
3. When the execution queue drains or supervisory routing needs a queue-health decision, run the bounded `check` action
4. Follow `check` exactly for queue-drain outcomes, without inventing a new code:
   - `BUILD`: continue the build loop
   - `DESIGN`: run one bounded design pass, then re-check
   - `POLISH`: run one bounded issue-refinement pass, then re-check
   - `ALIGN`: run reconciliation once if enabled, then re-check
   - `BACKFILL`: stop and hand off to `helix backfill <scope>`
   - `WAIT`: stop; do not attempt an unblock build pass
   - `GUIDANCE`: stop and ask for user or stakeholder input
   - `STOP`: stop because no actionable work remains

`helix tracker ready` is blocker-aware. `helix tracker list --ready` is not equivalent and should not
control an autonomous execution loop.

`design`, `polish`, and `review` participate in supervisory dispatch. `design` and
`polish` are now explicit `check` `NEXT_ACTION` codes for queue-drain routing;
`review` remains a post-build supervisory step rather than a
queue-drain code.

Execution principles:

- tracker-as-steering-wheel: use tracker primitives, not side channels, to
  redirect execution
- do-hard-things: stay on the active epic and retry governed work with bounded
  exponential backoff before giving up
- cross-model verification: prefer `--review-agent` for post-build review when
  available
- continuous useful work: absorb small adjacent work when clearly required,
  and end with an explicit blocker report when progress stops

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
  helix build
done

helix check
```

Interpret `check` as follows:

- `NEXT_ACTION: BUILD`
  More safe ready work exists; continue.
- `NEXT_ACTION: DESIGN`
  Run `helix design <scope>` once, then re-run `check`.
- `NEXT_ACTION: POLISH`
  Run `helix polish <scope>` once, then re-run `check`.
- `NEXT_ACTION: ALIGN`
  Run `reconcile-alignment` once for the indicated scope if auto-alignment is
  enabled, then re-run `check`.
- `NEXT_ACTION: BACKFILL`
  Stop and hand off to `backfill-helix-docs` for the indicated scope.
- `NEXT_ACTION: WAIT`
  Stop. Do not attempt to build around the blocker or auto-unblock it.
- `NEXT_ACTION: GUIDANCE`
  Stop and get user or stakeholder input.
- `NEXT_ACTION: STOP`
  No actionable work remains for the current scope.

`helix run` is a bounded controller, not a repair loop.

- It counts only completed build passes toward `--max-cycles`.
- It may dispatch `helix design` or `helix polish` before build when
  supervisory state indicates missing design authority or stale issue
  refinement.
- It may run fresh-eyes review after a successful build when review
  automation is enabled; `--no-auto-review` disables that post-implementation
  review.
- It may switch to `--review-agent` for cross-model verification during review.
- It may run `reconcile-alignment` every `N` completed implementation passes
  when `--review-every N` is set; `--no-auto-align` disables that post-drain
  alignment step.
- It may persist run-controller state for `helix status` including current
  issue, focused epic, attempt counters, cycle timing, and token totals.
- It should refresh `.helix/context.md` at run start, on epic switch, and
  every 5 completed implementation passes so long-lived sessions keep current
  build/test commands and tracker counts in view.
- It may stay on a selected epic until completion, then run a scoped post-epic
  review before leaving that scope.
- It should absorb small adjacent work that is clearly part of the current
  governed slice instead of creating avoidable tracker noise.
- It must emit a blocker report when it stops with skipped or intractable
  issues.
- It must capture Codex stdout and stderr together before token extraction so
  observability totals do not silently drop stderr-only token footers.
- It should batch related issues by shared parent or `spec-id`, and fall back
  to shared `area:*` labels when tracker data has no parent/spec sibling
  structure.
- It must not auto-dispatch backfill.
- It must not attempt an unblock build pass after `WAIT`.
- If a run is interrupted, recovery must be issue-scoped and non-destructive:
  do not clear a claim, revert files, or touch unrelated work without tracker
  evidence that the abandoned work belongs to that issue.
- After a failed or timed-out implementation attempt, retry is allowed only
  after issue-scoped cleanup leaves the worktree clean or the wrapper stops
  with a blocker; stale claims must be released before a fresh retry.

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
- `helix status`
- `helix build`
- `helix check`
- `helix align`
- `helix evolve`
- `helix design`
- `helix triage`
- `helix backfill`

`helix run`:

- loops only while true ready HELIX execution work exists
- routes to `helix design` or `helix polish` when supervisory state requires
  bounded design or issue refinement before build can resume
- runs one bounded build pass at a time
- runs `check` when the queue drains
- can trigger `reconcile-alignment` every `N` completed build passes
  or when `check` returns `ALIGN`
- may run `helix review` after each successful build pass when review
  automation is enabled; review findings are filed as tracker issues with
  label `review-finding` and the loop continues
- files acceptance check failures as tracker issues with label
  `acceptance-failure` instead of only logging to stderr
- may use `--review-agent` for cross-model review
- can stay focused on one epic through decomposition, child execution, and
  post-epic scoped review
- stops on `WAIT`, `BACKFILL`, `GUIDANCE`, or `STOP`
- uses the built-in tracker for queue state
- does not attempt an unblock build pass after `WAIT`
- does not auto-dispatch `helix backfill`
- treats interrupted runs as recoverable only when the abandoned work can be
  attributed safely and without reverting unrelated changes
- writes blocker reports and persisted lifecycle state for `helix status`

Examples:

```bash
helix run
helix run --review-every 5
helix status
helix check repo
helix align auth
helix design auth
```

## Reproducible Testing

The wrapper should be tested with deterministic command stubs rather than live
agent sessions.

Run:

```bash
bash tests/helix-cli.sh
```

This harness:

- creates temporary git workspaces
- stubs `helix tracker` and agent command execution
- drives exact ready-queue and `NEXT_ACTION` sequences
- verifies `helix run`, periodic alignment, auto-alignment, dry-run output, and
  installer behavior

## Pre-Execution Pipeline

Before the implementation loop, the recommended sequence for new work is:

1. `helix design [scope]` — create a comprehensive design document through
   iterative refinement (recommended for new features or major work)
2. `helix polish [scope]` — refine issues against the plan: deduplication,
   coverage verification, acceptance criteria sharpening (recommended after
   issue creation)
3. `helix run` — execute the bounded build loop

The public command names for this sequence are `helix design`, `helix polish`,
and `helix run`.

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

Review findings are durable: the review action files each actionable finding
as a tracker issue with label `review-finding`. The run loop continues after
review rather than stopping, because the findings are now in the tracker and
will surface via `helix tracker list --label review-finding` or
`helix tracker ready` once they are ready for implementation.

Similarly, when acceptance checks fail in the run loop, the specific failures
are filed as tracker issues with label `acceptance-failure` so they appear in
the ready queue for the next cycle.

Operators can query and manage these findings like any other issue:

```bash
helix tracker list --label review-finding    # all unresolved review findings
helix tracker list --label acceptance-failure # all unresolved acceptance failures
helix tracker close <id>                     # resolve a finding
```

## Experiment Loop

`helix experiment` runs a single iteration of a metric-optimization loop for
`phase:iterate` issues. Each invocation: hypothesize → edit → test → benchmark →
keep/discard → log → exit.

The loop is driven externally by the `helix-experiment` skill or by the
operator re-invoking the command. This preserves the bounded-action model.

Experiments are operator-invoked only — `helix check` does not produce a
`NEXT_ACTION: EXPERIMENT` code. The operator chooses `helix experiment` instead
of `helix build` for optimization work.

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
