---
ddx:
  id: example.technical-design.depositmatch.upload-csv
  depends_on:
    - example.user-story.depositmatch.upload-csv
    - example.solution-design.depositmatch.csv-import
    - example.contract.depositmatch.import-session-api
  review:
    self_hash: 064c51468da1d444da9c6f65d6c2502487724ac315fa3e6c50f9bbeffd3d69b9
    deps:
      example.contract.depositmatch.import-session-api: 0f6f77f7dca5d1d05590440459fe958f9620857ed3968839e537655dce27cd04
      example.solution-design.depositmatch.csv-import: 4d5a2bf5c6b05affdcf7ecc35497aae9f7bb64007e45b62f2a87b42a6914aa00
      example.user-story.depositmatch.upload-csv: ae65ec934b10e577641772c711eafec5a15dbb5854327d8240307341e2053f66
    reviewed_at: "2026-05-15T04:11:24Z"
---

# Technical Design: TD-001-upload-csv-files

**User Story**: US-001 Upload CSV Files for a Client | **Feature**: FEAT-001 |
**Solution Design**: SD-001 CSV Import and Column Mapping

## Scope

- Story-level design for uploading one bank CSV and one invoice CSV for a
  selected client and creating a draft import session.
- Inherits API-001, ADR-001, and the FEAT-001 solution design.
- Does not implement column mapping, row validation, import confirmation, or
  match generation.

## Technical Approach

**Strategy**: Implement the API-001 upload contract in the Fastify API and add a
React upload step that calls it. Store encrypted originals through the existing
source-file storage adapter and persist draft session metadata in PostgreSQL.

**Key Decisions**:

- Use the API-001 response shape directly in the UI state so the mapping step
  receives `importSessionId` and `next.href` without client-side inference.
- Validate file extension and MIME hints in the UI for quick feedback, but
  enforce all contract rules in the API before storage.
- Keep row parsing out of this story; parsing begins in the mapping/validation
  stories.

**Trade-offs**:

- Duplicating light file-type checks in UI and API improves feedback but means
  API tests remain the source of truth.
- Creating the session before row validation lets the reviewer recover from
  upload issues but requires draft-session cleanup later.

## Component Changes

### Modified: Web Import Workflow

- **Current State**: No DepositMatch import workflow exists.
- **Changes**: Add upload controls for bank and invoice CSV files, call API-001,
  show upload errors, and route successful responses to mapping review.
- **Files**: `apps/web/src/features/import/ImportSessionUpload.tsx`,
  `apps/web/src/features/import/importApi.ts`,
  `apps/web/src/routes/clientImportRoutes.tsx`

### New: API Import Session Route

- **Purpose**: Implement the API-001 import session route.
- **Interfaces**: Input/output semantics are governed by API-001; this TD owns
  local route wiring only.
- **Files**: `apps/api/src/routes/importSessions.ts`,
  `apps/api/src/schemas/importSessionSchemas.ts`

### New: Import Upload Service

- **Purpose**: Authorize client access, enforce file rules, store encrypted
  originals, and persist draft session/file metadata.
- **Interfaces**: Input: client ID, authenticated user, two file streams;
  Output: draft import-session DTO.
- **Files**: `apps/api/src/services/importUploadService.ts`,
  `apps/api/src/storage/sourceFileStore.ts`,
  `apps/api/src/repositories/importSessionRepository.ts`

## API/Interface Design

| Surface | Governing Contract | Story-Level Usage |
|---------|--------------------|-------------------|
| Import session API | API-001 | Route handler, upload service, and UI client call the existing contract without changing its normative surface. |

## Data Model Changes

