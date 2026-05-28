---
title: "Technical Design"
linkTitle: "Technical Design"
slug: technical-design
activity: "Design"
artifactRole: "core"
weight: 14
generated: true
---

## Purpose

Technical Design is the **story-level implementation design artifact**. Its
unique job is to make one user story buildable by naming the concrete component
changes, files, interfaces, data model changes, security implications, tests,
rollback path, and implementation sequence.

It inherits Architecture and Solution Design. It must not redesign the feature
or system. If the story cannot be implemented without changing the parent
Solution Design, ADR, Contract, or Architecture, update that governing artifact
first.

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
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

## Acceptance Criteria

1. **Given** Maya is viewing Acme Dental, **When** she uploads one valid bank
   CSV and one valid invoice CSV, **Then** DepositMatch creates one draft import
   session for Acme Dental and opens mapping review.
2. **Given** Maya is viewing Acme Dental, **When** she uploads a PDF instead of
   a CSV for either required file, **Then** DepositMatch rejects the file before
   parsing and keeps the import session in draft.
3. **Given** Maya has uploaded both required CSV files, **When** the files are
   accepted, **Then** the import session records the client, file names, upload
   time, and source type for each file.

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

- **Purpose**: Implement `POST /v1/clients/{clientId}/import-sessions`.
- **Interfaces**: Input: authenticated multipart request with `bankFile` and
  `invoiceFile`; Output: API-001 success or problem-details error response.
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

Use API-001 without changing the contract.

```yaml
endpoint: /v1/clients/{clientId}/import-sessions
method: POST
request:
  contentType: multipart/form-data
  parts:
    bankFile: csv file, required, max 10MB
    invoiceFile: csv file, required, max 10MB
response:
  status: 201
  body:
    importSessionId: uuid
    clientId: uuid
    status: draft
    files: uploaded file metadata
    next.href: mapping endpoint
```

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

- [ ] **Unit**: `importUploadService` rejects missing files, non-CSV files, and
  inaccessible clients.
- [ ] **Integration**: API route returns API-001 success shape and stores draft
  session/file metadata in one transaction.
- [ ] **API**: Contract tests for 201, 400 `missing-import-file`, 415
  `unsupported-import-file-type`, and 503 `import-storage-unavailable`.
- [ ] **Security**: Verify raw CSV row values are absent from logs for failed
  and successful uploads.
- [ ] **UI**: Upload component routes to `next.href` after successful upload and
  renders problem-details errors.

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
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="/reference/glossary/activities/"><strong>Design</strong></a> — Decide how to build it. Capture trade-offs, contracts, and architecture decisions.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/02-design/technical-designs/TD-{id}-{name}.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="/artifact-types/test/test-plan/">Test Plan</a><br><a href="/artifact-types/build/implementation-plan/">Implementation Plan</a></td></tr>
<tr><th>HELIX documents</th><td><a href="https://github.com/DocumentDrivenDX/helix/blob/main/docs/helix/02-design/technical-designs/TD-012-artifact-types-navigation.md"><code>docs/helix/02-design/technical-designs/TD-012-artifact-types-navigation.md</code></a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Technical Design for User Story Prompt

Create a concise technical design for one user story.

## Purpose

Technical Design is the **story-level implementation design artifact**. Its
unique job is to make one user story buildable by naming the concrete component
changes, files, interfaces, data model changes, security implications, tests,
rollback path, and implementation sequence.

It inherits Architecture and Solution Design. It must not redesign the feature
or system. If the story cannot be implemented without changing the parent
Solution Design, ADR, Contract, or Architecture, update that governing artifact
first.

## Reference Anchors

Use these local resource summaries as grounding:

- `docs/resources/google-small-cls.md` grounds bounded implementation slices
  with related tests and rollback.
- `docs/resources/cucumber-executable-specifications.md` grounds mapping
  acceptance criteria to observable tests.

## Active Concerns

For each concern selected in `docs/helix/01-frame/concerns.md`, apply its declared
`## Artifact Impact` (from `workflows/concerns/&lt;name&gt;/concern.md`) to THIS technical design — realize the
TD-level obligations it names (domain-driven-design -&gt; aggregates/value-objects/repositories; architecture-style -&gt; layering + dependency direction; cqrs -&gt; command/query split). A selected concern whose Artifact Impact names TD
but leaves no trace here is drift (reconcile-alignment Concern-&gt;Artifact Realization check).

## Focus
- Create a story-level artifact named `docs/helix/02-design/technical-designs/TD-XXX-[name].md`.
- Map each acceptance criterion to component changes, interfaces, data, security, and tests.
- Stay on the vertical slice for the story.
- Assume the broader architecture is already set by the parent solution design.
- Do not expand into a feature-wide or system-wide design; that belongs in a
  solution design (`SD-XXX-*`).
- Keep implementation sequence and rollout or migration notes only when they affect execution.

## Boundary Test

