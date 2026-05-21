---
ddx:
  id: helix.workflow.execution
  depends_on:
    - helix.workflow
    - helix.workflow.tracker
  review:
    self_hash: a975b0523a9037c2d769321e86af0eb3d804cfc143035562c5f40944d8349504
    deps:
      helix.workflow: 1225132b3050598055eacb5462639824d78ac204cca2cbeda3611766532e79c8
      helix.workflow.tracker: b1d3c681bb7f58276c6a81fe90cd7afd3143d11f49ed8889bf879ac84d05d312
    reviewed_at: "2026-05-15T04:11:24Z"
---
# HELIX Execution Guide (DDx Reference Runtime)

**Scope note.** This document is the DDx reference-runtime integration guide
for HELIX execution. It describes operator-facing HELIX execution flow when
HELIX runs under DDx: how to run bounded work passes, how to decide whether
more work remains, and how the DDx runtime controls the queue.

For runtime-neutral methodology — the artifact loop, authority order, the
methodology actions, and the alignment contract — read [README.md](README.md)
and [REFERENCE.md](REFERENCE.md) first. Other runtimes implementing HELIX
should provide their own equivalent execution-integration document; the
methodology requirements (bead-first, tracker-as-steering-wheel,
measure-and-record, report-and-feed-back) apply to every runtime, but the
command names and substrate below are DDx-specific.

For DDx tracker integration, labels, `spec-id`, and `ddx bead` conventions,
see `ddx bead --help` (DDx FEAT-004).

## Document Scope

This document owns DDx-runtime HELIX execution behavior.

- Follow this file for queue guards, loop shape, and `NEXT_ACTION` handling
  under DDx.
- Follow the bounded action prompts under `actions/` for action-specific
  behavior.
- Treat examples elsewhere in the workflows package as supportive summaries,
  not alternate execution contracts.

This is the HELIX-on-DDx integration layer, not the portable skill packaging
layer. Skill installation lives at `.agents/skills`; DDx queue control and
action semantics live here.

## The Double Helix

HELIX is built from two interleaved cycles — the double helix:

### Planning Helix

Identification and improvement of plans in bead format.

```
Review → Plan → Validate → (ready beads)
```

- **Review**: Assess current state (`check`, `align`). What work exists? What's
  missing? What concerns aren't threaded?
- **Plan**: Create or refine plan beads with consolidated context (`design`,
  `polish`, `evolve`, `triage`). Every plan bead consolidates inputs,
  cross-cutting concerns, current state, and acceptance criteria.
- **Validate**: Verify plan quality — are beads well-specified? Are concerns
  threaded? Are dependencies correct? Are acceptance criteria testable? This is
  what `polish` refinement passes do.

Output: a queue of well-specified, concern-threaded beads ready for execution.

### Execution Helix

Executing plans to update documents, reconcile artifacts, research next-stage
plans, implement code, test it, and optimize metrics.

```
Execute → Measure → Report → (new beads)
```

- HELIX models each governed execution step as a workspace-state
  transformation. Given workspace state `W`, executing bead `B` attempts to
  produce successor workspace state `W'`.
- Shorthand: `B : W -> W'`
- The bead is the intended transformation, not the evidence record.
- The execution run is the bounded attempt and evidence record for trying to
  realize `W -> W'`.
- The execution outcome records how that attempt landed (`merged`,
  `preserved`, `blocked`, `failed`, or equivalent workflow-visible result).
- The realized state delta is the material change between `W` and `W'`:
  docs, code, tracker state, generated artifacts, and other workspace changes.

- **Execute**: Claim a bead, do the work it describes (`build`, `review`,
  `experiment`, `backfill` — any action that modifies files on disk).
- **Measure**: Verify results against the bead's acceptance criteria. Run
  concern-declared quality gates. Run ratchets. Record results on the bead.
- **Report**: Analyze measurement results. Open new beads for issues found,
  regressions, or follow-on work. Close the executed bead with evidence. New
  beads feed back into the planning helix.

### Crossover

The helices interleave at two points:

1. **Planning → Execution**: Ready beads move from the planning helix to the
   execution queue.
2. **Execution → Planning**: Report creates new beads that enter the planning
   helix for refinement.

`/helix check` is the crossover point — it reads both helices and decides
which one needs attention next. It already does this implicitly (`BUILD` vs
`DESIGN`/`POLISH`/`ALIGN`), but the double-helix model makes the two cycles
explicit.

### Bead-First Principle

**Every action that modifies files must be governed by a bead.** No file
modifications without a plan bead — analogous to entering plan mode before
writing code.

