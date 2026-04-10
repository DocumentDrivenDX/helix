# Deployment Checklist Generation Prompt

Create a concise, service-specific deployment checklist for this release.

## Focus

- Keep the checklist short enough to use during the release itself.
- Include only the checks that materially change the technical go/no-go decision.
- Make rollout verification and rollback triggers explicit.
- Point to supporting artifacts such as `monitoring-setup` or `runbook`
  instead of duplicating them.
- Avoid communication boilerplate, launch marketing tasks, or generic
  enterprise release wish lists.

## Completion Criteria

- Prerequisites and owners are explicit.
- Rollout verification names the signals or commands that prove health.
- Rollback triggers and rollback entrypoint are explicit.
- The final decision section makes the release auditable.
