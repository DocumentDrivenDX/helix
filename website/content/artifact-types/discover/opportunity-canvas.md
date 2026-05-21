---
title: "Opportunity Canvas"
linkTitle: "Opportunity Canvas"
slug: opportunity-canvas
activity: "Discover"
artifactRole: "supporting"
weight: 13
generated: true
---

## Purpose

Answers: **Is this the right problem to solve?** Keep the canvas to one page and centered on the decision.

The Opportunity Canvas is not the Product Vision, Business Case, Competitive
Analysis, or PRD. It synthesizes those inputs into a go/no-go gate before
Frame. It owns problem-solution fit and readiness to create requirements.

## Authoring guidance

- **Start with the problem** - validate customer pain before proposing a solution.
- **Be specific about customers** - name exact segments and alternatives.
- **Define clear success** - use measurable metrics with realistic timelines.
- **Show evidence confidence** - distinguish validated facts from assumptions.
- **Keep the solution thin** - describe the minimum concept needed to test fit.
- **Be honest about advantage** - if the advantage is weak, say what must be built.

<details>
<summary>Quality checklist from the prompt</summary>

- [ ] Problem is validated
- [ ] Customer segments are specific
- [ ] Unique value is differentiated
- [ ] Solution addresses the stated problem
- [ ] Metrics are measurable
- [ ] Unfair advantage is honest
- [ ] Go/no-go decision includes unresolved assumptions and next action

</details>

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: example.opportunity-canvas.depositmatch
  depends_on:
    - example.product-vision.depositmatch
    - example.business-case.depositmatch
    - example.competitive-analysis.depositmatch
  review:
    self_hash: 75303097bfeeed0272bd68f90ef887f9a5e646a1272f9a57ccd0d899ae17497a
    deps:
      example.business-case.depositmatch: c09aae8ce2f4fe25d0cc3d021555b75cc6c0e6d713395957b368c7e17b4caf37
      example.competitive-analysis.depositmatch: 732b5273a4a651c0ac6e10f66ce97b29772b1b706582cf8bcc5b72f4767aa793
      example.product-vision.depositmatch: 8abbb2fcb552b536f07829f57d91ef3ae8dbf52a6066955222e83d196b59b5ae
    reviewed_at: "2026-05-15T04:11:24Z"
---

# Opportunity Canvas

## Problem Statement

| Aspect | Description |
|--------|-------------|
| Problem | Small bookkeeping firms lose reviewer capacity to manual deposit-to-invoice reconciliation. |
| Who | Bookkeeping firms with 5-25 employees and recurring small-business clients. |
| Impact | Weekly close work stretches across spreadsheets, exports, and email follow-up. |
| Evidence / Confidence | Product Vision and Competitive Analysis assumptions; validate through pilot interviews. |

**Problem Hypothesis**: Bookkeeping firms will adopt a focused reconciliation
workspace if it reduces weekly client reconciliation below 3 minutes per client
without hiding match evidence from reviewers.

## Customer Segments

| Segment | Priority | Size / Confidence | Characteristics | Current Solution |
|---------|----------|-------------------|-----------------|------------------|
| Multi-client bookkeeping firms | P0 | Medium-sized niche, medium confidence | 5-25 employees, recurring client close cycles, spreadsheet-heavy review | Accounting exports, bank reports, spreadsheets, email |
| Solo bookkeepers with growing client lists | P1 | Unknown, low confidence | Capacity constrained but more price sensitive | Spreadsheets and native accounting reports |

**Early Adopters**: Firms that already export bank and invoice data weekly, have
one reviewer handling multiple clients, and can name specific reconciliation
bottlenecks from the last close cycle.

## Unique Value

| Value Proposition | Customer Benefit | Proof Point |
|-------------------|------------------|-------------|
| Evidence-backed suggested matches | Reviewers can approve quickly without losing auditability. | Product Vision target: accepted suggestions above 95% in review samples. |
| Exception ownership by client | Unclear deposits stay visible until resolved. | Product Vision target: 90% of unresolved deposits have an owner and next action. |
| CSV-first onboarding | Firms can test value before bank-feed integrations. | Business Case recommends a three-month bounded pilot. |