Operationally, a bead should describe the intended transformation from current
workspace state `W` to successor workspace state `W'`. `measure` determines
whether the resulting `W'` satisfies the bead's acceptance criteria and quality
gates. `report` records evidence about the `W -> W'` transition and creates any
required follow-on beads.

Every action (except `triage` and `check`) follows this structure:

1. **Bead acquisition**: Find or create the governing bead for this work.
2. **Execution**: Do the work the bead describes.
3. **Measure**: Verify results and record evidence on the bead.
4. **Report**: Create follow-on beads and close the governing bead.

`triage` is the entry point that bootstraps the bead graph — it creates beads
and therefore cannot itself require one (that would be infinite regress).
`input` is also an entry point: it accepts sparse intent and creates or updates
the bead/workflow context that later actions execute. `check` is read-only and
does not modify files.

Planning-helix beads use the `kind:planning` label to distinguish them from
execution beads. Combined with an `action:<name>` label (e.g.,
`action:design`, `action:polish`), this makes the governing bead's purpose
visible in the tracker.

See `.ddx/plugins/helix/workflows/references/bead-first.md` for the full bead acquisition pattern,
`.ddx/plugins/helix/workflows/references/measure.md` for measurement recording, and
`.ddx/plugins/helix/workflows/references/report.md` for the report activity.

## Core Actions

HELIX supervision is built from bounded actions with distinct roles. Operators
invoke them through the unified `/helix <mode>` skill or DDx commands:

- `/helix input "<natural language request>" [--autonomy low|medium|high]`
  Accepts sparse intent, applies HELIX autonomy semantics, and creates or
  updates the bead/workflow context needed for later execution. This is the
  planning-helix intake surface for the slider-autonomy model; the expected
  default autonomy is `medium`.
- `ddx bead execute <id>` (build mode)
  Executes one ready execution issue end-to-end, then exits.
- `/helix check`
  Performs the queue-drain decision and returns the maintained
  `NEXT_ACTION` vocabulary: build, design, issue refinement,
  alignment, backfill, waiting, guidance, or stopping.
- `/helix align <scope>`
  Convenience entrypoint for a top-down reconciliation review. It first
  creates or claims the governing `kind:planning,action:align` bead, then
  runs the stored alignment prompt and emits properly ordered follow-on beads.
- `/helix evolve <requirement>`
  Threads a requirement change through the artifact stack and updates the
  tracker when authority shifts.
- `/helix design <scope>`
  Creates or extends the design stack when supervisory routing detects missing
  design authority for the requested scope.
- `/helix polish <scope>`
  Decomposes design plans into implementable beads, then refines issue
  definitions and dependencies. This is the mandatory step between design and
  build — without it, agents attempt ad-hoc decomposition during implementation.
- `/helix review [scope]`
  Performs fresh-eyes review after build before additional execution
  continues when review automation is enabled.
- `/helix measure [bead-id|scope]`
  Runs acceptance criteria, concern-declared quality gates, and ratchet
  enforcement against a bead or scope. Records results on the bead. Can be
  invoked standalone or runs as an embedded activity within other actions.
- `/helix report [bead-id|scope]`
  Analyzes measurement results, creates follow-on beads for identified work,
  and closes the governing bead with evidence. Per-bead by default; batch mode
  aggregates across a scope.
- `ddx bead create "Title" --type task ...`
  Creates tracker issues. This is the entry point that bootstraps the bead
  graph — the one action that does not require a governing bead.
- `/helix backfill <scope>`
  Reconstructs missing HELIX docs conservatively from current evidence.

## Execution Model

Use a supervisory control loop with an explicit queue-drain sub-step.

For sparse operator intent that is not yet represented as a bead or bounded
scope, start with `/helix input` before entering the normal execution loop.
`/helix input` shapes intent into governed work; `ddx work`, `ddx bead
execute`, and `/helix check` operate on the resulting bead/workflow state.

1. Guard on true ready work with `ddx bead ready`, not `ddx bead list --ready`
2. Route to the least-power bounded subroutine required by user intent and repository state:
   - `evolve` when a requirement change must propagate through canonical artifacts
   - `design` when requested work lacks sufficient design authority
   - `polish` when plans need decomposition into beads, or governing specs changed and open issues need refinement
   - `build` when safe ready execution work exists
   - `review` after successful build when review automation is enabled
