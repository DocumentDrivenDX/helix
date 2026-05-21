# Deployment and DevOps: CRM MVP

This directory contains the complete deployment and DevOps strategy for the CRM MVP, including infrastructure decisions, containerization, CI/CD pipelines, monitoring, backup strategy, and secret management.

## Documents

| Document | Purpose | Audience |
|----------|---------|----------|
| [ADR-004-deployment-and-devops.md](./ADR-004-deployment-and-devops.md) | Architecture decision record covering cloud platform, containerization, CI/CD, monitoring, backups, secrets | Architects, Tech Leads |
| [Dockerfile](./Dockerfile) | Docker image specification for FastAPI backend | DevOps, Backend engineers |
| [docker-compose.yml](./docker-compose.yml) | Local development environment setup (Postgres + API) | Developers |
| [deploy.yml.example](./deploy.yml.example) | GitHub Actions CI/CD workflow (example configuration) | DevOps, CI/CD engineers |
| [HEALTH-CHECK.md](./HEALTH-CHECK.md) | Health check endpoint specification and implementation | Backend engineers, DevOps |
| [MONITORING-AND-LOGGING.md](./MONITORING-AND-LOGGING.md) | Sentry, CloudWatch, and structured logging setup | DevOps, Platform engineers |
| [DATABASE-BACKUP-AND-DR.md](./DATABASE-BACKUP-AND-DR.md) | Backup strategy, restore procedures, and disaster recovery | DevOps, DBA |
| [SECRET-MANAGEMENT.md](./SECRET-MANAGEMENT.md) | AWS Secrets Manager setup, rotation, and best practices | DevOps, Security engineers |

## Quick Reference

### Infrastructure Stack

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Cloud Platform | AWS (us-east-1) | Market standard, team familiarity, single-region MVP |
| Containerization | Docker + ECR | Portability, AWS-native integration |
| Orchestration | ECS Fargate | Simpler than Kubernetes, pay-per-request |
| Database | RDS PostgreSQL 15 | ACID semantics, JSONB support, async ORM ready |
| Load Balancer | ALB (Application Load Balancer) | Layer 7 routing, health checks, HTTPS termination |
| CI/CD | GitHub Actions | Native GitHub integration, free tier sufficient for MVP |

### Deployment Pipeline (CI/CD Stages)

```
main branch push
    ↓
[Lint] (black, isort, flake8, mypy) → ❌ Stop if lint fails
    ↓
[Build] (unit tests with pytest) → ❌ Stop if tests fail
    ↓
[Integration Test] (pytest + PostgreSQL container) → ❌ Stop if tests fail
    ↓
[Build Docker Image] (tag + push to ECR)
    ↓
[Deploy to Staging] (ECS rolling update + smoke tests) → ❌ Stop if smoke tests fail
    ↓
[Monitor Staging] (health checks, latency metrics)
    ↓
[Deploy to Production] (canary: 10% → 50% → 100%, with rollback on errors)
```

**Total Pipeline Duration**: ~15–20 minutes (lint: 3m, tests: 5m, build: 2m, staging: 3m, prod: 2m + monitoring)

### Key Files to Update Before Deployment

1. **AWS Account Setup**:
   - [ ] VPC + subnets created
   - [ ] RDS PostgreSQL instance created
   - [ ] ECR repository created (`crm-api`)
   - [ ] ALB configured with health check (`GET /health`)
   - [ ] ECS cluster + task definition created
   - [ ] IAM roles configured (ECS task role, execution role)

2. **Secrets Manager**:
   - [ ] `crm/prod/db-password` created
   - [ ] `crm/prod/jwt-signing-key` created
   - [ ] `crm/prod/sentry-dsn` created
   - [ ] `crm/prod/email-api-key` created
   - [ ] ECS task role policy attached

3. **GitHub Actions**:
   - [ ] Copy `deploy.yml.example` to `.github/workflows/deploy.yml`
   - [ ] Update AWS account ID in workflow
   - [ ] Add GitHub secrets: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
   - [ ] Update ECS cluster/service names

4. **Application Code**:
   - [ ] Health check endpoint implemented in FastAPI (see [HEALTH-CHECK.md](./HEALTH-CHECK.md))
   - [ ] Sentry integration configured (see [MONITORING-AND-LOGGING.md](./MONITORING-AND-LOGGING.md))
   - [ ] CloudWatch metrics middleware configured
   - [ ] Structured logging setup (JSON format)

### Local Development Setup

```bash
# Clone repo and navigate to deployment directory
cd docs/examples/crm/03-deploy

# Start local database + API
docker-compose up

# Run migrations
docker-compose exec api alembic upgrade head

# Test health endpoint
curl http://localhost:8000/health

# Run tests
docker-compose exec api pytest

# Stop and clean up
docker-compose down
```

### Monitoring and Alerting

**Dashboard**: CloudWatch (14 metrics tracked)
- Request latency (p50/p95/p99)
- Error rate (5xx / total)
- Database latency (p50/p95/p99)
- Database connections (active)
- Task CPU/memory utilization
- Slow query count (>1s)

**Alerts** (triggered on thresholds):
| Alert | Threshold | Duration | Action |
|-------|-----------|----------|--------|
| High error rate | >5% | 2 min | Page oncall |
| High latency | p95 >2000ms | 5 min | Notify team |
| Database down | 0 connections | 1 min | Page oncall |
| Task unhealthy | <1 healthy | 2 min | Auto-restart |

