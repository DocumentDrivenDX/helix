---
ddx:
  id: deployment-checklist
---

# Deployment Checklist

## Release Scope

- Service or component: [name]
- Version or commit: [tag or SHA]
- Deployment window: [date and time]
- Release owner: [name]
- Rollback owner: [name]
- Supporting artifacts: [implementation plan, runbook, monitoring, release notes]

## Pre-Deploy Checks

| Area | Check | Evidence or Command | Status |
|------|-------|---------------------|--------|
| Build | [CI, tests, approvals] | [link or command] | [ ] |
| Config | [Secrets, flags, env vars] | [link or command] | [ ] |
| Data | [Migrations, backups, compatibility] | [link or command] | [ ] |
| Ops | [Dashboards, alerts, on-call] | [link or command] | [ ] |

## Rollout Plan

| Stage | Action | Exit Condition |
|-------|--------|----------------|
| Staging | [deploy and validate] | [what must be true] |
| Initial production | [first step or canary] | [what must be true] |
| Full rollout | [complete rollout] | [what must be true] |

## Verification Checks

| Signal or Check | Expected Result | Evidence or Command | Status |
|-----------------|-----------------|---------------------|--------|
| [health check] | [healthy value] | [command or dashboard] | [ ] |
| [error rate] | [threshold] | [dashboard or query] | [ ] |
| [latency] | [threshold] | [dashboard or query] | [ ] |
| [critical user journey] | [pass condition] | [test or observation] | [ ] |

## Rollback Triggers

| Trigger | Threshold or Condition | Immediate Action | Owner |
|---------|------------------------|------------------|-------|
| [trigger] | [threshold] | [rollback step or runbook] | [name] |
| [trigger] | [threshold] | [rollback step or runbook] | [name] |

## Go or No-Go Decision

- Decision: [Go / Hold / Roll Back]
- Decision time: [timestamp]
- Notes: [exceptions, deferred checks, follow-up]
- Follow-up owner: [name]
