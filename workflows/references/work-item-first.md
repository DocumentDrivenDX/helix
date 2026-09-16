# Reference: Work-Item-First Execution

Every HELIX action that modifies files is governed by a work item. This
reference defines the acquisition pattern the actions follow.

The pattern is runtime-neutral: it names the **actions** (find, create, claim,
close a governing work item), not the commands. The runtime supplies the
work-item store; for the DDx runtime the concrete commands are in the DDx
install guide.

## Why work-item-first

Without a governing work item, actions modify files ad hoc: no plan to measure
against, no acceptance criteria to verify, no record of intent. A governing
item gives:

- **Traceability**: every file change traces to an item with a description,
  acceptance criteria, and governing artifact references.
- **Measurability**: the item's acceptance criteria define "done"; measurement
  results are recorded on the item.
- **Feedback**: the report activity files follow-on items from measurement
  findings.

## Acquisition pattern

Every action except `input` and `check` runs Activity 0.5 (work-item
acquisition) immediately after bootstrap.

### 1. Find an existing governing work item

Search the tracker for an open item labelled for this action
(`kind:planning,action:<name>`). When the action was dispatched with a scope,
filter by scope or `spec-id` for an item that governs this exact work.

If a matching open item exists: verify it is still relevant (not stale, not
superseded), then claim it so concurrent work is prevented.

### 2. Create one when none exists

The new item carries:

- a title of the form `<action>: <scope description>`
- type `task` and labels `helix,activity:<activity>,kind:planning,action:<name>`
- a `spec-id` naming the governing artifact
- a description holding a `<context-digest>` assembled per
  `workflows/references/context-digest.md`, the action's inputs and scope, and
  references to governing artifacts
- specific, verifiable acceptance criteria

Acceptance criteria examples:

| Action | Example acceptance criteria |
|--------|---------------------------|
| `design` | "Design document converged with all required sections including concern-mandated sections; written to canonical path" |
| `polish` | "All plans in scope decomposed into work items; convergence reached (< 3 changes for 2 consecutive rounds); context digests refreshed" |
| `evolve` | "Requirement threaded through all affected artifacts; no unresolved conflicts; downstream work items created" |
| `align` | "Alignment review complete; all gaps classified; execution items created for real gaps" |
| `backfill` | "Missing artifacts reconstructed; assumption ledger complete; follow-up items created for guidance-dependent items" |
| `review` | "All review passes complete; findings filed as work items" |
| `frame` | "Artifacts created/updated per type requirements; downstream design items filed" |

### 3. Every later file change is governed by that item

After acquisition, the item ID anchors the action: commit messages reference
it, measurement records against it, report closes it.

## Label convention

Planning items carry two labels beyond `helix` and the activity label:

- `kind:planning` distinguishes planning work from execution work
- `action:<name>` names the action that will execute the item

Execution items, the ones a runtime executes against the governing artifacts,
carry no `kind:planning` or `action:*` label; they carry `activity:build`,
`activity:deploy`, or `activity:iterate`.

## Exceptions

- **`input`**: work-item creation is the entry point that bootstraps the
  work-item graph; requiring a governing item for it is infinite regress.
- **`check`**: read-only. It modifies no files and needs no governing item.
- **Operator-created items**: an operator (human or outer agent) may create the
  governing item before dispatching the action; acquisition then finds it
  instead of creating one. This is the preferred pattern for deliberate work.

## Lifecycle

```
find or create → claim → execute → measure → report → close
```

1. **Find or create**: Activity 0.5 of every action.
2. **Claim**: prevent concurrent work on the item.
3. **Execute**: the action's activities 1 through N.
4. **Measure**: verify acceptance criteria; record results on the item.
5. **Report**: file follow-on items; close the governing item with evidence.
6. **Close**: summarize what was done on the item.

`workflows/references/measure.md` and `workflows/references/report.md` define
the measure and report activities.
