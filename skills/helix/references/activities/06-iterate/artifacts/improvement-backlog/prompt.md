# Improvement Backlog Generation Prompt

Document the prioritized improvement inventory produced from iteration learnings.

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

## Reference Anchors

Use this local resource summary as grounding:

- `docs/resources/intercom-rice-prioritization.md` grounds evidence-backed
  ranking by impact, confidence, effort, and reach.

## Focus
- Turn the current iteration's learnings into a ranked list of follow-up work.
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
- The next iteration candidates are explicit.