3. When the execution queue drains or supervisory routing needs a queue-health decision, run the bounded `check` action
4. Follow `check` exactly for queue-drain outcomes, without inventing a new code:
   - `BUILD`: continue the build loop
   - `DESIGN`: run one bounded design pass, then re-check
   - `POLISH`: run one bounded issue-refinement pass, then re-check
   - `ALIGN`: run reconciliation once if enabled, then re-check
   - `BACKFILL`: stop and hand off to `/helix backfill <scope>`
   - `WAIT`: stop; do not attempt an unblock build pass
   - `GUIDANCE`: stop and ask for user or stakeholder input
   - `STOP`: stop because no actionable work remains

`ddx bead ready` is blocker-aware. `ddx bead list --ready` is not equivalent and should not
control an autonomous execution loop.

`design`, `polish`, and `review` participate in supervisory dispatch. `design` and
`polish` are now explicit `check` `NEXT_ACTION` codes for queue-drain routing;
`review` remains a post-build supervisory step rather than a
queue-drain code.

`ddx work` is the primary queue-drain substrate for execution-ready beads.
Operator-facing routing and policy decisions live in `/helix <mode>` skill
modes.

Execution principles:

- bead-first: every action that modifies files must have a governing bead
  before execution begins. No ad-hoc file changes without a plan bead.
- tracker-as-steering-wheel: use tracker primitives, not side channels, to
  redirect execution
- queue topology is explicit: if order matters, encode it with parent-child
  structure and dependencies instead of prose or operator memory
- measure-and-record: verification results are recorded on the bead, not just
  logged ephemerally. A closed bead carries its measurement evidence.
- report-and-feed-back: measurement findings create new beads that re-enter the
  planning helix, closing the feedback loop
- do-hard-things: stay on the active epic, prefer DDx-owned cooldown and
  preserve signals as the long-term retry surface, and file deterministic
  follow-on work instead of carrying hidden wrapper heuristics
- cross-model verification: prefer `--review-agent` for post-build review when
  available
- continuous useful work: absorb small adjacent work when clearly required,
  and surface blocked work through tracker state rather than prose-only memory

## Queue Guard

These examples assume `ddx` is available.

```bash
ddx_ready_count() {
  # Strip advisory lines (e.g. upgrade notices) before piping to ddx jq.
  # awk skips lines until the first JSON delimiter, preserving multi-line JSON.
  ddx bead ready --json | awk 'found || /^[{[]/ { found=1; print }' | ddx jq 'length'
}
```

## Manual Loop

This is the canonical operator path once work is execution-ready:

```bash
while [ "$(ddx_ready_count)" -gt 0 ]; do
  ddx work --once
done

/helix check
```

`ddx work` is the durable queue-drain primitive. The `/helix <mode>` skill
modes provide HELIX-owned routing, planning, review, and reconciliation
around it.

### Architecture

HELIX owns **queue curation**: maintaining accurate bead topology (dependencies,
`execution-eligible`, `superseded-by`, epic hierarchy) so DDx's deterministic
`ReadyExecution()` ordering produces the intended sequence. HELIX does not
predict which bead DDx will select.

DDx owns **loop, selection, and execution**: bead selection, managed worktree
execution, close-with-evidence, retry suppression, and orphan recovery.

The intended adoption end state is: after each `ddx work --once --json` call,
HELIX parses `results[].bead_id` and `results[].status`, then applies
post-cycle supervisory policy to the bead DDx actually executed, not a
pre-selected bead.

Interpret `check` as follows:

- `NEXT_ACTION: BUILD`
  More safe ready work exists; continue.
- `NEXT_ACTION: DESIGN`
  Run `/helix design <scope>` once, then re-run `/helix check`.
- `NEXT_ACTION: POLISH`
  Run `/helix polish <scope>` once to decompose plans and refine issues,
  then re-run `/helix check`.
- `NEXT_ACTION: ALIGN`
  Run `reconcile-alignment` once for the indicated scope if auto-alignment is
  enabled, then re-run `/helix check`.
- `NEXT_ACTION: BACKFILL`
  Stop and hand off to `backfill-helix-docs` for the indicated scope.
- `NEXT_ACTION: WAIT`
  Stop. Do not attempt to build around the blocker or auto-unblock it.
- `NEXT_ACTION: GUIDANCE`
  Stop and get user or stakeholder input.
- `NEXT_ACTION: STOP`
  No actionable work remains for the current scope.

## `ddx work`

`ddx work` drains the ready queue under DDx control:

- loops only while true ready HELIX execution work exists
- runs one bounded build pass at a time
- emits `NEXT_ACTION` codes that the operator or wrapping skill interprets
- stops on `WAIT`, `BACKFILL`, `GUIDANCE`, or `STOP`
- uses the built-in tracker for queue state
- DDx owns worktree orphan recovery

