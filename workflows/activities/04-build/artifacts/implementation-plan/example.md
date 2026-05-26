---
ddx:
  id: example.implementation-plan.depositmatch
  depends_on:
    - example.technical-design.depositmatch.upload-csv
    - example.story-test-plan.depositmatch.upload-csv
  review:
    self_hash: c470ce1b656f474335d2b2ec376a3e41e3389d5b83c7fcc1b350890b50a42d7c
    deps:
      example.story-test-plan.depositmatch.upload-csv: 20aed2c4e248a67b448b0528b49ae9b2724d5045879ddcda655ad220d1c276ed
      example.technical-design.depositmatch.upload-csv: 064c51468da1d444da9c6f65d6c2502487724ac315fa3e6c50f9bbeffd3d69b9
    reviewed_at: "2026-05-26T02:56:15Z"
---

# Build Plan

## Scope

Build the US-001 upload slice for DepositMatch CSV import. This plan covers
database migration, upload service, API route, UI upload flow, and story test
handoff. It does not cover column mapping, row validation, import confirmation,
or match generation.

**Governing Artifacts**:

- `example.user-story.depositmatch.upload-csv`
- `example.technical-design.depositmatch.upload-csv`
- `example.story-test-plan.depositmatch.upload-csv`
- `example.contract.depositmatch.import-session-api`
- `example.solution-design.depositmatch.csv-import`

## Shared Constraints

- API-001 is normative.
- Failing tests from STP-001 must exist before behavior implementation.
- Raw CSV row values must not appear in logs.
- Storage failure must not leave partial session metadata.
- Build slices should stay small enough for review and rollback.

## Implementation Slices

| Slice | Story / Area | Governing Artifacts | Depends On | Validation Gate | Notes |
|-------|---------------|---------------------|------------|-----------------|-------|
| B-001 | Database migration and repository | TD-001, STP-001 | None | `pnpm test -- importSessionRepository` | Establish persistence contract first |
| B-002 | Source-file storage adapter and upload service tests | TD-001, STP-001 | B-001 | `pnpm test -- importUploadService` | Add red tests before service implementation |
| B-003 | API route and contract tests | API-001, TD-001, STP-001 | B-001, B-002 | `pnpm test -- importSessions` | Proves success and problem-details errors |
| B-004 | React upload UI and component tests | US-001, TD-001, STP-001 | B-003 | `pnpm test -- ImportSessionUpload` | Uses API response `next.href` directly |
| B-005 | P0 E2E smoke and closeout | US-001, STP-001 | B-004 | `pnpm test:e2e -- upload-csv` | Final story evidence |

## Issue Decomposition

Story-level work is tracked as work items in the runtime's work-item store.

**Per-issue requirements**:

- Labels: `helix`, `activity:build`, `kind:build`, `story:US-001`
- References: US-001, TD-001, STP-001, API-001, this build plan
- `spec-id` pointing at the nearest governing artifact
- Blockers as dependency links

| Story / Area | Goal | Dependencies |
|--------------|------|--------------|
| US-001 / persistence | Create draft session and file metadata persistence | None |
| US-001 / upload service | Store encrypted originals and persist metadata transactionally | persistence |
| US-001 / API | Expose API-001 success and error behavior | upload service |
| US-001 / UI | Let Maya upload files and route to mapping review | API |
| US-001 / E2E | Prove happy path and rejection path in browser | UI |

## Validation Plan

- [ ] Failing tests exist before implementation starts for each slice.
- [ ] B-001 passes repository tests.
- [ ] B-002 passes upload service tests and log-redaction assertions.
- [ ] B-003 passes API-001 contract tests.
- [ ] B-004 passes UI component tests.
- [ ] B-005 passes Playwright upload smoke test.
- [ ] `pnpm test`, `pnpm test:coverage`, and `pnpm test:e2e -- upload-csv`
  pass before closing the story.

## Risks and Rollbacks

| Risk | Impact | Response | Rollback |
|------|--------|----------|----------|
| Multipart upload implementation buffers files in memory | H | Add memory regression test and stream files to storage | Revert B-002/B-003 before UI slice lands |
| API/UI validation drift | M | API contract tests remain authoritative; UI validation stays advisory | Disable `csvImportV1` UI entry point |
| Storage failure leaves partial data | H | Wrap metadata commit after storage success; test failure injection | Revert service slice and drop draft sessions created in test only |

## Exit Criteria

- [ ] Build issue set is defined with sequence and dependencies.
- [ ] Shared constraints are documented.
- [ ] Verification expectations are explicit.
- [ ] Runtime issues can be created from this plan without inventing scope.

## Review Checklist

- [ ] Governing artifacts are listed and exist on disk
- [ ] Shared constraints trace back to requirements, design, or architecture
- [ ] Build sequence has a justified ordering
- [ ] Dependencies between build steps are explicit
- [ ] Each story/area references its governing artifacts
- [ ] Issue decomposition follows tracker conventions
- [ ] Quality gates are specific and enforceable
- [ ] Risks have concrete responses
- [ ] Plan is consistent with governing test plan and technical designs
