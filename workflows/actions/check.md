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
- a scope selector such as `US-042`, `FEAT-003`, `area:auth`, or `phase:build`

Examples:

- `helix check`
- `helix check repo`
- `helix check FEAT-003`
- `helix check area:auth`

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
- `DESIGN` means run `helix design <scope>` once, then re-evaluate the queue.
- `POLISH` means run `helix polish <scope>` once, then re-evaluate the queue.
- `ALIGN` means run `helix align <scope>` once, then re-evaluate the queue.
- `BACKFILL` means stop implementation and run `helix backfill <scope>` before resuming any execution work.
- `WAIT` means stop the current loop, do not auto-implement, and wait for the blocker to clear or the scope to change.
- `GUIDANCE` means stop and request the missing decision from the user or stakeholder.
- `STOP` means stop because there is no actionable work in scope.

## Authority Order

When artifacts disagree, use this order:

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
- Prefer a real `ddx bead ready` view over status-only heuristics.

## PHASE 0 - Bootstrap

0. **Context Recovery**: Re-read AGENTS.md so project instructions are fresh
   in your working memory. After long sessions, context compaction may have
   dropped critical project rules. This step is cheap insurance against drift.
0a. **Load active concerns** following `workflows/references/concern-resolution.md`.
   Concern context informs queue health assessment — beads without area labels
   cannot be matched to concerns, and stale context digests indicate the queue
   needs a polish pass.
1. Verify the built-in tracker is available.
   - If `ddx bead status` fails, stop immediately.
2. Determine the scope.
3. Detect whether canonical HELIX docs exist for the scope.
   - check `docs/helix/`
   - check for alignment or backfill reports relevant to the scope when useful

## PHASE 1 - Queue Health

Inspect the current execution queue using tracker commands.

At minimum, inspect:

- `ddx bead status` for global queue health
- `ddx bead ready --json`
- `ddx bead list --status in_progress --label helix --json` for active claimed work
- `ddx bead blocked --json` and open HELIX issues for blocked work when relevant

Do not use review issues as evidence that implementation should continue.

## PHASE 2 - Artifact Health

Assess whether the planning stack is sufficient for continued execution.

Check for:

- missing or obviously incomplete `docs/helix/` coverage
- stale or contradictory upstream artifacts
- recent implementation changes without corresponding planning or test support
- open execution issues whose governing artifacts are too weak to execute safely
- queue starvation caused by missing review, decision, or doc work
- ratchet status if the project has adopted quality ratchets
  (see `workflows/ratchets.md`): current measured value vs. floor,
  trend direction, and whether any ratchet is approaching its failure
  threshold

### Concern Health

If active concerns are declared:

- **Missing area labels**: Count beads in scope that have no `area:*` labels.
  These beads cannot be matched to concerns, so their context digests will be
  incomplete. If the count is significant, recommend `POLISH` to assign labels.
- **Missing context digests**: Count beads in scope that lack a
  `<context-digest>` block. If the concern library has been updated since these
  beads were created, recommend `POLISH` to assemble digests.
- **Stale digests**: If concerns or practices were recently updated (check git
  log on `workflows/concerns/` and `docs/helix/01-frame/concerns.md`), flag
  that existing beads may have stale digests.
- **Missing concerns.md**: If `docs/helix/01-frame/concerns.md` does not exist,
  flag it. Recommend `BACKFILL` if the project clearly uses a technology with
  a library concern, or `GUIDANCE` if the technology choices are unclear.

## PHASE 3 - Decision Logic

Apply these rules in order:

1. Recommend `BUILD` when:
   - one or more safe ready HELIX execution issues exist
   - no higher-priority supervisory refinement such as required `design` or
     `polish` remains unresolved for the same scope
2. Recommend `DESIGN` when:
   - requested or discovered work lacks sufficient design authority
   - a bounded planning pass can create or extend the missing design stack
   - implementation would otherwise guess at solution details
3. Recommend `POLISH` when:
   - governing specs or designs changed and open issues need refinement before execution
   - issue dependencies, `spec-id`, parentage, or acceptance metadata are stale enough to make implementation unsafe
4. Recommend `BACKFILL` when:
   - the canonical HELIX stack is missing, stale, or contradictory enough to make safe execution impossible
5. Recommend `ALIGN` when:
   - the planning stack exists, but no safe ready execution issue exists and a reconciliation pass is likely to expose or refine the next work
   - or supervisory review shows that requirement/design drift exists above the issue queue and neither a bounded `DESIGN` nor `POLISH` pass is the right narrower repair step
6. Recommend `BUILD` (not `WAIT`) when:
   - work is blocked, but the blocking issues themselves are actionable
     (e.g., config changes, migrations, infrastructure-as-code fixes)
   - in this case, recommend implementing the blocker issue directly
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

## PHASE 4 - Suggested Command

Provide the exact next command for the recommended action where possible:

- `BUILD`:
  - `helix build`
- `DESIGN`:
  - `helix design <scope>`
- `POLISH`:
  - `helix polish <scope>`
- `ALIGN`:
  - `helix align <scope>`
- `BACKFILL`:
  - `helix backfill <scope>`

For `WAIT`, `GUIDANCE`, or `STOP`, provide the exact reason and the condition
that would change the result.

For `BACKFILL`, provide the exact backfill command and the missing or
contradictory artifacts that triggered it.

## Output Format

Output these sections in order:

1. `NEXT_ACTION: ...`
2. Scope
3. Queue Health
4. Artifact Health
5. Remaining Work Assessment
6. Recommended Command
7. Stop Or Escalation Condition

Be concise, explicit, and operational.
