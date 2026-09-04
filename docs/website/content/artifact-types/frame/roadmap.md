---
title: "Roadmap"
linkTitle: "Roadmap"
slug: roadmap
activity: "Frame"
artifactRole: "supporting"
weight: 90
generated: true
---

## Purpose

Roadmap is the **sequencing artifact** between PRD priorities and iteration
commitment. Its unique job is to order framed capabilities and outcomes
across iterations or horizons, with dependencies, confidence, and an explicit
rationale for the order, so each iteration plan can pull its slot without
re-litigating priority.

It commits sequence, not owners or dates. The iteration plan commits one
time-box; the runtime tracker owns live status.

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: example.roadmap.depositmatch
  authoring:
    home: repo
  depends_on:
    - example.prd.depositmatch
---

# Roadmap

**Scope**: DepositMatch — deposit reconciliation for community banks
**Owner**: Product Owner
**Last Revised**: 2026-05-20 — pilot go decision re-ranked reporting behind matching

## Horizon and Cadence

- **Horizon**: 3 iterations (through pilot exit decision)
- **Cadence**: 2-week iterations, review on the final Friday
- **Beyond the horizon**: multi-bank tenancy and audit export stay in the
  improvement backlog, unsequenced, until pilot evidence arrives

## Workstreams

Workstreams are the stable cross-iteration groupings of work. The alias is
the identifier: `WS-<n>`, assigned sequentially, never reused or renumbered.

| Alias | Workstream | Scope | Owner | Status |
|-------|------------|-------|-------|--------|
| WS-1 | Data Intake | CSV import, fixtures, validation; excludes matching logic | Priya | active |
| WS-2 | Matching & Review | Matching engine and exception-review queue; excludes reporting | Sam | active |
| WS-3 | Pilot Reporting | Reconciliation summaries and exports for pilot exit | Priya | active |

## Sequenced Outcomes

| Order | Outcome | Workstream | Governing Artifact | Target Iteration | Depends On | Confidence | Why This Order |
|-------|---------|------------|--------------------|------------------|------------|------------|----------------|
| 1 | CSV import validated against real pilot-bank exports | WS-1 | PRD R-1, FEAT-001 | IT-05 | None | High | Every downstream feature consumes imported data; fixture risk is the top test-plan risk |
| 2 | Matching engine reaches ≥95% auto-match on pilot data | WS-2 | PRD R-2, FEAT-002 | IT-06 | 1 | Medium | Value driver of the pilot; needs real imports first to be measurable |
| 3 | Exception-review queue usable by pilot operations staff | WS-2 | PRD R-3, FEAT-003 | IT-06 | 2 | Medium | Unmatched deposits must land somewhere reviewable before pilot exit |
| 4 | Reconciliation summary report exportable | WS-3 | PRD R-5 | IT-07 | 2 | Low | Wanted for pilot exit review; drops first if matching accuracy needs the slot |

## Revision Triggers

- Pilot-bank fixture findings contradict the import assumptions (re-sequence
  within one business day of the finding).
- Matching accuracy plateaus below 90% (reporting drops off the horizon;
  accuracy work takes IT-07).
- The active iteration's committed outcomes stay stable across revisions;
  re-sequencing applies from the next iteration forward.

## Review Checklist

