---
title: "Test Plan"
linkTitle: "Test Plan"
slug: test-plan
activity: "Test"
artifactRole: "core"
weight: 10
generated: true
---

## Purpose

The Test Plan is the **project-level verification strategy**. Its unique job is
to define test levels, coverage targets, critical paths, data strategy,
infrastructure, sequencing, risks, and build handoff commands before
implementation starts.

It does not contain every story-specific test case. Story Test Plans own the
exact executable checks for one story. The Test Plan owns the portfolio: what
must be covered, where confidence should come from, and how CI enforces it.

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
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
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="/reference/glossary/activities/"><strong>Test</strong></a> — Define how we know it works. Plans, suites, and procedures that bind specs to implementation.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/03-test/test-plan.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="/artifact-types/build/implementation-plan/">Implementation Plan</a></td></tr>
<tr><th>Referenced by</th><td><a href="/artifact-types/frame/prd/">PRD</a></td></tr>
<tr><th>HELIX documents</th><td><a href="https://github.com/DocumentDrivenDX/helix/blob/main/docs/helix/03-test/test-plans/TP-014-helix-workflow-coverage.md"><code>docs/helix/03-test/test-plans/TP-014-helix-workflow-coverage.md</code></a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Test Plan Generation Prompt

Create the project-level test plan for the Test activity. Keep it concise, but include the minimum structure needed to drive failing tests before implementation.

## Purpose

The Test Plan is the **project-level verification strategy**. Its unique job is
to define test levels, coverage targets, critical paths, data strategy,
infrastructure, sequencing, risks, and build handoff commands before
implementation starts.

It does not contain every story-specific test case. Story Test Plans own the
exact executable checks for one story. The Test Plan owns the portfolio: what
must be covered, where confidence should come from, and how CI enforces it.

## Reference Anchors

Use these local resource summaries as grounding:

- `docs/resources/google-test-sizes.md` grounds test levels by scope,
  isolation, dependencies, and CI enforcement.
- `docs/resources/fowler-practical-test-pyramid.md` grounds balanced coverage
  across fast focused tests and fewer broad end-to-end tests.

## Storage Location

`docs/helix/03-test/test-plan.md`

## What to Include

- test levels and scope
- framework choices only where they matter
- coverage targets and critical paths
- acceptance-criteria **layer allocation** — allocate each in-scope
  `US-&lt;n&gt;-AC&lt;m&gt;` criterion class to a primary test layer and confirm every P0 is
  allocated. **Aggregate** the story test plans; do **not** duplicate their
  per-AC matrix (the STP owns that, keyed by stable AC ID — FEAT-008 FR-6).
- test data strategy
- sequencing, dependencies, and infrastructure needs
- risks that can block test execution

## Keep In Mind

- tests are the executable specification
- every test should trace to a requirement or story
- coverage targets should be risk-based and enforced, not decorative
- do not add generic testing doctrine that the template already implies

## Boundary Test

| If you are writing... | Put it in... |
|---|---|
| Overall test levels, coverage targets, data strategy, CI gates | Test Plan |
| One story&#x27;s concrete test cases and fixtures | Story Test Plan |
| Feature behavior or acceptance criteria | Feature Specification or User Story |
| Implementation sequencing for code changes | Implementation Plan |

Use template at `workflows/activities/03-test/artifacts/test-plan/template.md`.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---
ddx:
  id: TP-XXX
---

# Test Plan

## Testing Strategy

**Goals**: [Primary objective] | [Quality gates]
**Out of Scope**: [Excluded areas]
**Traceability Source**: [PRD / FEAT / US artifacts that drive the plan]

### Test Levels

| Level | Coverage Target | Priority |
|-------|-----------------|----------|
| Contract | [Target and scope] | P0/P1 |
| Integration | [Target and scope] | P0/P1 |
| Unit | [Target and scope] | P0/P1 |
| E2E | [Target and scope] | P0/P1 |

### Frameworks

| Type | Framework | Reason |
|------|-----------|--------|
| Contract | [Framework] | [Why] |
| Integration | [Framework] | [Why] |
| Unit | [Framework] | [Why] |
| E2E | [Framework] | [Why] |

## Test Data

| Type | Strategy |
|------|----------|
| Fixtures | [Static data approach] |
| Factories | [Dynamic generation] |
| Mocks | [External service mocking] |

## Coverage Requirements

| Metric | Target | Minimum | Enforcement |
|--------|--------|---------|-------------|
| Line | 80% | 70% | CI blocks |
| Critical | 100% | 100% | Required |

### Critical Paths (P0)

1. [Auth flow]
2. [Core transaction]
3. [Data persistence]
4. [Error handling]

### Secondary Paths (P1-P2)

- P1: [Secondary features] | P2: [Edge cases, rare scenarios]

## Acceptance Criteria Layer Allocation

This project test plan **aggregates** strategy across stories. It does **not**
restate the per-criterion AC↔test matrix — that lives in each story test plan
(STP), keyed by stable `US-&lt;n&gt;-AC&lt;m&gt;` IDs (FEAT-008 FR-6). Here, allocate
criterion *classes* to test layers and confirm every P0 criterion is allocated:

| AC class / source | Story Test Plan(s) | Primary Layer | Why this layer |
|-------------------|--------------------|---------------|----------------|
| [e.g. upload/validation criteria] | [[STP-XXX]] | Integration | [boundary + persistence] |
| [e.g. visible reviewer flow] | [[STP-XXX]] | E2E | [user-observable outcome] |

**Allocation rule**: no P0 acceptance criterion is left unallocated — every
`US-&lt;n&gt;-AC&lt;m&gt;` from an in-scope story maps to exactly one primary layer here and
to concrete tests in its STP. The STP owns the per-AC rows; this plan owns the
layer allocation.

## Implementation Order
1. [What must be written first and why]
2. [What follows]
3. [What can wait]

## Infrastructure

| Requirement | Specification |
|-------------|---------------|
| CI Tool | [Tool, version] |
| Test DB | [Type, seeding, cleanup] |
| Services | [Required services] |

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Flaky tests | High | Retry logic, isolation |
| Slow execution | Med | Parallelize |

**Known Gaps**: [Limitations and accepted risks]

## Build Handoff

**Commands**: `[test command]` | `[coverage command]`
**Priority**: [Recommended order]

**Blocking Gate**: [What must pass before implementation is considered done]

## Review Checklist

Use this checklist when reviewing a test plan:

- [ ] Test levels cover contract, integration, unit, and E2E with coverage targets
- [ ] Framework choices are justified and consistent with project concerns
- [ ] Critical paths (P0) are identified and have 100% coverage requirements
- [ ] Test data strategy covers fixtures, factories, and mocks
- [ ] Coverage requirements have both targets and minimums with enforcement rules
- [ ] Implementation order is justified — what must be tested first and why
- [ ] Infrastructure requirements are specific (tool versions, service deps)
- [ ] Risks include flaky test mitigation and slow execution strategies
- [ ] Known gaps are documented with accepted risk rationale
- [ ] Build handoff commands are concrete and runnable
- [ ] Test plan traces back to acceptance criteria from governing feature specs
- [ ] No untested P0 requirement — every P0 acceptance criterion has a test
- [ ] Acceptance criteria are allocated to test layers by AC class without
      duplicating the per-AC `US-&lt;n&gt;-AC&lt;m&gt;` matrix owned by the story test plans</code></pre></details></td></tr>
</tbody>
</table>
