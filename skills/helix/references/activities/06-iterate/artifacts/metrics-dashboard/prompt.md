# Metrics Dashboard Generation Prompt

Document the iteration-level metrics summary used to judge whether the latest
changeset improved the system.

## Purpose

Metrics Dashboard is the **iteration-level measurement summary**. Its unique
job is to compare current metric values against explicit baselines, interpret
direction and tolerance, and produce a clear decision about improvement,
regression, or noise.

For how this artifact relates to metric definitions, security-metrics, and the
improvement backlog, see the "Metric Four-Way Slice" section of
`workflows/activities/06-iterate/README.md`.

## Reference Anchors

Use this local resource summary as grounding:

- `docs/resources/google-sre-monitoring-distributed-systems.md` grounds
  dashboard summaries as interpreted quantitative signals with clear sources.

## Focus
- Start from the canonical metric definitions in `docs/helix/06-iterate/metrics/`.
- Compare the current measurement against the previous baseline or committed floor.
- State whether the change improved, regressed, or stayed within noise.
- Include only the metrics needed to support the decision.
- Cite the source of each metric and the measurement command or report.
- Keep raw observability setup and implementation details out of this artifact.

## Boundary Test

| If you are writing... | Put it in... |
|---|---|
| Metric unit, command, tolerance, and labels | Metric Definition |
| Current-vs-baseline interpretation for one iteration | Metrics Dashboard |
| Prioritized follow-up work | Improvement Backlog |
| Alerting or dashboard implementation details | Monitoring Setup |

## Completion Criteria
- Every metric cited has a source definition and current value.
- The comparison baseline is explicit.
- The conclusion is actionable and easy to hand to the next iteration.
