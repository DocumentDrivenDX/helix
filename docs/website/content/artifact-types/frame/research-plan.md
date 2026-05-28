---
title: "Research Plan"
linkTitle: "Research Plan"
slug: research-plan
activity: "Frame"
artifactRole: "supporting"
weight: 20
generated: true
---

## Purpose

Time-boxed plan for answering specific uncertainty before requirements,
design, or investment decisions harden.

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: example.research-plan.depositmatch
  depends_on:
    - example.opportunity-canvas.depositmatch
    - example.feasibility-study.depositmatch
    - example.business-case.depositmatch
  review:
    self_hash: e1bd75c90a2407b8d84770a3d822fa64fc9b90fe1d36cfef5f5d615bf6ba6e06
    deps:
      example.business-case.depositmatch: c09aae8ce2f4fe25d0cc3d021555b75cc6c0e6d713395957b368c7e17b4caf37
      example.feasibility-study.depositmatch: 356da096953895f8c152a1ac8b880fbc03a3617c1c80516e6f0d3b4033a62c72
      example.opportunity-canvas.depositmatch: 75303097bfeeed0272bd68f90ef887f9a5e646a1272f9a57ccd0d899ae17497a
    reviewed_at: "2026-05-15T04:11:24Z"
---

# Research Plan: DepositMatch Pilot Validation

**Research Lead**: Product Lead
**Time Budget**: 2 weeks
**Status**: Example

## Research Objectives

### Primary Research Questions

1. **Question**: Do bookkeeping firms with 5-25 employees spend enough weekly
   time on deposit reconciliation to make DepositMatch a top-three workflow
   problem?
   - **Why Important**: The Business Case assumes reconciliation is a capacity
     bottleneck, not a minor annoyance.
   - **Success Criteria**: At least 4 of 5 interviewed firms report weekly
     reconciliation above 3 hours and can name a recent close-cycle failure
     caused by manual matching.

2. **Question**: Can representative pilot firms provide CSV exports that are
   consistent enough for column mapping and suggested matches?
   - **Why Important**: The Feasibility Study identifies CSV variability as the
     largest technical risk.
   - **Success Criteria**: Sample files from at least 3 firms can be mapped into
     the target import schema with fewer than 2 unsupported required fields per
     firm.

3. **Question**: Will pilot firms pay for a narrow reconciliation workspace
   before bank-feed integrations or ledger writeback exist?
   - **Why Important**: The Business Case pricing and obtainable market are
     low-confidence assumptions.
   - **Success Criteria**: At least 3 of 5 pilot firms agree that $149/month is
     reasonable if the pilot reaches the stated time and accuracy targets.

### Knowledge Gaps

| Gap | Impact | Current Confidence |
|-----|--------|--------------------|
| Actual weekly reconciliation time for target firms | High | Low |
| CSV field variability across accounting systems and bank portals | High | Low |
| Willingness to pay for CSV-first workflow | High | Low |
| Which exception states reviewers need on day one | Medium | Medium |

## Scope

**In Scope**: Interviews with target firms, sample CSV collection, lightweight
workflow observation, pricing reaction, and exception-state discovery.

**Out of Scope**: Full usability testing, production onboarding, bank-feed
integration research, and accounting-ledger writeback.

**Assumptions**: Product Vision target segment and pilot scope remain stable
through the research window.

**Decision Enabled**: Whether the PRD can commit to CSV import, match review,
exception ownership, pilot pricing, and success metrics.

## Research Methods

### Target Customer Interviews

- **Objective**: Address Questions 1 and 3.
- **Approach**: Conduct five 45-minute interviews with bookkeeping firm owners
  or reconciliation leads. Focus on recent close cycles, current tools, time
  spent, failure modes, and pricing reaction.
- **Participants/Sources**: Five U.S.-based bookkeeping firms with 5-25
  employees and recurring small-business clients.
- **Duration**: 1 week for recruiting and interviews.
- **Deliverable**: Interview notes, problem-intensity summary, pricing signal.
- **Decision Use**: Confirms whether to proceed with the pilot PRD or return to
  opportunity discovery.

### CSV Sample Review

- **Objective**: Address Question 2.
- **Approach**: Ask interview participants for anonymized or synthetic samples
  matching their real bank deposit and invoice exports. Map fields into the
  target import shape and record unsupported fields.
- **Participants/Sources**: At least three firms using different accounting or
  bank export patterns.
- **Duration**: 3 days.
- **Deliverable**: Import-compatibility matrix and required field list.
- **Decision Use**: Defines FEAT-001 import requirements and feasibility risk.

### Exception Workflow Probe

- **Objective**: Identify day-one exception states for FEAT-003.
- **Approach**: Walk participants through recent unresolved deposits and ask
  what owner, next action, and evidence they needed.
