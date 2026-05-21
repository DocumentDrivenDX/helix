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
    self_hash: a1bb2128a1335ff7b306902f4bc6ab433468c93f567943535c641fa2e53d617e
    deps:
      example.deployment-checklist.depositmatch.csv-import: 02e9e7c9c29b4a335e0e2eceacaaaa6673018042db2a706f89293ab6f58abcbf
      example.test-plan.depositmatch: ba055b639a94e62d3b24f3a7ca270f78c3f17f6bae78b936d399291225d7976f
    reviewed_at: "2026-05-15T04:11:24Z"
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
unit: [seconds|bytes|percent|count|...]
direction: [lower|higher]
command: [repeatable shell command]
output_pattern: &quot;[regex with capture group]&quot;
tolerance: [noise band, e.g. &quot;5%&quot; or &quot;100ms&quot;]
interpretation: [How to read meaningful changes]
labels:
  [key]: [value]
```</code></pre></details></td></tr>
</tbody>
</table>
