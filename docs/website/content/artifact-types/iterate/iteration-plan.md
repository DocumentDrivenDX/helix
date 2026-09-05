---
title: "Iteration Plan"
linkTitle: "Iteration Plan"
slug: iteration-plan
activity: "Iterate"
artifactRole: "supporting"
weight: 90
generated: true
---

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

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: example.iteration-plan.depositmatch
  authoring:
    home: repo
  depends_on:
    - example.roadmap.depositmatch
    - example.improvement-backlog.depositmatch
---

# Iteration Plan

| | |
|---|---|
| **Iteration** | IT-05 |
| **Dates** | Mon 1 Jun → Fri 12 Jun 2026 |
| **Review** | Fri 12 Jun, 30-minute demo with pilot-bank operations lead |
| **Lead** | Delivery Lead |
| **Roadmap Slot** | Roadmap order 1 — CSV import validated against real pilot-bank exports |

## Iteration Goal

> By 12 Jun, a pilot-bank operations user imports a real deposit export and
> sees validated rows with actionable errors — shown live in the review demo
> against an anonymized pilot fixture, with the import test suite green.

## Committed Outcomes

Each participating workstream commits exactly one Good, one Better, and one
Best outcome. Good is the protected floor; Best drops first, then Better.
Tiers: 🟢 Good = committed for the review · 🔵 Better = first traded under
pressure · 🟣 Best = only if the iteration runs clean.

| ID | Workstream | Tier | Outcome | Owner | Governing Artifact | Acceptance Evidence |
|----|------------|------|---------|-------|--------------------|---------------------|
| WS-1-good | WS-1 | 🟢 Good | A real anonymized pilot export imports with validated rows — fixtures collected, anonymization documented, all fixture error classes handled | Priya | Improvement backlog rank 1; FEAT-001; story test plan US-003 | Fixture set committed; tests citing US-003 ACs pass; live demo at review |
| WS-1-better | WS-1 | 🔵 Better | Upload p95 latency watch item on the pilot dashboard | Priya | Improvement backlog rank 2 | Dashboard panel live with alert threshold |
| WS-1-best | WS-1 | 🟣 Best | Per-row error messages include remediation hints | Sam | FEAT-001 | Hint text reviewed by operations lead; shown in demo |

**Not participating this iteration**: WS-2 (matching starts IT-06 per
roadmap order 2), WS-3 (reporting gated on matching)

## Trade Rules

- Best drops first, then Better — the Delivery Lead calls trades and records
  them in the status report.
- WS-1-good is never traded: without it the review demo has no honest data
  and the iteration fails. A Good at risk is an escalation, not a trade.

## Tasks

The plan owns membership; the tracker owns live state. Existing work items
are selected by ID in the Work Item column; rows marked `—` are created by
the runtime from this table and back-referenced here. Status records
planning-time state and is not maintained after derivation. Workstream
aliases come from the roadmap's registry; work items carry the alias as a
label (`ws:WS-1`).

### WS-1 · Data Intake — fixtures

| ID | Task | Outcome | Owner | Due | Status | Work Item |
|----|------|---------|-------|-----|--------|-----------|
| 1.1 | Collect three real pilot-bank exports under the data agreement | WS-1-good | Priya | Wed 3 Jun | Backlog | wi-231 (existing) |
| 1.2 | Script and document the anonymization pass | WS-1-good | Priya | Fri 5 Jun | Backlog | — |

### WS-1 · Data Intake — import validation

| ID | Task | Outcome | Owner | Due | Status | Work Item |
|----|------|---------|-------|-----|--------|-----------|
| 2.1 | Enumerate fixture error classes into US-003 test cases | WS-1-good | Sam | Fri 5 Jun | Backlog | — |
| 2.2 | Implement per-row validation error messages | WS-1-good | Sam | Wed 10 Jun | Backlog | — |
| 2.3 | Add remediation hints to error messages | WS-1-best | Sam | Thu 11 Jun | Backlog | — |

### WS-1 · Data Intake — pilot dashboard

| ID | Task | Outcome | Owner | Due | Status | Work Item |
|----|------|---------|-------|-----|--------|-----------|
| 3.1 | Add upload p95 latency panel with alert threshold to the pilot dashboard | WS-1-better | Priya | Tue 9 Jun | Backlog | — |

## Risks

| Risk | Impact | Response |
|------|--------|----------|
| Pilot bank delays export delivery | H | Escalate through the pilot sponsor by 3 Jun; fall back to synthetic fixtures and flag confidence in the review |
| Anonymization strips fields validation depends on | M | Review field list with operations lead before scripting |

## Review Checklist

