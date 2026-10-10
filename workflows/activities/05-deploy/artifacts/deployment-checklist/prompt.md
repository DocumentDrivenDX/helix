# Deployment Checklist Generation Prompt

Create a concise, service-specific deployment checklist for this release.

## Purpose

Deployment Checklist is the **release-window execution checklist**. Its unique
job is to capture the pre-deploy checks, validation gates, staged rollout, and
rollback for a specific release.

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
- Before Deploy covers the failures that actually bite: an unreviewed plan, a
  dependency landing out of order, config that is silently empty, and grants
  assumed rather than verified. Answer them for this release, not generically.
- Make validation gates and rollback triggers explicit.
- Omit owners, timestamps, and status checkboxes; the tracker and git hold them.
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

- Before Deploy is answered for this release.
- Each gate names the signal or command that proves it.
- Rollback returns to the last working state; a failed deploy never replaces it.
