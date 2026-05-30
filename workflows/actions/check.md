# HELIX Action: Check

You are performing a bounded HELIX execution-state check.

Your goal is to inspect the current HELIX planning and execution state, decide
whether there is more actionable work for the given scope, and recommend the
next HELIX action without inventing work or drifting from the authority stack.

This action is read-only by default. Do not modify product code. Do not claim
execution issues. Only recommend what should happen next.

## Action Input

You may receive:

- no argument
- `repo`
- a scope selector such as `US-042`, `FEAT-003`, `area:auth`, or `activity:build`

If no scope is given, default to the repository.

## Decision Codes

Your first output line must be exactly one of:

- `NEXT_ACTION: BUILD`
- `NEXT_ACTION: DESIGN`
- `NEXT_ACTION: POLISH`
- `NEXT_ACTION: ALIGN`
- `NEXT_ACTION: BACKFILL`
- `NEXT_ACTION: WAIT`
- `NEXT_ACTION: GUIDANCE`
- `NEXT_ACTION: STOP`

Use them precisely:

- `BUILD`: one or more safe ready HELIX execution issues exist and should be worked now
- `DESIGN`: design authority is missing or too weak for safe execution and a bounded planning pass should create or extend the governing design stack
- `POLISH`: governing specs changed or open issue metadata is stale enough that the queue should be refined before implementation resumes
- `ALIGN`: the planning stack exists, but no safe ready execution issue exists and a reconciliation pass is likely to expose or refine the next work set
- `BACKFILL`: the canonical HELIX stack is missing, stale, or contradictory enough that continued execution would be unsafe without reconstructing or repairing the governing docs
- `WAIT`: there is open work, but it is blocked by claimed work or a truly external dependency that code changes cannot resolve
- `GUIDANCE`: user or stakeholder input is required before safe work can continue
- `STOP`: there is no actionable work remaining for the scope right now

`check` owns the maintained queue-drain `NEXT_ACTION` vocabulary above. `design`
and `polish` are now first-class queue-drain outcomes when repository state
shows that design authority or issue refinement must happen before execution
can resume. `review` remains a supervisory subroutine outside this specific
`check` code set.

Supervisor interpretation:

- `BUILD` means continue the bounded implementation loop now.
- `DESIGN` means run the design action for the scope once, then re-evaluate the queue.
- `POLISH` means run the polish action for the scope once, then re-evaluate the queue.
- `ALIGN` means run the align action for the scope once, then re-evaluate the queue.
- `BACKFILL` means stop implementation and run the backfill action for the scope before resuming any execution work.
- `WAIT` means stop the current loop, do not auto-implement, and wait for the blocker to clear or the scope to change.
- `GUIDANCE` means stop and request the missing decision from the user or stakeholder.
- `STOP` means stop because there is no actionable work in scope.

## Authority Hierarchy

When artifacts disagree, use this hierarchy:

1. Product Vision
2. Product Requirements
3. Feature Specs / User Stories
4. Architecture / ADRs
5. Solution Designs / Technical Designs
6. Test Plans / Tests
7. Implementation Plans
8. Source Code / Build Artifacts

Rules:

- Higher layers govern lower layers.
- Tests govern build execution but do not override requirements or design.
- Source code reflects current state but does not redefine the plan.
- Do not treat open implementation work as proof that the plan is complete.
- Prefer a real queue-ready view from the tracker over status-only heuristics.

## STEP 0 - Bootstrap

0. **Context Recovery**: Re-read AGENTS.md so project instructions are fresh
   in your working memory. After long sessions, context compaction may have
   dropped critical project rules. This step is cheap insurance against drift.
0a. **Load active concerns** following the concern-resolution reference for
   this runtime. Concern context informs queue health assessment — work items
   without area labels cannot be matched to concerns, and stale context
   digests indicate the queue needs a polish pass.