- [x] Goal is falsifiable at the review date
- [x] Every participating workstream has exactly one Good, one Better, and one Best outcome
- [x] Every committed outcome has an owner, acceptance evidence, and at least one task
- [x] Workstream aliases match the roadmap's registry — none minted here
- [x] Trade rules make the drop order deterministic (Best, then Better; Good never)
- [x] Every task has a stable ID, maps to a committed outcome, and names its work item or is marked for creation
- [x] Runtime work items can derive from the task tables without inventing scope
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Iterate</strong></a> — Measure, align, and improve. Close the feedback loop back into the planning strand.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/06-iterate/iteration-plan-[iteration-id].md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="../../../artifact-types/iterate/status-report/">Status Report</a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Iteration Plan Generation Prompt&#10;&#10;Document one human iteration&#x27;s commitment.&#10;&#10;## Purpose&#10;&#10;Iteration Plan is the **commitment artifact** of the iterate loop. Its unique&#10;job is to convert the improvement backlog&#x27;s next-iteration selection and the&#10;roadmap&#x27;s current slot into one time-boxed commitment: a falsifiable goal,&#10;one Good / one Better / one Best outcome per participating workstream with&#10;owners and acceptance evidence, deterministic trade rules, and stable-ID task&#10;tables.&#10;&#10;It is not the live tracker. The plan owns commitment membership: task rows&#10;select existing work items by ID where they exist, and rows without one are&#10;the source from which the runtime creates items, back-referencing each new&#10;ID in the plan. The runtime&#x27;s tracker (work items, boards, issues) owns live&#10;status, assignment churn, and execution history. Scope changes route back&#10;through the plan — hand-added tracker items never silently widen the&#10;commitment.&#10;&#10;## Reference Anchors&#10;&#10;Use this local resource summary as grounding:&#10;&#10;- `docs/resources/agile-manifesto-principles.md` grounds time-boxed&#10;  commitment, sustainable cadence, and working evidence as the measure of&#10;  progress.&#10;&#10;## Focus&#10;&#10;- Author a plan only when there is a commitment to coordinate — multiple&#10;  owners, multiple workstreams, or a review with an audience. A solo&#10;  iteration may run straight from the backlog selection and the tracker;&#10;  the plan is coordination, not ceremony.&#10;- Make the goal falsifiable: what is true at review, shown by what evidence.&#10;- Commit exactly one Good, one Better, and one Best outcome per&#10;  participating workstream. Good is the protected floor; Best drops first,&#10;  then Better. More outcomes per workstream is confusing; fewer breaks the&#10;  flex model — a workstream that cannot fill all three tiers sits this&#10;  iteration out (not participating), never partially committed.&#10;- Once committed, a Good outcome&#x27;s ID, text, and acceptance evidence are&#10;  immutable for the iteration. A Good that becomes impossible is an&#10;  escalation recorded in the status report with its decider named — never an&#10;  in-place edit, re-tier, or silent replacement.&#10;- Give every outcome an owner, acceptance evidence, and at least one task.&#10;  Outcome IDs are `&lt;WS alias&gt;-good|better|best`, unique within the plan;&#10;  fully qualified as `&lt;iteration-id&gt;.&lt;outcome-id&gt;` when cited elsewhere.&#10;- Reference workstreams by their roadmap-registry alias (`WS-&lt;n&gt;`) when a&#10;  roadmap exists; a roadmap-less plan (single-workstream skip case) has one&#10;  implicit workstream and uses no aliases — a second workstream means author&#10;  the registry first. The plan never mints workstreams. Work items preserve&#10;  the alias: as a label where the runtime supports labels (e.g. `ws:WS-1`,&#10;  prefixed with the flow instance when several flows share one store),&#10;  otherwise in the item&#x27;s title or reference field.&#10;- Keep the plan derivable: a runtime should be able to create work items&#10;  from the task tables without inventing scope.&#10;- Write tier labels in table cells as emoji plus a non-breaking space&#10;  (U+00A0) plus the word — 🟢 Good, 🔵 Better, 🟣 Best — so the label never&#10;  wraps apart in rendered tables. Plain words are fine in prose.&#10;- Reference implementation plans where a committed outcome has one; do not&#10;  duplicate their build slices here.&#10;&#10;## Boundary Test&#10;&#10;| If you are writing... | Put it in... |&#10;|---|---|&#10;| Workstream definitions and their `WS-&lt;n&gt;` aliases | Roadmap |&#10;| Delivery sequence across iterations | Roadmap |&#10;| Ranked improvement candidates with evidence | Improvement Backlog |&#10;| One iteration&#x27;s committed outcomes, owners, and dates | Iteration Plan |&#10;| Design-derived build slices for one feature | Implementation Plan |&#10;| Live task status, assignees, execution history | runtime work item or issue |&#10;| How the iteration is going or went | Status Report |&#10;&#10;## Completion Criteria&#10;&#10;- The goal is falsifiable and the review date is set.&#10;- Every participating workstream has exactly one Good, one Better, and one&#10;  Best outcome, each with an owner and acceptance evidence.&#10;- Every committed outcome maps to at least one task.&#10;- Workstream aliases match the roadmap&#x27;s registry (or the plan is&#10;  roadmap-less and uses none).&#10;- Trade rules make the drop order deterministic (Best, then Better; Good&#10;  never).&#10;- Every task has a stable ID, maps to a committed outcome, and names its&#10;  work item or is marked for creation.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: iteration-plan&#10;  authoring:&#10;    home: repo&#10;---&#10;&#10;# Iteration Plan&#10;&#10;| | |&#10;|---|---|&#10;| **Iteration** | [id — e.g. IT-05, Sprint 3] |&#10;| **Dates** | [start → end] |&#10;| **Review** | [date and format of the iteration review] |&#10;| **Lead** | [who runs the iteration] |&#10;| **Roadmap Slot** | [roadmap order/iteration this fulfills, or N/A] |&#10;&#10;## Iteration Goal&#10;&#10;&gt; [One falsifiable sentence: what is true at review that is not true now,&#10;&gt; and what evidence shows it.]&#10;&#10;## Committed Outcomes&#10;&#10;Each participating workstream commits exactly one outcome per tier — one&#10;Good, one Better, one Best. Good is the protected floor: the iteration fails&#10;without it, and once committed its ID, text, and acceptance evidence are&#10;immutable for the iteration — a Good that becomes impossible is recorded as&#10;an escalation in the status report (decider named), never edited, re-tiered,&#10;or silently replaced. Best drops first under pressure, then Better. More&#10;outcomes per workstream is confusing; fewer breaks the flex model. A&#10;workstream sitting out this iteration is listed as not participating, never&#10;partially committed. (Participation is per-iteration; a workstream&#x27;s&#10;registry status — active/closed — lives in the roadmap and is a different&#10;axis.) Outcome IDs are unique within this plan; the fully qualified form is&#10;`&lt;iteration-id&gt;.&lt;outcome-id&gt;` (e.g. `IT-05.WS-1-good`).&#10;Tier labels render as emoji plus a non-breaking space (U+00A0) so they never&#10;wrap in table cells: 🟢 Good · 🔵 Better · 🟣 Best.&#10;&#10;| ID | Workstream | Tier | Outcome | Owner | Governing Artifact | Acceptance Evidence |&#10;|----|------------|------|---------|-------|--------------------|---------------------|&#10;| [WS-1-good] | [WS-1] | 🟢 Good | [the outcome the iteration fails without] | [name] | [artifact ref] | [what proves it landed] |&#10;| [WS-1-better] | [WS-1] | 🔵 Better | [real value, first traded after Best] | [name] | [artifact ref] | [what proves it landed] |&#10;| [WS-1-best] | [WS-1] | 🟣 Best | [taken only if the iteration runs clean] | [name] | [artifact ref] | [what proves it landed] |&#10;&#10;**Not participating this iteration**: [WS-n (reason), or None]&#10;&#10;## Trade Rules&#10;&#10;- Best drops first, then Better — per workstream. [Who] calls trades and&#10;  records them in the status report.&#10;- Good outcomes are never traded: a Good at risk is an escalation, not a&#10;  trade.&#10;&#10;## Tasks&#10;&#10;The plan owns membership; the runtime&#x27;s tracker owns live state. Select&#10;existing work items by ID in the Work Item column; a task without one is&#10;created by the runtime from this table and its new ID back-referenced here.&#10;Every committed outcome maps to at least one task. Task IDs are stable —&#10;never renumber mid-iteration — and unique within this plan (fully qualified:&#10;`&lt;iteration-id&gt;.&lt;task-id&gt;`, e.g. `IT-05.1.1`). The Status column records&#10;planning-time state (normally Backlog); once work items derive, the tracker&#10;is authoritative and this column is not maintained.&#10;&#10;Workstream aliases come from the roadmap&#x27;s registry when one exists. A plan&#10;authored without a roadmap (single-workstream skip case) has one implicit&#10;workstream and omits aliases entirely; the moment a second workstream&#10;appears, author the roadmap&#x27;s registry first. Aliases are unique within one&#10;flow instance. Work items preserve the alias: as a label where the runtime&#10;supports labels (e.g. `ws:WS-1`, prefixed with the flow instance when&#10;several flows share one store), otherwise in the item&#x27;s title or reference&#10;field.&#10;&#10;### [WS-1 · workstream name]&#10;&#10;| ID | Task | Outcome | Owner | Due | Status | Work Item |&#10;|----|------|---------|-------|-----|--------|-----------|&#10;| [1.1] | [task] | [WS-1-good] | [name] | [date] | [Backlog] | [existing item ID, or — until created] |&#10;&#10;## Risks&#10;&#10;| Risk | Impact | Response |&#10;|------|--------|----------|&#10;| [risk] | [H/M/L] | [action] |&#10;&#10;## Review Checklist&#10;&#10;- [ ] Goal is falsifiable at the review date&#10;- [ ] Every participating workstream has exactly one Good, one Better, and one Best outcome&#10;- [ ] Every committed outcome has an owner, acceptance evidence, and at least one task&#10;- [ ] Workstream aliases match the roadmap&#x27;s registry — none minted here (or the plan is roadmap-less and uses no aliases)&#10;- [ ] Trade rules make the drop order deterministic (Best, then Better; Good never)&#10;- [ ] Every task has a stable ID, maps to a committed outcome, and names its work item or is marked for creation&#10;- [ ] Runtime work items can derive from the task tables without inventing scope</code></pre></details></td></tr>
</tbody>
</table>
