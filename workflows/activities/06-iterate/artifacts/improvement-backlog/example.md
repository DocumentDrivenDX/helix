---
ddx:
  id: example.improvement-backlog.depositmatch
  depends_on:
    - example.metrics-dashboard.depositmatch.csv-import
  review:
    self_hash: ce764a566bffc81a77e3c174314022a4d2201a32cc6090fab0c585fda4284104
    deps:
      example.metrics-dashboard.depositmatch.csv-import: 55c3a758e5ff9beef2651c46bf668c6a31eab8be6a1f64662166de4135061398
    reviewed_at: "2026-05-26T03:19:52Z"
---

# Improvement Backlog

**Iteration**: DepositMatch CSV Import Pilot Readiness
**Source Learnings**: Metrics dashboard, deployment checklist, story test plan,
pilot-readiness review

## Prioritization Rules

- P0 safety, data integrity, or raw-financial-data exposure work outranks all
  performance or UX improvement work.
- Otherwise sort by evidence-backed impact, confidence, and effort.
- Prefer improvements that protect pilot trust before optimizations that only
  improve internal convenience.
- Medium-confidence items need either a small spike or more pilot evidence
  before becoming build work.

## Backlog Items

| Rank | Priority | Item | Evidence | Tracker or Follow-Up Target | Why Now | Confidence | Effort | Status |
|------|----------|------|----------|-----------------------------|---------|------------|--------|--------|
| 1 | P1 | Add pilot CSV fixture collection and anonymization workflow | Test Plan risk: fixtures may not match real exports | Follow-up target: create a runtime work item before next pilot import story | Realistic fixtures protect mapping and validation work from false confidence | High | M | open |
| 2 | P1 | Add upload p95 latency watch item to pilot dashboard | Metrics dashboard: production file sizes may differ from fixture data | Follow-up target: monitoring setup update | Keeps the 5-second validation target honest during pilot rollout | Medium | S | open |
| 3 | P2 | Add abandoned draft-session cleanup story | Technical Design risk: draft sessions can accumulate | Follow-up target: FEAT-001 follow-on story after upload/mapping | Useful hygiene, but not required for first upload slice | Medium | M | deferred |

## Selection for Next Iteration

- Selected: Add pilot CSV fixture collection and anonymization workflow.
- Why it wins: It has high confidence, protects multiple upcoming stories, and
  directly reduces risk in the validation and mapping work. The metrics
  dashboard currently passes, so latency optimization is not the next best use
  of the iteration.

## Review Checklist

- [x] Each item cites evidence
- [x] Tracker references or explicit follow-up targets are included
- [x] Ordering is deterministic