- **Participants/Sources**: Same interview participants; use recent examples.
- **Duration**: Included in interviews.
- **Deliverable**: Exception-state candidates and vocabulary.
- **Decision Use**: Prevents the PRD from inventing exception states detached
  from real reviewer work.

## Timeline

| Activity | Duration | Activities | Deliverables |
|-------|----------|------------|--------------|
| Planning | 1 day | Finalize screener, interview guide, data-handling plan | Approved plan |
| Investigation | 6 days | Interviews, CSV sample collection, workflow probes | Notes and sample inventory |
| Analysis | 3 days | Synthesize findings, map CSV compatibility, summarize pricing signal | Findings summary |
| Validation | 2 days | Review with product, engineering, and compliance | PRD readiness recommendation |

**Total Duration**: 2 weeks

## Research Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Firms cannot share representative CSVs | Medium | High | Accept anonymized or synthetic samples with real column shape. |
| Interviewees overstate willingness to pay | High | Medium | Ask for pilot commitment and compare against current cost/time. |
| Sample size is too small to generalize | High | Medium | Treat findings as pilot-scope evidence only; require follow-up before scale claims. |
| Compliance review limits data collection | Medium | High | Use synthetic/anonymized samples and avoid live financial data during research. |

## Completion Criteria

- [ ] All three primary research questions answered with evidence or deferred
  with rationale.
- [ ] Interview notes summarize problem intensity and current alternatives.
- [ ] CSV compatibility matrix identifies required fields and unsupported
  cases.
- [ ] Pricing signal is explicit enough to confirm or revise the pilot Business
  Case.
- [ ] PRD readiness recommendation reviewed by product, engineering, and
  compliance.
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="/reference/glossary/activities/"><strong>Frame</strong></a> — Define what the system should do, for whom, and how success will be measured.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/01-frame/research-plan.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="/artifact-types/frame/prd/">PRD</a><br><a href="/artifact-types/frame/principles/">Principles</a><br><a href="/artifact-types/frame/feature-specification/">Feature Specification</a><br><a href="/artifact-types/frame/stakeholder-map/">Stakeholder Map</a><br><a href="/artifact-types/frame/risk-register/">Risk Register</a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Research Plan Generation Prompt
Plan the smallest useful research effort that will close the key knowledge gaps.

## Reference Anchors

Use these local resource summaries as grounding:

- `docs/resources/nng-ux-research-methods.md` grounds matching research
  methods to questions, evidence types, and product activity.
- `docs/resources/sba-market-research-competitive-analysis.md` grounds demand,
  pricing, customer, and market evidence expectations.

## Focus
- Frame the primary questions and the evidence needed.
- Keep methods, timeline, and risks lean.
- Make the deliverable and success criteria specific.
- Tie every method to a decision that will change if the evidence changes.

## Role Boundary

Research Plan is not research findings, PRD, or Business Case. It defines how
the team will close uncertainty before downstream artifacts commit to scope,
pricing, metrics, or design assumptions.

## Completion Criteria
- Questions are bounded and answerable.
- Methods fit the uncertainty level.
- The plan is short enough to execute.
- Success criteria say what decision the evidence will enable.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---
ddx:
  id: research-plan
---

# Research Plan: {{research_topic}}

**Research Lead**: {{research_lead}}
**Time Budget**: {{time_budget}}
**Created**: {{date}}
**Status**: Draft

## Research Objectives

### Primary Research Questions

1. **Question**:
   - **Why Important**:
   - **Success Criteria**:

2. **Question**:
   - **Why Important**:
   - **Success Criteria**:

### Knowledge Gaps
| Gap | Impact | Current Confidence |
|-----|--------|--------------------|
| [Gap] | High/Med/Low | Low/Med/High |

## Scope

**In Scope**: [What will be investigated]
**Out of Scope**: [What will not]
**Assumptions**: [What we&#x27;re taking as given]
**Decision Enabled**: [What downstream decision this research will unlock]

## Research Methods

### [Method Name]
- **Objective**: [Which question this addresses]
- **Approach**: [How it will be executed]
- **Participants/Sources**: [Who/what]
- **Duration**: [Time required]
- **Deliverable**: [Specific output]
- **Decision Use**: [How the finding changes scope, design, pricing, or go/no-go]

## Timeline

| Activity | Duration | Activities | Deliverables |
|-------|----------|------------|--------------|
| Planning | | Define scope, recruit | Plan approved |
| Investigation | | Execute methods | Raw data |
| Analysis | | Synthesize findings | Findings report |
| Validation | | Review with stakeholders | Validated conclusions |

**Total Duration**:

## Research Risks
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| | | | |

## Completion Criteria
- [ ] All research questions answered with evidence
- [ ] Findings documented and validated
- [ ] Recommendations are actionable
- [ ] Stakeholders aligned on conclusions</code></pre></details></td></tr>
</tbody>
</table>
