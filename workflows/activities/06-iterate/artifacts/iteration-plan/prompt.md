# Iteration Plan Generation Prompt

Document one human iteration's commitment.

## Purpose

Iteration Plan is the **commitment artifact** of the iterate loop. Its unique
job is to convert the improvement backlog's next-iteration selection and the
roadmap's current slot into one time-boxed commitment: a falsifiable goal,
one Good / one Better / one Best outcome per participating workstream with
owners and acceptance evidence, deterministic trade rules, and stable-ID task
tables.

It is not the live tracker. The plan owns commitment membership: task rows
select existing work items by ID where they exist, and rows without one are
the source from which the runtime creates items, back-referencing each new
ID in the plan. The runtime's tracker (work items, boards, issues) owns live
status, assignment churn, and execution history. Scope changes route back
through the plan — hand-added tracker items never silently widen the
commitment.

## Reference Anchors

Use this local resource summary as grounding:

- `docs/resources/agile-manifesto-principles.md` grounds time-boxed
  commitment, sustainable cadence, and working evidence as the measure of
  progress.

## Focus

- Author a plan only when there is a commitment to coordinate — multiple
  owners, multiple workstreams, or a review with an audience. A solo
  iteration may run straight from the backlog selection and the tracker;
  the plan is coordination, not ceremony.
- Make the goal falsifiable: what is true at review, shown by what evidence.
- Commit exactly one Good, one Better, and one Best outcome per
  participating workstream. Good is the protected floor; Best drops first,
  then Better. More outcomes per workstream is confusing; fewer breaks the
  flex model — a workstream that cannot fill all three tiers sits this
  iteration out (not participating), never partially committed.
- Once committed, a Good outcome's ID, text, and acceptance evidence are
  immutable for the iteration. A Good that becomes impossible is an
  escalation recorded in the status report with its decider named — never an
  in-place edit, re-tier, or silent replacement.
- Give every outcome an owner, acceptance evidence, and at least one task.
  Outcome IDs are `<WS alias>-good|better|best`, unique within the plan;
  fully qualified as `<iteration-id>.<outcome-id>` when cited elsewhere.
- Reference workstreams by their roadmap-registry alias (`WS-<n>`) when a
  roadmap exists; a roadmap-less plan (single-workstream skip case) has one
  implicit workstream and uses no aliases — a second workstream means author
  the registry first. The plan never mints workstreams. Work items preserve
  the alias: as a label where the runtime supports labels (e.g. `ws:WS-1`,
  prefixed with the flow instance when several flows share one store),
  otherwise in the item's title or reference field.
- Keep the plan derivable: a runtime should be able to create work items
  from the task tables without inventing scope.
- Write tier labels in table cells as emoji plus a non-breaking space
  (U+00A0) plus the word — 🟢 Good, 🔵 Better, 🟣 Best — so the label never
  wraps apart in rendered tables. Plain words are fine in prose.
- Reference implementation plans where a committed outcome has one; do not
  duplicate their build slices here.

## Boundary Test

| If you are writing... | Put it in... |
|---|---|
| Workstream definitions and their `WS-<n>` aliases | Roadmap |
| Delivery sequence across iterations | Roadmap |
| Ranked improvement candidates with evidence | Improvement Backlog |
| One iteration's committed outcomes, owners, and dates | Iteration Plan |
| Design-derived build slices for one feature | Implementation Plan |
| Live task status, assignees, execution history | runtime work item or issue |
| How the iteration is going or went | Status Report |

## Completion Criteria

- The goal is falsifiable and the review date is set.
- Every participating workstream has exactly one Good, one Better, and one
  Best outcome, each with an owner and acceptance evidence.
- Every committed outcome maps to at least one task.
- Workstream aliases match the roadmap's registry (or the plan is
  roadmap-less and uses none).
- Trade rules make the drop order deterministic (Best, then Better; Good
  never).
- Every task has a stable ID, maps to a committed outcome, and names its
  work item or is marked for creation.
