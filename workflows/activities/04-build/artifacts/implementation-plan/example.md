---
ddx:
  id: example.implementation-plan.depositmatch
  authoring:
    home: repo
  depends_on:
    - example.technical-design.depositmatch.upload-csv
    - example.story-test-plan.depositmatch.upload-csv
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

## Execution Contract

The user authorizes implementation separately from plan readiness. Execute the
ordered slices through their verification gates and the goal's exit criteria.
A slice is a reviewable change, not necessarily a separately scheduled issue.
Stay within Scope; stop for authority conflicts, missing authorization, or
concrete blockers requiring a decision. Ordinary debugging remains in scope.

## Continuation Evidence

On interruption, record plan revision, completed slice IDs with evidence,
remaining slices, decisions, blockers, and the next action alongside this plan.
On resume, reconcile the record with the diff and tests before continuing.
When tracking is explicitly selected, its store owns claims and live status.

## Optional Tracking

Use work items only when requested or required by the active execution contract.
Prefer one item for this goal; split for independent scheduling, ownership,
parallel execution, or deferred work. Follow the selected runtime's acceptance,
dependency, audit, and closure requirements. Do not discover tracker binaries.

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

Plan readiness requires defined scope, ordered slices, shared constraints, and
explicit verification gates. These planning checks do not establish completion.
Execution is complete only when:

- [ ] US-001 upload succeeds end to end; governed rejection and storage-failure paths pass STP-001 tests.
- [ ] Every required slice validation gate and the final integration gate pass.
- [ ] Acceptance evidence is recorded; no required step or material blocker remains.
- [ ] Required canonical documentation and review are complete.
- [ ] Any explicitly selected runtime's audit and closure requirements are met.

## Diagnostic Evidence Sequencing

A diagnostic adoption slice requires its own story, Contract and Story Test Plan
before implementation. Sequence logger/capture wiring, actual OTel receiver and
privacy/failure proof, then service/CLI agent diagnosis. Runtime closeout records
run/attempt, safe manifest/receiver evidence, verification outcome and capture
limits. This example defines sequencing and does not report pilot completion.
