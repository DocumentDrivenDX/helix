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
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Discover</strong></a> — Validate that an opportunity is worth pursuing before committing to a development cycle.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/00-discover/opportunity-canvas.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="../../../artifact-types/frame/prd/">PRD</a><br><a href="../../../artifact-types/frame/user-stories/">User Stories</a><br><a href="../../../artifact-types/frame/feature-specification/">Feature Specification</a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Opportunity Canvas Prompt&#10;&#10;Create an opportunity canvas that validates problem-solution fit before proceeding to Frame.&#10;&#10;## Reference Anchors&#10;&#10;Use these local resource summaries as grounding:&#10;&#10;- `docs/resources/strategyzer-value-proposition-canvas.md` grounds customer&#10;  jobs, pains, gains, pain relievers, and gain creators.&#10;- `docs/resources/leanstack-lean-canvas.md` grounds problem-first validation,&#10;  key metrics, and unfair advantage.&#10;- `docs/resources/sba-market-research-competitive-analysis.md` grounds&#10;  customer, demand, pricing, and competitive evidence expectations.&#10;&#10;## Storage Location&#10;&#10;Store at: `docs/helix/00-discover/opportunity-canvas.md`&#10;&#10;## Purpose&#10;&#10;Answers: **Is this the right problem to solve?** Keep the canvas to one page and centered on the decision.&#10;&#10;The Opportunity Canvas is not the Product Vision, Business Case, Competitive&#10;Analysis, or PRD. It synthesizes those inputs into a go/no-go gate before&#10;Frame. It owns problem-solution fit and readiness to create requirements.&#10;&#10;## Key Principles&#10;&#10;- **Start with the problem** - validate customer pain before proposing a solution.&#10;- **Be specific about customers** - name exact segments and alternatives.&#10;- **Define clear success** - use measurable metrics with realistic timelines.&#10;- **Show evidence confidence** - distinguish validated facts from assumptions.&#10;- **Keep the solution thin** - describe the minimum concept needed to test fit.&#10;- **Be honest about advantage** - if the advantage is weak, say what must be built.&#10;&#10;## Quality Checklist&#10;&#10;- [ ] Problem is validated&#10;- [ ] Customer segments are specific&#10;- [ ] Unique value is differentiated&#10;- [ ] Solution addresses the stated problem&#10;- [ ] Metrics are measurable&#10;- [ ] Unfair advantage is honest&#10;- [ ] Go/no-go decision includes unresolved assumptions and next action</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: opportunity-canvas&#10;---&#10;&#10;# Opportunity Canvas&#10;&#10;## Problem Statement&#10;&#10;| Aspect | Description |&#10;|--------|-------------|&#10;| Problem | [What problem are you solving?] |&#10;| Who | [Who has this problem?] |&#10;| Impact | [What is the cost/pain of this problem?] |&#10;| Evidence / Confidence | [How do you know this is real?] |&#10;&#10;**Problem Hypothesis**: [One sentence describing the core problem]&#10;&#10;## Customer Segments&#10;&#10;| Segment | Priority | Size / Confidence | Characteristics | Current Solution |&#10;|---------|----------|-------------------|-----------------|------------------|&#10;| [Primary] | P0 | [Size, confidence] | [Key traits] | [What they use now] |&#10;| [Secondary] | P1 | [Size, confidence] | [Key traits] | [What they use now] |&#10;&#10;**Early Adopters**: [Who will use this first and why?]&#10;&#10;## Unique Value&#10;&#10;| Value Proposition | Customer Benefit | Proof Point |&#10;|-------------------|------------------|-------------|&#10;| [Value 1] | [Why it matters] | [Evidence] |&#10;| [Value 2] | [Why it matters] | [Evidence] |&#10;&#10;**Elevator Pitch**: [2 sentences max describing the unique value]&#10;&#10;## Customer Fit&#10;&#10;| Customer Job / Pain / Gain | Solution Response | Evidence / Confidence |&#10;|----------------------------|-------------------|-----------------------|&#10;| [Job, pain, or gain] | [Pain reliever or gain creator] | [Source or assumption] |&#10;&#10;## Solution Concept&#10;&#10;| Capability | Problem Addressed | Priority |&#10;|------------|-------------------|----------|&#10;| [Capability 1] | [Which problem aspect] | P0/P1/P2 |&#10;| [Capability 2] | [Which problem aspect] | P0/P1/P2 |&#10;&#10;**NOT in Scope**: [What this solution will NOT do]&#10;&#10;## Key Metrics&#10;&#10;| Metric | Type | Target | Timeline |&#10;|--------|------|--------|----------|&#10;| [Success metric 1] | Outcome | [Target] | [When] |&#10;| [Leading indicator 1] | Leading | [Target] | [When] |&#10;&#10;**North Star Metric**: [Single most important metric]&#10;&#10;## Unfair Advantage&#10;&#10;| Advantage Type | Our Position | Sustainability |&#10;|----------------|--------------|----------------|&#10;| [Type 1] | [Description] | H/M/L |&#10;&#10;**Honest Assessment**: [What we have vs. what we need to build]&#10;&#10;## Go/No-Go Decision&#10;&#10;| Gate | Status | Evidence / Gap |&#10;|------|--------|----------------|&#10;| Problem validated | Pass / Risk / Fail | [Evidence or gap] |&#10;| Segment reachable | Pass / Risk / Fail | [Evidence or gap] |&#10;| Value differentiated | Pass / Risk / Fail | [Evidence or gap] |&#10;| Metrics measurable | Pass / Risk / Fail | [Evidence or gap] |&#10;| Risks bounded | Pass / Risk / Fail | [Evidence or gap] |&#10;&#10;**Decision**: Go | Pivot | No-Go&#10;&#10;**Rationale**: [2-3 sentences explaining decision]&#10;&#10;**Next Action**: [Proceed to Frame / run research / revise opportunity / stop]</code></pre></details></td></tr>
</tbody>
</table>