Operator-side routing, planning, review, and reconciliation run as
`/helix <mode>` skill invocations around the DDx queue substrate.

### Command Boundary

Execution-oriented surfaces:

| Surface | Status | Intended use |
|---------|--------|--------------|
| `/helix input` | first-class | Shape sparse intent into governed work before execution begins |
| `/helix check` | first-class | Interpret queue state and DDx outcomes to choose the next bounded HELIX action |
| `/helix align` | first-class | Launch bead-governed alignment planning work |
| `/helix review`, `/helix design`, `/helix polish`, `/helix backfill` | first-class | HELIX planning/review/reconciliation entrypoints |
| `ddx work` | first-class | Primary queue-drain substrate |
| `ddx bead execute <id>` | first-class | Single-bead managed execution |

### Examples

```bash
ddx work
ddx work --once
/helix check repo
/helix align auth
/helix design auth
```

## Model Routing Contract

HELIX's DDx adapter selects the workflow stage and the routing intent for that
stage. It does not select concrete provider model versions.

When a HELIX skill mode dispatches planning, review, alignment, build, or
queue-steering work to DDx, it builds a routing request from three separate
inputs:

| Input | Owner | Examples |
|---|---|---|
| Stage tier intent | HELIX | `smart` for design/review/alignment, `cheap` or `fast` for `check`/`report`, DDx default for ordinary managed build work |
| Runtime-family constraint | Operator / HELIX skill | a selected harness, review harness, provider, or profile flag |
| Concrete model resolution | DDx agent service | provider/model selected from ddx-agent catalog data under the requested profile, power bounds, and user constraints |

Stage tier intent is expressed with DDx routing profiles (`--profile smart`,
`--profile fast`, `--profile cheap`, or no profile for DDx default policy).
`--harness`, `--provider`, `--min-power`, or `--max-power` may be passed when
those values come from an operator flag, environment variable, or
bead-specific requirement. HELIX must not translate `smart` or `cheap` into a
provider-specific model name.

Exact model strings remain supported only as compatibility pins. DDx treats
the model as an opaque user constraint and the agent-service catalog still
owns validation, fallback, and route evidence. HELIX must not parse the model
string, infer provider family from it, or use it as a fallback for other
stages.

## Reproducible Testing

The skill packaging contract is validated by `tests/validate-skills.sh`. The
DDx runtime ships its own deterministic execution harness; HELIX no longer
maintains a checkout CLI to test.

```bash
bash tests/validate-skills.sh
```

## Pre-Execution Pipeline

Before the implementation loop, the recommended sequence for new work is:

1. `/helix design [scope]` — create a comprehensive design document through
   iterative refinement. The action acquires a `kind:planning,action:design`
   bead before writing the design doc.
2. `/helix polish [scope]` — **decompose the plan into implementable beads**,
   then refine: deduplication, coverage verification, acceptance criteria
   sharpening, dependency wiring, concern threading (required before
   implementation). Polish acquires its own governing bead.
3. `ddx work` — execute the bounded build loop. Each build cycle claims a
   ready bead, executes, measures, and reports.

**Every step is bead-governed.** Design creates a planning bead before writing
docs. Polish creates a planning bead before decomposing. Build claims an
execution bead before writing code. No files change without a governing bead.

**Polish is the bridge between design and build.** A design plan produces a
document with a work breakdown, but it does not create execution beads. Polish
reads the plan, creates one bead per implementable slice, wires dependencies,
threads concerns into context digests and acceptance criteria, and then refines
the resulting queue. Without this step, agents encounter epics or vague work
items and attempt ad-hoc decomposition during build.

**Measure and report close each cycle.** After execution, every action measures
results against its bead's acceptance criteria and records evidence on the bead.
The report activity creates follow-on beads for any new work identified and closes
the governing bead. These follow-on beads re-enter the planning helix.

The operator entrypoints for this sequence are `/helix design`, `/helix
polish`, and `ddx work`.

`/helix check` enforces this pipeline: it recommends `POLISH` when a plan
exists but has not been decomposed into beads, even if epics appear in the
ready queue. It also recommends `POLISH` when concerns have changed since the
last polish pass.

These steps are optional for small changes but strongly recommended for any
scope that will produce more than a handful of issues.

## Cross-Cutting Context in Beads

`ddx bead create` (with the appropriate labels) and `/helix evolve` assemble a
**context digest** into every bead they create. The digest is a compact
~1000-1500 token summary of active principles, area-matched concerns, merged
practices, relevant ADRs, and governing spec context. It is prepended to the
bead description as a `<context-digest>` XML block.