**Elevator Pitch**: DepositMatch gives small bookkeeping firms a trustworthy
review queue for deposit reconciliation. It turns CSV exports into suggested
matches, visible evidence, and owned exceptions without replacing the ledger.

## Customer Fit

| Customer Job / Pain / Gain | Solution Response | Evidence / Confidence |
|----------------------------|-------------------|-----------------------|
| Close weekly reconciliation across many clients | Cross-client review queue | Product Vision, medium confidence |
| Avoid approving matches without proof | Evidence visible before acceptance | Product Vision and Competitive Analysis, medium confidence |
| Preserve follow-up work by client | Exception ownership and next actions | Product Vision, medium confidence |
| Start without integration work | CSV import and mapping | Business Case, medium confidence |

## Solution Concept

| Capability | Problem Addressed | Priority |
|------------|-------------------|----------|
| CSV import and column mapping | Gets firm data into the workspace quickly. | P0 |
| Suggested deposit-to-invoice matches with evidence | Reduces manual searching while preserving reviewer control. | P0 |
| Client-scoped exception queue | Keeps unresolved deposits owned and visible. | P0 |
| Review log export | Supports client questions and month-end auditability. | P1 |

**NOT in Scope**: Bank-feed integrations, accounting-ledger writeback, automatic
approval, payment collection, or replacing QuickBooks/Xero.

## Key Metrics

| Metric | Type | Target | Timeline |
|--------|------|--------|----------|
| Median weekly reconciliation time | Outcome | Below 3 minutes per client | Month 2 of pilot |
| Accepted suggestion accuracy | Quality | Above 95% in reviewer audit samples | Month 2 of pilot |
| Exception ownership | Leading | 90% of unresolved deposits have owner and next action | First month |
| Pilot conversion signal | Business | 3 of 5 pilot firms willing to pay at target pricing | End of pilot |

**North Star Metric**: Median weekly reconciliation time per client.

## Unfair Advantage

| Advantage Type | Our Position | Sustainability |
|----------------|--------------|----------------|
| Workflow focus | Narrow reconciliation review across clients rather than broad ledger management. | Medium |
| Trust model | Evidence-first suggestions instead of opaque automation. | Medium |
| Onboarding path | CSV-first pilot avoids integration delay. | Low |

**Honest Assessment**: The current advantage is focus, not a hard moat. It
becomes stronger only if pilot learning produces better mapping defaults,
review patterns, and exception workflows than generic tools can copy quickly.

## Go/No-Go Decision

| Gate | Status | Evidence / Gap |
|------|--------|----------------|
| Problem validated | Risk | Strong internal hypothesis; needs pilot interviews. |
| Segment reachable | Risk | Target segment is specific; recruiting channel still unvalidated. |
| Value differentiated | Pass | Competitive Analysis identifies trust-first review and exception ownership. |
| Metrics measurable | Pass | Product Vision defines time, accuracy, and exception targets. |
| Risks bounded | Pass | Business Case limits the first investment to a three-month CSV-first pilot. |

**Decision**: Go

**Rationale**: The opportunity is clear enough to enter Frame because the
target customer, problem, differentiators, and pilot metrics are specific. The
main uncertainties are recruiting and willingness to pay, so Frame should keep
the first scope focused on pilot validation.

**Next Action**: Proceed to Frame with explicit research and pilot-validation
requirements.
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="/reference/glossary/activities/"><strong>Discover</strong></a> — Validate that an opportunity is worth pursuing before committing to a development cycle.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/00-discover/opportunity-canvas.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="/artifact-types/frame/prd/">PRD</a><br><a href="/artifact-types/frame/user-stories/">User Stories</a><br><a href="/artifact-types/frame/feature-specification/">Feature Specification</a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Opportunity Canvas Prompt

Create an opportunity canvas that validates problem-solution fit before proceeding to Frame.

## Reference Anchors

Use these local resource summaries as grounding:

- `docs/resources/strategyzer-value-proposition-canvas.md` grounds customer
  jobs, pains, gains, pain relievers, and gain creators.
- `docs/resources/leanstack-lean-canvas.md` grounds problem-first validation,
  key metrics, and unfair advantage.
