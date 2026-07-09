---
title: "Data Flow Analysis"
linkTitle: "Data Flow Analysis"
slug: data-flow-analysis
activity: "Discover"
artifactRole: "supporting"
weight: 13
generated: true
---

## Purpose

Answers: **What does this flow actually do today, and what would we need to
know to modernize it?** This is a concrete, technical companion to
higher-level Discover artifacts — it documents a system as it exists, not a
market or an opportunity.

## Authoring guidance

- **One flow per document.** Do not try to cover an entire legacy system in
  a single pass — break it into individual flows first.
- **Name sources and sinks concretely.** The actual system, table, file, or
  API, not a vague description like "the database."
- **Type every actor.** Each one is either a person doing a manual step or
  an automated system; say which, and what they actually do.
- **Capture data on both sides.** What comes in and what goes out, in
  enough detail that another engineer could find it without asking the
  person who wrote this document.
- **Constraints matter as much as the happy path.** Format, timing, volume,
  and access requirements shape any future redesign as much as the
  transformation logic does.
- **Don't skip Risks, Assumptions, and Modernization Notes.** This section
  is the payoff for doing this analysis instead of just reading the code or
  spreadsheet directly.
- **Leave the Notes section genuinely open-ended.** An engineer who fills it

_Additional guidance continues in the full prompt below._

<details>
<summary>Quality checklist from the prompt</summary>

- [ ] Every source and sink is named concretely
- [ ] Every actor is identified as a Person or an Automated System
- [ ] Business value is stated explicitly in Flow Summary
- [ ] Constraints on inputs and outputs are captured
- [ ] Overall complexity or scale is estimated, even roughly
- [ ] Risks, assumptions, and modernization recommendations are present, not
      left blank

</details>

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: example.data-flow-analysis.depositmatch
---

# Data Flow Analysis

## Flow Summary

- Process name: Manual Deposit-to-Invoice Reconciliation
- Frequency: Weekly, every Friday
- Current state: Manual
- Business value: Ensures each client's bank deposits are matched to the
  correct outstanding invoice so the firm's books close accurately and real
  collection gaps get followed up on, instead of drifting unnoticed.

## Actors

| Actor | Type | Role in This Flow |
|-------|------|--------------------|
| Bookkeeper | Person | Downloads exports, matches deposits to invoices, resolves exceptions, updates invoice status |
| Client contact | Person | Occasionally emails to clarify an ambiguous or split deposit |
| Bank export job | Automated System | Nightly job that refreshes the bank portal's downloadable deposit CSV |

## Sources and Sinks

| Direction | System or Location | What It Provides or Receives |
|-----------|---------------------|-------------------------------|
| Source | Bank portal CSV export | Weekly list of incoming deposits (date, amount, payer reference, memo) |
| Source | Accounting platform invoice export | Outstanding invoices per client (invoice ID, amount due, due date) |
| Sink | Shared reconciliation spreadsheet | Master record of which deposit matched which invoice, and reviewer notes |
| Sink | Accounting platform invoice status field | Manually flipped to "Paid" for confirmed matches |

## Data and Data Structures

| Name | Format | Direction | Key Fields / Schema Notes |
|------|--------|-----------|-----------------------------|
| `bank_deposits.csv` | File (CSV) | Input | `date`, `amount`, `payer_ref`, `memo`; column order has changed without notice when the bank updated its export tool |
| `invoices_export.xlsx` | File (Excel) | Input | `invoice_id`, `client_id`, `amount_due`, `due_date` |
| `reconciliation-tracker.xlsx` | Spreadsheet | Output | One row per deposit: `deposit_id`, `matched_invoice_id`, `status`, `reviewer`, `notes`; layout differs per client, no canonical template |
| Invoice status field | UI field (accounting platform) | Output | Free-text-adjacent status dropdown, flipped manually per confirmed match |

## Transformations

