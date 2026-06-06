---
title: "Risk Register"
linkTitle: "Risk Register"
slug: risk-register
activity: "Frame"
artifactRole: "supporting"
weight: 21
generated: true
---

## Purpose

Action register for uncertain events that could change project outcome,
scored with probability, impact, owner, trigger, response, and review cadence.

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: example.risk-register.depositmatch
  depends_on:
    - example.feasibility-study.depositmatch
    - example.research-plan.depositmatch
    - example.compliance-requirements.depositmatch
  review:
    self_hash: 4cfb9a77765bfa4a63e8ad9d98a656bb5c9b9bfb5c5569389cb8cf73e8c1c3ba
    deps:
      example.compliance-requirements.depositmatch: ec7fb87a927f7e53a9c323e9af8ee73d667e4520ab596c130077d332d2783c9f
      example.feasibility-study.depositmatch: 356da096953895f8c152a1ac8b880fbc03a3617c1c80516e6f0d3b4033a62c72
      example.research-plan.depositmatch: e1bd75c90a2407b8d84770a3d822fa64fc9b90fe1d36cfef5f5d615bf6ba6e06
    reviewed_at: "2026-05-15T04:11:24Z"
---

# Risk Register

**Status**: Review
**Last Updated**: 2026-05-12
**Risk Owner**: Product Lead

## Summary

- **Critical Risks**: 0
- **High Risks**: 4
- **Medium Risks**: 2
- **Low Risks**: 0
- **Overall Risk Level**: High

## Risk Scoring

**Probability**: Very High (5) >80% | High (4) 60-80% | Medium (3) 40-60% | Low (2) 20-40% | Very Low (1) <20%
**Impact**: Critical (5) >30% overrun | High (4) 20-30% | Medium (3) 10-20% | Low (2) 5-10% | Negligible (1) <5%
**Risk Score** = Probability x Impact: Critical (20-25), High (12-19), Medium (6-11), Low (1-5)
**Response**: Avoid | Mitigate | Transfer | Accept | Escalate

## Active Risks

### RISK-001: CSV Variability Blocks Reliable Import

**Category**: Technical
**Status**: Mitigating
**Owner**: Engineering Lead

**Description**: Pilot firms may provide CSV exports with inconsistent fields,
formats, or missing identifiers, slowing onboarding and weakening match
quality.

**Assessment**:

- **Probability**: 4 - The Feasibility Study identifies CSV variability as the
  highest technical risk.
- **Impact**: 4 - Poor import reliability would block FEAT-001 and downstream
  match review.
- **Risk Score**: 16
- **Response**: Mitigate

**Triggers**: More than 2 unsupported required fields in sample exports from 2
or more pilot firms.

**Mitigation**:

- **Preventive**: Collect sample CSVs during Research Plan execution and define
  required/optional fields before PRD approval.
- **Contingency**: Limit pilot eligibility to firms with compatible exports.
- **Fallback**: Defer pilot until import mapping scope is redesigned.

**Review**: Weekly | **Next Review**: 2026-05-19

---

### RISK-002: Reviewers Do Not Trust Suggested Matches

**Category**: Product
**Status**: Open
**Owner**: Product Lead

**Description**: Reviewers may reject suggested matches if the evidence is not
visible or credible enough, eliminating the core time-saving benefit.

**Assessment**:

- **Probability**: 3 - Evidence-backed review is central but unvalidated.
- **Impact**: 5 - The core thesis fails if reviewers do not trust suggestions.
- **Risk Score**: 15
- **Response**: Mitigate

**Triggers**: Accepted suggestion accuracy below 95% or reviewers cannot explain
why they accepted a match in audit samples.

**Mitigation**:

- **Preventive**: Require amount, date, payer, invoice, and confidence evidence
  in FEAT-002.
- **Contingency**: Narrow suggestions to high-confidence matches and route more
  deposits to exception review.
- **Fallback**: Pivot to exception organization without automated suggestions.

