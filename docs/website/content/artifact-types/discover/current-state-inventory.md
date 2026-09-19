---
title: "Current-State Inventory"
linkTitle: "Current-State Inventory"
slug: current-state-inventory
activity: "Discover"
artifactRole: "supporting"
weight: 90
generated: true
---

## Purpose

Answers: **What does this organization actually have, and how much of that do
we know rather than assume?**

The second half is the point. An inventory that lists components without
grading them reads as knowledge and is often mostly hearsay — a slide box and
a running production system look identical in a table. The evidence grade is
what separates them, and it is the artifact's reason to exist.

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: current-state-inventory-analytics-estate
  type: current-state-inventory
  status: draft
  authoring:
    home: repo
---

# Current-State Inventory: Analytics Estate

Register of what Northwind Retail already runs for reporting and analytics,
each entry graded for evidence. **This is a survey, not a target.** The
warehouse consolidation decision lives in [[architecture]] and ADR-014.

## Scope and Boundary

- Estate: reporting, analytics and the pipelines feeding them
- Surveyed: 3–17 March 2026
- Excluded: transactional systems (covered by the order-platform inventory);
  marketing SaaS, which Marketing Ops owns and has not shared
- Owner: Priya Raman, Data Platform

## Evidence Grades

| Grade | Means |
|-------|-------|
| **Evidenced** | A named source attests it exists and works this way. Cited, with a date. |
| **Partial** | It exists, but a design-defining fact about it is unrecorded. |
| **Assumed** | Claimed, with no source. It may be real; we cannot say so. |
| **Aspirational** | Target state. It does not exist today. |
| **Spike-open** | A design-defining fact is assumed *and* blocks a decision. |

An entry graded Evidenced with no citation is Assumed.

## Inventory

### Ingestion

| Component | Supplier / incumbent | Grade | Evidence |
|-----------|----------------------|-------|----------|
| Nightly ETL | Airflow 2.6, self-hosted | Evidenced | Runbook walkthrough, Priya Raman, 5 Mar 2026. 41 DAGs, 02:00 UTC |
| CDC from orders DB | Debezium | Partial | Confirmed running (Priya, 5 Mar). Which tables it covers is unrecorded |
| Partner SFTP drops | — | Assumed | Named on the 2024 platform diagram; no owner found, no job scheduling it |

### Storage

| Component | Supplier / incumbent | Grade | Evidence |
|-----------|----------------------|-------|----------|
| Warehouse | Redshift, 4-node ra3.xlplus | Evidenced | Billing console, 6 Mar 2026 |
| Lake | S3, `nw-analytics-raw` | Partial | Exists (console). Retention policy and access model unrecorded |
| Lakehouse | Iceberg on S3 | Aspirational | On the FY27 plan. No table, no catalog, no owner |

### Consumption

| Component | Supplier / incumbent | Grade | Evidence |
|-----------|----------------------|-------|----------|
| Exec dashboards | Looker | Evidenced | Licence renewal, 12 Mar 2026. 9 of 340 dashboards viewed weekly |
| Ad-hoc SQL | Redshift Query Editor | Evidenced | Query logs, 11 Mar 2026 |
| Notebooks | — | Spike-open | Analysts describe "notebooks" without naming a platform. Blocks the compute-isolation decision in ADR-014 |
| Embedded reporting | — | Assumed | On the diagram. No consumer found |

## Totals

Tallied from the rows above, 17 March 2026.

| Grade | Count | Share |
|-------|-------|-------|
| Evidenced | 4 | 40% |
| Partial | 2 | 20% |
| Aspirational | 1 | 10% |
| Assumed | 2 | 20% |
| Spike-open | 1 | 10% |

**3 of 10 entries have no evidence they exist** — the Assumed and Aspirational
rows. Two of those three are on the 2024 platform diagram and nowhere else,
which is the strongest argument in this document for retiring that diagram.

## Open Questions

| # | Question | Blocks | Owner |
|---|----------|--------|-------|
| 1 | Which tables does CDC actually cover? | Warehouse consolidation scope | Priya Raman |
| 2 | What do analysts mean by "notebooks"? | ADR-014 compute isolation | Sam Okafor |
| 3 | Does anything consume the partner SFTP drops? | Whether ingestion can be retired | Priya Raman |

