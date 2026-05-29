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
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Deploy</strong></a> — Ship to users with appropriate operational support, monitoring, and rollback plans.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/05-deploy/runbook.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>HELIX documents</th><td><a href="https://github.com/DocumentDrivenDX/helix/blob/main/docs/helix/05-deploy/runbook.md"><code>docs/helix/05-deploy/runbook.md</code></a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Runbook Prompt&#10;&#10;Create a service-specific operational runbook for one deployed system.&#10;&#10;## Required Inputs&#10;- deployment checklist or rollout entrypoints&#10;- monitoring setup, dashboards, and alert routing&#10;- architecture or dependency boundaries&#10;- on-call ownership and escalation expectations&#10;- security-response constraints, if the service has them&#10;&#10;## Reference Anchors&#10;&#10;Use these local resource summaries as grounding:&#10;&#10;- `docs/resources/google-sre-incident-management-guide.md` grounds alert&#10;  response, ownership, escalation, mitigation, and follow-up.&#10;- `docs/resources/google-sre-release-engineering.md` grounds rollback and&#10;  release-control procedures.&#10;&#10;## Produced Output&#10;- `docs/helix/05-deploy/runbook.md`&#10;&#10;## Focus&#10;&#10;Keep the runbook executable during an incident or maintenance window. Include&#10;only the checks, commands, decisions, and escalation paths that are specific&#10;to this service.&#10;&#10;Differentiate the runbook from adjacent deploy artifacts:&#10;&#10;- `deployment-checklist` decides whether a release can proceed&#10;- `monitoring-setup` defines signals, dashboards, and alerts&#10;- `runbook` explains what operators do when those signals fire or when&#10;  rollback, recovery, or routine maintenance is required&#10;&#10;Map alerts or symptoms to first checks, dashboards, commands, and next&#10;decisions. Include rollback and recovery steps with prerequisites, stop&#10;conditions, and validation. Include recurring operational procedures only when&#10;somebody actually performs them.&#10;Preserve evidence before destructive containment when security or data exposure&#10;is possible.&#10;&#10;Do not produce a generic SRE handbook, sample vendor command dump, or broad&#10;release coordination plan.&#10;&#10;## Completion Criteria&#10;- [ ] Operator entry points map situations to first checks, commands, and owners&#10;- [ ] Alert triage is tied to concrete dashboards, logs, or commands&#10;- [ ] Rollback and recovery steps include prerequisites, stop conditions, and validation&#10;- [ ] Routine operational procedures are explicit or the document says none exist&#10;- [ ] Escalation and communication paths are explicit&#10;&#10;Use the template at `workflows/activities/05-deploy/artifacts/runbook/template.md`.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: runbook&#10;---&#10;&#10;# Runbook - [Service / System]&#10;&#10;## Service Summary&#10;&#10;- Service or component: [name]&#10;- Primary function: [what it does]&#10;- Business impact if degraded: [who is affected and how]&#10;- Ownership team: [team]&#10;- On-call rotation: [link or contact]&#10;- Environments covered: [production, staging, regional variants]&#10;&#10;## Operator Entry Points&#10;&#10;| Situation | First dashboard, log, or query | First command or check | Owner |&#10;|-----------|--------------------------------|------------------------|-------|&#10;| [rollout regression] | [dashboard or log] | [command or query] | [name or role] |&#10;| [service degradation] | [dashboard or log] | [command or query] | [name or role] |&#10;| [dependency failure] | [dashboard or log] | [command or query] | [name or role] |&#10;&#10;## Dependencies and Failure Boundaries&#10;&#10;| Dependency or boundary | Why it matters | Failure signal | Fallback or escalation |&#10;|------------------------|----------------|----------------|------------------------|&#10;| [database, queue, third-party API] | [impact] | [signal] | [action] |&#10;| [critical upstream or downstream] | [impact] | [signal] | [action] |&#10;&#10;## Alert Triage&#10;&#10;| Alert or symptom | Likely causes | Immediate checks | Stop and escalate when |&#10;|------------------|---------------|------------------|------------------------|&#10;| [high error rate] | [deploy, dependency, config] | [dashboard, logs, health check] | [condition] |&#10;| [latency spike] | [capacity, dependency, hot path] | [dashboard, trace, query] | [condition] |&#10;| [queue growth or saturation] | [worker failure, downstream slowness] | [dashboard, queue depth check] | [condition] |&#10;&#10;## Common Incident Procedures&#10;&#10;### [Incident Name]&#10;&#10;- Trigger: [how you know this procedure applies]&#10;- Immediate actions:&#10;  1. [first safe action]&#10;  2. [second safe action]&#10;  3. [containment or mitigation]&#10;- Validation:&#10;  - [signal proving recovery]&#10;  - [signal proving rollback or mitigation worked]&#10;- Escalate to: [role, team, or vendor]&#10;&#10;### [Security or Data-Safety Incident]&#10;&#10;- Trigger: [alert, report, or symptom]&#10;- Immediate actions:&#10;  1. [containment]&#10;  2. [evidence preservation]&#10;  3. [notification or coordination]&#10;- Validation:&#10;  - [proof the service is safe or contained]&#10;- Escalate to: [security owner or incident commander]&#10;&#10;## Rollback and Recovery&#10;&#10;### Rollback Entry Conditions&#10;&#10;- [condition that requires rollback]&#10;- [condition that requires holding rollout]&#10;&#10;### Rollback Procedure&#10;&#10;1. [rollback entrypoint or command]&#10;2. [stabilize traffic, config, or workers]&#10;3. [verify previous version or safe state]&#10;&#10;### Recovery Validation&#10;&#10;- [health check, dashboard, or user journey]&#10;- [error-rate or latency threshold]&#10;- [dependency confirmation]&#10;&#10;## Routine Operations&#10;&#10;| Operation | Trigger or cadence | Command or workflow | Verification |&#10;|-----------|--------------------|---------------------|--------------|&#10;| [key rotation, replay, cache warmup] | [when it happens] | [command or steps] | [proof] |&#10;| [backup or maintenance task] | [when it happens] | [command or steps] | [proof] |&#10;&#10;If no recurring operational tasks exist, state that explicitly and point to the&#10;systems that own them instead.&#10;&#10;## Escalation and Communications&#10;&#10;1. Primary on-call: [name, rotation, or channel]&#10;2. Secondary escalation: [name, team, or channel]&#10;3. Incident coordinator or manager: [name, team, or channel]&#10;4. External dependency or vendor support: [link, account, or contact]&#10;&#10;## References&#10;&#10;- Deployment checklist: [link]&#10;- Monitoring setup: [link]&#10;- Architecture or dependency map: [link]&#10;- Security architecture or policy, if applicable: [link]</code></pre></details></td></tr>
</tbody>
</table>