1. Verify the runtime-provided work-item source is available. Stop immediately if unavailable.
2. Determine the scope.
3. Detect whether canonical HELIX docs exist for the scope.
   - check `docs/helix/`
   - check for alignment or backfill reports relevant to the scope when useful

## STEP 1 - Queue Health

Inspect the current execution queue using tracker commands. At minimum,
inspect:

- global queue health (ready, in-progress, and blocked counts)
- ready execution work items
- active claimed work items
- blocked work items when relevant

Do not use review items as evidence that implementation should continue.

## STEP 2 - Artifact Health

Assess whether the planning stack is sufficient for continued execution.

Check for:

- missing or obviously incomplete `docs/helix/` coverage
- stale or contradictory upstream artifacts
- recent implementation changes without corresponding planning or test support
- open execution issues whose governing artifacts are too weak to execute safely
- queue starvation caused by missing review, decision, or doc work
- ratchet status if the project has adopted quality ratchets: current measured
  value vs. floor, trend direction, and whether any ratchet is approaching its
  failure threshold

### Plan Decomposition Health

Plans must be decomposed into tracker work items before implementation can begin.
Check for undecomposed plans:

1. Scan `docs/helix/02-design/plan-*.md` and
   `docs/helix/02-design/solution-designs/SD-*.md` for the scope.
2. For each plan document found, check whether tracker work items exist that
   reference it (via `spec-id`, description, or parent epic).
3. If a plan exists but has **no or very few** corresponding work items, the plan
   is undecomposed. Flag this as a `POLISH` trigger — `polish` is the action
   that decomposes plans into implementable work items.
4. If an epic exists for the plan but has no child work items, that is also an
   undecomposed plan — the epic alone is not sufficient for `BUILD`.

An undecomposed plan is a higher-priority signal than ready epics. Do not
recommend `BUILD` when the ready queue contains only epics that need
decomposition.

### Concern Health

If active concerns are declared:

- **Missing area labels**: Count work items in scope that have no `area:*`
  labels. These items cannot be matched to concerns, so their context digests
  will be incomplete. If the count is significant, recommend `POLISH` to
  assign labels.
- **Missing context digests**: Count work items in scope that lack a context
  digest. If the concern library has been updated since these items were
  created, recommend `POLISH` to assemble digests.
- **Stale digests**: If concerns or practices were recently updated, flag that
  existing work items may have stale digests.
- **Missing concerns.md**: If `docs/helix/01-frame/concerns.md` does not exist,
  flag it. Recommend `BACKFILL` if the project clearly uses a technology with
  a library concern, or `GUIDANCE` if the technology choices are unclear.
- **Concern propagation completeness**: If concerns exist and work items exist,
  verify that items with matching area labels have concern-appropriate
  acceptance criteria (e.g., a `typescript-bun` item should reference
  `bun:test` or `biome check`, not `vitest` or `eslint`). If a significant
  number of items have incorrect or missing concern references in their
  acceptance criteria, recommend `POLISH` to propagate concerns.
- **Concern change since last polish**: Check whether `docs/helix/01-frame/concerns.md`
  or the concern library has been modified more recently than the most recent
  polish pass completed. If so, recommend `POLISH` even if work items appear
  ready, because their context digests and acceptance criteria may be stale.

## STEP 3 - Decision Logic

Apply these rules in order:

1. Recommend `BUILD` when:
   - one or more safe ready HELIX execution work items exist that are **not**
     undecomposed epics
   - no higher-priority supervisory refinement such as required `design` or
     `polish` remains unresolved for the same scope
   - plan decomposition health shows all in-scope plans have corresponding work items
2. Recommend `DESIGN` when:
   - requested or discovered work lacks sufficient design authority
   - a bounded planning pass can create or extend the missing design stack
   - implementation would otherwise guess at solution details
