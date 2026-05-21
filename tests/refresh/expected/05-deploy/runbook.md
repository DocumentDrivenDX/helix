---
ddx:
  id: runbook
classification: INCOMPLETE
---

# Runbook - Alignment Service

## Service Summary

- Service or component: alignment-service
- Primary function: Validates and finds drift in HELIX artifacts
- Business impact if degraded: Teams cannot verify artifact alignment; work cannot be validated
- Ownership team: HELIX platform team
- On-call rotation: platform-oncall@example.com
- Environments covered: production, staging

## Operator Entry Points

| Situation | First dashboard, log, or query | First command or check | Owner |
|-----------|--------------------------------|------------------------|-------|
| High error rate | Grafana error dashboard | kubectl logs -f alignment-service | platform-oncall |
| Performance degradation | Prometheus p99 latency graph | kubectl top pods | platform-oncall |
| Pod restart loop | Kubernetes events | kubectl describe pod alignment-service | platform-oncall |

## Dependencies and Failure Boundaries

| Dependency or boundary | Why it matters | Failure signal | Fallback or escalation |
|------------------------|----------------|----------------|------------------------|
| PostgreSQL database | Stores artifact metadata | Connection timeout errors | Use read replica |
| Redis cache | Caches validation results | Cache miss spike | Disable cache layer temporarily |

## Alert Triage

| Alert or symptom | Likely causes | Immediate checks | Stop and escalate when |
|------------------|---------------|------------------|------------------------|
| High error rate | Code regression, dependency failure | Check error logs, check dependencies | Error rate > 5% sustained |
| Latency spike | Slow database queries, cache misses | Check query logs, check cache hit rate | p99 > 5s |
| Pod restarts | OOM killer, signal 9 | Check memory usage, kernel logs | Consistent OOM over time |

## Common Incident Procedures

### Database Connection Failure

- Trigger: Database connection timeout errors in logs
- Immediate actions:
  1. Check database availability on status page
  2. Check network connectivity from pods
  3. Initiate failover to read replica if primary is down
- Validation:
  - Connections recovering
  - Error rate returning to normal
- Escalate to: Database team

### Cache Layer Failure

- Trigger: Redis connection errors or excessive cache misses
- Immediate actions:
  1. Verify Redis service status
  2. Disable cache temporarily (set TTL to 0)
  3. Monitor response time degradation
- Validation:
  - Errors stop occurring
  - Service remains responsive
- Escalate to: Infrastructure team if Redis down

## Rollback and Recovery

### Rollback Entry Conditions

- New deployment introduced errors not seen in staging
- Performance degradation > 50% from baseline
- Data corruption or loss detected

### Rollback Procedure

1. kubectl rollout undo deployment/alignment-service
2. Monitor error rates and latency metrics
3. Verify previous version stability

### Recovery Validation

- Error rate < 1%
- p99 latency < 200ms
- All database connections healthy

## Routine Operations

| Operation | Trigger or cadence | Command or workflow | Verification |
|-----------|--------------------|---------------------|--------------|
| Cache warmup | Daily at 6am UTC | ./scripts/warm-cache.sh | Cache hit rate > 90% |
| Database optimization | Weekly maintenance window | REINDEX artifacts; VACUUM; | Query time < 100ms |
| Log rotation | Daily | logrotate /etc/logrotate.d/alignment | Logs not exceeding quota |

## Escalation and Communications

1. Primary on-call: platform-oncall@example.com (PagerDuty rotation)
2. Secondary escalation: @platform-team in Slack #incidents
3. Incident coordinator: incident-commander@example.com
4. Vendor support: AWS Support (SLA: 1 hour for production)

## References

- Deployment checklist: docs/helix/05-deploy/deployment-checklist.md
- Monitoring setup: docs/helix/05-deploy/monitoring-setup.md
- Architecture: docs/helix/02-design/architecture.md
- Security: docs/helix/02-design/security-architecture.md
