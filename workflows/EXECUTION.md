---
ddx:
  id: helix.workflow.execution
  depends_on:
    - helix.workflow
    - helix.workflow.tracker
  review:
    self_hash: dba8a581c733f48826b8f1fe995f96645cf30fce0eedcbeff35c36bfaab2643a
    deps:
      helix.workflow: 1b6caaf3ebc6950bc4fff314e09bc0ee1b71deaa9223a4a70a13f399291ad98c
      helix.workflow.tracker: 395b9ef6466577b751192c2b17008cdb3a6db1bc10554786d024e023c6e004f5
    reviewed_at: "2026-05-26T03:19:52Z"
---
# HELIX Execution Guide

**Scope note.** This document is the runtime-neutral execution-integration
model for HELIX: how to run bounded work passes, how to decide whether more
work remains, and how a runtime — *if* it provides one — steers a queue. It
specifies the **actions** a runtime performs, not the commands that perform
them. The methodology requirements (work-item-first, steer-through-the-tracker,
measure-and-record, report-and-feed-back) apply to every runtime; the concrete
command names and substrate are the runtime's own.

For runtime-neutral methodology — the artifact loop, the artifact
authority hierarchy, the
methodology actions, and the alignment contract — read [README.md](README.md)
and [REFERENCE.md](REFERENCE.md) first. For the concrete commands of a specific
runtime, read its install guide under
[`docs/install/`](../docs/install/); the DDx reference-runtime commands
(work-item tracker, execution loop, queue guard, model routing) live in
[`docs/install/ddx.md`](../docs/install/ddx.md).

HELIX does not require a tracker, a queue, or an execution loop. A runtime may
provide them; where this guide describes one, read it as "the runtime-provided
work-item source, if any."

## Document Scope

This document owns the runtime-neutral execution model.

- Follow this file for queue guards, loop shape, and `NEXT_ACTION` handling at
  the methodology level.
- Follow the bounded action prompts under `actions/` for action-specific
  behavior.
- Follow your runtime's install guide for the concrete command that realizes
  each action.
- Treat examples elsewhere in the workflows package as supportive summaries,
  not alternate execution contracts.

This is the methodology execution layer, not a runtime packaging layer. Skill
installation and concrete queue control live in the per-runtime install guides.

## Terminology

A **work item** is the governed unit of execution — a description of an
intended transformation with acceptance criteria, governing-artifact
references, and a status. Runtimes name it differently and store it in their own
tracker; each runtime's term and tracker commands are documented in its install
guide (DDx: [`docs/install/ddx.md`](../docs/install/ddx.md)). This guide uses
"work item"; read it as your runtime's equivalent.

## The Double Helix

HELIX is built from two interleaved cycles — the double helix:

### Planning Helix

Identification and improvement of plans as work items.

```
Review → Plan → Validate → (ready work items)
```

- **Review**: Assess current state (`check`, `align`). What work exists? What's
  missing? What concerns aren't threaded?
- **Plan**: Create or refine plan work items with consolidated context
  (`design`, `polish`, `evolve`, `triage`). Every plan item consolidates
  inputs, cross-cutting concerns, current state, and acceptance criteria.
- **Validate**: Verify plan quality — are work items well-specified? Are
  concerns threaded? Are dependencies correct? Are acceptance criteria testable?
  This is what `polish` refinement passes do.

Output: a set of well-specified, concern-threaded work items ready for
execution.

### Execution Helix

Executing plans to update documents, reconcile artifacts, research next-stage
plans, implement code, test it, and optimize metrics.

```
Execute → Measure → Report → (new work items)
```

- HELIX models each governed execution step as a workspace-state
  transformation. Given workspace state `W`, executing work item `B` attempts
  to produce successor workspace state `W'`.
- Shorthand: `B : W -> W'`
- The work item is the intended transformation, not the evidence record.
- The execution run is the bounded attempt and evidence record for trying to
  realize `W -> W'`.
- The execution outcome records how that attempt landed (`merged`,
  `preserved`, `blocked`, `failed`, or equivalent workflow-visible result).
- The realized state delta is the material change between `W` and `W'`:
  docs, code, tracker state, generated artifacts, and other workspace changes.

- **Execute**: Claim a work item, do the work it describes (`build`, `review`,
  `experiment`, `backfill` — any action that modifies files on disk).
