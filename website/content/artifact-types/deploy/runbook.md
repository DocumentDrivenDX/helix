---
title: "Runbook"
linkTitle: "Runbook"
slug: runbook
activity: "Deploy"
artifactRole: "supporting"
weight: 13
generated: true
---

## Purpose

Service-specific operational procedures for on-call response, rollback,
recovery, and routine maintenance tied to a deployed system.

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: example.runbook.depositmatch
  depends_on:
    - example.deployment-checklist.depositmatch.csv-import
    - example.monitoring-setup.depositmatch
    - example.security-architecture.depositmatch
  review:
    self_hash: 1f52bd1ba196f06837695269f3fee1829dd734eeccdb0ea4274c86c895270229
    deps:
      example.deployment-checklist.depositmatch.csv-import: 02e9e7c9c29b4a335e0e2eceacaaaa6673018042db2a706f89293ab6f58abcbf
      example.monitoring-setup.depositmatch: cd2e8ecd82900c19affde80ab89f2ad3e7f5ff19ab3956a8da5dcee8e710b4af
      example.security-architecture.depositmatch: eefd2c6eed5574e8d2960a55ec226b7e55bd7b09b6131dc02295047c163f13b7
    reviewed_at: "2026-05-15T04:11:24Z"
---

# Runbook - DepositMatch CSV-First Pilot

## Service Summary

- Service or component: DepositMatch API, import worker, and review UI.
- Primary function: import bank CSVs, suggest invoice/payment matches, record
  reviewer decisions, and export review logs.
- Business impact if degraded: accountants cannot complete reconciliation work;
  audit trail may become incomplete if decision writes fail.
- Ownership team: DepositMatch pilot team.
- On-call rotation: application on-call.
- Environments covered: staging and pilot production.

## Operator Entry Points

| Situation | First dashboard, log, or query | First command or check | Owner |
|-----------|--------------------------------|------------------------|-------|
| Import pipeline unavailable | Operations dashboard, import queue panel | `npm run ops:import-health` | application on-call |
| Review decision audit failure | Security Controls dashboard, audit writer logs | `npm run ops:audit-health` | application on-call |
| Restricted telemetry violation | Security Controls dashboard, log scan alert | `npm run ops:telemetry-scan -- --last=30m` | security lead |
| Cross-tenant authorization anomaly | Security Controls dashboard, authz denial logs | `npm run ops:actor-events -- <actor_id>` | security lead |
| Support access outside window | support grant audit log | `npm run ops:support-grants -- --active` | security lead |

## Dependencies and Failure Boundaries

| Dependency or boundary | Why it matters | Failure signal | Fallback or escalation |
|------------------------|----------------|----------------|------------------------|
| PostgreSQL | stores normalized records, matches, and audit events | readiness failure, audit write error, connection saturation | pause imports and review decisions; escalate to platform lead |
| Object storage | stores temporary source CSVs during retention window | storage error on import or export | disable imports and exports; preserve existing objects |
| Identity provider | authenticates firm staff and support users | login failures, token validation errors | escalate to platform lead; do not bypass auth |
| Firm/client authorization boundary | prevents cross-tenant data exposure | unexpected 200 for another firm/client scope | disable affected endpoint and preserve logs |
| Telemetry/log pipeline | must not receive restricted values | restricted-field alert | stop affected job or endpoint and rotate affected logs |

## Alert Triage

| Alert or symptom | Likely causes | Immediate checks | Stop and escalate when |
|------------------|---------------|------------------|------------------------|
| Import pipeline unavailable | bad deploy, parser crash, worker stuck, database saturation | import queue depth, worker logs, latest deploy, readiness check | queue stalled over 30 minutes or customer work blocked |
| Review decision audit failure | audit writer regression, database issue, schema mismatch | audit writer logs, decision endpoint errors, migration status | any accepted/rejected decision lacks an audit event |
| Restricted telemetry violation | logging regression, fixture leak, unsafe analytics event | telemetry scan output, latest deploy diff, affected trace IDs | any raw financial value appears in logs/events |
| Cross-tenant authorization anomaly | probing actor, authorization regression, bad test data | actor event history, endpoint logs, latest authz changes | any cross-tenant data is returned |

## Common Incident Procedures

### Import Pipeline Unavailable

- Trigger: import queue is stalled, import 5xx rate exceeds alert threshold, or
  customers cannot upload valid CSVs.
- Immediate actions:
  1. Check `Operations > Import Diagnostics` and latest deploy.
  2. Run `npm run ops:import-health`.
  3. If workers are stuck, restart import workers once.
  4. If errors continue, disable import through `FEATURE_IMPORTS=false`.
- Validation:
  - `GET /health/workers` passes.
  - Import queue drains for the latest pilot customer.
  - Error rate returns below alert threshold for 15 minutes.
- Escalate to: platform lead if database or storage health is degraded.

### Review Decision Audit Failure

- Trigger: any accepted or rejected match decision fails to produce an audit
  event.
- Immediate actions:
  1. Disable review decisions through `FEATURE_REVIEW_DECISIONS=false`.
  2. Preserve audit writer logs and affected trace IDs.
  3. Run `npm run ops:audit-health`.
  4. Compare latest migration and application version.