**Review**: Weekly during pilot | **Next Review**: 2026-05-19

---

### RISK-003: Compliance Review Expands Required Controls

**Category**: Compliance
**Status**: Open
**Owner**: Compliance Officer

**Description**: FTC Safeguards or state privacy obligations may require more
controls, vendor review, or data-handling procedures than the pilot plan
assumes.

**Assessment**:

- **Probability**: 3 - Applicability is unresolved in Compliance Requirements.
- **Impact**: 4 - Required controls could delay live-data onboarding.
- **Risk Score**: 12
- **Response**: Mitigate / Escalate

**Triggers**: Counsel determines live financial data requires controls not in
current design scope.

**Mitigation**:

- **Preventive**: Complete counsel review before live-data pilot and use
  anonymized/synthetic samples during research.
- **Contingency**: Delay live-data onboarding until required controls are in
  place.
- **Fallback**: Restrict pilot to synthetic or customer-redacted data.

**Review**: Weekly until counsel review complete | **Next Review**: 2026-05-19

---

### RISK-004: Firms Will Not Pay for CSV-First Scope

**Category**: Business
**Status**: Open
**Owner**: Product Lead

**Description**: Pilot firms may like the workflow but refuse to pay until bank
feeds or ledger writeback exist.

**Assessment**:

- **Probability**: 3 - Pricing and obtainable market are low-confidence
  assumptions.
- **Impact**: 4 - The Business Case weakens if the narrow pilot cannot convert.
- **Risk Score**: 12
- **Response**: Mitigate

**Triggers**: Fewer than 3 of 5 pilot firms agree $149/month is reasonable if
success metrics are met.

**Mitigation**:

- **Preventive**: Include willingness-to-pay questions and pilot commitment in
  the Research Plan.
- **Contingency**: Reprice or narrow ideal customer profile before build.
- **Fallback**: Stop before build commitment if pricing signal remains weak.

**Review**: End of research window | **Next Review**: 2026-05-26

---

### RISK-005: Support Burden Exceeds Pilot Capacity

**Category**: Operational
**Status**: Monitoring
**Owner**: Operations Lead

**Description**: CSV mapping and data questions may require more high-touch
support than the pilot team can provide.

**Assessment**:

- **Probability**: 3 - CSV onboarding is likely to require support.
- **Impact**: 3 - Support load could slow pilot but is unlikely to kill it
  alone.
- **Risk Score**: 9
- **Response**: Mitigate

**Triggers**: More than 2 support interactions per firm during import setup.

**Mitigation**:

- **Preventive**: Add import validation messages and sample mapping templates.
- **Contingency**: Cap pilot at 5 firms until onboarding effort is measured.
- **Fallback**: Add onboarding-service cost to Business Case.

**Review**: Biweekly | **Next Review**: 2026-05-26

---

### RISK-006: Pilot Sample Is Too Narrow

**Category**: Market
**Status**: Monitoring
**Owner**: Product Lead

**Description**: Research from five firms may not represent the broader market,
leading to overconfident PRD scope or Business Case assumptions.

**Assessment**:

- **Probability**: 4 - The sample is intentionally small.
- **Impact**: 2 - The pilot can proceed if conclusions are limited to pilot
  readiness.
- **Risk Score**: 8
- **Response**: Accept / Monitor

**Triggers**: Research findings are cited as scale-market proof instead of
pilot-scope evidence.

**Mitigation**:

- **Preventive**: Label research conclusions as pilot evidence only.
- **Contingency**: Add follow-up market research before general availability.
- **Fallback**: Keep Business Case market sizing at low confidence.

**Review**: At research synthesis | **Next Review**: 2026-05-26

## Closed Risks

| ID | Risk | Resolution | Date | Lessons Learned |
|----|------|------------|------|-----------------|
| None | None | None | None | None |

## Escalation Criteria