- **Measure**: Verify results against the item's acceptance criteria. Run
  concern-declared quality gates. Run ratchets. Record results on the item.
- **Report**: Analyze measurement results. Open new work items for issues found,
  regressions, or follow-on work. Close the executed item with evidence. New
  items feed back into the planning helix.

### Crossover

The helices interleave at two points:

1. **Planning → Execution**: Ready work items move from the planning helix to
   the execution queue.
2. **Execution → Planning**: Report creates new work items that enter the
   planning helix for refinement.

`/helix check` is the crossover point — it reads both helices and decides
which one needs attention next. It already does this implicitly (`BUILD` vs
`DESIGN`/`POLISH`/`ALIGN`), but the double-helix model makes the two cycles
explicit.

### Work-Item-First Principle

**Every action that modifies files must be governed by a work item.** No file
modifications without a governing plan item — analogous to entering plan mode
before writing code.

Operationally, a work item should describe the intended transformation from
current workspace state `W` to successor workspace state `W'`. `measure`
determines whether the resulting `W'` satisfies the item's acceptance criteria
and quality gates. `report` records evidence about the `W -> W'` transition and
creates any required follow-on items.

Every action (except `triage` and `check`) follows this structure:

1. **Work-item acquisition**: Find or create the governing item for this work.
2. **Execution**: Do the work the item describes.
3. **Measure**: Verify results and record evidence on the item.
4. **Report**: Create follow-on items and close the governing item.

`triage` is the entry point that bootstraps the work-item graph — it creates
items and therefore cannot itself require one (that would be infinite regress).
`input` is also an entry point: it accepts sparse intent and creates or updates
the work-item/workflow context that later actions execute. `check` is read-only
and does not modify files.

Planning-helix items use the `kind:planning` label to distinguish them from
execution items. Combined with an `action:<name>` label (e.g.,
`action:design`, `action:polish`), this makes the governing item's purpose
visible in the tracker.

See `workflows/references/bead-first.md` for the full work-item acquisition
pattern, `workflows/references/measure.md` for measurement recording, and
`workflows/references/report.md` for the report activity.

## Core Actions

HELIX supervision is built from bounded actions with distinct roles. Operators
invoke them through the unified `/helix <mode>` skill; a runtime may also expose
its own command for the execution-oriented ones:

- `/helix input "<natural language request>" [--autonomy low|medium|high]`
  Accepts sparse intent, applies HELIX autonomy semantics, and creates or
  updates the work-item/workflow context needed for later execution. This is the
  planning-helix intake surface for the slider-autonomy model; the expected
  default autonomy is `medium`.
- **build** (single-item execution)
  The runtime executes one ready execution item end-to-end, then exits.
- `/helix check`
  Performs the queue-drain decision and returns the maintained
  `NEXT_ACTION` vocabulary: build, design, issue refinement,
  alignment, backfill, waiting, guidance, or stopping.
- `/helix align <scope>`
  Convenience entrypoint for a top-down reconciliation review. It first
  creates or claims the governing `kind:planning,action:align` work item, then
  runs the stored alignment prompt and emits properly ordered follow-on items.
- `/helix evolve <requirement>`
  Threads a requirement change through the artifact stack and updates the
  tracker when authority shifts.
- `/helix design <scope>`
  Creates or extends the design stack when supervisory routing detects missing
  design authority for the requested scope.
- `/helix polish <scope>`
  Decomposes design plans into implementable work items, then refines their
  definitions and dependencies. This is the mandatory step between design and
  build — without it, agents attempt ad-hoc decomposition during implementation.
- `/helix review [scope]`
  Performs fresh-eyes review after build before additional execution
  continues when review automation is enabled.
- `/helix measure [item-id|scope]`
  Runs acceptance criteria, concern-declared quality gates, and ratchet
  enforcement against a work item or scope. Records results on the item. Can be
  invoked standalone or runs as an embedded activity within other actions.
- `/helix report [item-id|scope]`
  Analyzes measurement results, creates follow-on work items for identified work,
  and closes the governing item with evidence. Per-item by default; batch mode
  aggregates across a scope.
- **triage** (work-item creation)
  Creates tracker items. This is the entry point that bootstraps the work-item
  graph — the one action that does not require a governing item.
- `/helix backfill <scope>`
  Reconstructs missing HELIX docs conservatively from current evidence.

## Execution Model

