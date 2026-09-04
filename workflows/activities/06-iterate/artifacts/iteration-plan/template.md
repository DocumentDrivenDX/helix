---
ddx:
  id: iteration-plan
  authoring:
    home: repo
---

# Iteration Plan

| | |
|---|---|
| **Iteration** | [id — e.g. IT-05, Sprint 3] |
| **Dates** | [start → end] |
| **Review** | [date and format of the iteration review] |
| **Lead** | [who runs the iteration] |
| **Roadmap Slot** | [roadmap order/iteration this fulfills, or N/A] |

## Iteration Goal

> [One falsifiable sentence: what is true at review that is not true now,
> and what evidence shows it.]

## Committed Outcomes

Each participating workstream commits exactly one outcome per tier — one
Good, one Better, one Best. Good is the protected floor: the iteration fails
without it, and once committed its ID, text, and acceptance evidence are
immutable for the iteration — a Good that becomes impossible is recorded as
an escalation in the status report (decider named), never edited, re-tiered,
or silently replaced. Best drops first under pressure, then Better. More
outcomes per workstream is confusing; fewer breaks the flex model. A
workstream sitting out this iteration is listed as not participating, never
partially committed. (Participation is per-iteration; a workstream's
registry status — active/closed — lives in the roadmap and is a different
axis.) Outcome IDs are unique within this plan; the fully qualified form is
`<iteration-id>.<outcome-id>` (e.g. `IT-05.WS-1-good`).
Tier labels render as emoji plus a non-breaking space (U+00A0) so they never
wrap in table cells: 🟢 Good · 🔵 Better · 🟣 Best.

| ID | Workstream | Tier | Outcome | Owner | Governing Artifact | Acceptance Evidence |
|----|------------|------|---------|-------|--------------------|---------------------|
| [WS-1-good] | [WS-1] | 🟢 Good | [the outcome the iteration fails without] | [name] | [artifact ref] | [what proves it landed] |
| [WS-1-better] | [WS-1] | 🔵 Better | [real value, first traded after Best] | [name] | [artifact ref] | [what proves it landed] |
| [WS-1-best] | [WS-1] | 🟣 Best | [taken only if the iteration runs clean] | [name] | [artifact ref] | [what proves it landed] |

**Not participating this iteration**: [WS-n (reason), or None]

## Trade Rules

- Best drops first, then Better — per workstream. [Who] calls trades and
  records them in the status report.
- Good outcomes are never traded: a Good at risk is an escalation, not a
  trade.

## Tasks

The plan owns membership; the runtime's tracker owns live state. Select
existing work items by ID in the Work Item column; a task without one is
created by the runtime from this table and its new ID back-referenced here.
Every committed outcome maps to at least one task. Task IDs are stable —
never renumber mid-iteration — and unique within this plan (fully qualified:
`<iteration-id>.<task-id>`, e.g. `IT-05.1.1`). The Status column records
planning-time state (normally Backlog); once work items derive, the tracker
is authoritative and this column is not maintained.

Workstream aliases come from the roadmap's registry when one exists. A plan
authored without a roadmap (single-workstream skip case) has one implicit
workstream and omits aliases entirely; the moment a second workstream
appears, author the roadmap's registry first. Aliases are unique within one
flow instance. Work items preserve the alias: as a label where the runtime
supports labels (e.g. `ws:WS-1`, prefixed with the flow instance when
several flows share one store), otherwise in the item's title or reference
field.

### [WS-1 · workstream name]

| ID | Task | Outcome | Owner | Due | Status | Work Item |
|----|------|---------|-------|-----|--------|-----------|
| [1.1] | [task] | [WS-1-good] | [name] | [date] | [Backlog] | [existing item ID, or — until created] |

## Risks

| Risk | Impact | Response |
|------|--------|----------|
| [risk] | [H/M/L] | [action] |

## Review Checklist

- [ ] Goal is falsifiable at the review date
- [ ] Every participating workstream has exactly one Good, one Better, and one Best outcome
- [ ] Every committed outcome has an owner, acceptance evidence, and at least one task
- [ ] Workstream aliases match the roadmap's registry — none minted here (or the plan is roadmap-less and uses no aliases)
- [ ] Trade rules make the drop order deterministic (Best, then Better; Good never)
- [ ] Every task has a stable ID, maps to a committed outcome, and names its work item or is marked for creation
- [ ] Runtime work items can derive from the task tables without inventing scope
