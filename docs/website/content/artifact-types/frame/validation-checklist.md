---
title: "Validation Checklist"
linkTitle: "Validation Checklist"
slug: validation-checklist
activity: "Frame"
artifactRole: "supporting"
weight: 25
generated: true
---

## Purpose

Frame exit gate that verifies completeness, consistency, traceability,
evidence, stakeholder review, and readiness to enter Design.

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: example.validation-checklist.depositmatch
  authoring:
    home: repo
  depends_on:
    - example.prd.depositmatch
    - example.pr-faq.depositmatch
    - example.feature-registry.depositmatch
    - example.research-plan.depositmatch
    - example.risk-register.depositmatch
    - example.security-requirements.depositmatch
    - example.threat-model.depositmatch
    - example.stakeholder-map.depositmatch
---

# Frame Activity Validation Checklist

**Status**: [ ] Not Started | [ ] In Progress | [x] Complete
**Validated By**: Product Lead
**Date**: 2026-05-12
**Result**: [ ] Pass | [x] Conditional Pass | [ ] Fail

## Go / No-Go Gates

| Gate | Status | Evidence | Blocking Gap |
|------|--------|----------|--------------|
| Problem, goals, and success metrics are clear enough to judge outcomes | Pass | Product Vision, Opportunity Canvas, PR-FAQ | None |
| P0 scope is identified, prioritized, and separated from non-goals | Pass | PRD, Feature Registry, Parking Lot | None |
| Features and stories are traceable through IDs and links | Conditional | Feature Registry links FEAT-001; later features are pending | Complete trace links for FEAT-002 through FEAT-004 before design approval |
| Acceptance criteria are testable | Conditional | PRD and Security Requirements | Add story-level acceptance criteria for FEAT-002 and FEAT-003 before build |
| Major risks, dependencies, and external constraints are explicit | Pass | Risk Register, Compliance Requirements, Feasibility Study | None |
| Frame artifacts do not contradict each other | Pass | Parking Lot aligns with PRD non-goals and PR-FAQ v1 scope | None |
| Required stakeholders have reviewed the plan | Conditional | Stakeholder Map identifies required reviewers | Compliance/Legal signoff required before live-data design approval |

## Result

- [ ] **PASS**: Ready for Design activity
- [x] **CONDITIONAL PASS**: Proceed with noted conditions
- [ ] **FAIL**: Address blocking issues first

**Conditions/Notes**:
DepositMatch is ready to begin Design for the CSV-first pilot because the
customer problem, P0 scope, risks, security requirements, and deferred work are
clear. Design must not approve live-data onboarding until compliance/legal
review is complete, and build must not start for FEAT-002/FEAT-003 until their
story-level acceptance criteria are complete.

## Required Follow-Up

| Item | Owner | Due | Required Before |
|------|-------|-----|-----------------|
| Complete compliance/legal applicability review for live financial data | Compliance Officer / Legal Counsel | Before live-data design approval | Design approval |
| Complete trace links for FEAT-002, FEAT-003, and FEAT-004 | Product Lead | Before design approval | Design approval |
| Add story-level acceptance criteria for match review and exception queue | Product Lead | Before build planning | Build start |
| Confirm research plan recruiting and sample CSV intake path | Product Lead | Before design assumptions freeze | Design approval |
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Frame</strong></a> — Define what the system should do, for whom, and how success will be measured.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/01-frame/validation-checklist.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Validation Checklist Generation Prompt&#10;Create the checklist that decides whether Frame is ready to move forward.&#10;&#10;## Reference Anchors&#10;&#10;Use this local resource summary as grounding:&#10;&#10;- `docs/resources/ibm-requirements-management.md` grounds traceability,&#10;  validation, verification, and change management expectations.&#10;&#10;## Focus&#10;- Check only the gates that matter: completeness, consistency, traceability, and stakeholder approval.&#10;- Keep the pass/fail criteria concrete.&#10;- Avoid duplicating the content already covered by source artifacts.&#10;- Cite evidence or the missing artifact for every conditional or failed gate.&#10;&#10;## Role Boundary&#10;&#10;Validation Checklist is not a replacement for PRD review, risk review, or&#10;stakeholder review. It is the final Frame activity gate: it records whether the&#10;required artifacts are coherent enough for Design and what conditions remain.&#10;&#10;## Completion Criteria&#10;- The checklist is short and actionable.&#10;- Blocking gaps are easy to spot.&#10;- Cross-references are verified.&#10;- Result is Pass, Conditional Pass, or Fail with named conditions.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: validation-checklist&#10;  authoring:&#10;    home: repo&#10;---&#10;&#10;# Frame Activity Validation Checklist&#10;&#10;**Status**: [ ] Not Started | [ ] In Progress | [ ] Complete&#10;**Validated By**: [Name]&#10;**Date**: [Date]&#10;**Result**: [ ] Pass | [ ] Conditional Pass | [ ] Fail&#10;&#10;## Go / No-Go Gates&#10;| Gate | Status | Evidence | Blocking Gap |&#10;|------|--------|----------|--------------|&#10;| Problem, goals, and success metrics are clear enough to judge outcomes | Pass / Conditional / Fail | [Artifact/link] | [Gap or None] |&#10;| P0 scope is identified, prioritized, and separated from non-goals | Pass / Conditional / Fail | [Artifact/link] | [Gap or None] |&#10;| Features and stories are traceable through IDs and links | Pass / Conditional / Fail | [Artifact/link] | [Gap or None] |&#10;| Acceptance criteria are testable | Pass / Conditional / Fail | [Artifact/link] | [Gap or None] |&#10;| Major risks, dependencies, and external constraints are explicit | Pass / Conditional / Fail | [Artifact/link] | [Gap or None] |&#10;| Frame artifacts do not contradict each other | Pass / Conditional / Fail | [Artifact/link] | [Gap or None] |&#10;| Required stakeholders have reviewed the plan | Pass / Conditional / Fail | [Artifact/link] | [Gap or None] |&#10;&#10;## Result&#10;- [ ] **PASS**: Ready for Design activity&#10;- [ ] **CONDITIONAL PASS**: Proceed with noted conditions&#10;- [ ] **FAIL**: Address blocking issues first&#10;&#10;**Conditions/Notes**:&#10;[Assessment and any conditions]&#10;&#10;## Required Follow-Up&#10;&#10;| Item | Owner | Due | Required Before |&#10;|------|-------|-----|-----------------|&#10;| [Condition] | [Owner] | [Date] | [Design start / design approval / build start] |</code></pre></details></td></tr>
</tbody>
</table>