Escalate when a risk score reaches Critical (20+), when a high-risk mitigation
misses its trigger threshold, or when compliance/legal review blocks live-data
pilot onboarding.
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Frame</strong></a> — Define what the system should do, for whom, and how success will be measured.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/01-frame/risk-register.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Risk Register Generation Prompt&#10;Create a concise register of the project risks that matter.&#10;&#10;## Reference Anchors&#10;&#10;Use this local resource summary as grounding:&#10;&#10;- `docs/resources/pmi-risk-analysis-management.md` grounds&#10;  probability-impact scoring, triggers, ownership, and response planning.&#10;&#10;## Focus&#10;- Score risks clearly and consistently.&#10;- Tie each risk to an owner and a mitigation.&#10;- Include triggers and review cadence only where they change action.&#10;- Distinguish risks from issues. Risks are uncertain; issues have already happened.&#10;&#10;## Role Boundary&#10;&#10;Risk Register is not the issue tracker, PRD, or test plan. It tracks uncertain&#10;events that could affect project outcomes and names how the team will monitor,&#10;mitigate, accept, transfer, avoid, or escalate them.&#10;&#10;## Completion Criteria&#10;- Major risks are covered.&#10;- Ownership and mitigation are explicit.&#10;- The register is easy to scan.&#10;- High and critical risks have concrete triggers and contingency responses.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: risk-register&#10;---&#10;&#10;# Risk Register&#10;&#10;**Status**: [Draft | Review | Approved]&#10;**Last Updated**: [Date]&#10;**Risk Owner**: [Name]&#10;&#10;## Summary&#10;&#10;- **Critical Risks**: [Number]&#10;- **High Risks**: [Number]&#10;- **Medium Risks**: [Number]&#10;- **Low Risks**: [Number]&#10;- **Overall Risk Level**: [Low | Medium | High | Critical]&#10;&#10;## Risk Scoring&#10;&#10;**Probability**: Very High (5) &gt;80% | High (4) 60-80% | Medium (3) 40-60% | Low (2) 20-40% | Very Low (1) &lt;20%&#10;**Impact**: Critical (5) &gt;30% overrun | High (4) 20-30% | Medium (3) 10-20% | Low (2) 5-10% | Negligible (1) &lt;5%&#10;**Risk Score** = Probability x Impact: Critical (20-25), High (12-19), Medium (6-11), Low (1-5)&#10;**Response**: Avoid | Mitigate | Transfer | Accept | Escalate&#10;&#10;## Active Risks&#10;&#10;### RISK-001: [Risk Title]&#10;**Category**: [Technical | Business | Resource | External | Compliance]&#10;**Status**: [Open | Mitigating | Monitoring | Closed]&#10;**Owner**: [Name]&#10;&#10;**Description**: [Risk and its potential consequences]&#10;&#10;**Assessment**:&#10;- **Probability**: [1-5] - [Justification]&#10;- **Impact**: [1-5] - [Justification]&#10;- **Risk Score**: [P x I]&#10;- **Response**: [Avoid | Mitigate | Transfer | Accept | Escalate]&#10;&#10;**Triggers**: [Early warning signs]&#10;&#10;**Mitigation**:&#10;- **Preventive**: [Actions to reduce probability]&#10;- **Contingency**: [Actions if risk occurs]&#10;- **Fallback**: [Alternative if mitigation fails]&#10;&#10;**Review**: [Frequency] | **Next Review**: [Date]&#10;&#10;---&#10;&#10;### RISK-002: [Risk Title]&#10;[Repeat structure]&#10;&#10;## Closed Risks&#10;&#10;| ID | Risk | Resolution | Date | Lessons Learned |&#10;|----|------|------------|------|-----------------|&#10;| RISK-XXX | [Title] | [How resolved] | [Date] | [Learnings] |&#10;&#10;## Escalation Criteria&#10;&#10;Escalate when: risk score reaches Critical (20+), mitigation fails, or risk impacts multiple projects.</code></pre></details></td></tr>
</tbody>
</table>