| Step | What Happens | Performed By |
|------|---------------|--------------|
| 1 | Download the weekly bank CSV from the portal | Bookkeeper |
| 2 | Export the outstanding invoice list from the accounting platform | Bookkeeper |
| 3 | Compare deposit amount and payer name against open invoices to guess a match, then record it in the tracker spreadsheet | Bookkeeper |
| 4 | Flag ambiguous deposits (partial payments, multiple candidate invoices) in a "Needs Review" tab | Bookkeeper |
| 5 | For each confirmed match, manually set the invoice status to "Paid" in the accounting platform | Bookkeeper |

## Constraints

| Constraint | Detail |
|------------|--------|
| Format | Bank CSV column order is not contractually stable; it has silently broken spreadsheet formulas before |
| Timing | Must finish by Friday close-of-business so weekend ACH deposits don't roll into the next batch and confuse the count |
| Volume | 50-200 deposits per week per client at pilot-scale firms |
| Access | Bookkeeper needs manual read access to both the bank portal and the accounting platform; neither exposes an API today |

## Scale and Complexity

| Dimension | Assessment |
|-----------|------------|
| Manual steps | 5, all performed by one person |
| Systems touched | 3 (bank portal, accounting platform, spreadsheet) |
| Overall complexity | Medium — the per-deposit logic is simple, but volume and exception handling make it slow and error-prone |

## Risks, Assumptions, and Modernization Notes

- **Risks**: Matches are eyeballed with no audit trail of who decided what
  or why; a silent bank CSV schema change breaks spreadsheet formulas without
  warning; nothing prevents the same deposit from being matched twice.
- **Assumptions**: The bank CSV export format is stable enough to script
  against for an initial migration pass; the accounting platform will
  eventually expose an API instead of requiring a manual status flip.
- **Modernization Recommendations**: Replace manual matching with
  DepositMatch's suggested-match review queue (see
  [[product-vision]]); keep a human in the loop for exceptions, but replace
  free-form spreadsheet editing with a reviewable, audited decision log.

## Notes

Each client's spreadsheet layout is slightly different because bookkeepers
customized their own copies over time — there is no single canonical
template in use today, which will complicate any bulk import during
migration.

## Cross-References

