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
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Test Plan Generation Prompt&#10;&#10;Scope: project-level verification strategy — goal, framework choices with cost, critical paths, data strategy, known gaps, and build commands.&#10;&#10;Related:&#10;- [Story Test Plan](../story-test-plan/prompt.md) — per-story AC↔test traceability&#10;- [Test Suites](../test-suites/prompt.md) — suite inventory and boundaries under `tests/`&#10;- [Test Procedures](../test-procedures/prompt.md) — runner procedures, commands, evidence capture&#10;&#10;## Reference Anchors&#10;&#10;Use these local resource summaries as grounding:&#10;&#10;- `docs/resources/google-test-sizes.md` grounds test levels by scope,&#10;  isolation, dependencies, and CI enforcement.&#10;- `docs/resources/fowler-practical-test-pyramid.md` grounds balanced coverage&#10;  across fast focused tests and fewer broad end-to-end tests.&#10;&#10;## Storage Location&#10;&#10;`docs/helix/03-test/test-plan.md`&#10;&#10;## What to Include&#10;&#10;- the goal: what must be true to ship, and what is out of scope&#10;- framework choice per layer, with why, CI time, and maintenance burden&#10;- critical paths (P0)&#10;- acceptance-criteria **layer allocation**: map each in-scope `US-&lt;n&gt;-AC&lt;m&gt;`&#10;  criterion class to one primary layer and confirm every P0 is allocated (the&#10;  STP owns the per-AC rows)&#10;- test data strategy&#10;- known gaps and accepted risks&#10;- build commands and the blocking gate&#10;&#10;Do not hand-maintain test counts or timings. If you cite a baseline, pin it to a commit.&#10;&#10;## Keep In Mind&#10;&#10;- tests are the executable specification&#10;- every test should trace to a requirement or story&#10;- put effort where failure costs most; add coverage numbers only when CI enforces them&#10;- do not add generic testing doctrine that the template already implies&#10;&#10;## Boundary Test&#10;&#10;| If you are writing... | Put it in... |&#10;|---|---|&#10;| Overall strategy, framework choices, critical paths, CI gates | Test Plan |&#10;| One story&#x27;s concrete test cases and fixtures | Story Test Plan |&#10;| Feature behavior or acceptance criteria | Feature Specification or User Story |&#10;| Implementation sequencing for code changes | Implementation Plan |&#10;&#10;Use template at `workflows/activities/03-test/artifacts/test-plan/template.md`.&#10;&#10;## Boundary Verification&#10;&#10;For handwritten source, apply `modularity-and-encapsulation`. Name the actual&#10;project-local dependency checker command and exercise permitted imports and a&#10;forbidden import that must fail; cover cycles/private access where supported.&#10;Verify invariant protection through public APIs, review public vendor-type leakage,&#10;and test core isolation/substitution when promised by the selected style. Record&#10;unsupported static checks as named semantic review obligations; a presence check&#10;or green import graph does not prove encapsulation. Existing-debt baselines may&#10;allow unchanged violations but must reject new violations.&#10;&#10;## Diagnostic Test Strategy&#10;&#10;When `o11y-otel` applies, allocate the template&#x27;s diagnostic test layers and&#10;project-owned budgets. Require real receiver evidence and privacy/failure proof;&#10;put exact assertions and runnable tests in Story Test Plans. Use the pilot in&#10;`workflows/references/agent-diagnostics.md`; distinguish planned proof from&#10;executed measurements. Service-only expectations are conditional on actual&#10;surfaces, not on whether an agent edits the project.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: TP-XXX&#10;  authoring:&#10;    home: repo&#10;---&#10;&#10;# Test Plan&#10;&#10;## Strategy&#10;&#10;**Goal**: [What must be true for the feature to be production-ready?]&#10;&#10;**Out of scope**: [Behaviors not covered by this plan]&#10;&#10;## Framework Selection &amp; Cost&#10;&#10;| Layer | Framework | Justification | CI Time Impact | Maintenance Burden |&#10;|-------|-----------|---------------|---------------|--------------------|&#10;| Contract | [Framework] | [Why this framework for API contract tests] | [~] | [~] |&#10;| Unit | [Framework] | [Why this framework for unit tests] | [2min / ~neutral / +30%] | [Low/Med/High] |&#10;| Integration | [Framework] | [Why this framework for integration] | [~] | [~] |&#10;| E2E | [Framework] | [Why this framework for e2e] | [~] | [~] |&#10;&#10;**Cost/benefit summary**: [Total CI time impact, maintenance vs. confidence tradeoff, decision rationale]&#10;&#10;**Baseline**: [Only if you cite a measurement: what was measured and the commit it was taken at. Never hand-maintain counts; re-measure.]&#10;&#10;## Critical Paths (P0)&#10;&#10;These must pass before shipping:&#10;&#10;1. [Path description]&#10;2. [Path description]&#10;3. [Path description]&#10;&#10;## Acceptance Criteria Layer Allocation&#10;&#10;Every P0 acceptance criterion maps to exactly one primary test layer. Per-criterion rows (`US-&lt;n&gt;-AC&lt;m&gt;` to named tests) live in each story test plan; here, allocate criterion classes.&#10;&#10;| AC class / source | Story Test Plan | Primary Layer | Why this layer |&#10;|-------------------|-----------------|---------------|----------------|&#10;| [e.g. upload/validation criteria] | [[STP-XXX]] | [Integration] | [what boundary it proves] |&#10;&#10;## Secondary Paths (P1-P2)&#10;&#10;- **P1**: [Feature coverage]&#10;- **P2**: [Edge cases]&#10;&#10;## Test Data Strategy&#10;&#10;[How do you seed test data? Static fixtures, factories, production snapshots?]&#10;&#10;## Known Gaps&#10;&#10;[Accepted risks, deferred coverage, infrastructure constraints]&#10;&#10;## Build Commands&#10;&#10;```bash&#10;[test command]&#10;[coverage command]&#10;```&#10;&#10;**Blocking gate**: [What must pass before the build is considered complete]&#10;&#10;&lt;!-- For source projects, name the real boundary-check command, allowed/forbidden&#10;import controls, supported cycle/private-access checks, invariant tests and&#10;remaining semantic review obligations. Apply the modularity-and-encapsulation&#10;baseline; do not equate populated document fields with proven boundaries. --&gt;&#10;&#10;## Diagnostic Test Strategy (when applicable)&#10;&#10;For selected `o11y-otel` practices, allocate layers and budgets for real OTel&#10;receiver/mapping/correlation proof, duplicate ingestion, pre-sink privacy,&#10;bounded capture/export failures and authorized retrieval. Define service/CLI&#10;agent-pilot ground truth and diagnosis/evidence/time/call/context measurements&#10;against a baseline. Exact tests, commands and story AC rows belong in Story&#10;Test Plans. JSONL parsing alone does not establish an OTel integration.</code></pre></details></td></tr>
</tbody>
</table>
