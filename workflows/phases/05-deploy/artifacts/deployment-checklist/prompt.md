# Deployment Checklist Generation Prompt

Create a concise deployment checklist for a safe production deployment.

## Storage Location

`docs/helix/05-deploy/deployment-checklist.md`

## Key Requirements

- Keep it service-specific and execution-ready.
- Include only the checks needed to decide whether this release can proceed.
- Cover pre-deployment validation, rollout verification, rollback triggers, and go/no-go criteria.
- Omit generic launch boilerplate and broad enterprise wish lists.

## Completion Criteria

- [ ] Prerequisites are explicit and short
- [ ] Rollout and rollback checks are actionable
- [ ] Go/no-go thresholds are measurable
