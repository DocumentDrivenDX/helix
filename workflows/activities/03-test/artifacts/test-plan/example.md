---
ddx:
  id: example.test-plan.depositmatch
  depends_on:
    - example.prd.depositmatch
    - example.feature-specification.depositmatch.csv-import
    - example.user-story.depositmatch.upload-csv
    - example.contract.depositmatch.import-session-api
  review:
    self_hash: ba055b639a94e62d3b24f3a7ca270f78c3f17f6bae78b936d399291225d7976f
    deps:
      example.contract.depositmatch.import-session-api: 0f6f77f7dca5d1d05590440459fe958f9620857ed3968839e537655dce27cd04
      example.feature-specification.depositmatch.csv-import: d85530eb091209cf9989c9cac3bc1f1063358a5b79964ca0e5e7a384fa77c44a
      example.prd.depositmatch: c9c24e1694af4548a6deaad8d92059e365da110148bd9adc44d8640dff9770a4
      example.user-story.depositmatch.upload-csv: ae65ec934b10e577641772c711eafec5a15dbb5854327d8240307341e2053f66
    reviewed_at: "2026-05-15T04:11:24Z"
---

# Test Plan

## Testing Strategy

**Goals**: Prove CSV import, traceability, security boundaries, and critical
reviewer paths before implementation is accepted. | **Quality gates**: P0
requirements and accepted contracts block merge when failing.
**Out of Scope**: Bank feeds, accounting API sync, payroll, inventory, tax
workflows, and match-scoring optimization beyond FEAT-001.
**Traceability Source**: PRD P0 requirements, FEAT-001, US-001, API-001, and
active concerns.

### Test Levels

| Level | Coverage Target | Priority |
|-------|-----------------|----------|
| Contract | 100% of API-001 success and error semantics | P0 |
| Integration | 100% of FEAT-001 import-session persistence and source-file storage paths | P0 |
| Unit | 90% line coverage for import upload, mapping, validation, and evidence services; 100% branch coverage for validation rules | P0/P1 |
| E2E | One happy path and one rejection path for each P0 reviewer import workflow | P0 |

### Frameworks

| Type | Framework | Reason |
|------|-----------|--------|
| Contract | HTTP contract tests against Fastify with API-001 fixtures | Verifies independent API behavior and problem-details errors |
| Integration | API test runner with PostgreSQL 16 test container and S3-compatible fake | Exercises transaction, storage, and repository boundaries |
| Unit | Vitest for TypeScript services and React components | Fast feedback on parsing, validation, and UI state |
| E2E | Playwright desktop browser tests | Verifies reviewer import workflow and accessible upload controls |

## Test Data

| Type | Strategy |
|------|----------|
| Fixtures | Versioned CSV fixtures for valid Acme Dental imports, missing amount column, malformed amount, duplicate source identifier, and non-CSV upload |
| Factories | Client, import session, and authenticated firm-user factories for API and integration tests |
| Mocks | S3-compatible fake for source-file storage; no bank or accounting API mocks in v1 |

## Coverage Requirements

| Metric | Target | Minimum | Enforcement |
|--------|--------|---------|-------------|
| Service line coverage | 90% | 85% | CI blocks on `pnpm test:coverage` |
| Validation branch coverage | 100% | 100% | CI blocks validation package coverage |
| Contract coverage | 100% API-001 success/errors | 100% | CI blocks contract test suite |
| Critical reviewer workflows | 100% P0 happy/rejection paths | 100% | CI blocks Playwright smoke suite |

### Critical Paths (P0)

1. Upload valid bank and invoice CSV files for one client.
2. Reject missing, oversized, or non-CSV files before parsing.
3. Preserve source file metadata for accepted uploads.
4. Keep raw financial row values out of analytics and application logs.
5. Open mapping review only after a draft session is created.

### Secondary Paths (P1-P2)

- P1: saved mapping reuse, row-level validation, import summary confirmation.
- P2: large fixture performance and abandoned draft-session cleanup.

## Implementation Order

1. Contract tests for API-001 success and problem-details errors.
2. Repository and storage integration tests for draft sessions and source files.
3. Unit tests for upload service and UI upload state.
4. Playwright P0 upload happy path and rejection path.
5. Coverage gate wiring and fixture documentation.

## Infrastructure

| Requirement | Specification |
|-------------|---------------|
| CI Tool | GitHub Actions with Node 20 and PostgreSQL 16 service |
| Test DB | PostgreSQL 16 container; recreate schema per integration suite |
| Services | S3-compatible fake for source-file storage; Playwright browser install |
| Secrets | Test-only storage credentials; no production financial data in fixtures |

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| CSV fixtures become unrealistic | High | Collect pilot exports and add anonymized fixtures before paid launch |
| E2E upload tests become flaky | Med | Keep E2E suite to P0 paths; validate detailed file cases at contract/integration layers |
| Coverage target encourages shallow tests | Med | Require traceability to FEAT/US/API IDs in test names or metadata |

**Known Gaps**: Match suggestion accuracy tests wait for FEAT-002. Accessibility
coverage starts with upload controls and expands during mapping/review stories.

## Build Handoff

**Commands**: `pnpm test` | `pnpm test:coverage` | `pnpm test:e2e`
**Priority**: API contract tests first, then integration tests, then unit/UI,
then P0 E2E smoke.

**Blocking Gate**: All P0 contract, integration, security, and E2E tests pass;
coverage minimums hold; no raw financial fixture values appear in logs.
