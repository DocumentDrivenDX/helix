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