- Validation:
  - synthetic staging decision writes one append-only audit event.
  - production decision endpoint remains disabled until fix is deployed.
- Escalate to: product owner and security lead.

### Restricted Telemetry or Data Exposure

- Trigger: telemetry alert finds raw bank account numbers, invoice details,
  payer identifiers, client names, or raw CSV row values.
- Immediate actions:
  1. Preserve affected logs, trace IDs, and deploy SHA.
  2. Disable the suspected import, export, or analytics path.
  3. Run `npm run ops:telemetry-scan -- --last=24h`.
  4. Start security incident coordination before deleting or rotating evidence.
- Validation:
  - no new restricted-field alerts for 30 minutes.
  - security lead confirms evidence was preserved.
- Escalate to: security lead, incident coordinator, and product/legal owner.

## Rollback and Recovery

### Rollback Entry Conditions

- audit writer failure in production.
- confirmed cross-tenant data response.
- restricted telemetry violation introduced by latest deploy.
- import pipeline unavailable for more than 30 minutes after one worker restart.

### Rollback Procedure

1. Announce rollback in the pilot incident channel.
2. Record current deploy SHA, alert, and affected feature flags.
3. Run `npm run deploy:rollback -- --service=depositmatch`.
4. Keep import/review feature flags disabled until validation passes.
5. Verify previous version and migrations are compatible.

### Recovery Validation

- readiness and worker health checks pass.
- import and review smoke tests pass in staging.
- production error rate remains below threshold for 15 minutes.
- no audit, authorization, or telemetry alerts fire after rollback.

## Routine Operations

| Operation | Trigger or cadence | Command or workflow | Verification |
|-----------|--------------------|---------------------|--------------|
| Rotate support grants | weekly or after incident | `npm run ops:support-grants -- --expire-stale` | no expired active grants |
| Re-run telemetry scan | daily during pilot | `npm run ops:telemetry-scan -- --last=24h` | report shows zero restricted fields |
| Export pilot audit bundle | end of pilot or customer request | `npm run ops:audit-export -- <firm_id>` | export event appears in audit log |

## Escalation and Communications

1. Primary on-call: application on-call.
2. Secondary escalation: platform lead.
3. Incident coordinator or manager: product owner for pilot-impact decisions.
4. Security escalation: security lead for data exposure, support-access, or
   authorization incidents.
5. External dependency or vendor support: identity provider and hosting support
   through platform account.

## References

- Deployment checklist: `docs/helix/05-deploy/deployment-checklist.md`
- Monitoring setup: `docs/helix/05-deploy/monitoring-setup.md`
- Architecture: `docs/helix/02-design/architecture.md`
- Security architecture: `docs/helix/02-design/security-architecture.md`
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="/reference/glossary/activities/"><strong>Deploy</strong></a> — Ship to users with appropriate operational support, monitoring, and rollback plans.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/05-deploy/runbook.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>HELIX documents</th><td><a href="https://github.com/DocumentDrivenDX/helix/blob/main/docs/helix/05-deploy/runbook.md"><code>docs/helix/05-deploy/runbook.md</code></a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Runbook Prompt

Create a service-specific operational runbook for one deployed system.

## Required Inputs
- deployment checklist or rollout entrypoints
- monitoring setup, dashboards, and alert routing
- architecture or dependency boundaries
- on-call ownership and escalation expectations
- security-response constraints, if the service has them

## Reference Anchors

Use these local resource summaries as grounding:

- `docs/resources/google-sre-incident-management-guide.md` grounds alert
  response, ownership, escalation, mitigation, and follow-up.
- `docs/resources/google-sre-release-engineering.md` grounds rollback and
  release-control procedures.

## Produced Output
- `docs/helix/05-deploy/runbook.md`

## Focus

Keep the runbook executable during an incident or maintenance window. Include
only the checks, commands, decisions, and escalation paths that are specific
to this service.

Differentiate the runbook from adjacent deploy artifacts:

- `deployment-checklist` decides whether a release can proceed
- `monitoring-setup` defines signals, dashboards, and alerts
- `runbook` explains what operators do when those signals fire or when
  rollback, recovery, or routine maintenance is required

Map alerts or symptoms to first checks, dashboards, commands, and next
decisions. Include rollback and recovery steps with prerequisites, stop
conditions, and validation. Include recurring operational procedures only when
somebody actually performs them.
Preserve evidence before destructive containment when security or data exposure
is possible.

Do not produce a generic SRE handbook, sample vendor command dump, or broad
release coordination plan.

## Completion Criteria
- [ ] Operator entry points map situations to first checks, commands, and owners
- [ ] Alert triage is tied to concrete dashboards, logs, or commands
- [ ] Rollback and recovery steps include prerequisites, stop conditions, and validation
- [ ] Routine operational procedures are explicit or the document says none exist
- [ ] Escalation and communication paths are explicit

Use the template at `workflows/activities/05-deploy/artifacts/runbook/template.md`.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---
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
- Security architecture or policy, if applicable: [link]</code></pre></details></td></tr>
</tbody>
</table>
