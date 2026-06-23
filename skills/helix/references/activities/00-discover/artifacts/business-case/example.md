---
ddx:
  id: example.business-case.depositmatch
  depends_on:
    - example.product-vision.depositmatch
  review:
    self_hash: c09aae8ce2f4fe25d0cc3d021555b75cc6c0e6d713395957b368c7e17b4caf37
    deps:
      example.product-vision.depositmatch: 8abbb2fcb552b536f07829f57d91ef3ae8dbf52a6066955222e83d196b59b5ae
    reviewed_at: "2026-05-15T04:11:24Z"
---

# Business Case

## Executive Summary

DepositMatch is a focused reconciliation workspace for bookkeeping firms that
are losing reviewer capacity to manual deposit matching. The recommended
investment is a three-month pilot build for CSV import, evidence-backed match
review, and exception ownership. The expected return is increased client
capacity for pilot firms and a paid product path if weekly reconciliation time
falls below 3 minutes per client.

## Opportunity Sizing

| Market Tier | Size | Calculation | Source / Confidence |
|-------------|------|-------------|---------------------|
| TAM (Total) | $1.2B annual workflow spend | 60,000 small bookkeeping firms x $20,000 estimated annual reconciliation labor/tooling spend | Planning assumption, low confidence |
| SAM (Serviceable) | $180M annual workflow spend | 9,000 firms with 5-25 employees and recurring small-business clients x $20,000 | Target-market filter from Product Vision, medium confidence |
| SOM (Obtainable) | $3.6M ARR | 600 pilot-fit firms x $500/month average subscription | Three-year obtainable target assumption, low confidence |

**Key Assumptions**: Firms can export usable CSVs, reconciliation is a weekly
capacity constraint, and firm owners will pay for auditability plus time saved.
The sizing numbers are intentionally marked as assumptions until a research
plan validates demand, market counts, and willingness to pay.

## Investment Required

| Category | Year 1 | Year 2 | Year 3 |
|----------|--------|--------|--------|
| Development | $180,000 | $240,000 | $360,000 |
| Infrastructure | $12,000 | $30,000 | $60,000 |
| Go-to-Market | $40,000 | $120,000 | $240,000 |
| Operations | $30,000 | $90,000 | $180,000 |

## Alternatives Considered

| Option | Benefits | Costs / Limits | Decision |
|--------|----------|----------------|----------|
| Build DepositMatch CSV-first pilot | Validates trust and time savings with limited integration cost | Requires pilot recruiting and careful financial-data handling | Carry forward |
| Build bank feed and accounting sync first | Stronger automation story | Longer build, higher integration risk, slower learning | Reject for v1 |
| Stay with spreadsheet workflow templates | Lowest build cost | Does not preserve evidence or reduce context switching enough | Reject |
| Do nothing for one quarter | Preserves current engineering capacity | Delays learning on reviewer trust and keeps pilot firms in manual workflows | Reject |

## Expected ROI

| Metric | Year 1 | Year 2 | Year 3 |
|--------|--------|--------|--------|
| Revenue/Value | $120,000 | $900,000 | $3,600,000 |
| Costs | $262,000 | $480,000 | $840,000 |
| Net | -$142,000 | $420,000 | $2,760,000 |

**Breakeven**: Month 18 | **3-Year ROI**: 283% | **Confidence**: Low until pilot conversion and pricing are validated.

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| CSV exports vary too much for a reliable pilot | High | Medium | Recruit pilots across at least three accounting systems and build per-client mapping. |
| Reviewers distrust suggested matches | Medium | High | Make evidence visible before approval and require reviewer acceptance. |
| Firms will not pay enough for a narrow workflow | Medium | High | Validate willingness to pay before expanding beyond pilot scope. |

## Strategic Alignment

| Strategic Goal | How This Contributes |
|----------------|---------------------|
| Increase capacity for small bookkeeping firms | Reduces routine reconciliation time and keeps exceptions owned. |
| Build trust-first AI workflow products | Uses suggestions as reviewable support, not invisible automation. |

**Opportunity Cost**: Building DepositMatch delays broader accounting-platform
integrations, but it learns faster about reviewer trust and weekly time savings.

## Recommendation

**Decision**: Conditional Go

**Rationale**: The opportunity is attractive if the pilot proves time savings
and reviewer trust with CSV-first workflows. The investment should stay bounded
until willingness to pay and CSV variability are validated.

**Conditions**:

- Recruit at least five pilot firms before expanding beyond CSV import and
  review.
- Measure median reconciliation time and suggestion acceptance accuracy during
  the first two months.