- [[data-design]] — Design-phase target-state entity model this analysis may
  inform once a future solution is chosen.
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Discover</strong></a> — Validate that an opportunity is worth pursuing before committing to a development cycle.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/00-discover/data-flow-analysis-[flow-name].md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="../../../artifact-types/design/data-design/">Data Design</a><br><a href="../../../artifact-types/frame/feasibility-study/">Feasibility Study</a><br><a href="../../../artifact-types/frame/prd/">PRD</a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Data Flow Analysis Generation Prompt&#10;&#10;Document one existing business process or data flow exactly as it operates&#10;today, before any future-state solution is chosen.&#10;&#10;## Storage Location&#10;&#10;Store at: `docs/helix/00-discover/data-flow-analysis-[flow-name].md`&#10;&#10;## Purpose&#10;&#10;Answers: **What does this flow actually do today, and what would we need to&#10;know to modernize it?** This is a concrete, technical companion to&#10;higher-level Discover artifacts — it documents a system as it exists, not a&#10;market or an opportunity.&#10;&#10;## Role Boundary&#10;&#10;Data Flow Analysis is not Data Design. Data Design documents the entity&#10;model for a system being built (Design phase, future-state). Data Flow&#10;Analysis documents an existing flow as it runs today (Discover phase,&#10;as-is), before anyone has decided what the future solution looks like. One&#10;instance covers one flow; a legacy migration effort typically produces&#10;several, one per row of a discovery inventory.&#10;&#10;## Key Principles&#10;&#10;- **One flow per document.** Do not try to cover an entire legacy system in&#10;  a single pass — break it into individual flows first.&#10;- **Name sources and sinks concretely.** The actual system, table, file, or&#10;  API, not a vague description like &quot;the database.&quot;&#10;- **Type every actor.** Each one is either a person doing a manual step or&#10;  an automated system; say which, and what they actually do.&#10;- **Capture data on both sides.** What comes in and what goes out, in&#10;  enough detail that another engineer could find it without asking the&#10;  person who wrote this document.&#10;- **Constraints matter as much as the happy path.** Format, timing, volume,&#10;  and access requirements shape any future redesign as much as the&#10;  transformation logic does.&#10;- **Don&#x27;t skip Risks, Assumptions, and Modernization Notes.** This section&#10;  is the payoff for doing this analysis instead of just reading the code or&#10;  spreadsheet directly.&#10;- **Leave the Notes section genuinely open-ended.** An engineer who fills it&#10;  with several unprompted observations engaged with the problem; an empty&#10;  Notes section on a nontrivial flow is a sign the analysis was rushed.&#10;&#10;## Quality Checklist&#10;&#10;- [ ] Every source and sink is named concretely&#10;- [ ] Every actor is identified as a Person or an Automated System&#10;- [ ] Business value is stated explicitly in Flow Summary&#10;- [ ] Constraints on inputs and outputs are captured&#10;- [ ] Overall complexity or scale is estimated, even roughly&#10;- [ ] Risks, assumptions, and modernization recommendations are present, not&#10;      left blank</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: data-flow-analysis&#10;---&#10;&#10;# Data Flow Analysis&#10;&#10;As-is documentation of one existing business process or data flow: what it&#10;does today, who and what is involved, and what would need to change to&#10;modernize it. Captured during Discover, before any future-state solution is&#10;chosen — the target-state entity model for a system being built belongs in&#10;[[data-design]] (Design phase). One instance covers one flow; a migration&#10;effort typically produces several.&#10;&#10;## Flow Summary&#10;&#10;- Process name: [Name of the business process or flow]&#10;- Frequency: [How often this runs — daily, weekly, on-demand, event-driven]&#10;- Current state: [Manual / Automated / Hybrid]&#10;- Business value: [Why this process exists — the outcome it produces or protects]&#10;&#10;## Actors&#10;&#10;| Actor | Type | Role in This Flow |&#10;|-------|------|--------------------|&#10;| [Name] | Person / Automated System | [What they do in this flow] |&#10;&#10;## Sources and Sinks&#10;&#10;| Direction | System or Location | What It Provides or Receives |&#10;|-----------|---------------------|-------------------------------|&#10;| Source | [System, portal, or export] | [Data provided] |&#10;| Sink | [System, database, or report] | [Data received] |&#10;&#10;## Data and Data Structures&#10;&#10;| Name | Format | Direction | Key Fields / Schema Notes |&#10;|------|--------|-----------|-----------------------------|&#10;| [Table, file, API, or spreadsheet name] | Table / File / API / Spreadsheet / Other | Input / Output | [Fields, types, or notable structure] |&#10;&#10;## Transformations&#10;&#10;| Step | What Happens | Performed By |&#10;|------|---------------|--------------|&#10;| 1 | [Processing or business logic applied to the data] | [Actor] |&#10;&#10;## Constraints&#10;&#10;| Constraint | Detail |&#10;|------------|--------|&#10;| Format | [Expected shape of inputs or outputs, and how brittle it is] |&#10;| Timing | [Deadlines, ordering, or freshness requirements] |&#10;| Volume | [Typical and peak data volume] |&#10;| Access | [What credentials, permissions, or network access this flow requires] |&#10;&#10;## Scale and Complexity&#10;&#10;| Dimension | Assessment |&#10;|-----------|------------|&#10;| Manual steps | [Count or description] |&#10;| Systems touched | [Count or list] |&#10;| Overall complexity | Low / Medium / High |&#10;&#10;## Risks, Assumptions, and Modernization Notes&#10;&#10;- **Risks**: [What&#x27;s fragile, undocumented, error-prone, or likely to break]&#10;- **Assumptions**: [What we&#x27;re taking on faith about how this flow behaves]&#10;- **Modernization Recommendations**: [What we&#x27;d do differently, and why]&#10;&#10;## Notes&#10;&#10;[Freeform — anything real about this flow that doesn&#x27;t fit the sections above]&#10;&#10;## Cross-References&#10;&#10;- [[data-design]] — Design-phase target-state entity model this analysis may&#10;  inform once a future solution is chosen.</code></pre></details></td></tr>
</tbody>
</table>
