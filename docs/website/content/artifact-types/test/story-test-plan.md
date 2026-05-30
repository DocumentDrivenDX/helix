---
title: "Story Test Plan"
linkTitle: "Story Test Plan"
slug: story-test-plan
activity: "Test"
artifactRole: "core"
weight: 11
generated: true
---

## Purpose

The story test plan translates one bounded technical design into executable
verification intent before implementation starts. It maps story acceptance
criteria to concrete failing tests, names the required setup and data, and
gives Build a precise handoff for one story-sized slice.

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
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
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Test</strong></a> — Define how we know it works. Plans, suites, and procedures that bind specs to implementation.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/03-test/test-plans/STP-{id}-{name}.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="../../../artifact-types/test/test-suites/">Test Suites</a><br><a href="../../../artifact-types/build/implementation-plan/">Implementation Plan</a></td></tr>
<tr><th>Referenced by</th><td><a href="../../../artifact-types/design/technical-design/">Technical Design</a><br><a href="../../../artifact-types/build/implementation-plan/">Implementation Plan</a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Story Test Plan Generation Prompt&#10;&#10;Scope: one story&#x27;s acceptance-criteria-to-test traceability — concrete failing tests, fixtures, commands, and setup for a single bounded slice.&#10;&#10;Related:&#10;- [Test Plan](../test-plan/prompt.md) — project-wide strategy this STP inherits&#10;- [Test Suites](../test-suites/prompt.md) — where these story tests live under `tests/`&#10;- [Test Procedures](../test-procedures/prompt.md) — how tests get written and run&#10;&#10;## Reference Anchors&#10;&#10;Use these local resource summaries as grounding:&#10;&#10;- `docs/resources/cucumber-executable-specifications.md` grounds acceptance&#10;  criteria as observable executable examples.&#10;- `docs/resources/google-test-sizes.md` grounds story test levels by scope,&#10;  dependency, and execution cost.&#10;&#10;## Storage Location&#10;&#10;`docs/helix/03-test/test-plans/STP-{id}-{name}.md`&#10;&#10;## What to Include&#10;&#10;- the governing `[[US-XXX-*]]` and `[[TD-XXX-*]]` references&#10;- a tight scope statement plus explicit out-of-scope boundaries&#10;- a matrix mapping each active acceptance criterion to concrete failing tests,&#10;  keyed by the story&#x27;s **stable `US-&lt;n&gt;-AC&lt;m&gt;` ID** (this story-level matrix is&#10;  the AC↔test traceability surface; the project test plan aggregates strategy&#10;  and allocates layers but does not duplicate these rows — FEAT-008 FR-6). Each&#10;  row names the **behavior/assertion the test makes** (the observable outcome it&#10;  checks), not just a test name — a named test with no named assertion does not&#10;  show the criterion is *exercised*. Each row also names the **covering test AND&#10;  records that the test cites the AC ID** in the canonical, parseable syntax&#10;  `@covers US-&lt;n&gt;-AC&lt;m&gt;` — a test that exercises and passes but does not cite the&#10;  AC ID is `UNCITED_COVERAGE` (not covered for traceability; fix = add the&#10;  citation, not a new test), distinct from `UNTESTED`. Citation is an additional&#10;  gate on top of exercise+pass+satisfy, never a replacement&#10;- executable proof details: test file paths, commands, or named test cases&#10;- setup, fixtures, seed data, mocks, and environment assumptions&#10;- edge cases and error scenarios that the story must prove before build begins&#10;- build handoff notes that help implementation sequence the work&#10;&#10;## Minimum Quality Bar&#10;&#10;- Stay story-scoped. Do not drift into feature-wide strategy or generic testing doctrine.&#10;- Name runnable evidence, not just test categories.&#10;- Prefer one compact mapping table over repeated prose.&#10;- If an acceptance criterion is not being covered now, say why explicitly.&#10;&#10;## Boundary Test&#10;&#10;| If you are writing... | Put it in... |&#10;|---|---|&#10;| Project-wide test levels, coverage, and CI gates | Test Plan |&#10;| One story&#x27;s concrete tests, fixtures, commands, and setup | Story Test Plan |&#10;| Product behavior or acceptance criteria | User Story / Feature Specification |&#10;| Implementation file changes | Technical Design / Implementation Plan |&#10;&#10;Use template at `workflows/activities/03-test/artifacts/story-test-plan/template.md`.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: STP-XXX&#10;---&#10;&#10;# Story Test Plan: STP-XXX-[story-name]&#10;&#10;## Story Reference&#10;&#10;**User Story**: [[US-XXX-[story-name]]]&#10;**Technical Design**: [[TD-XXX-[story-name]]]&#10;**Related Solution Design**: [[SD-XXX-[feature-name]]] or N/A&#10;**Project Test Plan**: [[test-plan]]&#10;&#10;## Scope and Objective&#10;&#10;**Goal**: [What this story must prove before build starts]&#10;**Blocking Gate**: [Command or suite that must pass for this story]&#10;&#10;**In Scope**&#10;- [Bounded behavior this TP governs]&#10;&#10;**Out of Scope**&#10;- [Adjacent behavior intentionally left to another TP, feature, or future slice]&#10;&#10;## Acceptance Criteria Test Mapping&#10;&#10;This matrix is the **story-level** AC↔test traceability surface. Key each row on&#10;the story&#x27;s **stable AC ID** (`US-&lt;n&gt;-AC&lt;m&gt;`) so a specific criterion maps to a&#10;specific failing test. This story test plan owns this matrix; the project-level&#10;test plan aggregates strategy and allocates layers — it does **not** duplicate&#10;these rows (FEAT-008 FR-6).&#10;&#10;Each row must name the **behavior the test asserts** — the specific observable&#10;outcome it checks — not merely a test name. A row that lists a test name with no&#10;named assertion does not prove the criterion is *exercised*; reconcile-alignment&#10;classifies such a criterion `UNTESTED` (or `ASSERTED_UNBACKED` if the named test&#10;does not exist), not covered.&#10;&#10;Each row must also name the **covering test AND record that the test cites the&#10;AC ID** in the canonical, parseable syntax `@covers US-&lt;n&gt;-AC&lt;m&gt;` (the structured&#10;tag in the test body, name, or doc comment). The citation makes AC→test&#10;traceability machine-checkable. A test that exercises and passes but does **not**&#10;cite the AC ID is classified `UNCITED_COVERAGE` (not covered for traceability;&#10;the fix is to add the citation, not a new test) — distinct from `UNTESTED`. The&#10;citation is an *additional* gate on top of exercise+pass+satisfy, never a&#10;replacement. The canonical, parseable citation syntax is `@covers US-&lt;n&gt;-AC&lt;m&gt;`&#10;with numeric stable IDs (e.g. `@covers US-001-AC1`); `US-XXX` below is a&#10;placeholder for the numeric story id — replace `XXX` with the real number.&#10;&#10;| AC ID | Acceptance Criterion (Given/When/Then) | Failing Test(s) to Create or Run | Asserted Behavior (what the test verifies) | AC-ID Citation (`@covers`) | Test Level | File or Command | Setup / Data | Notes |&#10;|-------|----------------------------------------|----------------------------------|--------------------------------------------|----------------------------|------------|-----------------|--------------|-------|&#10;| US-001-AC1 | [Given/When/Then criterion] | `[test_name]` | [the concrete outcome the test asserts — e.g. &quot;response is 200 with body {id}&quot;] | `@covers US-001-AC1` | Unit / Integration / Contract / E2E | `tests/...` or `bash ...` | [Fixture, seed, mock] | [Edge case or sequencing note] |&#10;&#10;## Executable Proof&#10;&#10;### Primary Commands&#10;&#10;```bash&#10;[command that proves this TP]&#10;```&#10;&#10;### Planned Test Files&#10;&#10;- `tests/...`&#10;- `tests/...`&#10;&#10;### Coverage Focus&#10;&#10;- P0: [Must-pass behavior]&#10;- P1: [Important secondary behavior]&#10;&#10;## Data and Setup&#10;&#10;| Need | Required For | Source / Strategy |&#10;|------|--------------|-------------------|&#10;| [Fixture / seed / mock / env var] | [Tests] | [Where it comes from] |&#10;&#10;## Edge Cases and Failure Modes&#10;&#10;- [Boundary value or empty-state handling]&#10;- [Validation failure or invalid input]&#10;- [Dependency failure, timeout, or permission edge]&#10;&#10;## Build Handoff&#10;&#10;**Implementation Order**&#10;1. [What should be implemented first to turn the first red test green]&#10;2. [What follows once the core path passes]&#10;&#10;**Constraints**&#10;- [Constraint inherited from requirements, design, concern, or contract]&#10;&#10;**Done When**&#10;- [ ] Every in-scope acceptance criterion has passing evidence&#10;- [ ] Named commands or test files exist and run&#10;- [ ] Out-of-scope coverage remains explicitly deferred rather than silently skipped&#10;- [ ] The story can fail red before implementation and pass green after implementation&#10;&#10;## Review Checklist&#10;&#10;- [ ] References the governing story and technical design&#10;- [ ] Every active acceptance criterion maps to concrete failing tests, keyed by its stable `US-&lt;n&gt;-AC&lt;m&gt;` ID&#10;- [ ] Every AC row names the behavior/assertion the test makes, not just a test name&#10;- [ ] Every AC row names the covering test AND records its `@covers US-&lt;n&gt;-AC&lt;m&gt;` citation (canonical AC-ID syntax)&#10;- [ ] File paths, commands, or test identifiers are specific enough to execute&#10;- [ ] Setup, fixtures, mocks, and seed data are explicit&#10;- [ ] Edge cases cover real story risks rather than generic boilerplate&#10;- [ ] Scope remains bounded to one story slice&#10;- [ ] Build handoff gives implementation a usable sequence</code></pre></details></td></tr>
</tbody>
</table>