Use a supervisory control loop with an explicit queue-drain sub-step.

For sparse operator intent that is not yet represented as a work item or bounded
scope, start with `/helix input` before entering the normal execution loop.
`/helix input` shapes intent into governed work; the runtime's execution and the
`/helix check` decision operate on the resulting work-item/workflow state.

1. Guard on true ready work — items with all dependencies satisfied — not on a
   raw "all open items" list
2. Route to the least-power bounded subroutine required by user intent and repository state:
   - `evolve` when a requirement change must propagate through canonical artifacts
   - `design` when requested work lacks sufficient design authority
   - `polish` when plans need decomposition into work items, or governing specs changed and open items need refinement
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

A blocker-aware ready check is required: an "all open items" listing is not
equivalent to "items whose dependencies are satisfied" and must not control an
autonomous execution loop.

`design`, `polish`, and `review` participate in supervisory dispatch. `design` and
`polish` are now explicit `check` `NEXT_ACTION` codes for queue-drain routing;
`review` remains a post-build supervisory step rather than a
queue-drain code.

The runtime's queue-drain loop is the primary substrate for execution-ready
work items. Operator-facing routing and policy decisions live in `/helix <mode>`
skill modes.

Execution principles:

- work-item-first: every action that modifies files must have a governing item
  before execution begins. No ad-hoc file changes without a plan item.
- steer-through-the-tracker: use the runtime's tracker primitives, not side
  channels, to redirect execution
- queue topology is explicit: if order matters, encode it with parent-child
  structure and dependencies instead of prose or operator memory
- measure-and-record: verification results are recorded on the work item, not
  just logged ephemerally. A closed item carries its measurement evidence.
- report-and-feed-back: measurement findings create new work items that re-enter
  the planning helix, closing the feedback loop
- do-hard-things: stay on the active epic, prefer a runtime-provided cooldown
  and preserve signals as the long-term retry surface, and file deterministic
  follow-on work instead of carrying hidden wrapper heuristics
- cross-model verification: prefer a distinct review agent for post-build review
  when the runtime offers one
- continuous useful work: absorb small adjacent work when clearly required,
  and surface blocked work through tracker state rather than prose-only memory

## Queue Guard

If the runtime provides a queue, guard an autonomous loop on *true* ready work —
items whose dependencies are all satisfied — not on a raw "all open items"
listing. The two are not equivalent, and only the blocker-aware count is safe to
drive an unattended loop.

For the concrete blocker-aware ready check and a copy-paste guard function, see
your runtime's install guide (for DDx, [`docs/install/ddx.md`](../docs/install/ddx.md)).

## Manual Loop

The canonical operator path once work is execution-ready is: while true ready
work remains, run one bounded execution pass; when the queue drains, run
`/helix check`. The runtime's execution loop is the durable queue-drain
primitive; the `/helix <mode>` skill modes provide HELIX-owned routing,
planning, review, and reconciliation around it.

The concrete loop for a given runtime is in its install guide.

### Architecture

HELIX owns **queue curation**: maintaining accurate work-item topology
(dependencies, execution-eligibility, supersession, epic hierarchy) so the
runtime's deterministic ready-ordering produces the intended sequence. HELIX
does not predict which item the runtime will select.

The runtime owns **loop, selection, and execution**: item selection, isolated
execution, close-with-evidence, retry suppression, and orphan recovery.

The intended adoption end state is: after each bounded execution cycle, HELIX
reads the executed item's id and status, then applies post-cycle supervisory
policy to the item the runtime actually executed, not a pre-selected item.

Interpret `check` as follows:

- `NEXT_ACTION: BUILD`
  More safe ready work exists; continue.
- `NEXT_ACTION: DESIGN`
  Run `/helix design <scope>` once, then re-run `/helix check`.
- `NEXT_ACTION: POLISH`
  Run `/helix polish <scope>` once to decompose plans and refine items,
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

## The Execution Loop

When the runtime provides a queue-drain loop, it:

- loops only while true ready HELIX execution work exists
- runs one bounded build pass at a time
- emits `NEXT_ACTION` codes that the operator or wrapping skill interprets
- stops on `WAIT`, `BACKFILL`, `GUIDANCE`, or `STOP`
- uses the runtime-provided tracker for queue state
- owns isolated-worktree orphan recovery

