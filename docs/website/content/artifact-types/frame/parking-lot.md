---
title: "Parking Lot"
linkTitle: "Parking Lot"
slug: parking-lot
activity: "Frame"
artifactRole: "supporting"
weight: 18
generated: true
---

## Purpose

Registry for deferred or future work that should remain visible but outside
current scope until a specific revisit trigger is met.

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: example.parking-lot.depositmatch
  parking_lot: true
  depends_on:
    - example.feature-registry.depositmatch
---

# Parking Lot (Deferred / Future Work)

## Purpose

Track DepositMatch work that may matter later without letting it distort the
CSV-first pilot scope.

## Policy

- Rejected items do not belong here; close or cancel them instead.
- Active pilot work does not belong here; track it in the Feature Registry and
  DDx.
- Deferred items must include rationale, owner, and revisit trigger.
- Future items must include source and expected value.
- Any parked artifact must set `ddx.parking_lot: true`.

## Deferred / Future Items

### Bank Feed Integration

- **Type**: Deferred
- **Artifact Type**: Feature Spec
- **Source**: Feasibility Study alternative analysis
- **Rationale**: Higher integration and compliance surface would slow the
  CSV-first pilot.
- **Impact if Omitted**: Pilot users continue exporting CSVs manually.
- **Dependencies**: Pilot proves time savings and willingness to pay.
- **Revisit Trigger**: At least 3 of 5 pilot firms convert at target pricing
  and request bank-feed support.
- **Target Activity/Milestone**: Post-pilot
- **Owner**: Product Lead
- **Last Reviewed**: 2026-05-12

### Accounting Ledger Writeback

- **Type**: Future
- **Artifact Type**: Solution Design
- **Source**: Product Vision not-in-scope boundary
- **Rationale**: Writeback changes the trust, liability, and integration model;
  the pilot only needs review and export.
- **Impact if Omitted**: Reviewers must manually apply approved outcomes in
  their accounting system.
- **Dependencies**: Security architecture, compliance review, and integration
  partner selection.
- **Revisit Trigger**: Pilot customers complete review-log export workflow but
  cite manual ledger update as a blocker to renewal.
- **Target Activity/Milestone**: Post-pilot discovery
- **Owner**: Product / Engineering
- **Last Reviewed**: 2026-05-12

### Automatic Approval

- **Type**: Deferred
- **Artifact Type**: ADR
- **Source**: Opportunity Canvas scope boundary
- **Rationale**: The pilot differentiates on reviewer trust, not invisible
  automation.
- **Impact if Omitted**: Reviewers must approve suggested matches explicitly.
- **Dependencies**: Match accuracy evidence, compliance review, customer risk
  tolerance, and audit-log design.
- **Revisit Trigger**: Accepted suggestion accuracy exceeds 98% for two months
  and pilot firms request supervised automation.
- **Target Activity/Milestone**: Future trust-model review
- **Owner**: Product / Compliance
- **Last Reviewed**: 2026-05-12

## Parked Artifacts (Links)

### FEAT Future Bank Feed Integration

- **Artifact File**: `docs/helix/01-frame/features/FEAT-005-bank-feed-integration.md`
- **Status**: Parking Lot (Deferred)

### ADR Future Automatic Approval

- **Artifact File**: `docs/helix/02-design/adr/ADR-002-automatic-approval.md`
- **Status**: Parking Lot (Deferred)
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="/reference/glossary/activities/"><strong>Frame</strong></a> — Define what the system should do, for whom, and how success will be measured.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/parking-lot.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Parking Lot Prompt
Capture deferred work that should not stay in the active path.

## Reference Anchors

Use this local resource summary as grounding:

- `docs/resources/atlassian-product-backlog.md` grounds visible deferred work,
  reprioritization, and closing items that will not be pursued.

## Focus
- Record the item, why it is deferred, and where it belongs next.
- Keep the entry short.
- Link to any relevant artifact or issue.
- Include a concrete revisit trigger; &quot;later&quot; is not a trigger.

## Role Boundary

The Parking Lot is not the backlog or tracker. It holds deferred or future work
that should remain findable without contaminating current scope. Active work
belongs in the Feature Registry and runtime work items. Rejected work should be closed
or cancelled, not parked forever.

## Completion Criteria
- Deferred items are easy to find later.
- Nothing active is buried here.
- Every item has source, rationale, owner, and revisit trigger.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---
ddx:
  id: parking-lot
---

# Parking Lot (Deferred / Future Work)

## Policy
- Rejected items do not belong here; close or cancel them instead.
- Active work does not belong here; track it in the Feature Registry and DDx.
- Deferred items must include rationale and revisit trigger.
- Revisit triggers must be objective enough for another agent to evaluate.
- Any parked artifact must set `ddx.parking_lot: true` in its frontmatter.

## Deferred / Future Items

### [Item Title]
- **Type**: Deferred | Future
- **Artifact Type**: Feature Spec | User Story | ADR | Solution Design | Implementation Plan | Other
- **Source**: FEAT-XXX / US-XXX / ADR-XXX / external
- **Rationale**: [Why deferred / why future]
- **Impact if Omitted**: [Risk/impact]
- **Dependencies**: [Blocked by / prerequisites]
- **Revisit Trigger**: [What must happen before reconsidering]
- **Target Activity/Milestone**: [Activity or release]
- **Owner**: [Person/team responsible for review]
- **Last Reviewed**: [Date]

## Parked Artifacts (Links)

### [Artifact Title]
- **Artifact File**: [path to parked artifact]
- **Status**: Parking Lot (Deferred | Future)</code></pre></details></td></tr>
</tbody>
</table>
