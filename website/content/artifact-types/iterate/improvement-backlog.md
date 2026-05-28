---
title: "Improvement Backlog"
linkTitle: "Improvement Backlog"
slug: improvement-backlog
activity: "Iterate"
artifactRole: "core"
weight: 12
generated: true
---

## Purpose

Improvement Backlog is the **iteration follow-up prioritization artifact**. Its
unique job is to convert metrics, feedback, incidents, and retrospective
learnings into ordered improvement candidates with evidence, rationale, tracker
or explicit follow-up targets, and a next-iteration selection.

It is not the live tracker. DDx or another runtime owns issue status, assignees,
and execution history. This artifact explains what should compete for attention
next and why.

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
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
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="/reference/glossary/activities/"><strong>Iterate</strong></a> — Measure, align, and improve. Close the feedback loop back into the planning strand.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/06-iterate/improvement-backlog.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td>Tracker Issues</td></tr>
<tr><th>HELIX documents</th><td><a href="https://github.com/DocumentDrivenDX/helix/blob/main/docs/helix/06-iterate/improvement-backlog.md"><code>docs/helix/06-iterate/improvement-backlog.md</code></a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Improvement Backlog Generation Prompt

Document the prioritized improvement inventory produced from iteration learnings.

## Purpose

Improvement Backlog is the **iteration follow-up prioritization artifact**. Its
unique job is to convert metrics, feedback, incidents, and retrospective
learnings into ordered improvement candidates with evidence, rationale, tracker
or explicit follow-up targets, and a next-iteration selection.

It is not the live tracker. DDx or another runtime owns issue status, assignees,
and execution history. This artifact explains what should compete for attention
next and why.

## Reference Anchors

Use this local resource summary as grounding:

- `docs/resources/intercom-rice-prioritization.md` grounds evidence-backed
  ranking by impact, confidence, effort, and reach.

## Focus
- Turn the current iteration&#x27;s learnings into a ranked list of follow-up work.
- Prefer concrete tracker-backed items over vague TODOs.
- Use metrics, feedback, and retrospective findings as evidence.
- Make the next selection obvious by sorting by priority and impact.
- Link each item to the relevant work item, report, or supporting artifact.

## Boundary Test

| If you are writing... | Put it in... |
|---|---|
| Measurement interpretation for this iteration | Metrics Dashboard |
| Prioritized follow-up candidates and selection rationale | Improvement Backlog |
| Live issue status, assignee, and execution history | runtime work item or issue |
| New product requirements or design changes | Appropriate upstream artifact |

## Completion Criteria
- The inventory is prioritized.
- Every item has an evidence source.
- The next iteration candidates are explicit.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---
ddx:
  id: improvement-backlog
---

# Improvement Backlog

**Iteration**: [iteration or release]
**Source Learnings**: [metrics, feedback, retrospective, incident review]

## Prioritization Rules

- [Rule for ordering work]
- [Rule for handling safety or risk]
- [How confidence and effort affect ordering]

## Backlog Items

| Rank | Priority | Item | Evidence | Tracker or Follow-Up Target | Why Now | Confidence | Effort | Status |
|------|----------|------|----------|-----------------------------|---------|------------|--------|--------|
| 1 | P1 | [item] | [metric or finding] | [work item ID or explicit target] | [reason] | [high/med/low] | [S/M/L] | [open/blocked] |

## Selection for Next Iteration

- [Chosen item]
- [Why it wins the next slot]

## Review Checklist

- [ ] Each item cites evidence
- [ ] Tracker references are included
- [ ] Ordering is deterministic</code></pre></details></td></tr>
</tbody>
</table>
