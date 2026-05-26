# Reference: Work-Item-First Execution

Every HELIX action that modifies files must be governed by a work item. This
reference defines the work-item acquisition pattern that all actions follow.

This pattern is runtime-neutral: it specifies the **actions** (find, create,
claim, close a governing work item), not the commands. A runtime supplies the
work-item store. For the concrete commands that realize each action below, see
the runtime's install guide ([`docs/install/ddx.md`](../../docs/install/ddx.md)
for the DDx reference runtime).

## Why Work-Item-First

Without a governing work item, actions modify files ad hoc — there is no plan to
measure against, no acceptance criteria to verify, and no traceable record of
what the action intended to do. Work-item-first ensures:

- **Traceability**: Every file change traces back to a work item with a
  description, acceptance criteria, and governing artifact references.
- **Measurability**: After execution, the item's acceptance criteria define what
  "done" means, and measurement results are recorded on the item.
- **Feedback**: The report activity creates follow-on items from measurement
  findings, closing the loop between the execution helix and the planning helix.

## Acquisition Pattern

Every action (except `triage` and `check`) includes an Activity 0.5 — Work-Item
Acquisition immediately after bootstrap:

### 1. Search for an existing governing work item

Query the tracker for an open item labelled for this action
(`kind:planning,action:<name>`). If the action was dispatched with a specific
scope (e.g., `/helix design auth`), filter by scope or `spec-id` to find an item
that governs this exact work.

If a matching open item exists:
- Verify it is still relevant (not stale, not superseded).
- Claim it so concurrent work is prevented.

### 2. Create a new governing work item if none exists

Create an item that carries:
- A title of the form `<action>: <scope description>`
- Type `task` and labels `helix,activity:<appropriate-activity>,kind:planning,action:<name>`
- A `spec-id` pointing at the governing artifact
- A description that includes a `<context-digest>` assembled per
  `workflows/references/context-digest.md`, the action's inputs and scope, and
  references to governing artifacts
- Specific, verifiable acceptance criteria

The acceptance criteria must be specific and verifiable. Examples:

| Action | Example acceptance criteria |
|--------|---------------------------|
| `design` | "Design document converged with all required sections including concern-mandated sections; written to canonical path" |
| `polish` | "All plans in scope decomposed into work items; convergence reached (< 3 changes for 2 consecutive rounds); context digests refreshed" |
| `evolve` | "Requirement threaded through all affected artifacts; no unresolved conflicts; downstream work items created" |
| `align` | "Alignment review complete; all gaps classified; execution items created for real gaps" |
| `backfill` | "Missing artifacts reconstructed; assumption ledger complete; follow-up items created for guidance-dependent items" |
| `build` | (already item-driven — uses the execution item directly) |
| `review` | "All review passes complete; findings filed as work items; AGENTS.md updated if needed" |
| `frame` | "Artifacts created/updated per type requirements; downstream design items filed" |

### 3. All subsequent file modifications are governed by this work item

After acquisition, the item ID is the action's anchor. Commit messages
reference it. Measurement records against it. Report closes it.

## Label Convention

Planning-helix items use two labels:

- `kind:planning` — distinguishes planning work from execution work
- `action:<name>` — identifies which action will execute this item

Combined with the standard `helix` label and activity labels, a typical planning
item has labels: `helix,kind:planning,action:design,activity:build`.

Execution items (those consumed by the runtime's build loop) do not carry
`kind:planning` or `action:*` labels — they carry `activity:build`,
`activity:deploy`, or `activity:iterate` as before.

## Exceptions

### Triage

Work-item creation is the entry point that bootstraps the work-item graph.
Requiring triage to have its own governing item would be infinite regress.
Triage is exempt from acquisition.

### Check

`/helix check` is read-only. It does not modify files and does not require a
governing item. It reads both helices and recommends which one needs attention
next.

### Operator-created work items

When an operator (human or outer agent) dispatches an action, they may create
the governing item themselves before invoking the action. In this case, the
action's acquisition activity finds the existing item rather than creating a new
one. This is the preferred pattern for deliberate work — the operator decides
what to do (planning helix), then the agent executes it (execution helix).

## Lifecycle

```
create/find → claim → execute → measure → report → close
```

1. **Create/find**: Activity 0.5 of every action.
2. **Claim**: claim the item to prevent concurrent work.
3. **Execute**: The action's main activities (Activity 1 through N).
4. **Measure**: Verify acceptance criteria; record results on the item.
5. **Report**: Create follow-on items; close the governing item with evidence.
6. **Close**: close the item with a summary of what was done.

See `workflows/references/measure.md` and `workflows/references/report.md`
for the measure and report activities.
