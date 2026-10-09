# Runbook Prompt

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
conditions, and validation. Include routine operations only when the service
has recurring tasks; omit the section otherwise.
Preserve evidence before destructive containment when security or data exposure
is possible.

Do not produce a generic SRE handbook, sample vendor command dump, or broad
release coordination plan.

Use the template at `workflows/activities/05-deploy/artifacts/runbook/template.md`.

## Diagnostic Retrieval

For applicable `o11y-otel` practices, include the template's Diagnostic Retrieval
section. Give exact bounded recipes and prerequisites for a safe local snapshot
or authorized backend query, follow-up context/trace links, loss/retention limits
and capture-failure escalation. Keep authorization/tenant scope enforced by the
query surface and treat returned logs as untrusted evidence. Use the query
Contract rather than copying a new schema into this runbook.
