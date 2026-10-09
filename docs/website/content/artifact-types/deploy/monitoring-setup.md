---
title: "Monitoring Setup"
linkTitle: "Monitoring Setup"
slug: monitoring-setup
activity: "Deploy"
artifactRole: "supporting"
weight: 12
generated: true
---

## Purpose

Service-specific observability and alerting setup required before or during
rollout.

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: example.monitoring-setup.depositmatch
  authoring:
    home: repo
  depends_on:
    - example.deployment-checklist.depositmatch.csv-import
    - example.security-architecture.depositmatch
    - example.metric-definition.depositmatch.csv-import-validation-seconds
---

# Monitoring Setup

## Service Summary

- Service: DepositMatch CSV-first pilot
- Signals that matter most: import success, match-review availability, review
  decision latency, cross-tenant authorization denials, restricted telemetry
  violations, and audit-log write failures.

## Metrics Collection

| Category | Metrics | Notes |
|----------|---------|-------|
| Application | request latency, 5xx rate, import job duration, import failure count | Split by endpoint and workload |
| System | worker queue depth, database connection saturation, object-storage errors | Only page when user work is blocked |
| Business | imports completed, suggestions reviewed, manual match overrides | Dashboard only during pilot |
| Security | authorization denials, unsafe CSV cells neutralized, telemetry redaction failures, support grant usage | Alerts only for likely incident or control failure |
| Quality | match suggestion acceptance rate, ambiguous suggestion rate | Feeds Iterate metrics, not paging |

## Alerting Rules

| Alert | Condition | Action |
|-------|-----------|--------|
| Import pipeline unavailable | `POST /imports` 5xx rate above 5% for 10 minutes or import queue stalled for 15 minutes | Page primary on-call; use runbook import triage |
| Review decision audit failure | Any accepted/rejected decision fails to write an audit event | Page primary on-call; disable decision endpoint if unresolved |
| Cross-tenant authorization anomaly | More than 5 denied cross-firm/client attempts for one actor in 10 minutes | Notify security lead; inspect actor and preserve logs |
| Restricted telemetry violation | Any prohibited fixture value appears in telemetry assertion or production log scan | Page security lead; rotate affected logs per runbook |
| Support access outside approved window | Any support grant used after expiry or without approval | Page security lead and incident coordinator |

## Dashboards

| Dashboard | Must Show |
|-----------|-----------|
| Operations | availability, latency, error rate, import queue depth, database saturation |
| Pilot Outcome | imports completed, suggestions reviewed, accepted suggestions, manual overrides |
| Security Controls | authorization denials, support grants, audit-log failures, telemetry violations |
| Import Diagnostics | file validation failures, unsupported encodings, malformed rows, formula-neutralized cells |

## Logs and Tracing

### Logging
- Schema authority: the pilot diagnostic Contract owns exact fields and their
  OTel mapping; service/version/environment identify the Resource.
- Trace/span IDs are recorded only with valid context. Independent run/attempt
  and authorized firm/client/import correlation follow that Contract.
- Collection: platform-captured structured logs mapped to OTel through one
  ingestion route. A staging receiver test must prove mapping and no duplicates.
- CI evidence: the runner publishes an access-controlled run manifest and safe
  JSONL; console shows readiness, transitions, actionable warnings and outcome.
  Capture/rotation belong to the runner, not the deployed service.
- Retrieval: the runbook provides a closed-snapshot query capped at 50 records;
  backend queries enforce authenticated firm scope and bounded time/results.
- Privacy: allowlist/redact before console, file, export and subprocess capture.
  Raw command output is excluded if the runner cannot enforce that policy.
- Loss: configured queue/flush bounds and sampling/drop/capture state appear in
  run evidence; receiver outage tests must establish actual bounded behavior.
- Prohibited fields: raw account numbers, invoice details, payer identifiers,
  client names, and raw CSV row values.
- Retention: application logs hot for 14 days; security/audit events retained
  for the pilot audit window.

### Tracing
- Critical journeys: upload CSV, normalize import, generate suggestions,
  accept/reject match, export review log.
- Sampling: sample all failed imports and audit-write failures; baseline sample
  successful review flow at 10%.

## Health Checks

| Check | Endpoint or Mechanism | What It Verifies |
|-------|-----------------------|------------------|
| Liveness | `GET /health/live` | API process is running |
| Readiness | `GET /health/ready` | database reachable, migrations current, object storage reachable |
| Worker readiness | `GET /health/workers` | import worker can claim jobs and write results |
| Audit readiness | synthetic review-decision write in staging | audit writer can persist decision events |

## SLI/SLO Tracking

| Indicator | SLI | SLO |
|-----------|-----|-----|
| Import availability | successful import requests / total valid import requests | 99% during pilot business hours |
| Review availability | successful match queue and decision requests / total requests | 99.5% during pilot business hours |
| Review latency | p95 match queue response time | under 750 ms |
| Audit durability | decisions with audit event / total decisions | 100% |
| Telemetry safety | restricted telemetry violations | 0 |

### Error Budget
- Any audit durability or telemetry safety breach consumes the full pilot error
  budget and blocks further rollout until the runbook action is complete.
- Import/review SLO burn above 25% in a day triggers rollout hold and owner
  review.

## Alert Routing

