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
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Deploy</strong></a> — Ship to users with appropriate operational support, monitoring, and rollback plans.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/05-deploy/deployment-checklist.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="../../../artifact-types/deploy/monitoring-setup/">Monitoring Setup</a></td></tr>
<tr><th>HELIX documents</th><td><a href="https://github.com/DocumentDrivenDX/helix/blob/main/docs/helix/05-deploy/deployment-checklist.md"><code>docs/helix/05-deploy/deployment-checklist.md</code></a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Deployment Checklist Generation Prompt&#10;&#10;Create a concise, service-specific deployment checklist for this release.&#10;&#10;## Purpose&#10;&#10;Deployment Checklist is the **release-window execution checklist**. Its unique&#10;job is to capture the technical go/no-go checks, staged rollout steps,&#10;post-deploy verification, rollback triggers, and auditable decision point for a&#10;specific release.&#10;&#10;It is not a runbook, monitoring design, implementation plan, or release note.&#10;Point to those artifacts instead of duplicating them.&#10;&#10;## Reference Anchors&#10;&#10;Use these local resource summaries as grounding:&#10;&#10;- `docs/resources/google-sre-release-engineering.md` grounds repeatable,&#10;  staged, evidence-based releases with explicit rollback paths.&#10;- `docs/resources/microsoft-azure-well-architected-framework.md` grounds&#10;  operational readiness, reliability, and deployment risk checks.&#10;&#10;## Focus&#10;&#10;- Keep the checklist short enough to use during the release itself.&#10;- Include only the checks that materially change the technical go/no-go decision.&#10;- Make rollout verification and rollback triggers explicit.&#10;- Point to supporting artifacts such as `monitoring-setup` or `runbook`&#10;  instead of duplicating them.&#10;- Avoid communication boilerplate, launch marketing tasks, or generic&#10;  enterprise release wish lists.&#10;&#10;## Boundary Test&#10;&#10;| If you are writing... | Put it in... |&#10;|---|---|&#10;| Build sequence and implementation validation | Implementation Plan |&#10;| Operational procedures and incident response | Runbook |&#10;| Dashboards, alerts, and SLO instrumentation | Monitoring Setup |&#10;| User-facing release communication | Release Notes |&#10;| Release-window go/no-go checks and rollback triggers | Deployment Checklist |&#10;&#10;## Completion Criteria&#10;&#10;- Prerequisites and owners are explicit.&#10;- Rollout verification names the signals or commands that prove health.&#10;- Rollback triggers and rollback entrypoint are explicit.&#10;- The final decision section makes the release auditable.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: deployment-checklist&#10;---&#10;&#10;# Deployment Checklist&#10;&#10;## Release Scope&#10;&#10;- Service or component: [name]&#10;- Version or commit: [tag or SHA]&#10;- Deployment window: [date and time]&#10;- Release owner: [name]&#10;- Rollback owner: [name]&#10;- Supporting artifacts: [implementation plan, runbook, monitoring, release notes]&#10;&#10;## Pre-Deploy Checks&#10;&#10;| Area | Check | Evidence or Command | Status |&#10;|------|-------|---------------------|--------|&#10;| Build | [CI, tests, approvals] | [link or command] | [ ] |&#10;| Config | [Secrets, flags, env vars] | [link or command] | [ ] |&#10;| Data | [Migrations, backups, compatibility] | [link or command] | [ ] |&#10;| Ops | [Dashboards, alerts, on-call] | [link or command] | [ ] |&#10;&#10;## Rollout Plan&#10;&#10;| Stage | Action | Exit Condition |&#10;|-------|--------|----------------|&#10;| Staging | [deploy and validate] | [what must be true] |&#10;| Initial production | [first step or canary] | [what must be true] |&#10;| Full rollout | [complete rollout] | [what must be true] |&#10;&#10;## Verification Checks&#10;&#10;| Signal or Check | Expected Result | Evidence or Command | Status |&#10;|-----------------|-----------------|---------------------|--------|&#10;| [health check] | [healthy value] | [command or dashboard] | [ ] |&#10;| [error rate] | [threshold] | [dashboard or query] | [ ] |&#10;| [latency] | [threshold] | [dashboard or query] | [ ] |&#10;| [critical user journey] | [pass condition] | [test or observation] | [ ] |&#10;&#10;## Rollback Triggers&#10;&#10;| Trigger | Threshold or Condition | Immediate Action | Owner |&#10;|---------|------------------------|------------------|-------|&#10;| [trigger] | [threshold] | [rollback step or runbook] | [name] |&#10;| [trigger] | [threshold] | [rollback step or runbook] | [name] |&#10;&#10;## Go or No-Go Decision&#10;&#10;- Decision: [Go / Hold / Roll Back]&#10;- Decision time: [timestamp]&#10;- Notes: [exceptions, deferred checks, follow-up]&#10;- Follow-up owner: [name]</code></pre></details></td></tr>
</tbody>
</table>
