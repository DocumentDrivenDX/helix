---
ddx:
  id: example.release-notes.depositmatch.csv-import
  depends_on:
    - example.deployment-checklist.depositmatch.csv-import
    - example.implementation-plan.depositmatch
  review:
    self_hash: 3f1390445de6ce94fda9daf662dce73605ddf07d6ea73f7f0acde563b9af7360
    deps:
      example.deployment-checklist.depositmatch.csv-import: 02e9e7c9c29b4a335e0e2eceacaaaa6673018042db2a706f89293ab6f58abcbf
      example.implementation-plan.depositmatch: 8f48b07ab604fe52786de7648f7ab37da251cfade0ea38bb4e802082d4f977de
    reviewed_at: "2026-05-15T04:11:24Z"
---

# Release Notes - DepositMatch CSV Import v1

## Release Scope

- Release identifier or version: `release-2026-05-12-csv-import`
- Release date: 2026-05-12
- Rollout window or environment: staged pilot rollout
- Release owner: Engineering lead
- Source commit or build: `release-2026-05-12-csv-import`

## Audience and Channels

| Audience | Why they care | Delivery channel |
|----------|---------------|------------------|
| Pilot reconciliation leads | They can start weekly reconciliation by uploading bank and invoice CSV files for one client. | In-app release note and pilot email |
| Support | They need to recognize CSV upload, file-type, and storage errors. | Support runbook update and team channel |
| Operators | They need to monitor upload health and disable `csvImportV1` if triggers fire. | Deployment checklist and on-call channel |

## Highlights

- Reviewers can create a draft import session by uploading one bank deposit CSV
  and one invoice export CSV for a client.
- DepositMatch rejects non-CSV files before parsing and explains which file
  must be replaced.
- Accepted uploads preserve source file metadata needed for later mapping,
  validation, evidence, and audit trails.

## Required Actions Summary

- Users: no account action required; pilot users should export bank and invoice
  CSV files before starting an import.
- Operators: monitor upload error rate, p95 upload latency, and log-redaction
  checks during pilot rollout.
- Support: route CSV file-type problems to the upload troubleshooting path;
  do not ask users to send raw financial CSVs over email.

## Changes and Fixes

### New or Improved

| Area | What changed | Who is affected |
|------|--------------|-----------------|
| CSV import | Added draft import-session creation for one bank CSV and one invoice CSV. | Pilot reconciliation leads |
| Upload errors | Added structured non-CSV rejection before parsing. | Pilot users and support |
| Source metadata | Recorded file name, source type, size, and upload context for accepted files. | Reviewers, support, operators |

### Fixes

| Issue or symptom | Resolution | User or operator impact |
|------------------|------------|-------------------------|
| None in this release | This is the first pilot release of CSV import. | N/A |

## Breaking Changes and Required Actions

There are no breaking changes and no required migrations for users. Operators
must complete the deployment checklist before enabling `csvImportV1` for pilot
firms.

| Change | Impact | Required action | Deadline or trigger |
|--------|--------|-----------------|---------------------|
| New `import_sessions` and `import_files` tables | Operator-visible migration | Verify migration during staged rollout | Before enabling `csvImportV1` |

## Migration or Rollback Guidance

### Upgrade or Migration

1. Deploy API and web build with `csvImportV1` disabled.
2. Apply `import_sessions` and `import_files` migration.
3. Enable `csvImportV1` for one pilot firm after staging checks pass.

### Rollback or Hold Guidance

- Pause rollout when: upload endpoint 5xx exceeds 1% for 15 minutes, any raw
  CSV row value appears in logs, or any partial metadata commit is observed.
- Roll back using: deployment checklist rollback triggers.
- Ask for help in: on-call channel for operators; pilot-support channel for
  user questions.

## Known Issues and Support

| Issue | Who is affected | Workaround or next step |
|------|------------------|-------------------------|
| Column mapping is not part of this release note scope | Pilot reviewers | Mapping review is the next step after upload and is covered by follow-on release notes. |
| Bank feeds and accounting API sync are not available | Pilot firms | Continue exporting CSV files from existing systems. |
| Uploads larger than 10 MB are rejected | Pilot reviewers | Export a smaller date range or split the file before upload. |

## References

- Deployment checklist: `example.deployment-checklist.depositmatch.csv-import`
- Feature specification: `example.feature-specification.depositmatch.csv-import`
- API contract: `example.contract.depositmatch.import-session-api`
- Support path: pilot-support channel
