# Deployment Checklist Generation Prompt

Create a concise, service-specific deployment checklist for this release.

## Purpose

Deployment Checklist is the **release-window execution checklist**. Its unique
job is to capture the technical go/no-go checks, staged rollout steps,
post-deploy verification, rollback triggers, and auditable decision point for a
specific release.

It is not a runbook, monitoring design, implementation plan, or release note.
Point to those artifacts instead of duplicating them.

## Reference Anchors

Use these local resource summaries as grounding:

- `docs/resources/google-sre-release-engineering.md` grounds repeatable,
  staged, evidence-based releases with explicit rollback paths.
- `docs/resources/microsoft-azure-well-architected-framework.md` grounds
  operational readiness, reliability, and deployment risk checks.

## Focus

- Keep the checklist short enough to use during the release itself.
- Include only the checks that materially change the technical go/no-go decision.
- Make rollout verification and rollback triggers explicit.
- Point to supporting artifacts such as `monitoring-setup` or `runbook`
  instead of duplicating them.
- Avoid communication boilerplate, launch marketing tasks, or generic
  enterprise release wish lists.

## Boundary Test

| If you are writing... | Put it in... |
|---|---|
| Build sequence and implementation validation | Implementation Plan |
| Operational procedures and incident response | Runbook |
| Dashboards, alerts, and SLO instrumentation | Monitoring Setup |
| User-facing release communication | Release Notes |
| Release-window go/no-go checks and rollback triggers | Deployment Checklist |

## Completion Criteria

- Prerequisites and owners are explicit.
- Rollout verification names the signals or commands that prove health.
- Rollback triggers and rollback entrypoint are explicit.
- The final decision section makes the release auditable.
