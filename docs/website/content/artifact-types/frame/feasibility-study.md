---
title: "Feasibility Study"
linkTitle: "Feasibility Study"
slug: feasibility-study
activity: "Frame"
artifactRole: "supporting"
weight: 16
generated: true
---

## Purpose

Pre-commitment viability assessment across technical, business, operational,
resource, schedule, compliance, risk, and alternative dimensions.

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: example.feasibility-study.depositmatch
  depends_on:
    - example.opportunity-canvas.depositmatch
    - example.business-case.depositmatch
    - example.compliance-requirements.depositmatch
  review:
    self_hash: 356da096953895f8c152a1ac8b880fbc03a3617c1c80516e6f0d3b4033a62c72
    deps:
      example.business-case.depositmatch: c09aae8ce2f4fe25d0cc3d021555b75cc6c0e6d713395957b368c7e17b4caf37
      example.compliance-requirements.depositmatch: ec7fb87a927f7e53a9c323e9af8ee73d667e4520ab596c130077d332d2783c9f
      example.opportunity-canvas.depositmatch: 75303097bfeeed0272bd68f90ef887f9a5e646a1272f9a57ccd0d899ae17497a
    reviewed_at: "2026-05-15T04:11:24Z"
---

# Feasibility Study: DepositMatch CSV-first Pilot

**Feasibility Lead**: Product and engineering leads
**Evaluation Timeframe**: 2 weeks
**Decision Deadline**: 2026-05-31
**Status**: Example

## Executive Summary

### Project Overview

DepositMatch is a focused reconciliation workspace for small bookkeeping firms.
The pilot scope imports CSV bank and invoice exports, suggests matches with
visible evidence, tracks reviewer decisions, and keeps unresolved deposits in a
client-scoped exception queue.

### Recommendation

**Overall Assessment**: CONDITIONALLY FEASIBLE
**Decision**: CONDITIONAL GO
**Rationale**: The CSV-first pilot is technically and operationally feasible if
the first release stays narrow. The highest risks are CSV variability, live
financial-data handling, and willingness to pay, so the project should proceed
only with pilot recruiting, compliance review, and explicit success metrics.
**Confidence**: Medium

## Feasibility Assessment

### Technical

- **Assessment**: FEASIBLE
- **Key requirements**: CSV import and mapping, suggested matching, evidence
  display, firm/client access boundaries, review log export, and exception
  queue.
- **Main risks**: CSV format variability, false-positive matches, and audit log
  integrity.
- **Evidence**: Product Vision defines a narrow workflow; Opportunity Canvas
  keeps v1 out of bank feeds and ledger writeback.

### Business

- **Assessment**: HIGH RISK
- **Market opportunity**: Small bookkeeping firms have a specific weekly
  reconciliation bottleneck, but segment size and pricing are still planning
  assumptions.
- **Value proposition**: Reviewer capacity, visible evidence, and exception
  ownership are differentiated against spreadsheets and generic matching tools.
- **Evidence**: Business Case marks TAM/SAM/SOM and pricing as assumptions;
  Opportunity Canvas requires pilot conversion evidence.

### Operational

- **Assessment**: HIGH RISK
- **Support and deployment needs**: Pilot onboarding, CSV sampling, per-firm
  mapping support, deletion requests, incident response, and support access
  controls.
- **Regulatory requirements**: FTC Safeguards and state privacy applicability
  need counsel review before live client financial data is uploaded.
- **Evidence**: Compliance Requirements identifies financial-data handling,
  retention, vendor, and counsel-review gaps.

### Resource

- **Assessment**: FEASIBLE
- **Budget**: Year-one pilot budget in Business Case: $262,000 across
  development, infrastructure, go-to-market, and operations.
- **Team and timeline**: Three-month pilot build is feasible with a focused
  product/engineering pair and limited support coverage.
- **Evidence**: Business Case bounds the first investment; Opportunity Canvas
  keeps bank feeds, ledger writeback, and automatic approval out of scope.

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| CSV exports vary enough to slow onboarding | High | Medium | Recruit pilots across at least three accounting systems and build explicit column mapping. |
| Reviewers distrust suggestions | Medium | High | Show evidence before approval and measure accepted suggestion accuracy. |
| Compliance review expands required controls | Medium | High | Complete legal applicability review before live-data pilot. |
| Pilot firms do not pay at target pricing | Medium | High | Validate willingness to pay before expanding beyond CSV-first scope. |

## Alternatives

### CSV-first Pilot

- **Pros**: Fastest path to validate reviewer trust, time savings, and
  willingness to pay without integration dependencies.
- **Cons**: Requires manual CSV mapping support and does not prove bank-feed
  integration value.
- **Feasibility**: CONDITIONALLY FEASIBLE
- **Decision**: Carry forward

### Bank-feed and Ledger Integration First

- **Pros**: Stronger automation story and richer transaction context.
- **Cons**: Higher integration complexity, slower learning, larger compliance
  and support surface.
- **Feasibility**: HIGH RISK
- **Decision**: Reject for v1

### Do Nothing / Delay

- **Pros**: Avoids compliance and support burden while market assumptions are
  weak.
- **Cons**: Delays learning on the core reviewer-trust problem and leaves pilot
  firms in manual spreadsheet workflows.
- **Feasibility**: FEASIBLE but strategically weak
- **Decision**: Reject

## Decision Framework

| Criterion | Status | Rationale |
|-----------|--------|-----------|
| Technical buildability | Pass | CSV-first scope is bounded and avoids complex integrations. |
| Business value | Risk | Pain is clear, but pricing and obtainable market remain assumptions. |
| Operational supportability | Risk | CSV onboarding and financial-data handling need explicit procedures. |
| Compliance readiness | Risk | Counsel review is required before live-data pilot. |
| Resource availability | Pass | Three-month pilot fits the bounded investment case. |