Operator-side routing, planning, review, and reconciliation run as
`/helix <mode>` skill invocations around the runtime's queue substrate.

### Command Boundary

Execution-oriented surfaces:

| Surface | Status | Intended use |
|---------|--------|--------------|
| `/helix input` | first-class | Shape sparse intent into governed work before execution begins |
| `/helix check` | first-class | Interpret queue state and execution outcomes to choose the next bounded HELIX action |
| `/helix align` | first-class | Launch work-item-governed alignment planning work |
| `/helix review`, `/helix design`, `/helix polish`, `/helix backfill` | first-class | HELIX planning/review/reconciliation entrypoints |
| runtime queue-drain loop | runtime-provided | Primary queue-drain substrate |
| runtime single-item execution | runtime-provided | Single-item managed execution |

The concrete commands for these runtime-provided surfaces are in the runtime's
install guide.

## Model Routing Contract

A HELIX runtime adapter selects the workflow stage and the routing intent for
that stage. It does not select concrete provider model versions.

When a HELIX skill mode dispatches planning, review, alignment, build, or
queue-steering work, it builds a routing request from three separate inputs:

| Input | Owner | Examples |
|---|---|---|
| Stage tier intent | HELIX | `smart` for design/review/alignment, `cheap` or `fast` for `check`/`report`, runtime default for ordinary managed build work |
| Runtime-family constraint | Operator / HELIX skill | a selected harness, review harness, provider, or profile flag |
| Concrete model resolution | runtime agent service | provider/model selected from the runtime's catalog data under the requested profile, power bounds, and user constraints |

Stage tier intent is expressed with the runtime's routing profiles (a `smart`,
`fast`, or `cheap` tier, or the runtime default policy). Harness, provider, or
power-bound constraints may be passed when those values come from an operator
flag, environment variable, or item-specific requirement. HELIX must not
translate `smart` or `cheap` into a provider-specific model name.

Exact model strings remain supported only as compatibility pins. The runtime
treats the model as an opaque user constraint and its agent-service catalog
still owns validation, fallback, and route evidence. HELIX must not parse the
model string, infer provider family from it, or use it as a fallback for other
stages.

(For DDx's concrete profile flags, see [`docs/install/ddx.md`](../docs/install/ddx.md).)

## Reproducible Testing

The skill packaging contract is validated by `tests/validate-skills.sh`. The
runtime ships its own deterministic execution harness; HELIX does not maintain
a checkout CLI to test.

```bash
bash tests/validate-skills.sh
```

## Pre-Execution Pipeline

Before the implementation loop, the recommended sequence for new work is:

1. `/helix design [scope]` — create a comprehensive design document through
   iterative refinement. The action acquires a `kind:planning,action:design`
   work item before writing the design doc.
2. `/helix polish [scope]` — **decompose the plan into implementable work
   items**, then refine: deduplication, coverage verification, acceptance
   criteria sharpening, dependency wiring, concern threading (required before
   implementation). Polish acquires its own governing item.
3. The runtime's build loop — execute the bounded build loop. Each build cycle
   claims a ready item, executes, measures, and reports.

**Every step is work-item-governed.** Design creates a planning item before
writing docs. Polish creates a planning item before decomposing. Build claims an
execution item before writing code. No files change without a governing item.

**Polish is the bridge between design and build.** A design plan produces a
document with a work breakdown, but it does not create execution items. Polish
reads the plan, creates one item per implementable slice, wires dependencies,
threads concerns into context digests and acceptance criteria, and then refines
the resulting queue. Without this step, agents encounter epics or vague work
items and attempt ad-hoc decomposition during build.

**Measure and report close each cycle.** After execution, every action measures
results against its item's acceptance criteria and records evidence on the item.
The report activity creates follow-on items for any new work identified and closes
the governing item. These follow-on items re-enter the planning helix.

The operator entrypoints for this sequence are `/helix design`, `/helix
polish`, and the runtime's build loop.

`/helix check` enforces this pipeline: it recommends `POLISH` when a plan
exists but has not been decomposed into work items, even if epics appear in the
ready queue. It also recommends `POLISH` when concerns have changed since the
last polish pass.

These steps are optional for small changes but strongly recommended for any
scope that will produce more than a handful of items.

## Cross-Cutting Context in Work Items

Item-creating actions (`triage`-style creation with the appropriate labels, and
`/helix evolve`) assemble a **context digest** into every item they create. The
digest is a compact ~1000-1500 token summary of active principles, area-matched
concerns, merged practices, relevant ADRs, and governing spec context. It is
prepended to the item description as a `<context-digest>` XML block.

`/helix polish` refreshes stale digests against current upstream state and
verifies that concern-appropriate acceptance criteria are present on every
item in scope. When concerns change, polish propagates the change to all
affected items — not just their digests but their acceptance criteria and
quality gates.

Execution and `/helix review` read the digest from the item and use it as
working authority — they do not redundantly read the upstream files that the
digest summarizes.

`/helix measure` verifies concern-declared quality gates as part of its
acceptance criteria check. Measurement results are recorded on the item so
that a closed item carries its verification evidence.

Execution-ready items must also carry deterministic success-measurement
criteria. An item meant for the runtime's build loop should name the exact
commands, checks, files, fields, or ratchets that demonstrate success. Prefer:

- `bash tests/validate-skills.sh` passes and `git diff --check` passes
- `workflows/EXECUTION.md` names the runtime's loop as the queue-drain substrate

Avoid:

- `queue draining works`
- `docs are aligned`

If an item cannot be closed from explicit evidence, it is not ready for a
managed execution lane and should be refined by `/helix polish` or recreated
with sharper acceptance text before entering the execution queue.

If execution order matters, encode that order in the tracker as well: use
parent-child structure for grouped scope and dependency links for hard
prerequisites. The execution loop should never rely on prose-only sequencing or
operator memory to know what is safe to land next.

Concern threading is end-to-end: once a concern is introduced in
`docs/helix/01-frame/concerns.md`, it must propagate through context digests,
acceptance criteria, quality gates, and measurement evidence on every item
whose area matches the concern's scope.

See `workflows/references/context-digest.md` for the assembly algorithm,
`workflows/references/concern-resolution.md` for concern loading, and
`workflows/references/principles-resolution.md` for principles loading.

## Next Item

To see the recommended next execution-ready item without dispatching an agent,
use the runtime's ready-item query (for DDx, see
[`docs/install/ddx.md`](../docs/install/ddx.md)).