## Review Checklist

- [x] Every entry carries exactly one grade from the declared vocabulary
- [x] Every Evidenced entry names a source and a date
- [x] Totals are tallied from this revision, not carried forward
- [x] The unevidenced share is stated, not implied
- [x] Scope and exclusions are both stated
- [x] No target state, recommendation or decision has crept in
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Discover</strong></a> — Validate that an opportunity is worth pursuing before committing to a development cycle.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/00-discover/current-state-inventory-[estate-name].md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="../../../artifact-types/design/architecture/">Architecture</a><br><a href="../../../artifact-types/frame/feasibility-study/">Feasibility Study</a><br><a href="../../../artifact-types/discover/business-case/">Business Case</a><br><a href="../../../artifact-types/frame/prd/">PRD</a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Current-State Inventory Generation Prompt&#10;&#10;Record what the organization already has, graded for evidence, before any&#10;target state is proposed.&#10;&#10;## Storage Location&#10;&#10;Store at: `docs/helix/00-discover/current-state-inventory-[estate-name].md`&#10;&#10;## Purpose&#10;&#10;Answers: **What does this organization actually have, and how much of that do&#10;we know rather than assume?**&#10;&#10;The second half is the point. An inventory that lists components without&#10;grading them reads as knowledge and is often mostly hearsay — a slide box and&#10;a running production system look identical in a table. The evidence grade is&#10;what separates them, and it is the artifact&#x27;s reason to exist.&#10;&#10;## Role Boundary&#10;&#10;A Current-State Inventory is not an architecture. Architecture states what the&#10;system should be and records the decisions that get it there; this states what&#10;is there now. When an entry needs a decision, the decision goes in an ADR and&#10;this inventory cites it.&#10;&#10;It is also not a [[data-flow-analysis]]. That documents **one** business&#10;process end to end — its actors, transformations and constraints. This covers&#10;**many** components at register depth, one row each.&#10;&#10;It is not a vendor evaluation. Comparative assessment belongs in&#10;[[competitive-analysis]].&#10;&#10;## Method&#10;&#10;1. **Fix the boundary first.** Name what the inventory covers and what it&#10;   excludes. An unbounded inventory is never finishable and never trusted.&#10;2. **Choose one grouping scheme** — capability, layer, owning function, vendor&#10;   — and hold it for the whole instance. Mixed schemes hide gaps.&#10;3. **One row per component.** Resist bundling: two products under one row take&#10;   one grade, and the weaker evidence disappears behind the stronger. If two&#10;   things have different grades, owners or adoption states, they are two rows.&#10;4. **Grade every row, then find the source.** Write the citation before the&#10;   grade is allowed to be Evidenced. A source is a named document, meeting,&#10;   or person plus a date — not &quot;the team says&quot;.&#10;5. **Tally the totals from the rows you just wrote.** Never carry them&#10;   forward.&#10;6. **State the unevidenced share in words.** The reader should not have to do&#10;   arithmetic to learn how much of this is assumption.&#10;&#10;## Grading Honestly&#10;&#10;The pressure on this artifact is always toward optimism: a sponsor wants the&#10;estate to look known, and every Assumed row reads as a gap in the author&#x27;s&#10;work rather than a gap in the organization&#x27;s knowledge. It is the opposite.&#10;**The unevidenced rows are the finding.** An inventory that grades two-thirds&#10;of its entries Assumed has done its job and should say so in its own words.&#10;&#10;Watch for these specifically:&#10;&#10;- **Bundling as flattery.** Merging rows reduces the count of unevidenced&#10;  entries without changing what is known.&#10;- **Evidenced by familiarity.** &quot;Everyone knows we use X&quot; is Assumed.&#10;- **Aspirational drift.** A component that is planned, funded and staffed is&#10;  still Aspirational until it exists.&#10;- **Stale totals.** Numbers carried from a previous revision assert a&#10;  freshness the revision does not have.&#10;&#10;## Inputs&#10;&#10;- Existing architecture diagrams, slides and vendor lists — treat each as a&#10;  claim to verify, never as a source&#10;- Meeting notes, emails and interviews, which are where citations come from&#10;- Any system of record for assets, licences or spend&#10;&#10;## Quality Checks&#10;&#10;- Every entry carries exactly one grade from the declared vocabulary&#10;- Every Evidenced entry names a source and a date&#10;- Totals tally against the rows in this revision&#10;- The unevidenced share appears in prose&#10;- Scope and exclusions are both stated&#10;- No target state, recommendation or decision appears anywhere</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: current-state-inventory&#10;  authoring:&#10;    home: repo&#10;---&#10;&#10;# Current-State Inventory: [Estate or Domain Name]&#10;&#10;Register of what the organization already has, each entry graded for evidence.&#10;Captured during Discover to ground architecture and modernization decisions in&#10;the estate as it is. **This is a survey, not a target.** Target state,&#10;recommendations and decisions belong in [[architecture]] and its ADRs.&#10;&#10;One instance covers one estate or domain. A large organization produces&#10;several — by business unit, by platform, or by capability area.&#10;&#10;## Scope and Boundary&#10;&#10;- Estate: [What this inventory covers]&#10;- Surveyed: [Date range the evidence was gathered]&#10;- Excluded: [What is deliberately out of scope, and why]&#10;- Owner: [Who maintains this inventory]&#10;&#10;## Evidence Grades&#10;&#10;Every entry carries exactly one grade. State the vocabulary here so a reader&#10;knows what each grade licenses them to claim.&#10;&#10;| Grade | Means |&#10;|-------|-------|&#10;| **Evidenced** | A named source attests it exists and works this way. Cited, with a date. |&#10;| **Partial** | It exists, but a design-defining fact about it is unrecorded. |&#10;| **Assumed** | Claimed — on a slide, in conversation — with no source. It may be real; we cannot say so. |&#10;| **Aspirational** | Target state. It does not exist today, and this entry does not claim it does. |&#10;| **Spike-open** | A design-defining fact is assumed *and* blocks a decision. Name the decision it blocks. |&#10;&#10;An entry graded **Evidenced** with no citation is **Assumed**. Grade honestly:&#10;an inventory that flatters the estate is worse than no inventory, because it&#10;is trusted.&#10;&#10;## Inventory&#10;&#10;Group by whatever structure the estate actually has — capability, layer,&#10;owning function, vendor. Keep one grouping scheme for the whole instance.&#10;&#10;### [Group name]&#10;&#10;| Component | Supplier / incumbent | Grade | Evidence |&#10;|-----------|----------------------|-------|----------|&#10;| [Name] | [Who provides it, or *No incumbent*] | [Grade] | [Named source and date, or what is missing] |&#10;&#10;## Totals&#10;&#10;Tally from the inventory above **in this revision**. Never carry totals&#10;forward from a previous one — a stale total is a false claim about how much&#10;is known.&#10;&#10;| Grade | Count | Share |&#10;|-------|-------|-------|&#10;| Evidenced | [n] | [%] |&#10;| Partial | [n] | [%] |&#10;| Aspirational | [n] | [%] |&#10;| Assumed | [n] | [%] |&#10;| Spike-open | [n] | [%] |&#10;&#10;**[n] of [total] entries have no evidence they exist** — the Assumed and&#10;Aspirational rows. State this plainly; do not leave the reader to count.&#10;&#10;## Open Questions&#10;&#10;| # | Question | Blocks | Owner |&#10;|---|----------|--------|-------|&#10;| 1 | [What is unknown about a component, stated as a question] | [What the answer unblocks] | [Named person] |&#10;&#10;## Review Checklist&#10;&#10;- [ ] Every entry carries exactly one grade from the declared vocabulary&#10;- [ ] Every Evidenced entry names a source and a date&#10;- [ ] Totals are tallied from this revision, not carried forward&#10;- [ ] The unevidenced share is stated, not implied&#10;- [ ] Scope and exclusions are both stated&#10;- [ ] No target state, recommendation or decision has crept in</code></pre></details></td></tr>
</tbody>
</table>
