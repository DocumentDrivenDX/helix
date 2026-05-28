---
title: "Metric Definition"
linkTitle: "Metric Definition"
slug: metric-definition
activity: "Iterate"
artifactRole: "core"
weight: 10
generated: true
---

## Purpose

Metric Definition is the **single-measurement contract**. Its unique job is to
define exactly what is measured, how to collect it, what unit it uses, whether
higher or lower is better, what tolerance applies, and how dashboards,
ratchets, experiments, or monitoring should interpret it.

It is not a dashboard, alert policy, or improvement backlog item. Those artifacts
consume metric definitions.

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: example.metric-definition.depositmatch.csv-import-validation-seconds
  depends_on:
    - example.test-plan.depositmatch
    - example.deployment-checklist.depositmatch.csv-import
  review:
    self_hash: 7889a106bd3b349d17124fe2fcd082f9f79c1b12947785617af369273603b0c8
    deps:
      example.deployment-checklist.depositmatch.csv-import: 02e9e7c9c29b4a335e0e2eceacaaaa6673018042db2a706f89293ab6f58abcbf
      example.test-plan.depositmatch: ba055b639a94e62d3b24f3a7ca270f78c3f17f6bae78b936d399291225d7976f
    reviewed_at: "2026-05-25T15:46:40Z"
---

# Metric Definition: csv-import-validation-seconds

> Store at `docs/helix/06-iterate/metrics/csv-import-validation-seconds.yaml`

```yaml
name: csv-import-validation-seconds
description: Time required to validate and summarize a representative DepositMatch CSV import fixture totaling 10,000 rows.
unit: seconds
direction: lower
command: pnpm metric:csv-import-validation -- --fixture fixtures/import/acme-10000-rows
output_pattern: "METRIC csv-import-validation-seconds=([0-9]+\\.?[0-9]*)"
tolerance: "5%"
interpretation: A value above 5 seconds violates the FEAT-001 performance target and should create an improvement backlog item unless the fixture changed.
labels:
  product: depositmatch
  feature: FEAT-001
  area: import
  signal: latency
```

## Example: regression-bench metric (methodology/skill change)

A regression bench validates a methodology or skill change. The metric scores a
fixed brief, the `command` re-runs it from the bare prompt with the improved
skill installed, and `baseline`/`target` carry the bare-prompt reading versus
the value that earns the change its keep.

```yaml
name: recipe-app-build-conformance
description: Intrinsic conformance score for the recipe-app bench brief run from the bare prompt with the candidate HELIX skill installed (build passes + template-conformant PRD + zero phantom claims).
unit: score
direction: higher
command: bash tests/workflows/run-all.sh --bench recipe-app --score
output_pattern: "METRIC recipe-app-build-conformance=([0-9]+\\.?[0-9]*)"
baseline: 0.62
target: 0.85
tolerance: "0.05"
last_verified: "2026-05-25"
interpretation: Below baseline means the candidate skill change regressed the bench; at or above target means the change earned its keep. A score that disagrees with the PRD it scores (template↔meta drift) is a broken instrument — fix the instrument before trusting the reading (FEAT-016).
labels:
  product: helix
  feature: FEAT-014
  area: methodology
  signal: conformance
```
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="/reference/glossary/activities/"><strong>Iterate</strong></a> — Measure, align, and improve. Close the feedback loop back into the planning strand.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/06-iterate/metrics/[name].yaml</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="/artifact-types/iterate/metrics-dashboard/">Metrics Dashboard</a><br><a href="/artifact-types/deploy/monitoring-setup/">Monitoring Setup</a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Metric Definition Prompt

Create one reusable metric definition.

## Purpose

Metric Definition is the **single-measurement contract**. Its unique job is to
define exactly what is measured, how to collect it, what unit it uses, whether
higher or lower is better, what tolerance applies, and how dashboards,
ratchets, experiments, or monitoring should interpret it.

It is not a dashboard, alert policy, or improvement backlog item. Those artifacts
consume metric definitions.

## Reference Anchors

Use this local resource summary as grounding:

- `docs/resources/google-sre-monitoring-distributed-systems.md` grounds metric
  definitions as precise quantitative signals with clear interpretation.

## Focus
Define the metric as the authoritative source for ratchets, dashboards, experiments, and monitoring.

Keep the definition minimal: required fields are `name`, `description`, `unit`, `direction`, and `command`. Add `output_pattern`, `tolerance`, and `labels` only when needed.

The command must be deterministic, repeatable, and free of side effects or external service dependencies. Prefer `METRIC &lt;name&gt;=&lt;value&gt;` output unless an `output_pattern` is required.

## Boundary Test

| If you are writing... | Put it in... |
|---|---|
| One metric&#x27;s unit, command, direction, tolerance, and labels | Metric Definition |
| A view comparing multiple metrics over time | Metrics Dashboard |
| A decision about what to improve next | Improvement Backlog |
| Production alerting or runbook behavior | Monitoring Setup / Runbook |

## Completion Criteria
- All required fields are populated.
- The command is deterministic and repeatable.
- The filename matches the `name` field.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---
ddx:
  id: METRIC-name
---

# Metric Definition: [NAME]

&gt; Store at `docs/helix/06-iterate/metrics/[NAME].yaml`

```yaml
name: [kebab-case-identifier]
description: [What this metric measures]
unit: [seconds|bytes|percent|count|score|...]
direction: [lower|higher]
command: [repeatable shell command that actually runs and emits the value]
output_pattern: &quot;[regex with capture group]&quot;
baseline: [the value the command produced on a recorded run — measured, not asserted]
target: [the value that counts as success, in the same unit]
tolerance: [noise band, e.g. &quot;5%&quot; or &quot;100ms&quot;]
last_verified: [ISO-8601 date the command was last run and confirmed to emit this value]
interpretation: [How to read meaningful changes]
labels:
  [key]: [value]
```

**The measurement must be real.** `command` must have actually been run and
confirmed to emit the value before this metric is trusted; record that run date
in `last_verified`. A metric whose command was never run — an
asserted-but-unmeasured number — is a phantom claim (FEAT-016), not a metric.
`baseline` is what the command *produced*, never a target typed in by hand; for
a regression bench (a metric validating a methodology/skill change), `baseline`
is the bare-prompt reading and `target` is the value that earns the change its
keep.</code></pre></details></td></tr>
</tbody>
</table>
