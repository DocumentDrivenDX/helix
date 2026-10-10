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
