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

For how this artifact relates to dashboards, security-metrics, and the
improvement backlog, see the "Metric Four-Way Slice" section of
`workflows/activities/06-iterate/README.md`.

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
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Iterate</strong></a> — Measure, align, and improve. Close the feedback loop back into the planning strand.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/06-iterate/metrics/[name].yaml</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="../../../artifact-types/iterate/metrics-dashboard/">Metrics Dashboard</a><br><a href="../../../artifact-types/deploy/monitoring-setup/">Monitoring Setup</a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Metric Definition Prompt&#10;&#10;Create one reusable metric definition.&#10;&#10;## Purpose&#10;&#10;Metric Definition is the **single-measurement contract**. Its unique job is to&#10;define exactly what is measured, how to collect it, what unit it uses, whether&#10;higher or lower is better, what tolerance applies, and how dashboards,&#10;ratchets, experiments, or monitoring should interpret it.&#10;&#10;For how this artifact relates to dashboards, security-metrics, and the&#10;improvement backlog, see the &quot;Metric Four-Way Slice&quot; section of&#10;`workflows/activities/06-iterate/README.md`.&#10;&#10;## Reference Anchors&#10;&#10;Use this local resource summary as grounding:&#10;&#10;- `docs/resources/google-sre-monitoring-distributed-systems.md` grounds metric&#10;  definitions as precise quantitative signals with clear interpretation.&#10;&#10;## Focus&#10;Define the metric as the authoritative source for ratchets, dashboards, experiments, and monitoring.&#10;&#10;Keep the definition minimal: required fields are `name`, `description`, `unit`, `direction`, and `command`. Add `output_pattern`, `tolerance`, and `labels` only when needed.&#10;&#10;The command must be deterministic, repeatable, and free of side effects or external service dependencies. Prefer `METRIC &lt;name&gt;=&lt;value&gt;` output unless an `output_pattern` is required.&#10;&#10;## Boundary Test&#10;&#10;| If you are writing... | Put it in... |&#10;|---|---|&#10;| One metric&#x27;s unit, command, direction, tolerance, and labels | Metric Definition |&#10;| A view comparing multiple metrics over time | Metrics Dashboard |&#10;| A decision about what to improve next | Improvement Backlog |&#10;| Production alerting or runbook behavior | Monitoring Setup / Runbook |&#10;&#10;## Completion Criteria&#10;- All required fields are populated.&#10;- The command is deterministic and repeatable.&#10;- The filename matches the `name` field.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: METRIC-name&#10;---&#10;&#10;# Metric Definition: [NAME]&#10;&#10;&gt; Store at `docs/helix/06-iterate/metrics/[NAME].yaml`&#10;&#10;```yaml&#10;name: [kebab-case-identifier]&#10;description: [What this metric measures]&#10;unit: [seconds|bytes|percent|count|score|...]&#10;direction: [lower|higher]&#10;command: [repeatable shell command that actually runs and emits the value]&#10;output_pattern: &quot;[regex with capture group]&quot;&#10;baseline: [the value the command produced on a recorded run — measured, not asserted]&#10;target: [the value that counts as success, in the same unit]&#10;tolerance: [noise band, e.g. &quot;5%&quot; or &quot;100ms&quot;]&#10;last_verified: [ISO-8601 date the command was last run and confirmed to emit this value]&#10;interpretation: [How to read meaningful changes]&#10;labels:&#10;  [key]: [value]&#10;```&#10;&#10;**The measurement must be real.** `command` must have actually been run and&#10;confirmed to emit the value before this metric is trusted; record that run date&#10;in `last_verified`. A metric whose command was never run — an&#10;asserted-but-unmeasured number — is a phantom claim (FEAT-016), not a metric.&#10;`baseline` is what the command *produced*, never a target typed in by hand; for&#10;a regression bench (a metric validating a methodology/skill change), `baseline`&#10;is the bare-prompt reading and `target` is the value that earns the change its&#10;keep.</code></pre></details></td></tr>
</tbody>
</table>