- Primary: application on-call (DepositMatch on-call engineer).
- Secondary: platform lead.
- Escalation: product owner for pilot-impact decisions; security lead for data
  exposure or control failure.
- Runbook entry point: `docs/helix/05-deploy/runbook.md`.
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Deploy</strong></a> — Ship to users with appropriate operational support, monitoring, and rollback plans.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/05-deploy/monitoring-setup.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Monitoring Setup Generation Prompt&#10;&#10;Create a concise, service-specific monitoring setup for this deployment.&#10;&#10;## Reference Anchors&#10;&#10;Use these local resources as grounding:&#10;&#10;- `docs/resources/google-sre-monitoring-distributed-systems.md` grounds&#10;  operational signals, dashboards, alerting, and the four golden signals.&#10;&#10;## Focus&#10;- Include only the metrics, logs, alerts, dashboards, and tracing needed to operate this service.&#10;- Define measurable thresholds, routing, and escalation where they matter.&#10;- Connect health checks and SLOs to rollout safety and rollback decisions.&#10;- Avoid generic observability boilerplate that does not change operator behavior.&#10;- Separate user-impacting alerts from dashboards that are only for diagnosis.&#10;&#10;## Completion Criteria&#10;- Core metrics and dashboards are defined.&#10;- Alert thresholds and routing are explicit.&#10;- Logging, tracing, and health-check expectations are clear.&#10;- The setup is specific enough to support deployment and incident response.&#10;- Every page-worthy alert has an operator action or runbook entrypoint.&#10;&#10;## OpenTelemetry Diagnostics&#10;&#10;For applicable `o11y-otel` practices, complete Logging from the governing&#10;Contract; do not define a competing schema. Make trace context conditional and&#10;run/attempt correlation independent. Record actual collection route, duplication&#10;control, runner evidence/console policy, pre-sink privacy, retention/access and&#10;sampling/loss/outage/flush behavior. Link bounded retrieval and receiver-proof&#10;evidence. Collector topology follows the deploy target. Do not turn operational&#10;logs into authoritative security audit or billing records.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: monitoring-setup&#10;  authoring:&#10;    home: repo&#10;---&#10;&#10;# Monitoring Setup&#10;&#10;## Service Summary&#10;&#10;- Service: [service name]&#10;- Signals that matter most: [availability, latency, throughput, errors, business KPIs]&#10;&#10;## Metrics Collection&#10;&#10;| Category | Metrics | Notes |&#10;|----------|---------|-------|&#10;| Application | [Latency, throughput, error rate] | [By endpoint or workload if needed] |&#10;| System | [CPU, memory, disk, network] | [Only what affects service health] |&#10;| Business | [KPI names] | [Only if operationally relevant] |&#10;| Custom | [Metric name] | [Why it matters] |&#10;&#10;## Alerting Rules&#10;&#10;| Alert | Condition | Action |&#10;|-------|-----------|--------|&#10;| [Critical alert] | [Page threshold] | [Page path] |&#10;| [Warning alert] | [Notification threshold] | [Notify path] |&#10;&#10;## Dashboards&#10;&#10;| Dashboard | Must Show |&#10;|-----------|-----------|&#10;| Operations | [Health, latency, errors, dependency status] |&#10;| Business | [Adoption or outcome metrics] |&#10;| Technical | [Resource use, queues, caches, jobs] |&#10;&#10;## Logs and Tracing&#10;&#10;### Logging&#10;- Governing telemetry/capture/query Contract: [link; schema/mapping and adopted OTel versions]&#10;- Resource/scope and event coverage: [service/version/environment and required events]&#10;- Trace/span correlation: [valid context when present; absent outside spans]&#10;- Run/attempt correlation: [Contract reference; independent of trace context]&#10;- Collection route: [platform stream, logger bridge or supported managed OTLP; duplication control]&#10;- Local/CI capture and console: [runner owner, evidence location, independent filters, clean protocol stdout]&#10;- Privacy/access: [pre-sink redaction including subprocess capture; query authorization]&#10;- Retention: [local and shared hot/cold retention, rotation/size bounds and deletion]&#10;- Loss policy: [sampling, queue/drop limits, outage/flush behavior and coverage disclosure]&#10;- Query entrypoint: [bounded command/interface; ordering/cursor and evidence references]&#10;&#10;### Tracing&#10;- Critical journeys: [What must be traceable]&#10;- Sampling: [Baseline and overrides]&#10;&#10;## Health Checks&#10;&#10;| Check | Endpoint or Mechanism | What It Verifies |&#10;|-------|-----------------------|------------------|&#10;| Liveness | `GET /health/live` | [Process is running] |&#10;| Readiness | `GET /health/ready` | [Dependencies, capacity, migrations] |&#10;&#10;## SLI/SLO Tracking&#10;&#10;| Indicator | SLI | SLO |&#10;|-----------|-----|-----|&#10;| Availability | [Formula] | [Target] |&#10;| Latency | [Formula] | [Target] |&#10;| Quality | [Formula] | [Target] |&#10;&#10;### Error Budget&#10;- [Budget and escalation thresholds]&#10;&#10;## Alert Routing&#10;&#10;- Primary: [Schedule receiving first page]&#10;- Secondary: [Backup schedule]&#10;- Escalation: [Manager or coordinator path]&#10;- Runbook entry point: [Link to runbook once it exists]</code></pre></details></td></tr>
</tbody>
</table>
