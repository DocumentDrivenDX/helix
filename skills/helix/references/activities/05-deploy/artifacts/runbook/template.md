---
ddx:
  id: runbook
---

# Runbook - [Service / System]

## Service Summary

- Service or component: [name]
- Primary function: [what it does]
- Business impact if degraded: [who is affected and how]
- Ownership team: [team]
- On-call rotation: [link or contact]
- Environments covered: [production, staging, regional variants]

## Operator Entry Points

| Situation | First dashboard, log, or query | First command or check | Owner |
|-----------|--------------------------------|------------------------|-------|
| [rollout regression] | [dashboard or log] | [command or query] | [name or role] |
| [service degradation] | [dashboard or log] | [command or query] | [name or role] |
| [dependency failure] | [dashboard or log] | [command or query] | [name or role] |

## Dependencies and Failure Boundaries

| Dependency or boundary | Why it matters | Failure signal | Fallback or escalation |
|------------------------|----------------|----------------|------------------------|
| [database, queue, third-party API] | [impact] | [signal] | [action] |
| [critical upstream or downstream] | [impact] | [signal] | [action] |

## Alert Triage

| Alert or symptom | Likely causes | Immediate checks | Stop and escalate when |
|------------------|---------------|------------------|------------------------|
| [high error rate] | [deploy, dependency, config] | [dashboard, logs, health check] | [condition] |
| [latency spike] | [capacity, dependency, hot path] | [dashboard, trace, query] | [condition] |
| [queue growth or saturation] | [worker failure, downstream slowness] | [dashboard, queue depth check] | [condition] |

## Common Incident Procedures

### [Incident Name]

- Trigger: [how you know this procedure applies]
- Immediate actions:
  1. [first safe action]
  2. [second safe action]
  3. [containment or mitigation]
- Validation:
  - [signal proving recovery]
  - [signal proving rollback or mitigation worked]
- Escalate to: [role, team, or vendor]

### [Security or Data-Safety Incident]

- Trigger: [alert, report, or symptom]
- Immediate actions:
  1. [containment]
  2. [evidence preservation]
  3. [notification or coordination]
- Validation:
  - [proof the service is safe or contained]
- Escalate to: [security owner or incident commander]

## Rollback and Recovery

### Rollback Entry Conditions

- [condition that requires rollback]
- [condition that requires holding rollout]

### Rollback Procedure

1. [rollback entrypoint or command]
2. [stabilize traffic, config, or workers]
3. [verify previous version or safe state]

### Recovery Validation

- [health check, dashboard, or user journey]
- [error-rate or latency threshold]
- [dependency confirmation]

## Routine Operations

| Operation | Trigger or cadence | Command or workflow | Verification |
|-----------|--------------------|---------------------|--------------|
| [key rotation, replay, cache warmup] | [when it happens] | [command or steps] | [proof] |
| [backup or maintenance task] | [when it happens] | [command or steps] | [proof] |

If no recurring operational tasks exist, state that explicitly and point to the
systems that own them instead.

## Escalation and Communications

1. Primary on-call: [name, rotation, or channel]
2. Secondary escalation: [name, team, or channel]
3. Incident coordinator or manager: [name, team, or channel]
4. External dependency or vendor support: [link, account, or contact]

## References

- Deployment checklist: [link]
- Monitoring setup: [link]
- Architecture or dependency map: [link]
- Security architecture or policy, if applicable: [link]
