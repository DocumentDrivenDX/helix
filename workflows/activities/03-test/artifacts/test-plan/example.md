---
ddx:
  id: example.test-plan.depositmatch
  authoring:
    home: repo
  depends_on:
    - example.prd.depositmatch
    - example.feature-specification.depositmatch.csv-import
    - example.user-story.depositmatch.upload-csv
    - example.contract.depositmatch.import-session-api
---

# Test Plan

## Strategy

**Goal**: Before implementation is accepted, prove CSV import, traceability, security boundaries, and the critical reviewer paths. P0 requirements and accepted contracts block merge when failing.

**Out of scope**: Bank feeds, accounting API sync, payroll, inventory, tax workflows, and match-scoring optimization beyond FEAT-001.

## Framework Selection & Cost

| Layer | Framework | Justification | CI Time Impact | Maintenance Burden |
|-------|-----------|---------------|----------------|--------------------|
| Contract | HTTP tests against Fastify with API-001 fixtures | Checks API behavior and problem-details errors independently of the UI | ~1 min | Low |
| Integration | API test runner, PostgreSQL 16 container, S3-compatible fake | Exercises transaction, storage, and repository boundaries together | ~3 min | Med (container startup) |
| Unit | Vitest | Fast feedback on parsing, validation, and UI state | <1 min | Low |
| E2E | Playwright, desktop browser | Only layer that proves the reviewer workflow and accessible upload controls | ~4 min | High (flaky if overused) |

**Cost/benefit summary**: About 9 minutes of CI. E2E is the costliest and most fragile, so it covers P0 happy and rejection paths only; detailed file cases are checked at the contract and integration layers.

**Baseline**: CI time measured at `3f9c2ab` (main); re-measure rather than edit.

## Critical Paths (P0)

1. Upload valid bank and invoice CSV files for one client.
2. Reject missing, oversized, or non-CSV files before parsing.
3. Preserve source file metadata for accepted uploads.
4. Keep raw financial row values out of analytics and application logs.
5. Open mapping review only after a draft session exists.

## Acceptance Criteria Layer Allocation

Every P0 acceptance criterion maps to exactly one primary test layer. Per-criterion rows (`US-<n>-AC<m>` to named tests) live in each story test plan; here, allocate criterion classes.

| AC class / source | Story Test Plan | Primary Layer | Why this layer |
|-------------------|-----------------|---------------|----------------|
| Upload acceptance and draft-session creation (US-001-AC1) | [[STP-001-upload-csv-files]] | Integration | API-001, source-file storage, and draft-session persistence must hold together |
| File rejection before parsing (US-001-AC2) | [[STP-001-upload-csv-files]] | Contract | API-001 problem-details errors are the observable boundary |
| Mapping review opens once both files land (US-001-AC3) | [[STP-001-upload-csv-files]] | E2E | Reviewer-visible navigation outcome |

## Secondary Paths (P1-P2)

- **P1**: saved mapping reuse, row-level validation, import summary confirmation.
- **P2**: large fixture performance, abandoned draft-session cleanup.

## Test Data Strategy

Versioned CSV fixtures: valid, missing amount column, malformed amount, duplicate source identifier, non-CSV upload. Factories for client, import session, and authenticated firm user. S3-compatible fake for storage; no bank or accounting API mocks in v1. No production financial data in fixtures.

## Known Gaps

Match suggestion accuracy waits for FEAT-002. Accessibility coverage starts with upload controls and expands with mapping and review stories. Fixtures are synthetic until pilot exports can be anonymized.

## Build Commands

```bash
pnpm test
pnpm test:coverage
pnpm test:e2e
```

**Blocking gate**: All P0 contract, integration, security, and E2E tests pass, and no raw financial fixture values appear in logs.

## Diagnostic Test Strategy

The diagnostic adoption slice allocates integration tests to actual OTel
receiver/mapping and trace correlation, security tests to pre-sink privacy,
and failure tests to capture/export bounds and query rotation. A service and
CLI pilot will measure diagnosis accuracy, evidence citations, time/calls/context
and overhead against agreed budgets. The slice needs its own governing story,
Contract and Story Test Plan; this example does not claim those tests ran.
