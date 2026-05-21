---
classification: INCOMPLETE
---

# Runbook - Alignment Service

## Service Summary

- Service: alignment-service
- Primary function: Validates and finds drift in HELIX artifacts
- Business impact: If down, teams cannot verify artifact alignment
- Ownership team: HELIX platform
- On-call rotation: platform-oncall@example.com
- Environments: production, staging

## Operator Entry Points

| Situation | Dashboard | First Command | Owner |
|-----------|-----------|----------------|-------|
| High error rate | Grafana error dashboard | kubectl logs alignment-service | platform-oncall |
| Performance degradation | Prometheus p99 latency | kubectl top pods | platform-oncall |
| Pod restart loop | Kubernetes events | kubectl describe pod | platform-oncall |

## Dependencies

| Dependency | Why | Failure Signal | Fallback |
|------------|-----|----------------|----------|
| Postgres | Stores artifact metadata | Connection timeout | Use replica |
| Redis | Caches validation results | Cache misses spike | Disable cache temporarily |

## Alert Triage

| Alert | Likely Causes | Check | Escalate When |
|-------|---------------|-------|----------------|
| High error rate | Code bug, dependency failure | Check logs | Error rate > 5% |
| Pod restarts | OOM, signal 9 | Check memory usage | Consistent OOM |