`/helix polish` refreshes stale digests against current upstream state and
verifies that concern-appropriate acceptance criteria are present on every
bead in scope. When concerns change, polish propagates the change to all
affected beads — not just their digests but their acceptance criteria and
quality gates.

`ddx bead execute` and `/helix review` read the digest from the bead and use
it as working authority — they do not redundantly read the upstream files
that the digest summarizes.

`/helix measure` verifies concern-declared quality gates as part of its
acceptance criteria check. Measurement results are recorded on the bead so
that a closed bead carries its verification evidence.

Execution-ready beads must also carry deterministic success-measurement
criteria. A bead meant for `ddx work` should name the exact commands, checks,
files, fields, or ratchets that demonstrate success. Prefer:

- `bash tests/validate-skills.sh` passes and `git diff --check` passes
- `.ddx/plugins/helix/workflows/EXECUTION.md` names `ddx work` as the queue-drain substrate

Avoid:

- `queue draining works`
- `docs are aligned`

If a bead cannot be closed from explicit evidence, it is not ready for a
DDx-managed execution lane and should be refined by `/helix polish` or
recreated via `ddx bead` with sharper acceptance text before entering the
execution queue.

If execution order matters, encode that order in the tracker as well: use
parent-child structure for grouped scope and `ddx bead dep add` for hard
prerequisites. `ddx work` should never rely on prose-only sequencing or
operator memory to know what is safe to land next.

Concern threading is end-to-end: once a concern is introduced in
`docs/helix/01-frame/concerns.md`, it must propagate through context digests,
acceptance criteria, quality gates, and measurement evidence on every bead
whose area matches the concern's scope.

See `.ddx/plugins/helix/workflows/references/context-digest.md` for the assembly algorithm,
`.ddx/plugins/helix/workflows/references/concern-resolution.md` for concern loading, and
`.ddx/plugins/helix/workflows/references/principles-resolution.md` for principles loading.

## Next Issue

To see the recommended next issue without dispatching an agent, use:

```bash
ddx bead ready --json --execution
```

## Fresh-Eyes Review

After implementing an issue, `/helix review` performs 1-3 self-review passes
looking for bugs, integration issues, and security concerns with fresh
perspective:

```bash
/helix review                  # review last commit
/helix review ddx-abc123       # review changes for a specific issue
/helix review src/auth/        # review specific files
```

When the queue-drain loop runs review automation, the post-implementation
review target is resolved from the executed bead first. When the
implementation pass closes the bead and a tracker-sync commit lands after the
code commit, the loop reviews the bead's `closing_commit_sha` instead of raw
`HEAD~1`, so the threshold and review scope still inspect the implementation
diff rather than the tracker bookkeeping diff.

Review findings are durable: the review action files each actionable finding
as a tracker issue with label `review-finding` plus at least one
scope-appropriate `area:*` label derived from the reviewed bead or scope. The
run loop continues after review rather than stopping, because the findings are
now in the tracker and will surface via `ddx bead list --label review-finding` or
`ddx bead ready` once they are ready for implementation.

Similarly, when acceptance checks fail in the run loop, the specific failures
are filed as tracker issues with label `acceptance-failure` so they appear in
the ready queue for the next cycle.

Operators can query and manage these findings like any other issue:

```bash
ddx bead list --label review-finding    # all unresolved review findings
ddx bead list --label acceptance-failure # all unresolved acceptance failures
ddx bead close <id>                     # resolve a finding
```

## Experiment Loop

`/helix experiment` runs a single iteration of a metric-optimization loop for
`activity:iterate` issues. Each invocation: hypothesize → edit → test →
benchmark → keep/discard → log → exit.

The loop is driven externally by the HELIX skill in experiment mode or by the
operator re-invoking the command. This preserves the bounded-action model.

Experiments are operator-invoked only — `/helix check` does not produce a
`NEXT_ACTION: EXPERIMENT` code. The operator chooses `/helix experiment`
instead of build work for optimization.

The experiment action requires a clean worktree. The skill prompts the user
to commit uncommitted changes before proceeding.

The optimization target is a HELIX metric definition at
`docs/helix/06-iterate/metrics/<name>.yaml`. If one exists, the experiment
reads it; if not, the experiment creates one during setup. This connects
experiments to ratchets and monitoring through a shared metric definition.

Session artifacts (`autoresearch.*`, `experiments/`) are untracked local
files, gitignored on the experiment branch. At session close (`/helix
experiment --close`), the action squash-merges the experiment branch back to
produce a single commit and records the result in the issue close comment.
Experiments are execution-layer work tracked by issues, not canonical HELIX
docs.

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
