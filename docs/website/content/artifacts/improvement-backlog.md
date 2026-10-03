---
title: "Improvement Candidates"
slug: improvement-backlog
weight: 540
activity: "Iterate"
source: "06-iterate/improvement-backlog.md"
generated: true
---

> **Example from HELIX's own docs.** This generated page comes from `docs/helix/`. Use it to see the method in practice; start with the [artifact-type catalog](/artifact-types/) for reusable templates. Historical plans and reports may describe retired architecture.

> **Source identity** (from `06-iterate/improvement-backlog.md`):

```yaml
ddx:
  id: improvement-backlog
  authoring:
    home: repo
  depends_on:
    - metrics-dashboard
  review:
    self_hash: 952df3e5bbb6e967cd0e3d485ae7106893c464008ecda327e9c0c6a33527e2cd
    deps:
      metrics-dashboard: 486cd18a01712b15850ce7dd808d432a8a52cc56d1db22a8939ed31b633191c0
    reviewed_at: "2026-09-16T03:20:07Z"
```

# Improvement Candidates

This page records evidence-backed questions for future work. The runtime work
tracker owns execution status and priority commitments.

## Evaluation

[The metrics dashboard](/artifacts/metrics-dashboard/) reports the first evaluation
sample: nine briefs produced 33/36 deterministic checks and a rubric score of
57/62. The alignment target remains unmeasured because the sample used a
fixture seeded with drift.

| Candidate | Evidence | Question |
|---|---|---|
| Measure alignment on a healthy artifact set | The current alignment sample has 26 findings on a drift-seeded fixture. | Does a healthy set average fewer than three findings per alignment run? |
| Compare first-pass review of template-authored and free-form PRDs | Two template-authored PRDs passed instance validation; no free-form comparison exists. | Do HELIX templates improve first-pass review outcomes? |
| Reassess overlapping catalog types | The test and discovery activities contain several related analysis and test-plan types. | Do these types serve distinct reader needs? |
| Consider a `.docx` renderer | The present renderer produces HTML and PDF. | Is a Word format needed by adopters? |
