---
ddx:
  id: example.monitoring-setup.depositmatch
  depends_on:
    - example.deployment-checklist.depositmatch.csv-import
    - example.security-architecture.depositmatch
    - example.metric-definition.depositmatch.csv-import-validation-seconds
  review:
    self_hash: cd2e8ecd82900c19affde80ab89f2ad3e7f5ff19ab3956a8da5dcee8e710b4af
    deps:
      example.deployment-checklist.depositmatch.csv-import: 02e9e7c9c29b4a335e0e2eceacaaaa6673018042db2a706f89293ab6f58abcbf
      example.metric-definition.depositmatch.csv-import-validation-seconds: a1bb2128a1335ff7b306902f4bc6ab433468c93f567943535c641fa2e53d617e
      example.security-architecture.depositmatch: eefd2c6eed5574e8d2960a55ec226b7e55bd7b09b6131dc02295047c163f13b7
    reviewed_at: "2026-05-15T04:11:24Z"
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
- Required fields: `timestamp`, `level`, `service`, `trace_id`, `firm_id`,
  `client_id`, `actor_id`, `event_type`, `import_id` where applicable.
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
