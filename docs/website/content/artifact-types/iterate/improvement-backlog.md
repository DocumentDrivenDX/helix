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

It is not the live tracker. The runtime owns issue status, assignees, and
execution history. This artifact explains what should compete for attention
next and why.

For how this artifact relates to metric definitions, the metrics dashboard,
and security-metrics, see the "Metric Four-Way Slice" section of
`workflows/activities/06-iterate/README.md`.

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
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Iterate</strong></a> — Measure, align, and improve. Close the feedback loop back into the planning strand.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/06-iterate/improvement-backlog.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>HELIX documents</th><td><a href="https://github.com/DocumentDrivenDX/helix/blob/main/docs/helix/06-iterate/improvement-backlog.md"><code>docs/helix/06-iterate/improvement-backlog.md</code></a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Improvement Backlog Generation Prompt&#10;&#10;Document the prioritized improvement inventory produced from iteration learnings.&#10;&#10;## Purpose&#10;&#10;Improvement Backlog is the **iteration follow-up prioritization artifact**. Its&#10;unique job is to convert metrics, feedback, incidents, and retrospective&#10;learnings into ordered improvement candidates with evidence, rationale, tracker&#10;or explicit follow-up targets, and a next-iteration selection.&#10;&#10;It is not the live tracker. The runtime owns issue status, assignees, and&#10;execution history. This artifact explains what should compete for attention&#10;next and why.&#10;&#10;For how this artifact relates to metric definitions, the metrics dashboard,&#10;and security-metrics, see the &quot;Metric Four-Way Slice&quot; section of&#10;`workflows/activities/06-iterate/README.md`.&#10;&#10;## Reference Anchors&#10;&#10;Use this local resource summary as grounding:&#10;&#10;- `docs/resources/intercom-rice-prioritization.md` grounds evidence-backed&#10;  ranking by impact, confidence, effort, and reach.&#10;&#10;## Focus&#10;- Turn the current iteration&#x27;s learnings into a ranked list of follow-up work.&#10;- Prefer concrete tracker-backed items over vague TODOs.&#10;- Use metrics, feedback, and retrospective findings as evidence.&#10;- Make the next selection obvious by sorting by priority and impact.&#10;- Link each item to the relevant work item, report, or supporting artifact.&#10;&#10;## Boundary Test&#10;&#10;| If you are writing... | Put it in... |&#10;|---|---|&#10;| Measurement interpretation for this iteration | Metrics Dashboard |&#10;| Prioritized follow-up candidates and selection rationale | Improvement Backlog |&#10;| Live issue status, assignee, and execution history | runtime work item or issue |&#10;| New product requirements or design changes | Appropriate upstream artifact |&#10;&#10;## Completion Criteria&#10;- The inventory is prioritized.&#10;- Every item has an evidence source.&#10;- The next iteration candidates are explicit.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: improvement-backlog&#10;---&#10;&#10;# Improvement Backlog&#10;&#10;**Iteration**: [iteration or release]&#10;**Source Learnings**: [metrics, feedback, retrospective, incident review]&#10;&#10;## Prioritization Rules&#10;&#10;- [Rule for ordering work]&#10;- [Rule for handling safety or risk]&#10;- [How confidence and effort affect ordering]&#10;&#10;## Backlog Items&#10;&#10;| Rank | Priority | Item | Evidence | Tracker or Follow-Up Target | Why Now | Confidence | Effort | Status |&#10;|------|----------|------|----------|-----------------------------|---------|------------|--------|--------|&#10;| 1 | P1 | [item] | [metric or finding] | [work item ID or explicit target] | [reason] | [high/med/low] | [S/M/L] | [open/blocked] |&#10;&#10;## Selection for Next Iteration&#10;&#10;- [Chosen item]&#10;- [Why it wins the next slot]&#10;&#10;## Review Checklist&#10;&#10;- [ ] Each item cites evidence&#10;- [ ] Tracker references are included&#10;- [ ] Ordering is deterministic</code></pre></details></td></tr>
</tbody>
</table>