## Fresh-Eyes Review

After implementing an item, `/helix review` performs 1-3 self-review passes
looking for bugs, integration issues, and security concerns with fresh
perspective:

```bash
/helix review                  # review last commit
/helix review <item-id>        # review changes for a specific item
/helix review src/auth/        # review specific files
```

When the queue-drain loop runs review automation, the post-implementation
review target is resolved from the executed item first. When the
implementation pass closes the item and a tracker-sync commit lands after the
code commit, the loop reviews the item's closing commit instead of raw
`HEAD~1`, so the threshold and review scope still inspect the implementation
diff rather than the tracker bookkeeping diff.

Review findings are durable: the review action files each actionable finding
as a tracker item with label `review-finding` plus at least one
scope-appropriate `area:*` label derived from the reviewed item or scope. The
run loop continues after review rather than stopping, because the findings are
now in the tracker and will surface in the ready queue once they are ready for
implementation.

Similarly, when acceptance checks fail in the run loop, the specific failures
are filed as tracker items with label `acceptance-failure` so they appear in
the ready queue for the next cycle.

Operators can query and manage these findings like any other item through the
runtime's tracker (for DDx, see [`docs/install/ddx.md`](../docs/install/ddx.md)).

## Experiment Loop

`/helix experiment` runs a single iteration of a metric-optimization loop for
`activity:iterate` items. Each invocation: hypothesize → edit → test →
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
produce a single commit and records the result in the item's close comment.
Experiments are execution-layer work tracked by items, not canonical HELIX
docs.

`--close` is unique to the experiment command — it directs the action to
execute session close (squash-merge, ratchet update, item close) instead of
running another iteration.

Experiments validate governing artifacts at session setup and close (not
per-iteration). Per-iteration guardrails are: scoped files, mandatory test
passage, and the experiment's own constraints. All existing tests must pass
after every kept iteration.

## Practical Rules

- Keep execution bounded to one item per implementation pass.
- Do not use an unconditional `while true` loop.
- Treat `check` as the queue-drain decision point, not `reconcile-alignment`.
- Use alignment to expose or refine the next work set, not as the default work
  picker.
- Do not auto-run backfill unless you are intentionally reconstructing missing
  canonical docs.
