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

Technical Design applies shared interface contracts; it does not define them.
When exact API, CLI, event, schema, config, telemetry, or adapter surface is
needed, reference the governing Contract ID. If the story uncovers a missing or
changed shared surface, create or update the Contract first, then reference it
from the TD.

It inherits Architecture and Solution Design. For what belongs at this level
versus those higher levels, see the zoom-stack matrix in
`workflows/activities/02-design/README.md`; if the story forces a change at a
higher level, update that governing artifact first.

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
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Design</strong></a> — Decide how to build it. Capture trade-offs, contracts, and architecture decisions.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/02-design/technical-designs/TD-{id}-{name}.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="../../../artifact-types/test/test-plan/">Test Plan</a><br><a href="../../../artifact-types/build/implementation-plan/">Implementation Plan</a></td></tr>
<tr><th>HELIX documents</th><td><a href="https://github.com/DocumentDrivenDX/helix/blob/main/docs/helix/02-design/technical-designs/TD-012-artifact-types-navigation.md"><code>docs/helix/02-design/technical-designs/TD-012-artifact-types-navigation.md</code></a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Technical Design for User Story Prompt&#10;&#10;Create a concise technical design for one user story.&#10;&#10;## Purpose&#10;&#10;Technical Design is the **story-level implementation design artifact**. Its&#10;unique job is to make one user story buildable by naming the concrete component&#10;changes, files, interfaces, data model changes, security implications, tests,&#10;rollback path, and implementation sequence.&#10;&#10;Technical Design applies shared interface contracts; it does not define them.&#10;When exact API, CLI, event, schema, config, telemetry, or adapter surface is&#10;needed, reference the governing Contract ID. If the story uncovers a missing or&#10;changed shared surface, create or update the Contract first, then reference it&#10;from the TD.&#10;&#10;It inherits Architecture and Solution Design. For what belongs at this level&#10;versus those higher levels, see the zoom-stack matrix in&#10;`workflows/activities/02-design/README.md`; if the story forces a change at a&#10;higher level, update that governing artifact first.&#10;&#10;## Reference Anchors&#10;&#10;Use these local resource summaries as grounding:&#10;&#10;- `docs/resources/google-small-cls.md` grounds bounded implementation slices&#10;  with related tests and rollback.&#10;- `docs/resources/cucumber-executable-specifications.md` grounds mapping&#10;  acceptance criteria to observable tests.&#10;&#10;## Active Concerns&#10;&#10;For each concern selected in `docs/helix/01-frame/concerns.md`, apply its declared&#10;`## Artifact Impact` (from `workflows/concerns/&lt;name&gt;/concern.md`) to THIS technical design — realize the&#10;TD-level obligations it names (domain-driven-design -&gt; aggregates/value-objects/repositories; architecture-style -&gt; layering + dependency direction; cqrs -&gt; command/query split). A selected concern whose Artifact Impact names TD&#10;but leaves no trace here is drift (reconcile-alignment Concern-&gt;Artifact Realization check).&#10;&#10;## Focus&#10;- Create a story-level artifact named `docs/helix/02-design/technical-designs/TD-XXX-[name].md`.&#10;- Realize each governing-story AC-ID (US-{n}-AC{m}) through component changes, interfaces, data, security, and tests; reference AC-IDs, do not restate AC text (ADR-009 — AC ownership lives in user-stories).&#10;- Stay on the vertical slice for the story, within the story scope defined in&#10;  the zoom-stack matrix (`workflows/activities/02-design/README.md`).&#10;- Reference Contract IDs for exact commands, endpoints, payloads, error&#10;  semantics, config keys, telemetry fields, event schemas, and adapter&#10;  signatures instead of defining those normative surfaces inline.&#10;- Keep implementation sequence and rollout or migration notes only when they affect execution.&#10;&#10;## Boundary Test&#10;&#10;See the zoom-stack matrix in `workflows/activities/02-design/README.md` for&#10;which decisions belong at the system, feature, and story levels.&#10;&#10;## Completion Criteria&#10;- The story is implementable.&#10;- Key interfaces, changes, and test coverage are explicit.&#10;- Shared interface changes are captured in Contract artifacts before this TD&#10;  references them.&#10;- The design stays compact.&#10;- The output is clearly story-level and disambiguated from a solution design.&#10;- The implementation sequence can be turned into one or more small,&#10;  reviewable changes without losing test coverage.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: TD-XXX&#10;  review:&#10;    self_hash: 081ac39c2360ed0034e2a9bc05b5932fbd2baa2930b605c2ab947bf4548a2015&#10;    deps:&#10;      FEAT-XXX: a685da86c4c18a509196cb163f264af507cc966f804db574070e108a555bdf02&#10;      SD-XXX: ea6f092342409cc3f74e945b3ae421392eb4787113b828331c0fdfab359bf86d&#10;      US-XXX: 48b416257cf7acd8b225b785edcb09a125fed67521af9c8f115ec7dc2fbf23a3&#10;    reviewed_at: &quot;2026-05-15T04:11:24Z&quot;&#10;---&#10;&#10;# Technical Design: TD-XXX-[story-name]&#10;&#10;**User Story**: [[US-XXX]] | **Feature**: [[FEAT-XXX]] | **Solution Design**: [[SD-XXX]]&#10;&#10;## Scope&#10;&#10;- Story-level design artifact&#10;- Use for one vertical slice or one bounded implementation story&#10;- Must inherit the broader approach from the parent solution design&#10;- Do not redefine cross-component architecture here; that belongs in `SD-XXX`&#10;- Governing artifacts: [User Story, Solution Design, Contracts, Concerns]&#10;&#10;## Technical Approach&#10;&#10;**Strategy**: [Brief description]&#10;&#10;**Key Decisions**:&#10;- [Decision]: [Rationale]&#10;&#10;**Trade-offs**:&#10;- [What we gain vs. lose]&#10;&#10;## Component Changes&#10;&#10;### Modified: [Component Name]&#10;- **Current State**: [What exists]&#10;- **Changes**: [What changes]&#10;- **Files**: `[path]`&#10;&#10;### New: [Component Name]&#10;- **Purpose**: [Why needed]&#10;- **Interfaces**: Input: [receives] / Output: [produces]&#10;- **Files**: `[path]`&#10;&#10;## API/Interface Design&#10;&#10;Reference the governing Contract for any exact shared API, CLI, event, schema,&#10;config, telemetry, or adapter surface. This TD may describe story-level usage&#10;and local wiring, but it must not define endpoints, commands, flags, payload&#10;fields, status codes, error semantics, or adapter signatures inline.&#10;&#10;| Surface | Governing Contract | Story-Level Usage |&#10;|---------|--------------------|-------------------|&#10;| [API/CLI/event/schema] | [CONTRACT-XXX or API-XXX] | [How this story uses it] |&#10;&#10;## Data Model Changes&#10;&#10;```sql&#10;-- New tables or schema modifications&#10;CREATE TABLE [table_name] (&#10;    id UUID PRIMARY KEY,&#10;    [columns]&#10;);&#10;```&#10;&#10;## Integration Points&#10;&#10;| From | To | Method | Data |&#10;|------|-----|--------|------|&#10;| [Source] | [Target] | [REST/Event/Direct] | [What data] |&#10;&#10;### External Dependencies&#10;- **[Service]**: [Usage] | Fallback: [If unavailable]&#10;&#10;## Security&#10;&#10;- **Authentication**: [Required auth level]&#10;- **Authorization**: [Required permissions]&#10;- **Data Protection**: [Encryption/masking]&#10;- **Threats**: [Specific threats and mitigations]&#10;&#10;## Performance&#10;&#10;- **Expected Load**: [Requests/sec, data volume]&#10;- **Response Target**: [Milliseconds]&#10;- **Optimizations**: [Caching, indexing, etc.]&#10;&#10;## Testing&#10;&#10;- [ ] **Unit**: [What to test]&#10;- [ ] **Integration**: [What integrations to test]&#10;- [ ] **Contract**: [CONTRACT/API IDs and story-specific cases to test]&#10;- [ ] **Security**: [Security scenarios]&#10;&#10;## Migration &amp; Rollback&#10;&#10;- **Backward Compatibility**: [Strategy]&#10;- **Data Migration**: [Required migrations]&#10;- **Feature Toggle**: [Enable/disable mechanism]&#10;- **Rollback**: [Steps to reverse]&#10;&#10;## Implementation Sequence&#10;&#10;1. [What to build first] -- Files: `[paths]` -- Tests: `[paths]`&#10;2. [What to build next]&#10;3. [Integration and verification]&#10;&#10;**Prerequisites**: [Dependencies that must be complete first]&#10;&#10;## Risks&#10;&#10;| Risk | Prob | Impact | Mitigation |&#10;|------|------|--------|------------|&#10;| [Risk] | H/M/L | H/M/L | [Strategy] |&#10;&#10;## Review Checklist&#10;&#10;Use this checklist when reviewing a technical design:&#10;&#10;- [ ] Each governing-story AC-ID (US-{n}-AC{m}) is realized by the technical changes (AC text is not restated here — ADR-009)&#10;- [ ] Technical approach inherits from the parent solution design — no contradictions&#10;- [ ] Key decisions have documented rationale&#10;- [ ] Trade-offs are explicit — what we gain and what we lose&#10;- [ ] Component changes clearly describe current state vs. changes&#10;- [ ] API/interface design references Contract IDs for exact shared surfaces instead of defining schemas inline&#10;- [ ] Data model changes include migration SQL&#10;- [ ] Integration points specify fallback behavior for external dependencies&#10;- [ ] Security section addresses authentication, authorization, and data protection&#10;- [ ] Performance targets are numeric with specific metrics&#10;- [ ] Testing section covers unit, integration, API, and security scenarios&#10;- [ ] Migration and rollback strategy is documented&#10;- [ ] Implementation sequence is ordered with file paths and test paths&#10;- [ ] Design is consistent with governing solution design and feature spec</code></pre></details></td></tr>
</tbody>
</table>
