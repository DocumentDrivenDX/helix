---
ddx:
  id: example.story-test-plan.depositmatch.upload-csv
  depends_on:
    - example.user-story.depositmatch.upload-csv
    - example.technical-design.depositmatch.upload-csv
    - example.test-plan.depositmatch
  review:
    self_hash: 20aed2c4e248a67b448b0528b49ae9b2724d5045879ddcda655ad220d1c276ed
    deps:
      example.technical-design.depositmatch.upload-csv: 064c51468da1d444da9c6f65d6c2502487724ac315fa3e6c50f9bbeffd3d69b9
      example.test-plan.depositmatch: ba055b639a94e62d3b24f3a7ca270f78c3f17f6bae78b936d399291225d7976f
      example.user-story.depositmatch.upload-csv: b87b259be7a0ac9a75516d5868742aed44b6af05ab12d10aa4535a3cae24e9b6
    reviewed_at: "2026-05-24T23:28:08Z"
---

# Story Test Plan: STP-001-upload-csv-files

## Story Reference

**User Story**: [[US-001-upload-csv-files]]
**Technical Design**: [[TD-001-upload-csv-files]]
**Related Solution Design**: [[SD-001-csv-import-column-mapping]]
**Project Test Plan**: [[test-plan]]

## Scope and Objective

**Goal**: Prove that a reviewer can upload one bank CSV and one invoice CSV for
a selected client, create a draft import session, reject invalid file types, and
record source file metadata.
**Blocking Gate**: `pnpm test -- importSessions && pnpm test:e2e -- upload-csv`

**In Scope**

- API-001 success response for a valid two-file upload.
- Problem-details error for non-CSV file upload.
- Draft import-session and import-file metadata persistence.
- React upload flow routing to mapping review after success.

**Out of Scope**

- Column mapping.
- Row-level validation.
- Import confirmation.
- Match suggestion generation.
- Cleanup of abandoned draft sessions.

## Acceptance Criteria Test Mapping

| AC ID | Acceptance Criterion (Given/When/Then) | Failing Test(s) to Create or Run | Test Level | File or Command | Setup / Data | Notes |
|-------|----------------------------------------|----------------------------------|------------|-----------------|--------------|-------|
| US-001-AC1 | Given Maya is viewing Acme Dental, when she uploads one valid bank CSV and one valid invoice CSV, then DepositMatch creates one draft import session for Acme Dental and opens mapping review. | `creates_draft_import_session_for_two_csv_files`, `routes_to_mapping_review_after_success` | Contract, Integration, E2E | `apps/api/test/routes/importSessions.test.ts`; `apps/web/src/features/import/ImportSessionUpload.test.tsx`; `pnpm test:e2e -- upload-csv` | `fixtures/acme-bank-2026-05-08.csv`, `fixtures/acme-invoices-2026-05-08.csv`, authenticated Maya user, Acme Dental client | Covers API and visible reviewer flow |
| US-001-AC2 | Given Maya is viewing Acme Dental, when she uploads a PDF instead of a CSV for either required file, then DepositMatch rejects the file before parsing and keeps the import session in draft. | `rejects_non_csv_bank_file`, `renders_problem_details_for_invalid_file_type` | Contract, UI | `apps/api/test/routes/importSessions.test.ts`; `apps/web/src/features/import/ImportSessionUpload.test.tsx` | `fixtures/statement.pdf`, valid invoice CSV | Asserts 415 `unsupported-import-file-type` |
| US-001-AC3 | Given Maya has uploaded both required CSV files, when the files are accepted, then the import session records the client, file names, upload time, and source type for each file. | `persists_import_file_metadata`, `does_not_log_raw_csv_rows` | Integration, Security | `apps/api/test/services/importUploadService.test.ts`; `pnpm test -- importUploadService` | S3 fake, PostgreSQL test DB, log capture | Verifies metadata and financial-data logging concern |

## Executable Proof

### Primary Commands

```bash
pnpm test -- importSessions
pnpm test -- importUploadService
pnpm test -- ImportSessionUpload
pnpm test:e2e -- upload-csv
```

### Planned Test Files

- `apps/api/test/routes/importSessions.test.ts`
- `apps/api/test/services/importUploadService.test.ts`
- `apps/web/src/features/import/ImportSessionUpload.test.tsx`
- `apps/web/e2e/upload-csv.spec.ts`

### Coverage Focus

- P0: valid two-file upload, non-CSV rejection, metadata persistence, no raw
  financial row logging.
- P1: UI advisory validation for missing second file.

## Data and Setup

| Need | Required For | Source / Strategy |
|------|--------------|-------------------|
| Authenticated Maya user | API, UI, E2E | Test user factory with Acme Dental access |
| Acme Dental client | API, UI, E2E | Client factory seeded before each test |
| Valid bank CSV | Happy path | `fixtures/acme-bank-2026-05-08.csv` |
| Valid invoice CSV | Happy path | `fixtures/acme-invoices-2026-05-08.csv` |
| Invalid PDF | Error path | `fixtures/statement.pdf` |
| S3-compatible fake | Integration | Test storage adapter with failure injection |
| Log capture | Security assertion | Test logger sink scanned for raw CSV values |

## Edge Cases and Failure Modes

- Non-CSV bank file returns 415 and does not create a committed import session.
- Missing invoice file keeps the UI in draft state and does not call mapping
  review.
- Storage failure returns 503 and does not commit session metadata.
- Uploaded filenames are stored without local path components.

## Build Handoff

**Implementation Order**

1. Create API contract tests for success, missing file, non-CSV, and storage
   failure responses.
2. Create repository/service integration tests for draft-session and file
   metadata persistence.
3. Create UI component tests for successful routing and problem-details errors.
4. Create the Playwright happy-path smoke test after API/UI tests are green.

**Constraints**

- API-001 is normative.
- Raw CSV row values must not appear in application logs.
- S3 storage failure must not leave partial database state.

**Done When**

- [ ] Every in-scope acceptance criterion has passing evidence.
- [ ] Named commands and test files exist and run.
- [ ] Out-of-scope mapping and row-validation coverage remains deferred to
  later story test plans.
- [ ] The story can fail red before implementation and pass green after
  implementation.

## Review Checklist

- [ ] References the governing story and technical design
- [ ] Every active acceptance criterion maps to concrete failing tests
- [ ] File paths, commands, or test identifiers are specific enough to execute
- [ ] Setup, fixtures, mocks, and seed data are explicit
- [ ] Edge cases cover real story risks rather than generic boilerplate
- [ ] Scope remains bounded to one story slice
- [ ] Build handoff gives implementation a usable sequence
