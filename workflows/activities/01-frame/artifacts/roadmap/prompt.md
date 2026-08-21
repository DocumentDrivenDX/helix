# Roadmap Generation Prompt

Document the delivery sequence for framed outcomes across iterations.

## Purpose

Roadmap is the **sequencing artifact** between PRD priorities and iteration
commitment. Its unique job is to order framed capabilities and outcomes
across iterations or horizons, with dependencies, confidence, and an explicit
rationale for the order, so each iteration plan can pull its slot without
re-litigating priority.

It commits sequence, not owners or dates. The iteration plan commits one
time-box; the runtime tracker owns live status.

## Reference Anchors

Use this local resource summary as grounding:

- `docs/resources/safe-framework-2025.md` grounds outcome-based,
  horizon-bounded roadmaps that stay revisable as evidence arrives.

## Focus

- Author a roadmap only when at least one of these holds: the project has
  two or more workstreams, OR sequencing across two or more future
  iterations is contested. When neither holds, skip it — the PRD's
  priorities and the improvement backlog carry the order, and a roadmap is
  ceremony. (Same predicate as the routing skill's Iterate skip test.)
- Define the workstreams here, once. The roadmap is the registry of record
  for workstream aliases: `WS-<n>`, assigned sequentially, never reused or
  renumbered. Downstream artifacts and runtime work items reference the
  alias (work items carry it as a label, e.g. `ws:WS-1`); they never mint
  new workstreams.
- Sequence outcomes, not tasks: each row delivers a governing artifact's
  requirement, feature, or backlog selection, inside a named workstream.
- State why each item holds its position — dependency, risk retirement, or
  value. An unexplained order is a quality-check failure.
- Bound the horizon. Candidates beyond it stay in the improvement backlog or
  parking lot, unsequenced.
- Name the revision triggers. A roadmap that cannot say when it must change
  will drift silently instead.

## Boundary Test

| If you are writing... | Put it in... |
|---|---|
| What the product must do and why | PRD |
| Ranked improvement candidates with evidence | Improvement Backlog |
| Workstream definitions and their `WS-<n>` aliases | Roadmap |
| Delivery sequence across iterations | Roadmap |
| One iteration's committed outcomes, owners, and dates | Iteration Plan |
| Live work-item status | runtime work item or issue |

## Completion Criteria

- Every workstream has a stable `WS-<n>` alias, a scope line, and an owner.
- Every sequenced outcome traces to a workstream and a governing artifact.
- Every position has a rationale.
- The horizon and revision triggers are explicit.