| If you are writing... | Put it in... |
|---|---|
| Feature-wide approach or decomposition | Solution Design |
| One architectural decision | ADR |
| Exact external interface contract | Contract |
| One story&#x27;s implementation shape, files, tests, and rollback | Technical Design |
| Test fixtures and detailed test cases | Story Test Plan |
| Work queue slicing and execution status | Implementation Plan or runtime work item |

## Completion Criteria
- The story is implementable.
- Key interfaces, changes, and test coverage are explicit.
- The design stays compact.
- The output is clearly story-level and disambiguated from a solution design.
- The implementation sequence can be turned into one or more small,
  reviewable changes without losing test coverage.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---
ddx:
  id: TD-XXX
  review:
    self_hash: 081ac39c2360ed0034e2a9bc05b5932fbd2baa2930b605c2ab947bf4548a2015
    deps:
      FEAT-XXX: a685da86c4c18a509196cb163f264af507cc966f804db574070e108a555bdf02
      SD-XXX: ea6f092342409cc3f74e945b3ae421392eb4787113b828331c0fdfab359bf86d
      US-XXX: 48b416257cf7acd8b225b785edcb09a125fed67521af9c8f115ec7dc2fbf23a3
    reviewed_at: &quot;2026-05-15T04:11:24Z&quot;
---

# Technical Design: TD-XXX-[story-name]

**User Story**: [[US-XXX]] | **Feature**: [[FEAT-XXX]] | **Solution Design**: [[SD-XXX]]

## Scope

- Story-level design artifact
- Use for one vertical slice or one bounded implementation story
- Must inherit the broader approach from the parent solution design
- Do not redefine cross-component architecture here; that belongs in `SD-XXX`
- Governing artifacts: [User Story, Solution Design, Contracts, Concerns]

## Acceptance Criteria

1. **Given** [precondition], **When** [action], **Then** [expected outcome]
2. **Given** [precondition], **When** [action], **Then** [expected outcome]

## Technical Approach

**Strategy**: [Brief description]

**Key Decisions**:
- [Decision]: [Rationale]

**Trade-offs**:
- [What we gain vs. lose]

## Component Changes

### Modified: [Component Name]
- **Current State**: [What exists]
- **Changes**: [What changes]
- **Files**: `[path]`

### New: [Component Name]
- **Purpose**: [Why needed]
- **Interfaces**: Input: [receives] / Output: [produces]
- **Files**: `[path]`

## API/Interface Design

```yaml
endpoint: /api/v1/[resource]
method: POST
request:
  type: object
  properties:
    field1: string
response:
  type: object
  properties:
    id: string
    status: string
```

## Data Model Changes

```sql
-- New tables or schema modifications
CREATE TABLE [table_name] (
    id UUID PRIMARY KEY,
    [columns]
);
```

## Integration Points

| From | To | Method | Data |
|------|-----|--------|------|
| [Source] | [Target] | [REST/Event/Direct] | [What data] |

### External Dependencies
- **[Service]**: [Usage] | Fallback: [If unavailable]

## Security

- **Authentication**: [Required auth level]
- **Authorization**: [Required permissions]
- **Data Protection**: [Encryption/masking]
- **Threats**: [Specific threats and mitigations]

## Performance

- **Expected Load**: [Requests/sec, data volume]
- **Response Target**: [Milliseconds]
- **Optimizations**: [Caching, indexing, etc.]

## Testing

- [ ] **Unit**: [What to test]
- [ ] **Integration**: [What integrations to test]
- [ ] **API**: [Endpoints to test]
- [ ] **Security**: [Security scenarios]

## Migration &amp; Rollback

- **Backward Compatibility**: [Strategy]
- **Data Migration**: [Required migrations]
- **Feature Toggle**: [Enable/disable mechanism]
- **Rollback**: [Steps to reverse]

## Implementation Sequence

1. [What to build first] -- Files: `[paths]` -- Tests: `[paths]`
2. [What to build next]
3. [Integration and verification]

**Prerequisites**: [Dependencies that must be complete first]

## Risks

| Risk | Prob | Impact | Mitigation |
|------|------|--------|------------|
| [Risk] | H/M/L | H/M/L | [Strategy] |

## Review Checklist

Use this checklist when reviewing a technical design:

- [ ] Acceptance criteria use Given/When/Then format and are verifiable
- [ ] Technical approach inherits from the parent solution design — no contradictions
- [ ] Key decisions have documented rationale
- [ ] Trade-offs are explicit — what we gain and what we lose
- [ ] Component changes clearly describe current state vs. changes
- [ ] API/interface design includes request and response schemas
- [ ] Data model changes include migration SQL
- [ ] Integration points specify fallback behavior for external dependencies
- [ ] Security section addresses authentication, authorization, and data protection
- [ ] Performance targets are numeric with specific metrics
- [ ] Testing section covers unit, integration, API, and security scenarios
- [ ] Migration and rollback strategy is documented
- [ ] Implementation sequence is ordered with file paths and test paths
- [ ] Design is consistent with governing solution design and feature spec</code></pre></details></td></tr>
</tbody>
</table>