- `docs/resources/sba-market-research-competitive-analysis.md` grounds
  customer, demand, pricing, and competitive evidence expectations.

## Storage Location

Store at: `docs/helix/00-discover/opportunity-canvas.md`

## Purpose

Answers: **Is this the right problem to solve?** Keep the canvas to one page and centered on the decision.

The Opportunity Canvas is not the Product Vision, Business Case, Competitive
Analysis, or PRD. It synthesizes those inputs into a go/no-go gate before
Frame. It owns problem-solution fit and readiness to create requirements.

## Key Principles

- **Start with the problem** - validate customer pain before proposing a solution.
- **Be specific about customers** - name exact segments and alternatives.
- **Define clear success** - use measurable metrics with realistic timelines.
- **Show evidence confidence** - distinguish validated facts from assumptions.
- **Keep the solution thin** - describe the minimum concept needed to test fit.
- **Be honest about advantage** - if the advantage is weak, say what must be built.

## Quality Checklist

- [ ] Problem is validated
- [ ] Customer segments are specific
- [ ] Unique value is differentiated
- [ ] Solution addresses the stated problem
- [ ] Metrics are measurable
- [ ] Unfair advantage is honest
- [ ] Go/no-go decision includes unresolved assumptions and next action</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---
ddx:
  id: opportunity-canvas
---

# Opportunity Canvas

## Problem Statement

| Aspect | Description |
|--------|-------------|
| Problem | [What problem are you solving?] |
| Who | [Who has this problem?] |
| Impact | [What is the cost/pain of this problem?] |
| Evidence / Confidence | [How do you know this is real?] |

**Problem Hypothesis**: [One sentence describing the core problem]

## Customer Segments

| Segment | Priority | Size / Confidence | Characteristics | Current Solution |
|---------|----------|-------------------|-----------------|------------------|
| [Primary] | P0 | [Size, confidence] | [Key traits] | [What they use now] |
| [Secondary] | P1 | [Size, confidence] | [Key traits] | [What they use now] |

**Early Adopters**: [Who will use this first and why?]

## Unique Value

| Value Proposition | Customer Benefit | Proof Point |
|-------------------|------------------|-------------|
| [Value 1] | [Why it matters] | [Evidence] |
| [Value 2] | [Why it matters] | [Evidence] |

**Elevator Pitch**: [2 sentences max describing the unique value]

## Customer Fit

| Customer Job / Pain / Gain | Solution Response | Evidence / Confidence |
|----------------------------|-------------------|-----------------------|
| [Job, pain, or gain] | [Pain reliever or gain creator] | [Source or assumption] |

## Solution Concept

| Capability | Problem Addressed | Priority |
|------------|-------------------|----------|
| [Capability 1] | [Which problem aspect] | P0/P1/P2 |
| [Capability 2] | [Which problem aspect] | P0/P1/P2 |

**NOT in Scope**: [What this solution will NOT do]

## Key Metrics

| Metric | Type | Target | Timeline |
|--------|------|--------|----------|
| [Success metric 1] | Outcome | [Target] | [When] |
| [Leading indicator 1] | Leading | [Target] | [When] |

**North Star Metric**: [Single most important metric]

## Unfair Advantage

| Advantage Type | Our Position | Sustainability |
|----------------|--------------|----------------|
| [Type 1] | [Description] | H/M/L |

**Honest Assessment**: [What we have vs. what we need to build]

## Go/No-Go Decision

| Gate | Status | Evidence / Gap |
|------|--------|----------------|
| Problem validated | Pass / Risk / Fail | [Evidence or gap] |
| Segment reachable | Pass / Risk / Fail | [Evidence or gap] |
| Value differentiated | Pass / Risk / Fail | [Evidence or gap] |
| Metrics measurable | Pass / Risk / Fail | [Evidence or gap] |
| Risks bounded | Pass / Risk / Fail | [Evidence or gap] |

**Decision**: Go | Pivot | No-Go

**Rationale**: [2-3 sentences explaining decision]

**Next Action**: [Proceed to Frame / run research / revise opportunity / stop]</code></pre></details></td></tr>
</tbody>
</table>
