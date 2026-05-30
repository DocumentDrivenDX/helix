---
title: "Feature Registry"
linkTitle: "Feature Registry"
slug: feature-registry
activity: "Frame"
artifactRole: "supporting"
weight: 17
generated: true
---

## Purpose

Compact source of truth for feature IDs, names, status, priority, owner,
dependencies, and artifact trace links.

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: example.feature-registry.depositmatch
  depends_on:
    - example.prd.depositmatch
    - example.opportunity-canvas.depositmatch
  review:
    self_hash: 227c7c30edf5318187982fad9b7c868365600d4ffb8f92da25b1f932769dddb8
    deps:
      example.opportunity-canvas.depositmatch: 75303097bfeeed0272bd68f90ef887f9a5e646a1272f9a57ccd0d899ae17497a
      example.prd.depositmatch: c9c24e1694af4548a6deaad8d92059e365da110148bd9adc44d8640dff9770a4
    reviewed_at: "2026-05-15T04:11:24Z"
---

# Feature Registry

**Status**: Active
**Last Updated**: 2026-05-12

## Active Features

| ID | Name | Description | Status | Priority | Owner | Source | Updated |
|----|------|-------------|--------|----------|-------|--------|---------|
| FEAT-001 | CSV Import and Column Mapping | Import bank/invoice CSVs and map columns per client. | Specified | P0 | Product / Engineering | PRD, Opportunity Canvas | 2026-05-12 |
| FEAT-002 | Evidence-Backed Match Review | Suggest deposit-to-invoice matches with visible evidence before reviewer approval. | Draft | P0 | Product / Engineering | PRD, Product Vision | 2026-05-12 |
| FEAT-003 | Client Exception Queue | Keep unresolved deposits grouped by client with owner and next action. | Draft | P0 | Product | PRD, Opportunity Canvas | 2026-05-12 |
| FEAT-004 | Review Log Export | Export accepted matches, exceptions, reviewer actions, and evidence for client review. | Draft | P1 | Product / Compliance | Compliance Requirements, PRD | 2026-05-12 |

## Status Definitions

- **Draft**: Requirements being gathered
- **Specified**: Feature spec complete (Frame done)
- **Designed**: Technical design complete (Design done)
- **In Test**: Tests being written
- **In Build**: Implementation in progress
- **Built**: Implementation complete
- **Deployed**: Released to production
- **Deprecated**: Scheduled for removal
- **Cancelled**: Will not be pursued

## Dependencies

| Feature | Depends On | Type | Notes |
|---------|------------|------|-------|
| FEAT-002 | FEAT-001 | Required | Match suggestions need normalized imported records. |
| FEAT-003 | FEAT-001 | Required | Exceptions originate from imported unmatched or ambiguous deposits. |
| FEAT-004 | FEAT-002, FEAT-003 | Required | Export needs accepted matches and exception history. |

## Trace Links

| Feature | Spec | Stories | Designs | Tests | Release |
|---------|------|---------|---------|-------|---------|
| FEAT-001 | `feature-specification/example.md` | `user-stories/example.md` | Pending | Pending | Pilot |
| FEAT-002 | Pending | Pending | Pending | Pending | Pilot |
| FEAT-003 | Pending | Pending | Pending | Pending | Pilot |
| FEAT-004 | Pending | Pending | Pending | Pending | Pilot |

## Feature Categories

### Pilot Foundation

- FEAT-001: CSV Import and Column Mapping

### Review Workflow

- FEAT-002: Evidence-Backed Match Review
- FEAT-003: Client Exception Queue
- FEAT-004: Review Log Export

## ID Rules

1. Sequential numbering: FEAT-XXX (zero-padded 3 digits)
2. Never reuse IDs, even for cancelled features
3. Do not encode category or priority into the ID
4. Keep full behavior in Feature Specifications, not in this registry

## Deprecated/Cancelled

