---
title: "Improvement Candidates"
slug: improvement-backlog
weight: 580
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
    self_hash: ed5edb10332f47e1faf1ff63ff3bd6d2b47a8ed959acc9aece1b2f1be8e2bf2c
    deps:
      metrics-dashboard: a6eeafc50ce55540e195d0613e8e23f97e05ca23f39b812821324ee74c78a125
    reviewed_at: "2026-10-04T02:22:28Z"
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
