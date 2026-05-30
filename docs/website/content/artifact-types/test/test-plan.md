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

The project-level test plan defines the testing strategy for the full
project: test levels and scope, framework choices, coverage targets,
critical paths, test data strategy, infrastructure requirements, and
sequencing. It drives failing tests before implementation begins and
provides traceability from requirements to test execution.

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
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Test</strong></a> — Define how we know it works. Plans, suites, and procedures that bind specs to implementation.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/03-test/test-plan.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="../../../artifact-types/build/implementation-plan/">Implementation Plan</a></td></tr>
<tr><th>Referenced by</th><td><a href="../../../artifact-types/frame/prd/">PRD</a></td></tr>
<tr><th>HELIX documents</th><td><a href="https://github.com/DocumentDrivenDX/helix/blob/main/docs/helix/03-test/test-plans/TP-014-helix-workflow-coverage.md"><code>docs/helix/03-test/test-plans/TP-014-helix-workflow-coverage.md</code></a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Test Plan Generation Prompt&#10;&#10;Scope: project-level verification strategy — test levels, coverage targets, critical paths, data strategy, infrastructure, sequencing, risks, and build handoff commands.&#10;&#10;Related:&#10;- [Story Test Plan](../story-test-plan/prompt.md) — per-story AC↔test traceability&#10;- [Test Suites](../test-suites/prompt.md) — suite inventory and boundaries under `tests/`&#10;- [Test Procedures](../test-procedures/prompt.md) — runner procedures, commands, evidence capture&#10;&#10;## Reference Anchors&#10;&#10;Use these local resource summaries as grounding:&#10;&#10;- `docs/resources/google-test-sizes.md` grounds test levels by scope,&#10;  isolation, dependencies, and CI enforcement.&#10;- `docs/resources/fowler-practical-test-pyramid.md` grounds balanced coverage&#10;  across fast focused tests and fewer broad end-to-end tests.&#10;&#10;## Storage Location&#10;&#10;`docs/helix/03-test/test-plan.md`&#10;&#10;## What to Include&#10;&#10;- test levels and scope&#10;- framework choices only where they matter&#10;- coverage targets and critical paths&#10;- acceptance-criteria **layer allocation** — allocate each in-scope&#10;  `US-&lt;n&gt;-AC&lt;m&gt;` criterion class to a primary test layer and confirm every P0 is&#10;  allocated. **Aggregate** the story test plans; do **not** duplicate their&#10;  per-AC matrix (the STP owns that, keyed by stable AC ID — FEAT-008 FR-6).&#10;- test data strategy&#10;- sequencing, dependencies, and infrastructure needs&#10;- risks that can block test execution&#10;&#10;## Keep In Mind&#10;&#10;- tests are the executable specification&#10;- every test should trace to a requirement or story&#10;- coverage targets should be risk-based and enforced, not decorative&#10;- do not add generic testing doctrine that the template already implies&#10;&#10;## Boundary Test&#10;&#10;| If you are writing... | Put it in... |&#10;|---|---|&#10;| Overall test levels, coverage targets, data strategy, CI gates | Test Plan |&#10;| One story&#x27;s concrete test cases and fixtures | Story Test Plan |&#10;| Feature behavior or acceptance criteria | Feature Specification or User Story |&#10;| Implementation sequencing for code changes | Implementation Plan |&#10;&#10;Use template at `workflows/activities/03-test/artifacts/test-plan/template.md`.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: TP-XXX&#10;---&#10;&#10;# Test Plan&#10;&#10;## Testing Strategy&#10;&#10;**Goals**: [Primary objective] | [Quality gates]&#10;**Out of Scope**: [Excluded areas]&#10;**Traceability Source**: [PRD / FEAT / US artifacts that drive the plan]&#10;&#10;### Test Levels&#10;&#10;| Level | Coverage Target | Priority |&#10;|-------|-----------------|----------|&#10;| Contract | [Target and scope] | P0/P1 |&#10;| Integration | [Target and scope] | P0/P1 |&#10;| Unit | [Target and scope] | P0/P1 |&#10;| E2E | [Target and scope] | P0/P1 |&#10;&#10;### Frameworks&#10;&#10;| Type | Framework | Reason |&#10;|------|-----------|--------|&#10;| Contract | [Framework] | [Why] |&#10;| Integration | [Framework] | [Why] |&#10;| Unit | [Framework] | [Why] |&#10;| E2E | [Framework] | [Why] |&#10;&#10;## Test Data&#10;&#10;| Type | Strategy |&#10;|------|----------|&#10;| Fixtures | [Static data approach] |&#10;| Factories | [Dynamic generation] |&#10;| Mocks | [External service mocking] |&#10;&#10;## Coverage Requirements&#10;&#10;| Metric | Target | Minimum | Enforcement |&#10;|--------|--------|---------|-------------|&#10;| Line | 80% | 70% | CI blocks |&#10;| Critical | 100% | 100% | Required |&#10;&#10;### Critical Paths (P0)&#10;&#10;1. [Auth flow]&#10;2. [Core transaction]&#10;3. [Data persistence]&#10;4. [Error handling]&#10;&#10;### Secondary Paths (P1-P2)&#10;&#10;- P1: [Secondary features] | P2: [Edge cases, rare scenarios]&#10;&#10;## Acceptance Criteria Layer Allocation&#10;&#10;This project test plan **aggregates** strategy across stories. It does **not**&#10;restate the per-criterion AC↔test matrix — that lives in each story test plan&#10;(STP), keyed by stable `US-&lt;n&gt;-AC&lt;m&gt;` IDs (FEAT-008 FR-6). Here, allocate&#10;criterion *classes* to test layers and confirm every P0 criterion is allocated:&#10;&#10;| AC class / source | Story Test Plan(s) | Primary Layer | Why this layer |&#10;|-------------------|--------------------|---------------|----------------|&#10;| [e.g. upload/validation criteria] | [[STP-XXX]] | Integration | [boundary + persistence] |&#10;| [e.g. visible reviewer flow] | [[STP-XXX]] | E2E | [user-observable outcome] |&#10;&#10;**Allocation rule**: no P0 acceptance criterion is left unallocated — every&#10;`US-&lt;n&gt;-AC&lt;m&gt;` from an in-scope story maps to exactly one primary layer here and&#10;to concrete tests in its STP. The STP owns the per-AC rows; this plan owns the&#10;layer allocation.&#10;&#10;## Implementation Order&#10;1. [What must be written first and why]&#10;2. [What follows]&#10;3. [What can wait]&#10;&#10;## Infrastructure&#10;&#10;| Requirement | Specification |&#10;|-------------|---------------|&#10;| CI Tool | [Tool, version] |&#10;| Test DB | [Type, seeding, cleanup] |&#10;| Services | [Required services] |&#10;&#10;## Risks&#10;&#10;| Risk | Impact | Mitigation |&#10;|------|--------|------------|&#10;| Flaky tests | High | Retry logic, isolation |&#10;| Slow execution | Med | Parallelize |&#10;&#10;**Known Gaps**: [Limitations and accepted risks]&#10;&#10;## Build Handoff&#10;&#10;**Commands**: `[test command]` | `[coverage command]`&#10;**Priority**: [Recommended order]&#10;&#10;**Blocking Gate**: [What must pass before implementation is considered done]&#10;&#10;## Review Checklist&#10;&#10;Use this checklist when reviewing a test plan:&#10;&#10;- [ ] Test levels cover contract, integration, unit, and E2E with coverage targets&#10;- [ ] Framework choices are justified and consistent with project concerns&#10;- [ ] Critical paths (P0) are identified and have 100% coverage requirements&#10;- [ ] Test data strategy covers fixtures, factories, and mocks&#10;- [ ] Coverage requirements have both targets and minimums with enforcement rules&#10;- [ ] Implementation order is justified — what must be tested first and why&#10;- [ ] Infrastructure requirements are specific (tool versions, service deps)&#10;- [ ] Risks include flaky test mitigation and slow execution strategies&#10;- [ ] Known gaps are documented with accepted risk rationale&#10;- [ ] Build handoff commands are concrete and runnable&#10;- [ ] Test plan traces back to acceptance criteria from governing feature specs&#10;- [ ] No untested P0 requirement — every P0 acceptance criterion has a test&#10;- [ ] Acceptance criteria are allocated to test layers by AC class without&#10;      duplicating the per-AC `US-&lt;n&gt;-AC&lt;m&gt;` matrix owned by the story test plans</code></pre></details></td></tr>
</tbody>
</table>
