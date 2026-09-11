# Iterate

Use to plan or report a human iteration: sequence a roadmap, define
workstreams, cut an iteration plan from the backlog and roadmap, or record
status against the active plan. This is the human-cadence loop of activity
`06-iterate`; runtime execution loops stay with the runtime
(§Runtime Handoff).

**Skip test — apply per artifact, before authoring.** These artifacts exist
to coordinate people; they cut risk only when there is coordination to do.
Each is authored only when its own predicate holds (conditions joined by
OR — any one suffices; none → skip that artifact):

- `roadmap`: two or more workstreams exist, OR sequencing across two or
  more future iterations is contested.
- `iteration-plan`: the iteration has two or more owners, OR two or more
  workstreams, OR ends in a review with an audience.
- `status-report`: the report has an audience (a review, a client
  checkpoint, a stakeholder update).

When an artifact's predicate fails, the tracker and the governing specs
already carry that work. Authoring all three because the types exist is
process as deliverable, which this methodology forbids (Deliverable Over
Machinery).

1. Read the governing artifacts first: PRD, roadmap, improvement backlog,
   and the active iteration plan when one exists.
2. Sequencing (`roadmap`): define the workstream registry and order framed
   outcomes across iterations with dependencies, confidence, and rationale;
   commit nothing beyond the stated horizon. Workstream aliases are stable
   `WS-<n>` — assigned sequentially, never reused or renumbered; a closed
   workstream keeps its alias. Aliases are unique within one flow instance.
   Downstream artifacts reference aliases and never mint workstreams; work
   items preserve the alias — as a label where the runtime supports labels
   (e.g. `ws:WS-1`, prefixed with the flow instance when several flows
   share one store), otherwise in the item's title or reference field.
3. Planning (`iteration-plan`): a time-boxed commitment — a falsifiable
   goal, and per participating workstream exactly one Good, one Better, and
   one Best outcome with owners and acceptance evidence. Good is the
   protected floor: never traded, and once committed its ID, text, and
   acceptance evidence are immutable for the iteration — a Good that
   becomes impossible is an escalation recorded in the status report with
   its decider named, never an in-place edit or re-tier. Best drops first,
   then Better; a workstream that cannot fill all three tiers is not
   participating this iteration, never partially committed. Workstream
   aliases come from the roadmap when one exists; a roadmap-less plan has
   one implicit workstream and uses no aliases — a second workstream means
   author the registry first. Every outcome maps to at least one task;
   outcome and task IDs are unique within the plan (fully qualified as
   `<iteration-id>.<id>`).
4. **Plan-owns-membership invariant**: the plan owns commitment membership —
   task rows select existing work items by ID, and rows without one are the
   source from which the runtime creates items (via §Runtime Handoff),
   back-referencing each new ID in the plan. The tracker owns live status
   and execution history; the plan's Status column is planning-time state
   only. Never turn the plan into the live tracker, and never let
   hand-added tracker items silently widen the plan — scope changes route
   back through the plan.
5. Reporting (`status-report`): outcome status against the plan's IDs with
   evidence per claim, whatever the status — done and at-risk cite proof or
   threat, on-track cites observable progress, dropped cites the trade or
   escalation; an evidence-free claim is a phantom claim. Trades cite the
   plan's trade rules; a Good at risk names its decider.
6. Close the loop: review learnings land in the improvement backlog, and
   revision triggers may re-sequence the roadmap. Do not fork an untracked
   side-plan.
