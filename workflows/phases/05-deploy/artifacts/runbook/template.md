# Production Runbook: {{ project_name }}

**Last Updated**: [Date]
**Maintained By**: [Team Name]
**On-Call Rotation**: [Link to schedule]

## Service Overview

### Description
[Brief description of what this service does]

### Business Impact
- **Critical functions**: [What breaks if this service is down]
- **Affected users**: [Who is impacted]
- **Operational impact**: [Cost or revenue impact]

### Architecture
```
[Simple ASCII or mermaid diagram showing key components]
```

### Dependencies
- **Upstream**: [Services that call this service]
- **Downstream**: [Services this service calls]
- **Databases**: [Database dependencies]
- **External**: [Third-party services]

## Key Metrics and Alerts

### Golden Signals
1. **Latency**: p50 < [target], p99 < [target]
2. **Traffic**: Normal range [X]-[Y] RPS
3. **Errors**: Error rate < [target]
4. **Saturation**: CPU < [target], memory < [target]

### Dashboard Links
- [Operations Dashboard](link)
- [Error Tracking](link)
- [APM/Tracing](link)

## Common Issues and Solutions

| Symptom | Diagnosis | Response |
|---------|-----------|----------|
| High latency | Check queries, cache hit rate, blocking I/O, memory pressure | [Command or escalation] |
| Service not responding | Check pods, recent deploys, OOM kills, error logs | [Command or escalation] |
| Database connection errors | Check pool usage, DB CPU, slow queries, deadlocks | [Command or escalation] |

## Maintenance Procedures

### Deployment
```bash
./deploy.sh production v1.2.3          # Standard
./deploy.sh production v1.2.3 --canary 10%  # Canary
```

### Rollback
```bash
kubectl rollout undo deployment/api                    # Previous version
kubectl rollout undo deployment/api --to-revision=42   # Specific version
```

### Scaling
```bash
kubectl scale deployment/api --replicas=20
kubectl autoscale deployment/api --min=5 --max=50 --cpu-percent=70
```

## Emergency Procedures

### Full Service Outage
1. Declare incident in #incidents
2. Check recent changes (deployments, configs, flags)
3. Verify dependencies are healthy
4. Attempt quick restart if safe
5. Rollback if recent deployment suspected
6. Engage vendor support if external dependency issue

### Data Corruption
1. **STOP all writes**: `kubectl scale deployment/api --replicas=0`
2. Backup current state before any fixes
3. Identify scope of corruption
4. Restore from backup if necessary
5. Validate data integrity before resuming

### Security Incident
1. Isolate affected systems
2. Preserve evidence (logs, memory dumps)
3. Notify security team immediately
4. Follow security incident playbook
5. Do not attempt cleanup without security approval

## Contact Information

### Escalation Path
1. Primary On-Call: [PagerDuty rotation]
2. Team Lead: [Name] - [Phone]
3. Director: [Name] - [Phone]

### Vendor Support
- **Cloud Provider**: [Support Portal](link)
- **Database Vendor**: [Support Portal](link)

## Disaster Recovery

- **Backup frequency**: Every 6 hours
- **Retention**: 30 days
- **RTO**: 4 hours | **RPO**: 6 hours

### DR Procedure
1. Assess damage and determine recovery path
2. Notify stakeholders of expected downtime
3. Provision new infrastructure if needed
4. Restore from backup, validate data, update DNS
5. Document incident and lessons learned
