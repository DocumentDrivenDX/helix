---
ddx:
  id: deployment-checklist
  authoring:
    home: repo
---

# Deployment Checklist

## Release

- **Component**: [name]
- **Release version**: [tag/build]
- **Related artifacts**: [runbook, monitoring-setup, release-notes]

## Before Deploy

- **Plan reviewed**: [For infra or config changes, the plan/diff was read and every change is expected. Name anything unrelated that would also change.]
- **Order of operations**: [What must land first (infra variable, migration, grant) and what depends on it.]
- **Config is complete**: [Every required env/config value is non-empty after render. Name the values that fail silently when empty.]
- **Access verified**: [The deploy principal holds the grants it needs, checked by a real run, not assumed from a merged change.]

## Validation Gates

| Gate | Must Pass Before | Check |
|------|------------------|-------|
| [Build and tests] | staging | [CI link / command] |
| [Migration or data check] | production | [query / log] |
| [Critical path works] | full rollout | [test / smoke script] |
| [Error rate and latency] | full rollout | [threshold and dashboard] |

## Rollout Stages

| Stage | Deploy Action | Exit Condition |
|-------|---------------|----------------|
| Staging | [steps] | [what must be true] |
| Canary | [steps] | [what must be true] |
| Full | [steps] | [what must be true] |

## Rollback

**Path**: [How to get back to the last working state, and how long that takes. A failed deploy must not replace the working one.]

| Signal | Threshold | Immediate Action |
|--------|-----------|------------------|
| [error rate / failed path / data issue] | [threshold] | [command or runbook section] |
