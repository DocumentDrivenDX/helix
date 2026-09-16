# Deployment Checklist — Restoration Decision

> Historical decision; superseded by the worked example at `docs/helix/05-deploy/deployment-checklist.md`.

`deployment-checklist` is restored as the canonical deploy-activity artifact for
technical release readiness and rollout go/no-go checks.

## Decision

This artifact is restored rather than retired.

Current HELIX still requires `docs/helix/05-deploy/deployment-checklist.md` in
the deploy exit gate and the iterate entry gate. `monitoring-setup` also
treats it as a distinct input rather than a replacement. The intent therefore
still exists in the live contract even though the original artifact stub was
pruned.

## Why It Exists

- The deployment checklist is the short operational surface used to decide
  whether a release can start, continue, pause, or roll back.
- `monitoring-setup` defines the observability configuration and alerting that
  the checklist must verify, but it is not itself the live go/no-go surface.
- `runbook` explains how operators respond when rollout fails or an incident
  occurs, but it is broader and more procedural than the release checklist.
- Release communication belongs in `release-notes`, and broader launch
  coordination belongs in linked `activity:deploy` tracker issues rather than the
  technical deployment checklist.

## Canonical Inputs

- build completion evidence and any blocking test or security gates
- environment, secret, and migration readiness
- staged rollout checkpoints and health checks
- monitoring dashboards and alerts that prove safe rollout
- rollback owner and rollback entrypoint

## Minimum Prompt Bar

- Keep the checklist service-specific and short enough to use live during a deployment.
- Include only checks that materially change the release decision.
- Require explicit verification signals or commands for rollout health.
- Require explicit rollback triggers and the rollback entrypoint.
- Link to monitoring setup and runbook instead of duplicating them.
- Exclude broad cross-functional launch tasks that belong in separate artifacts.

## Minimum Template Bar

- release scope and owners
- pre-deploy readiness checks
- rollout sequence or staged rollout checkpoints
- production verification checks with evidence
- rollback triggers and responsible owner
- final go/no-go decision record

## Canonical Replacement Status

`deployment-checklist` is not replaced by `monitoring-setup` or `runbook`.
Those artifacts define adjacent responsibilities that the checklist references.
The deleted prompt and template were too thin, so restoration requires a real
prompt and template bar rather than reintroducing the old stub verbatim.

The deleted `launch-checklist` artifact stays superseded rather than restored.
Its surviving intent is intentionally decomposed: technical readiness lives in
`deployment-checklist`, observability readiness lives in `monitoring-setup`,
rollback and recovery procedures live in `runbook`, release communication lives
in `release-notes`, and cross-functional coordination lives in linked
`activity:deploy` tracker issues. Reintroducing `launch-checklist` would duplicate
those surfaces instead of defining a distinct deploy artifact.