3. Recommend `POLISH` when:
   - a plan or solution design exists but has not been decomposed into
     implementable work items (this takes priority over `BUILD` even when epics
     appear in the ready queue)
   - the ready queue contains only epics without child task items
   - governing specs or designs changed and open items need refinement before execution
   - item dependencies, `spec-id`, parentage, or acceptance metadata are stale enough to make implementation unsafe
4. Recommend `BACKFILL` when:
   - the canonical HELIX stack is missing, stale, or contradictory enough to make safe execution impossible
5. Recommend `ALIGN` when:
   - the planning stack exists, but no safe ready execution work item exists and a reconciliation pass is likely to expose or refine the next work
   - or supervisory review shows that requirement/design drift exists above the work queue and neither a bounded `DESIGN` nor `POLISH` pass is the right narrower repair step
6. Recommend `BUILD` (not `WAIT`) when:
   - work is blocked, but the blocking items themselves are actionable
     (e.g., config changes, migrations, infrastructure-as-code fixes)
   - in this case, recommend implementing the blocker item directly
7. Recommend `WAIT` when:
   - work exists, but is claimed by another agent or blocked on a truly
     external dependency that cannot be resolved by code changes (e.g.,
     waiting for a third-party service, hardware provisioning, or human
     approval)
   - the correct supervisor response is to pause execution, surface the
     blocker, and retry only after the blocking condition changes
8. Recommend `GUIDANCE` when:
   - a user or stakeholder decision is the real blocker
9. Recommend `STOP` when:
   - there are no ready execution issues
   - no missing planning work is indicated
   - no blocked or in-progress scope requires action

Do not recommend `ALIGN` just because the queue is empty. Distinguish true work
exhaustion from planning gaps. Be explicit when a returned `ALIGN` is carrying
a broader supervisory need to reconcile, plan, or polish before implementation
can safely resume.

## STEP 4 - Suggested Command

Provide the recommended next action and enough context for the runtime to
invoke it. Name the scope and any specific work item or artifact that prompted
the recommendation.

For `WAIT`, `GUIDANCE`, or `STOP`, provide the exact reason and the condition
that would change the result.

For `BACKFILL`, identify the missing or contradictory artifacts that triggered
the recommendation.

## Output Format

Output these sections in order:

1. `NEXT_ACTION: ...`
2. Scope
3. Queue Health
4. Artifact Health
5. Remaining Work Assessment
6. Recommended Next Step
7. Stop Or Escalation Condition

Be concise, explicit, and operational.

## Runtime Integration Appendix

This appendix covers how a runtime realizes the check action. The reference
paths and work-item acquisition below are runtime-neutral; for the concrete
commands of a specific runtime, see its install guide (DDx:
[docs/install/ddx.md](../../docs/install/ddx.md)).

### STEP 0 — Reference resolution

Confirm the runtime-provided work-item source is available before proceeding; stop immediately if
it is not.

Load active concerns following `workflows/references/concern-resolution.md`.

### Action Input — examples

```
/helix check
/helix check repo
/helix check FEAT-003
/helix check area:auth
```

### STEP 1 — Queue health

Use the runtime's tracker as the authoritative queue source: inspect global
queue health (ready, in-progress, and blocked counts), ready execution items,
active claimed items, and blocked items. Prefer a real blocker-aware ready view
over status-only heuristics.

### STEP 2 — Artifact health references

- Ratchets: `workflows/ratchets.md`
- Concern library: `workflows/concerns/`
- Concern change since last polish: check git log on
  `workflows/concerns/` and `docs/helix/01-frame/concerns.md`
  against the timestamp of the most recent `kind:planning,action:polish` work
  item closed.

### STEP 4 — Suggested next steps

- `BUILD`: run the runtime's build loop (or single-item managed execution for a
  specific work item)
- `DESIGN`: `/helix design <scope>`
- `POLISH`: `/helix polish <scope>`
- `ALIGN`: `/helix align <scope>`
- `BACKFILL`: `/helix backfill <scope>`