- [x] Every workstream has a stable `WS-<n>` alias, a scope line, and an owner
- [x] Every outcome cites its workstream and its governing artifact
- [x] Ordering states its rationale
- [x] The horizon is explicit; nothing beyond it is committed
- [x] Current-iteration outcomes match the active iteration plan
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Frame</strong></a> — Define what the system should do, for whom, and how success will be measured.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/01-frame/roadmap.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="../../../artifact-types/iterate/iteration-plan/">Iteration Plan</a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Roadmap Generation Prompt&#10;&#10;Document the delivery sequence for framed outcomes across iterations.&#10;&#10;## Purpose&#10;&#10;Roadmap is the **sequencing artifact** between PRD priorities and iteration&#10;commitment. Its unique job is to order framed capabilities and outcomes&#10;across iterations or horizons, with dependencies, confidence, and an explicit&#10;rationale for the order, so each iteration plan can pull its slot without&#10;re-litigating priority.&#10;&#10;It commits sequence, not owners or dates. The iteration plan commits one&#10;time-box; the runtime tracker owns live status.&#10;&#10;## Reference Anchors&#10;&#10;Use this local resource summary as grounding:&#10;&#10;- `docs/resources/safe-framework-2025.md` grounds outcome-based,&#10;  horizon-bounded roadmaps that stay revisable as evidence arrives.&#10;&#10;## Focus&#10;&#10;- Author a roadmap only when at least one of these holds: the project has&#10;  two or more workstreams, OR sequencing across two or more future&#10;  iterations is contested. When neither holds, skip it — the PRD&#x27;s&#10;  priorities and the improvement backlog carry the order, and a roadmap is&#10;  ceremony. (Same predicate as the routing skill&#x27;s Iterate skip test.)&#10;- Define the workstreams here, once. The roadmap is the registry of record&#10;  for workstream aliases: `WS-&lt;n&gt;`, assigned sequentially, never reused or&#10;  renumbered. Downstream artifacts and runtime work items reference the&#10;  alias (work items carry it as a label, e.g. `ws:WS-1`); they never mint&#10;  new workstreams.&#10;- Sequence outcomes, not tasks: each row delivers a governing artifact&#x27;s&#10;  requirement, feature, or backlog selection, inside a named workstream.&#10;- State why each item holds its position — dependency, risk retirement, or&#10;  value. An unexplained order is a quality-check failure.&#10;- Bound the horizon. Candidates beyond it stay in the improvement backlog or&#10;  parking lot, unsequenced.&#10;- Name the revision triggers. A roadmap that cannot say when it must change&#10;  will drift silently instead.&#10;&#10;## Boundary Test&#10;&#10;| If you are writing... | Put it in... |&#10;|---|---|&#10;| What the product must do and why | PRD |&#10;| Ranked improvement candidates with evidence | Improvement Backlog |&#10;| Workstream definitions and their `WS-&lt;n&gt;` aliases | Roadmap |&#10;| Delivery sequence across iterations | Roadmap |&#10;| One iteration&#x27;s committed outcomes, owners, and dates | Iteration Plan |&#10;| Live work-item status | runtime work item or issue |&#10;&#10;## Completion Criteria&#10;&#10;- Every workstream has a stable `WS-&lt;n&gt;` alias, a scope line, and an owner.&#10;- Every sequenced outcome traces to a workstream and a governing artifact.&#10;- Every position has a rationale.&#10;- The horizon and revision triggers are explicit.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: roadmap&#10;  authoring:&#10;    home: repo&#10;---&#10;&#10;# Roadmap&#10;&#10;**Scope**: [product or program this roadmap sequences]&#10;**Owner**: [role]&#10;**Last Revised**: [date — and which revision trigger fired]&#10;&#10;## Horizon and Cadence&#10;&#10;- **Horizon**: [how far ahead this roadmap commits — e.g. 3 iterations, 2 quarters]&#10;- **Cadence**: [iteration length and review rhythm]&#10;- **Beyond the horizon**: [where unsequenced candidates live — improvement backlog, parking lot]&#10;&#10;## Workstreams&#10;&#10;Workstreams are the stable cross-iteration groupings of work. The alias is&#10;the identifier: `WS-&lt;n&gt;`, assigned sequentially, never reused or renumbered —&#10;a closed workstream keeps its alias. Iteration plans and runtime work items&#10;reference workstreams by alias; they never mint new ones.&#10;&#10;| Alias | Workstream | Scope | Owner | Status |&#10;|-------|------------|-------|-------|--------|&#10;| [WS-1] | [name] | [one line: what belongs in it and what does not] | [name] | [active/closed] |&#10;&#10;## Sequenced Outcomes&#10;&#10;| Order | Outcome | Workstream | Governing Artifact | Target Iteration | Depends On | Confidence | Why This Order |&#10;|-------|---------|------------|--------------------|------------------|------------|------------|----------------|&#10;| 1 | [outcome] | [WS-1] | [PRD R-n / FEAT-nnn / backlog item] | [iteration id] | [dependency or None] | [high/med/low] | [dependency, risk, or value rationale] |&#10;| 2 | [outcome] | [WS-1] | [ref] | [iteration id] | [1] | [high/med/low] | [rationale] |&#10;&#10;## Revision Triggers&#10;&#10;- [Event that forces a re-sequence — e.g. a go/no-go finding, a slipped dependency, a backlog re-rank]&#10;- [What stays stable across revisions — e.g. the active iteration&#x27;s committed outcomes]&#10;&#10;## Review Checklist&#10;&#10;- [ ] Every workstream has a stable `WS-&lt;n&gt;` alias, a scope line, and an owner&#10;- [ ] Every outcome cites its workstream and its governing artifact&#10;- [ ] Ordering states its rationale&#10;- [ ] The horizon is explicit; nothing beyond it is committed&#10;- [ ] Current-iteration outcomes match the active iteration plan</code></pre></details></td></tr>
</tbody>
</table>
