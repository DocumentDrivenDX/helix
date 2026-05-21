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