## Next Steps

1. Confirm five pilot firms and collect sample CSVs before finalizing PRD scope.
2. Complete legal/compliance applicability review for live financial data.
3. Turn the CSV import, evidence-backed matching, exception queue, and review
   log into PRD requirements.
4. Add pilot success gates: reconciliation time below 3 minutes per client,
   accepted suggestion accuracy above 95%, and 3 of 5 pilot firms willing to
   pay target pricing.
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Frame</strong></a> — Define what the system should do, for whom, and how success will be measured.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/01-frame/feasibility-study.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="../../../artifact-types/frame/prd/">PRD</a><br><a href="../../../artifact-types/frame/principles/">Principles</a><br><a href="../../../artifact-types/frame/risk-register/">Risk Register</a><br><a href="../../../artifact-types/frame/stakeholder-map/">Stakeholder Map</a><br><a href="../../../artifact-types/frame/feature-registry/">Feature Registry</a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Feasibility Study Generation Prompt&#10;Assess whether the project is feasible and what it would take to proceed.&#10;&#10;## Reference Anchors&#10;&#10;Use these local resource summaries as grounding:&#10;&#10;- `docs/resources/doj-feasibility-study.md` grounds pre-commitment&#10;  feasibility, alternatives, decision criteria, and recommendation.&#10;- `docs/resources/eib-project-feasibility.md` grounds option analysis,&#10;  cost-benefit, organizational, compliance, and risk dimensions.&#10;&#10;## Focus&#10;- Separate technical, business, operational, and resource feasibility.&#10;- Compare realistic alternatives, including delaying or doing nothing where useful.&#10;- State the recommendation clearly.&#10;- Capture the main risks, constraints, and open questions.&#10;- Tie conclusions to evidence and confidence, not optimism.&#10;&#10;## Role Boundary&#10;&#10;Feasibility Study is not the Business Case, PRD, or Solution Design. It decides&#10;whether the opportunity is viable enough to justify deeper framing or delivery&#10;commitment. Business Case owns investment return; PRD owns required behavior;&#10;Solution Design owns the chosen implementation approach.&#10;&#10;## Completion Criteria&#10;- The recommendation is unambiguous.&#10;- Each feasibility dimension is summarized briefly.&#10;- Assumptions and mitigations are explicit.&#10;- The preferred alternative is justified against at least one rejected alternative.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: feasibility-study&#10;---&#10;&#10;# Feasibility Study: {{project_name}}&#10;&#10;**Decision Deadline**: {{decision_deadline}}&#10;**Status**: Draft&#10;&#10;## Executive Summary&#10;&#10;### Project Overview&#10;[Brief description of the proposed project or solution]&#10;&#10;### Recommendation&#10;**Overall Assessment**: FEASIBLE | CONDITIONALLY FEASIBLE | NOT FEASIBLE&#10;**Decision**: GO | CONDITIONAL GO | NO GO&#10;**Rationale**: [2-3 sentences on the main factors]&#10;**Confidence**: High | Medium | Low&#10;&#10;## Feasibility Assessment&#10;&#10;### Technical&#10;- **Assessment**: FEASIBLE | HIGH RISK | NOT FEASIBLE&#10;- **Key requirements**: [Brief list]&#10;- **Main risks**: [Brief list]&#10;- **Evidence**: [What supports the assessment]&#10;&#10;### Business&#10;- **Assessment**: FEASIBLE | HIGH RISK | NOT FEASIBLE&#10;- **Market opportunity**: [Brief summary]&#10;- **Value proposition**: [Brief summary]&#10;- **Evidence**: [What supports the assessment]&#10;&#10;### Operational&#10;- **Assessment**: FEASIBLE | HIGH RISK | NOT FEASIBLE&#10;- **Support and deployment needs**: [Brief summary]&#10;- **Regulatory requirements**: [Brief summary]&#10;- **Evidence**: [What supports the assessment]&#10;&#10;### Resource&#10;- **Assessment**: FEASIBLE | HIGH RISK | NOT FEASIBLE&#10;- **Budget**: [Estimate]&#10;- **Team and timeline**: [Estimate]&#10;- **Evidence**: [What supports the assessment]&#10;&#10;## Risks&#10;&#10;| Risk | Probability | Impact | Mitigation |&#10;|------|-------------|--------|------------|&#10;| [Risk] | High/Med/Low | High/Med/Low | [Strategy] |&#10;&#10;## Alternatives&#10;&#10;### [Alternative Approach]&#10;- **Pros**: [Brief]&#10;- **Cons**: [Brief]&#10;- **Feasibility**: [Brief]&#10;- **Decision**: Carry forward | Reject&#10;&#10;### Do Nothing / Delay&#10;- **Pros**: [Brief]&#10;- **Cons**: [Brief]&#10;- **Feasibility**: [Brief]&#10;- **Decision**: Carry forward | Reject&#10;&#10;## Decision Framework&#10;&#10;| Criterion | Status | Rationale |&#10;|-----------|--------|-----------|&#10;| Technical buildability | Pass / Risk / Fail | [Rationale] |&#10;| Business value | Pass / Risk / Fail | [Rationale] |&#10;| Operational supportability | Pass / Risk / Fail | [Rationale] |&#10;| Compliance readiness | Pass / Risk / Fail | [Rationale] |&#10;| Resource availability | Pass / Risk / Fail | [Rationale] |&#10;&#10;## Next Steps&#10;1. [Action]&#10;2. [Action]</code></pre></details></td></tr>
</tbody>
</table>
