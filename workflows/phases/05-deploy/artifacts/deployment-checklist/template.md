# Deployment Checklist

**Project**: {{ project_name }}
**Version**: [Version Number]
**Date**: [Deployment Date]
**Deploy Lead**: [Name]

## Pre-Deployment

### Code Readiness
- [ ] CI passing
- [ ] Security scan clean
- [ ] Review approved
- [ ] Performance baseline met

### Configuration
- [ ] Env vars and secrets ready
- [ ] Feature flags configured
- [ ] Migrations tested
- [ ] External credentials verified

### Communication
- [ ] Release notes ready
- [ ] Support and stakeholders briefed

## Deployment Process

### Staging Validation
- [ ] Staging deployment successful
- [ ] Smoke tests passing
- [ ] Monitoring verified
- [ ] Rollback tested

### Production Deployment

#### Preparation
- [ ] Backup complete
- [ ] Rollback confirmed
- [ ] Dashboards ready
- [ ] On-call available

#### Rollout
- [ ] Canary or phased rollout complete
- [ ] Error rate and latency monitored
- [ ] Rollout reaches 100%
- [ ] Final verification complete

#### Validation
- [ ] Production smoke tests pass
- [ ] Critical journeys verified
- [ ] No regression in errors or latency

## Rollback Criteria

Initiate rollback if:
- Error rate exceeds [threshold] for [duration]
- Latency exceeds [threshold] for [duration]
- Critical functionality breaks
- Data integrity is at risk

## Rollback Procedure

1. Incident commander decides rollback
2. Notify stakeholders
3. Execute rollback automation
4. Verify system restored
5. Root cause analysis

## Release Metadata

- Build ID: [Build Number]
- Git SHA: [Commit Hash]
- Rollback Build: [Previous Build ID]
