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