```sql
CREATE TABLE import_sessions (
    id UUID PRIMARY KEY,
    client_id UUID NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('draft', 'mapping', 'confirmed')),
    created_by UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE import_files (
    id UUID PRIMARY KEY,
    import_session_id UUID NOT NULL REFERENCES import_sessions(id),
    source_type TEXT NOT NULL CHECK (source_type IN ('bank_csv', 'invoice_csv')),
    original_name TEXT NOT NULL,
    size_bytes INTEGER NOT NULL CHECK (size_bytes > 0),
    storage_key TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

## Integration Points

| From | To | Method | Data |
|------|----|--------|------|
| Web Import Workflow | API Import Session Route | HTTPS multipart POST | bank CSV, invoice CSV |
| API Import Session Route | Import Upload Service | Internal call | authenticated user, client ID, files |
| Import Upload Service | Source File Store | S3 SDK | encrypted file stream and metadata |
| Import Upload Service | PostgreSQL | SQL transaction | session and file metadata |

### External Dependencies

- **S3 Source File Store**: Store encrypted originals. Fallback: return 503
  `import-storage-unavailable`; no draft session should be committed.

## Security

- **Authentication**: Require authenticated firm user.
- **Authorization**: User must have access to the requested client.
- **Data Protection**: Store files encrypted; never log raw row contents.
- **Threats**: Path leakage from uploaded filenames, oversized uploads, and
  unauthorized client access. Strip path components, enforce 10 MB per-file
  limit, and return 404 for inaccessible clients.

## Performance

- **Expected Load**: Pilot firms upload at most two 10 MB files per import
  session.
- **Response Target**: Return success or contract error in under 2 seconds
  before row parsing.
- **Optimizations**: Stream file upload to storage; do not buffer entire files
  in application memory.

## Testing

Each governing-story AC-ID is realized below (ADR-009 — AC text lives in [[US-001]], not here):

- [ ] **Unit** (US-001-AC1, US-001-AC2): `importUploadService` rejects missing
  files, non-CSV files, and inaccessible clients.
- [ ] **Integration** (US-001-AC1, US-001-AC3): API route returns API-001
  success shape and stores draft session/file metadata in one transaction.
- [ ] **API** (US-001-AC2): Contract tests for 201, 400 `missing-import-file`,
  415 `unsupported-import-file-type`, and 503 `import-storage-unavailable`.
- [ ] **Security**: Verify raw CSV row values are absent from logs for failed
  and successful uploads.
- [ ] **UI** (US-001-AC1): Upload component routes to `next.href` after
  successful upload and renders problem-details errors.

## Migration & Rollback

- **Backward Compatibility**: New tables and endpoint only; no existing API
  behavior changes.
- **Data Migration**: Create `import_sessions` and `import_files` tables.
- **Feature Toggle**: Hide upload entry point behind `csvImportV1`.
- **Rollback**: Disable `csvImportV1`; leave unused draft-session tables in
  place until cleanup migration.

## Implementation Sequence

1. Add database migration and repository. Files:
   `apps/api/migrations/001_import_sessions.sql`,
   `apps/api/src/repositories/importSessionRepository.ts`. Tests:
   `apps/api/test/repositories/importSessionRepository.test.ts`.
2. Add source-file storage adapter and upload service. Files:
   `apps/api/src/storage/sourceFileStore.ts`,
   `apps/api/src/services/importUploadService.ts`. Tests:
   `apps/api/test/services/importUploadService.test.ts`.
3. Add Fastify route and contract tests. Files:
   `apps/api/src/routes/importSessions.ts`,
   `apps/api/src/schemas/importSessionSchemas.ts`. Tests:
   `apps/api/test/routes/importSessions.test.ts`.
4. Add React upload UI and API client. Files:
   `apps/web/src/features/import/ImportSessionUpload.tsx`,
   `apps/web/src/features/import/importApi.ts`. Tests:
   `apps/web/src/features/import/ImportSessionUpload.test.tsx`.

**Prerequisites**: API-001 accepted; S3 bucket and database connection available
in development/test environments.

## Risks

| Risk | Prob | Impact | Mitigation |
|------|------|--------|------------|
| Multipart parsing buffers large files in memory | M | H | Use streaming parser configuration and add memory regression test. |
| UI and API validation drift | M | M | Treat API contract tests as authoritative; keep UI validation advisory only. |
| Draft sessions accumulate after abandoned uploads | M | L | Add cleanup task in a later story; do not block US-001 on cleanup automation. |
