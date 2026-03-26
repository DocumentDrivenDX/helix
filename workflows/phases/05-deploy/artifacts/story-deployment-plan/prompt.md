# Story Deploy Issue Generation

## Required Inputs
- build issue(s) labeled `helix`, `phase:build`, `story:US-{XXX}`
- `docs/helix/05-deploy/deployment-checklist.md` - Project deployment readiness
- `docs/helix/05-deploy/monitoring-setup.md` - Monitoring requirements
- `docs/helix/05-deploy/runbook.md` - Operational procedures

## Produced Output
- one or more tracker issues labeled `helix`, `phase:deploy`, `story:US-{XXX}`

## Prompt

Create deploy issues for one user story. Keep each issue small, dependency-linked, and rollout-focused.

Each issue should reference the governing deploy artifacts and build issue(s), define a rollout objective, include rollback and verification steps, and be independently executable.

Use the mapping guidance at:
`workflows/phases/05-deploy/artifacts/story-deployment-plan/template.md`

Use tracker guidance at:
`workflows/TRACKER.md`

## Completion Criteria
- [ ] Every story rollout task is captured by one or more deploy issues
- [ ] Rollback and monitoring checks are explicit
- [ ] Dependencies on build issues are explicit
