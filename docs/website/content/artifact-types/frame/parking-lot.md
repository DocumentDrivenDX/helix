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
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Frame</strong></a> — Define what the system should do, for whom, and how success will be measured.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/parking-lot.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Parking Lot Prompt&#10;Capture deferred work that should not stay in the active path.&#10;&#10;## Reference Anchors&#10;&#10;Use this local resource summary as grounding:&#10;&#10;- `docs/resources/atlassian-product-backlog.md` grounds visible deferred work,&#10;  reprioritization, and closing items that will not be pursued.&#10;&#10;## Focus&#10;- Record the item, why it is deferred, and where it belongs next.&#10;- Keep the entry short.&#10;- Link to any relevant artifact or issue.&#10;- Include a concrete revisit trigger; &quot;later&quot; is not a trigger.&#10;&#10;## Role Boundary&#10;&#10;The Parking Lot is not the backlog or tracker. It holds deferred or future work&#10;that should remain findable without contaminating current scope. Active work&#10;belongs in the Feature Registry and runtime work items. Rejected work should be closed&#10;or cancelled, not parked forever.&#10;&#10;## Completion Criteria&#10;- Deferred items are easy to find later.&#10;- Nothing active is buried here.&#10;- Every item has source, rationale, owner, and revisit trigger.&#10;&#10;## Promotion to Feature Registry&#10;&#10;When a parked entry&#x27;s revisit trigger fires and the item is ready to enter the&#10;active pipeline, follow the promotion procedure documented in the&#10;[Feature Registry prompt](../feature-registry/prompt.md#promotion-from-parking-lot)&#10;(per [ADR-010](../../../../../docs/helix/02-design/adr/ADR-010-feature-registry-parking-lot-handoff.md)).</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: parking-lot&#10;---&#10;&#10;# Parking Lot (Deferred / Future Work)&#10;&#10;## Purpose&#10;&#10;[Why this parking lot exists and what it covers — scope of deferred / future&#10;work tracked here without distorting current commitments.]&#10;&#10;## Policy&#10;- Rejected items do not belong here; close or cancel them instead.&#10;- Active work does not belong here; track it in the Feature Registry and DDx.&#10;- Deferred items must include rationale and revisit trigger.&#10;- Revisit triggers must be objective enough for another agent to evaluate.&#10;- Any parked artifact must set `ddx.parking_lot: true` in its frontmatter.&#10;&#10;## Deferred / Future Items&#10;&#10;### [Item Title]&#10;- **Type**: Deferred | Future&#10;- **Artifact Type**: Feature Spec | User Story | ADR | Solution Design | Implementation Plan | Other&#10;- **Source**: FEAT-XXX / US-XXX / ADR-XXX / external&#10;- **Rationale**: [Why deferred / why future]&#10;- **Impact if Omitted**: [Risk/impact]&#10;- **Dependencies**: [Blocked by / prerequisites]&#10;- **Revisit Trigger**: [What must happen before reconsidering]&#10;- **Target Activity/Milestone**: [Activity or release]&#10;- **Owner**: [Person/team responsible for review]&#10;- **Last Reviewed**: [Date]&#10;&#10;## Parked Artifacts (Links)&#10;&#10;### [Artifact Title]&#10;- **Artifact File**: [path to parked artifact]&#10;- **Status**: Parking Lot (Deferred | Future)</code></pre></details></td></tr>
</tbody>
</table>
