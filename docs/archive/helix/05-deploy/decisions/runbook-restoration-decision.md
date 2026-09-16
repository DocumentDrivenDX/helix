# Runbook — Restoration Decision

> Historical decision; superseded by the worked example at `docs/helix/05-deploy/runbook.md`.

`runbook` is restored as the canonical deploy-activity artifact for
service-specific on-call response, rollback, recovery, and routine operating
procedures.

## Decision

This artifact is restored rather than retired.

Current HELIX still requires `docs/helix/05-deploy/runbook.md` in the deploy
exit gate, checks it for rollback guidance, and references it from the live
deploy artifact surface in `workflows/DDX.md`, `workflows/conventions.md`,
`workflows/diagrams/artifact-flow.md`, `deployment-checklist`, and
`monitoring-setup`. The intent therefore still exists in the current contract.

## Why It Exists

- `deployment-checklist` is the short go/no-go surface for a release.
- `monitoring-setup` defines the signals, dashboards, and alerts operators use.
- `runbook` explains what operators do when those signals fire or when a
  routine operational task must be executed safely.
- Tracker issues record rollout work, but they do not replace durable,
  service-specific procedures that on-call responders need during incidents,
  rollback, or recovery.

## Canonical Inputs

- deployment checklist and rollback entrypoints
- monitoring setup, dashboards, and alert routing
- architecture and dependency boundaries
- on-call ownership and escalation paths
- service-specific recovery and maintenance procedures

## Minimum Prompt Bar

- Keep the runbook service-specific, concise, and executable during real
  incidents or maintenance windows.
- Map concrete alerts or symptoms to first checks, commands, dashboards, and
  owners rather than writing generic advice.
- Include rollback and recovery procedures with prerequisites, stop conditions,
  and validation steps.
- Include only recurring operational procedures that somebody is actually
  expected to perform.
- Distinguish the runbook from `deployment-checklist` and `monitoring-setup`
  instead of duplicating those artifacts.
- Include security or data-safety response only when the service has
  service-specific handling beyond a shared organization playbook.
- Omit generic SRE handbook filler, sample vendor commands, and broad launch
  coordination tasks.

## Minimum Template Bar

- service summary and ownership
- operator entry points
- dependencies and failure boundaries
- alert triage table
- common incident procedures
- rollback and recovery steps
- routine operations or maintenance
- escalation and communications

## Canonical Replacement Status

`runbook` is not replaced by `deployment-checklist` or `monitoring-setup`.
Those artifacts define release decision points and observability configuration;
the runbook is the durable response surface that ties signals to operator
action. `activity:deploy` beads track rollout work, but they do not replace the
persistent per-service procedures operators need during incidents and
recovery.

The deleted prompt and template were too broad and generic to justify keeping
them. Restoration is warranted only with a tighter prompt and template bar
that forces service-specific operational guidance.