| ID | Name | Status | Reason | Date |
|----|------|--------|--------|------|
| None | None | None | None | None |
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Frame</strong></a> — Define what the system should do, for whom, and how success will be measured.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/01-frame/feature-registry.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Referenced by</th><td>Project Dashboard<br><a href="../../../artifact-types/deploy/release-notes/">Release Notes</a><br>Progress Reports</td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Feature Registry Generation Prompt&#10;Maintain the feature registry as the source of truth for IDs, status, dependencies, ownership, and traceability.&#10;&#10;## Reference Anchors&#10;&#10;Use these local resource summaries as grounding:&#10;&#10;- `docs/resources/ibm-requirements-management.md` grounds requirements&#10;  traceability, prioritization, validation, and change management.&#10;- `docs/resources/atlassian-product-backlog.md` grounds visible prioritized&#10;  work, dependency awareness, and refinement.&#10;&#10;## Focus&#10;- Assign new FEAT-XXX IDs sequentially.&#10;- Keep status changes and dependencies explicit.&#10;- Preserve traceability to stories, designs, contracts, tests, and code.&#10;- Keep descriptions short; detail belongs in feature specs, stories, designs, and tests.&#10;&#10;## Role Boundary&#10;&#10;The Feature Registry is not the PRD, backlog, or tracker. It assigns durable&#10;feature identity and preserves feature-level traceability. The PRD defines&#10;requirements; Feature Specifications define behavior; runtime work items track execution.&#10;&#10;## Completion Criteria&#10;- Entries are brief and complete.&#10;- IDs are unique and never reused.&#10;- The registry stays easy to scan.&#10;- Every active feature links to its governing artifact or clearly states the missing link.&#10;&#10;## Promotion from Parking Lot&#10;&#10;Per [ADR-010](../../../../../docs/helix/02-design/adr/ADR-010-feature-registry-parking-lot-handoff.md),&#10;`feature-registry` and `parking-lot` stay separate and the handoff is an&#10;explicit recorded transition. When a parking-lot entry&#x27;s revisit criteria are&#10;met, promote it to the registry with the following procedure.&#10;&#10;### Promotion Criteria&#10;&#10;A parking-lot entry is eligible for promotion when all of these hold:&#10;&#10;- **Revisit trigger fired**: the objective condition recorded on the entry has&#10;  occurred (date reached, dependency landed, external signal observed).&#10;- **Scope decided**: the item has been re-scoped into something a feature spec&#10;  can be written against — not a vague idea kept warm.&#10;- **Owner assigned**: a named owner accepts responsibility for the feature&#10;  through at least the `specified` status.&#10;- **Blocking ADRs resolved**: any ADR that the entry was waiting on has landed&#10;  (accepted or rejected); items still pending ADRs stay parked.&#10;- **Dependencies available**: prerequisite features listed on the entry are at&#10;  a status that unblocks this one (typically `built` or later).&#10;&#10;If any criterion fails, leave the entry parked and update the rationale or&#10;revisit trigger to reflect what is still missing.&#10;&#10;### Promotion Procedure&#10;&#10;1. **Assign the next sequential FEAT-XXX**: never reuse an ID, including IDs&#10;   from cancelled or deprecated features. Add the new row to `Active Features`&#10;   with initial status `Draft` (or `Specified` if the spec is ready to land in&#10;   the same change).&#10;2. **Record the back-link to the parking-lot source**: in the new feature row&#x27;s&#10;   `Source` column, cite the parking-lot entry title (e.g.&#10;   `parking-lot:&lt;entry-title&gt;`). This makes the parked-to-active transition&#10;   auditable.&#10;3. **Update the parking-lot entry**: mark the entry as promoted, record the&#10;   assigned `FEAT-XXX`, and the promotion date. Do not delete the parking-lot&#10;   entry — the historical record is part of the back-link.&#10;4. **Seed traceability**: populate the new feature&#x27;s `Trace Links` row with the&#10;   feature spec, stories, designs, tests, and release placeholders. Empty cells&#10;   are fine; missing cells are not.&#10;5. **Carry over dependencies**: copy any `Dependencies` from the parking-lot&#10;   entry into the registry&#x27;s `Dependencies` table, expressed as FEAT-to-FEAT&#10;   edges where the prerequisites have FEAT-XXX IDs.&#10;&#10;The promotion is complete when the new `FEAT-XXX` row exists with a back-link,&#10;the parking-lot entry records the promotion, and traceability rows are seeded.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: feature-registry&#10;---&#10;&#10;# Feature Registry&#10;&#10;**Status**: [Active | Archived]&#10;**Last Updated**: [Date]&#10;&#10;## Active Features&#10;&#10;| ID | Name | Description | Status | Priority | Owner | Source | Updated |&#10;|----|------|-------------|--------|----------|-------|--------|---------|&#10;| FEAT-001 | [Name] | [Brief description] | [Status] | P0 | [Owner] | [PRD/spec/story] | [Date] |&#10;&#10;## Status Definitions&#10;&#10;- **Draft**: Requirements being gathered&#10;- **Specified**: Feature spec complete (Frame done)&#10;- **Designed**: Technical design complete (Design done)&#10;- **In Test**: Tests being written&#10;- **In Build**: Implementation in progress&#10;- **Built**: Implementation complete&#10;- **Deployed**: Released to production&#10;- **Deprecated**: Scheduled for removal&#10;- **Cancelled**: Will not be pursued&#10;&#10;## Dependencies&#10;&#10;| Feature | Depends On | Type | Notes |&#10;|---------|------------|------|-------|&#10;| FEAT-002 | FEAT-001 | Required | [Why] |&#10;&#10;## Trace Links&#10;&#10;| Feature | Spec | Stories | Designs | Tests | Release |&#10;|---------|------|---------|---------|-------|---------|&#10;| FEAT-001 | [Feature spec] | [Stories] | [Designs] | [Tests] | [Release] |&#10;&#10;## Feature Categories&#10;&#10;### [Category Name]&#10;- FEAT-XXX: [Feature Name]&#10;&#10;## ID Rules&#10;&#10;1. Sequential numbering: FEAT-XXX (zero-padded 3 digits)&#10;2. Never reuse IDs, even for cancelled features&#10;3. Do not encode category or priority into the ID&#10;4. Keep full behavior in Feature Specifications, not in this registry&#10;&#10;## Deprecated/Cancelled&#10;&#10;| ID | Name | Status | Reason | Date |&#10;|----|------|--------|--------|------|&#10;| FEAT-XXX | [Name] | [Cancelled/Deprecated] | [Why] | [Date] |</code></pre></details></td></tr>
</tbody>
</table>
