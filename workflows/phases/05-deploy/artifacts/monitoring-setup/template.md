# Monitoring Setup

## Overview
Monitoring configuration for {{ project_name }} production deployment.

## Metrics Collection

### Application Metrics
- **Response time**: p50, p95, p99
- **Throughput**: requests per second by endpoint
- **Error rate**: 4xx and 5xx by type
- **Business metrics**: [Define specific KPIs]

### System Metrics
- **CPU and memory**: average and peak utilization
- **Disk I/O**: read/write operations, latency
- **Network**: bandwidth, connection pool usage

### Custom Metrics
```yaml
metrics:
  - name: [metric_name]
    type: counter|gauge|histogram
    description: [what this measures]
    labels: [dimensions for aggregation]
```

## Alerting Rules

### Critical Alerts (Page immediately)
| Alert | Condition | Action |
|-------|-----------|--------|
| Service Down | Health check fails 3x in 1 min | Page on-call |
| High Error Rate | 5xx > 1% for 5 min | Page on-call |
| Data Loss Risk | Queue backup > 10K messages | Page on-call |

### Warning Alerts (Notify team)
| Alert | Condition | Action |
|-------|-----------|--------|
| High Latency | p95 > 1s for 10 min | Slack notification |
| Memory Pressure | Heap > 80% for 15 min | Email team |
| Disk Space | < 20% free | Create ticket |

## Dashboards

### Operations Dashboard
- Service health, request rate/latency, error rate, active users, database performance

### Business Dashboard
- User engagement, feature adoption, transaction volume, revenue, conversion funnel

### Technical Dashboard
- Resource utilization, dependency health, cache hit rates, queue depth, background jobs

## Log Aggregation

### Structured Logging
```json
{
  "timestamp": "ISO-8601",
  "level": "ERROR|WARN|INFO|DEBUG",
  "service": "service-name",
  "trace_id": "correlation-id",
  "message": "human-readable",
  "context": {}
}
```

### Log Retention
- Production: 30 days hot, 1 year cold

## Health Checks

### Liveness: `GET /health/live` -> 200 OK
### Readiness: `GET /health/ready` -> 200 OK | 503
Checks: database, cache, dependencies

## Tracing

- Trace critical user journeys and cross-service calls
- Sampling: Production 1% baseline, 100% errors | Staging 10% | Dev 100%

## SLI/SLO Tracking

| Indicator | SLI | SLO |
|-----------|-----|-----|
| Availability | Successful / Total requests | 99.9% monthly |
| Latency | Requests under 1s / Total | 95% under 1s |
| Quality | Successful transactions / Total | 99% success |

### Error Budget
- Monthly budget: 0.1% (43.8 minutes)
- Alert at 50% consumed, freeze features at 80%

## Incident Response

### Runbook Links
- [Service restart], [Database issues], [High latency], [Rollback procedure]

### On-Call Rotation
- Primary: [Schedule]
- Secondary: [Schedule]
- Escalation: [Manager]
