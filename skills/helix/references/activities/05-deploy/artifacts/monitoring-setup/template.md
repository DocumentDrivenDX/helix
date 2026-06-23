---
ddx:
  id: monitoring-setup
---

# Monitoring Setup

## Service Summary

- Service: [service name]
- Signals that matter most: [availability, latency, throughput, errors, business KPIs]

## Metrics Collection

| Category | Metrics | Notes |
|----------|---------|-------|
| Application | [Latency, throughput, error rate] | [By endpoint or workload if needed] |
| System | [CPU, memory, disk, network] | [Only what affects service health] |
| Business | [KPI names] | [Only if operationally relevant] |
| Custom | [Metric name] | [Why it matters] |

## Alerting Rules

| Alert | Condition | Action |
|-------|-----------|--------|
| [Critical alert] | [Page threshold] | [Page path] |
| [Warning alert] | [Notification threshold] | [Notify path] |

## Dashboards

| Dashboard | Must Show |
|-----------|-----------|
| Operations | [Health, latency, errors, dependency status] |
| Business | [Adoption or outcome metrics] |
| Technical | [Resource use, queues, caches, jobs] |

## Logs and Tracing

### Logging
- Required fields: `timestamp`, `level`, `service`, `trace_id`, `message`
- Retention: [hot and cold retention]

### Tracing
- Critical journeys: [What must be traceable]
- Sampling: [Baseline and overrides]

## Health Checks

| Check | Endpoint or Mechanism | What It Verifies |
|-------|-----------------------|------------------|
| Liveness | `GET /health/live` | [Process is running] |
| Readiness | `GET /health/ready` | [Dependencies, capacity, migrations] |

## SLI/SLO Tracking

| Indicator | SLI | SLO |
|-----------|-----|-----|
| Availability | [Formula] | [Target] |
| Latency | [Formula] | [Target] |
| Quality | [Formula] | [Target] |

### Error Budget
- [Budget and escalation thresholds]

## Alert Routing

- Primary: [Schedule receiving first page]
- Secondary: [Backup schedule]
- Escalation: [Manager or coordinator path]
- Runbook entry point: [Link to runbook once it exists]