### Backup and Recovery

| Scenario | RPO | RTO | Procedure |
|----------|-----|-----|-----------|
| Accidental data deletion | 24 hours | 15 min | Restore from automated backup |
| Database corruption | 24 hours | 15 min | Point-in-time restore |
| Major incident | 24 hours | 15 min | Restore from snapshot |
| **Multi-AZ failover (P1)** | 0 hours | <1 min | Automatic RDS failover |

**Backup Testing**: Monthly restore drill (first Tuesday, 10:00 AM UTC)

### Secret Management

**Secrets Stored**:
- Database password (auto-rotated every 90 days by AWS)
- JWT signing key (manual rotation if compromised)
- Sentry DSN (manual rotation, rare)
- Email API key (manual rotation per provider policy)

**Access Control**:
- ECS task role: read-only, limited to `crm/prod/*` secrets
- CloudTrail logging: all secret access audited
- Environment variable injection: secrets never logged

### Performance Targets (MVP)

| Target | Baseline | Achievable With |
|--------|----------|-----------------|
| API latency (p95) | <1000ms | Async FastAPI + indexed queries |
| Database latency (p99) | <2000ms | PostgreSQL + proper indexing |
| Error rate | <0.1% | Comprehensive error handling + monitoring |
| Uptime (RDS) | 99.5% | Single-AZ, daily backups (99.95% with Multi-AZ) |
| Deployment time | <20 min | GitHub Actions + ECS rolling update |

### Scaling Path (P1+)

| Phase | Change | Rationale |
|-------|--------|-----------|
| MVP | 1 task, single-AZ RDS, single region | Minimize cost, validate product-market fit |
| P1 | 2–5 tasks + auto-scaling, Multi-AZ RDS | HA, prepare for scale |
| P2 | Multi-region (us-east-1 + eu-west-1), CDN | Global availability |
| P3 | Kubernetes (EKS) if pod count >100 | Complexity justified by scale |

## Checklist: Pre-Launch

**Infrastructure**:
- [ ] VPC, subnets, security groups configured
- [ ] RDS instance created and accessible
- [ ] ECR repository created
- [ ] ALB/ECS cluster/task definition created
- [ ] CloudWatch logs/metrics enabled
- [ ] Secrets Manager secrets created
- [ ] IAM roles and policies configured

**Application**:
- [ ] Health endpoint implemented
- [ ] Sentry integration tested (errors captured)
- [ ] CloudWatch metrics middleware tested
- [ ] Structured logging configured
- [ ] All tests passing (unit + integration)
- [ ] Linting passes (black, isort, flake8, mypy)

**CI/CD**:
- [ ] GitHub Actions workflow copied and configured
- [ ] AWS credentials added to GitHub secrets
- [ ] Staging deployment tested end-to-end
- [ ] Production deployment procedure documented
- [ ] Rollback procedure tested

**Monitoring**:
- [ ] CloudWatch dashboard created
- [ ] Alarms configured (error rate, latency, health)
- [ ] Sentry project configured with proper alerts
- [ ] On-call rotation setup (PagerDuty/OpsGenie)

**Backup & DR**:
- [ ] RDS automated backups enabled (7-day retention)
- [ ] Backup restore procedure documented and tested
- [ ] Monthly backup drill scheduled
- [ ] Disaster recovery runbook written

**Security**:
- [ ] Secrets never in source code
- [ ] TLS certificates provisioned (ACM)
- [ ] CloudTrail logging enabled
- [ ] VPC security groups restricted
- [ ] Database encryption at rest enabled

## Runbook: Common Operations

### Deploy New Version
1. Merge PR to `main`
2. GitHub Actions automatically triggers CI/CD
3. Monitor CloudWatch dashboard during deployment
4. Verify health endpoint returning 200 after 5 minutes
5. Run smoke tests against production

### Investigate High Error Rate
1. Check Sentry dashboard: https://sentry.io/organizations/crm/
2. Filter to recent errors: identify pattern
3. Check CloudWatch logs: search for error context
4. If database error: check RDS slow query log
5. If code error: check recent commits and rollback if needed

### Restore from Backup
1. Restore RDS from snapshot/PITR
2. Run data validation queries (see DATABASE-BACKUP-AND-DR.md)
3. Update ECS task definition with new database URL
4. Restart ECS service
5. Monitor health checks; rollback if issues arise

### Rotate Secrets
1. Update secret in Secrets Manager
2. Force ECS task restart: `aws ecs update-service --force-new-deployment`
3. Verify tasks are healthy
4. Revoke old secret from provider (if applicable)

## References

- ADR-001: [Backend Framework](../02-design/adr/ADR-001-backend-framework.md) (FastAPI)
- ADR-003: [Database & ORM](../02-design/adr/ADR-003-database-orm.md) (PostgreSQL + SQLAlchemy async)
- ADR-005: [Authentication Provider](../02-design/adr/ADR-005-authentication-provider.md)
- PRD: [Product Requirements](../01-frame/prd.md)

## Support

- **DevOps Help**: #devops Slack channel
- **Incident Response**: Page oncall engineer via PagerDuty
- **Documentation**: Refer to MONITORING-AND-LOGGING.md, DATABASE-BACKUP-AND-DR.md, SECRET-MANAGEMENT.md
- **Troubleshooting**: See Runbooks in individual documents (HEALTH-CHECK.md, etc.)
