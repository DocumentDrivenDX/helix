---
title: "Deployment Checklist"
linkTitle: "Deployment Checklist"
slug: deployment-checklist
activity: "Deploy"
artifactRole: "core"
weight: 10
generated: true
---

## Purpose

Deployment Checklist is the **release-window execution checklist**. Its unique
job is to capture the technical go/no-go checks, staged rollout steps,
post-deploy verification, rollback triggers, and auditable decision point for a
specific release.

It is not a runbook, monitoring design, implementation plan, or release note.
Point to those artifacts instead of duplicating them.

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: example.deployment-checklist.depositmatch.csv-import
  depends_on:
    - example.implementation-plan.depositmatch
    - example.test-plan.depositmatch
  review:
    self_hash: 02e9e7c9c29b4a335e0e2eceacaaaa6673018042db2a706f89293ab6f58abcbf
    deps:
      example.implementation-plan.depositmatch: 8f48b07ab604fe52786de7648f7ab37da251cfade0ea38bb4e802082d4f977de
      example.test-plan.depositmatch: ba055b639a94e62d3b24f3a7ca270f78c3f17f6bae78b936d399291225d7976f
    reviewed_at: "2026-05-15T04:11:24Z"
---

# Deployment Checklist

## Release Scope

- Service or component: DepositMatch CSV Import v1 (`csvImportV1`)
- Version or commit: `release-2026-05-12-csv-import`
- Deployment window: 2026-05-12 21:00-22:00 UTC
- Release owner: Engineering lead
- Rollback owner: On-call API engineer
- Supporting artifacts: implementation plan `example.implementation-plan.depositmatch`,
  test plan `example.test-plan.depositmatch`, API contract `API-001`

## Pre-Deploy Checks

| Area | Check | Evidence or Command | Status |
|------|-------|---------------------|--------|
| Build | Main branch CI green for upload slice | `gh run list --branch main --limit 1` | [ ] |
| Tests | Contract, integration, UI, and P0 E2E upload tests pass | `pnpm test && pnpm test:e2e -- upload-csv` | [ ] |
| Config | `csvImportV1` flag exists and defaults off in production | Feature flag dashboard or config diff | [ ] |
| Data | `import_sessions` and `import_files` migration applied in staging | Migration job log | [ ] |
| Ops | Upload error-rate and latency panels visible | Dashboard link | [ ] |
| Security | Log scan shows no raw CSV row values in test/staging logs | `pnpm test -- importUploadService` | [ ] |

## Rollout Plan

| Stage | Action | Exit Condition |
|-------|--------|----------------|
| Staging | Deploy API/web, run migration, enable `csvImportV1` for staging | Upload happy path and PDF rejection pass in staging |
| Initial production | Deploy API/web with `csvImportV1` off, run migration | Health checks green for 15 minutes; no migration errors |
| Canary | Enable `csvImportV1` for one pilot firm | 3 successful import sessions or 30 minutes without trigger |
| Full pilot rollout | Enable `csvImportV1` for all pilot firms | Upload error rate below 2% and p95 upload response below 2 seconds |

## Verification Checks

| Signal or Check | Expected Result | Evidence or Command | Status |
|-----------------|-----------------|---------------------|--------|
| API health | 2xx from `/healthz` | `curl -fsS https://api.depositmatch.example/healthz` | [ ] |
| Upload contract | 201 for valid CSV pair; 415 for PDF | Production smoke script with synthetic pilot client | [ ] |
| Error rate | Upload endpoint 5xx below 1% over 15 minutes | Dashboard query | [ ] |
| Latency | p95 upload response below 2 seconds before row parsing | Dashboard query | [ ] |
| Logging | No raw CSV values in application logs | Log query for fixture sentinel values | [ ] |

## Rollback Triggers

| Trigger | Threshold or Condition | Immediate Action | Owner |
|---------|------------------------|------------------|-------|
| Upload endpoint 5xx | Above 1% for 15 minutes | Disable `csvImportV1`; keep deployment in place | Release owner |
| Data integrity issue | Any partial session/file metadata commit | Disable flag, stop canary, open incident, run cleanup script | Rollback owner |
| Raw financial row values in logs | Any confirmed occurrence | Disable flag and rotate affected logs per runbook | Security lead |
| Migration failure | Migration does not complete or blocks API deploy | Stop rollout and restore previous task definition | Rollback owner |

## Go or No-Go Decision

- Decision: [Go / Hold / Roll Back]
- Decision time: [timestamp]
- Notes: [exceptions, deferred checks, follow-up]
- Follow-up owner: Release owner
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="/reference/glossary/activities/"><strong>Deploy</strong></a> — Ship to users with appropriate operational support, monitoring, and rollback plans.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/05-deploy/deployment-checklist.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="/artifact-types/deploy/monitoring-setup/">Monitoring Setup</a></td></tr>
<tr><th>HELIX documents</th><td><a href="https://github.com/DocumentDrivenDX/helix/blob/main/docs/helix/05-deploy/deployment-checklist.md"><code>docs/helix/05-deploy/deployment-checklist.md</code></a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Deployment Checklist Generation Prompt

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
- The final decision section makes the release auditable.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---
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
- Follow-up owner: [name]</code></pre></details></td></tr>
</tbody>
</table>
