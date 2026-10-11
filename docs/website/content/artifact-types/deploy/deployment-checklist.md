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
job is to capture the pre-deploy checks, validation gates, staged rollout, and
rollback for a specific release.

It is not a runbook, monitoring design, implementation plan, or release note.
Point to those artifacts instead of duplicating them.

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: example.deployment-checklist.depositmatch.csv-import
  authoring:
    home: repo
  depends_on:
    - example.implementation-plan.depositmatch
    - example.test-plan.depositmatch
---

# Deployment Checklist

## Release

- **Component**: DepositMatch CSV Import v1, behind the `csvImportV1` flag (defaults off in production)
- **Release version**: `release-2026-05-12-csv-import`
- **Related artifacts**: implementation plan, test plan, API-001

## Before Deploy

- **Plan reviewed**: Migration plan shows only `import_sessions` and `import_files`; nothing else changes.
- **Order of operations**: Migration first, then API and web with the flag off, then enable the flag.
- **Config is complete**: Storage bucket name and credentials are non-empty after render. An empty bucket disables uploads silently, so the smoke script asserts a real upload succeeds.
- **Access verified**: The upload service account can write to the source-file bucket and no other bucket, confirmed by a staging upload.

## Validation Gates

| Gate | Must Pass Before | Check |
|------|------------------|-------|
| CI green on main, P0 upload tests pass | staging | `pnpm test && pnpm test:e2e -- upload-csv` |
| Migration applied | production | Staging migration job log |
| Valid CSV pair uploads; PDF is rejected | production | Staging smoke script |
| No raw CSV row values in logs | production | Log query for fixture sentinel values |
| Health green 15 minutes, flag off | canary | `curl -fsS https://api.depositmatch.example/healthz` |
| Upload 5xx below 1%, p95 under 2s | full pilot | Upload dashboard |

## Rollout Stages

| Stage | Deploy Action | Exit Condition |
|-------|---------------|----------------|
| Staging | Deploy, migrate, enable flag | Happy path and rejection pass |
| Production, flag off | Deploy and migrate | Health green 15 minutes |
| Canary | Enable for one pilot firm | 3 successful imports or 30 minutes without a trigger |
| Full pilot | Enable for all pilot firms | Gates above hold |

## Rollback

**Path**: Disable `csvImportV1`; the previous deploy stays in place, so recovery is immediate. If the migration blocks the API deploy, restore the previous task definition.

| Signal | Threshold | Immediate Action |
|--------|-----------|------------------|
| Upload 5xx | Above 1% for 15 minutes | Disable the flag |
| Partial session or file commit | Any | Disable flag, stop canary, run cleanup script |
| Raw row values in logs | Any confirmed | Disable flag, purge logs per runbook |
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
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Deployment Checklist Generation Prompt&#10;&#10;Create a concise, service-specific deployment checklist for this release.&#10;&#10;## Purpose&#10;&#10;Deployment Checklist is the **release-window execution checklist**. Its unique&#10;job is to capture the pre-deploy checks, validation gates, staged rollout, and&#10;rollback for a specific release.&#10;&#10;It is not a runbook, monitoring design, implementation plan, or release note.&#10;Point to those artifacts instead of duplicating them.&#10;&#10;## Reference Anchors&#10;&#10;Use these local resource summaries as grounding:&#10;&#10;- `docs/resources/google-sre-release-engineering.md` grounds repeatable,&#10;  staged, evidence-based releases with explicit rollback paths.&#10;- `docs/resources/microsoft-azure-well-architected-framework.md` grounds&#10;  operational readiness, reliability, and deployment risk checks.&#10;&#10;## Focus&#10;&#10;- Keep the checklist short enough to use during the release itself.&#10;- Include only the checks that materially change the technical go/no-go decision.&#10;- Before Deploy covers the failures that actually bite: an unreviewed plan, a&#10;  dependency landing out of order, config that is silently empty, and grants&#10;  assumed rather than verified. Answer them for this release, not generically.&#10;- Make validation gates and rollback triggers explicit.&#10;- Omit owners, timestamps, and status checkboxes; the tracker and git hold them.&#10;- Point to supporting artifacts such as `monitoring-setup` or `runbook`&#10;  instead of duplicating them.&#10;- Avoid communication boilerplate, launch marketing tasks, or generic&#10;  enterprise release wish lists.&#10;&#10;## Boundary Test&#10;&#10;| If you are writing... | Put it in... |&#10;|---|---|&#10;| Build sequence and implementation validation | Implementation Plan |&#10;| Operational procedures and incident response | Runbook |&#10;| Dashboards, alerts, and SLO instrumentation | Monitoring Setup |&#10;| User-facing release communication | Release Notes |&#10;| Release-window go/no-go checks and rollback triggers | Deployment Checklist |&#10;&#10;## Completion Criteria&#10;&#10;- Before Deploy is answered for this release.&#10;- Each gate names the signal or command that proves it.&#10;- Rollback returns to the last working state; a failed deploy never replaces it.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: deployment-checklist&#10;  authoring:&#10;    home: repo&#10;---&#10;&#10;# Deployment Checklist&#10;&#10;## Release&#10;&#10;- **Component**: [name]&#10;- **Release version**: [tag/build]&#10;- **Related artifacts**: [runbook, monitoring-setup, release-notes]&#10;&#10;## Before Deploy&#10;&#10;- **Plan reviewed**: [For infra or config changes, the plan/diff was read and every change is expected. Name anything unrelated that would also change.]&#10;- **Order of operations**: [What must land first (infra variable, migration, grant) and what depends on it.]&#10;- **Config is complete**: [Every required env/config value is non-empty after render. Name the values that fail silently when empty.]&#10;- **Access verified**: [The deploy principal holds the grants it needs, checked by a real run, not assumed from a merged change.]&#10;&#10;## Validation Gates&#10;&#10;| Gate | Must Pass Before | Check |&#10;|------|------------------|-------|&#10;| [Build and tests] | staging | [CI link / command] |&#10;| [Migration or data check] | production | [query / log] |&#10;| [Critical path works] | full rollout | [test / smoke script] |&#10;| [Error rate and latency] | full rollout | [threshold and dashboard] |&#10;&#10;## Rollout Stages&#10;&#10;| Stage | Deploy Action | Exit Condition |&#10;|-------|---------------|----------------|&#10;| Staging | [steps] | [what must be true] |&#10;| Canary | [steps] | [what must be true] |&#10;| Full | [steps] | [what must be true] |&#10;&#10;## Rollback&#10;&#10;**Path**: [How to get back to the last working state, and how long that takes. A failed deploy must not replace the working one.]&#10;&#10;| Signal | Threshold | Immediate Action |&#10;|--------|-----------|------------------|&#10;| [error rate / failed path / data issue] | [threshold] | [command or runbook section] |</code></pre></details></td></tr>
</tbody>
</table>
