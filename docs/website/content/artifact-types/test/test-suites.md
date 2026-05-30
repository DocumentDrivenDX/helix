---
title: "Test Suites"
linkTitle: "Test Suites"
slug: test-suites
activity: "Test"
artifactRole: "supporting"
weight: 14
generated: true
---

## Purpose

Inventory of executable test suites with boundaries, coverage ownership,
commands, runtime expectations, and evidence outputs.

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: example.test-suites.depositmatch
  depends_on:
    - example.test-plan.depositmatch
    - example.test-procedures.depositmatch
    - example.security-tests.depositmatch
  review:
    self_hash: 74cfbb7fab43a7d303eeaaa1fdc676e2e2065b45a7788271f1d14b8c0647f7ea
    deps:
      example.security-tests.depositmatch: 00be76c876686ebff233fc3829f9df5f6458132e61f4f3d4a9243c7b3f017be8
      example.test-plan.depositmatch: ba055b639a94e62d3b24f3a7ca270f78c3f17f6bae78b936d399291225d7976f
      example.test-procedures.depositmatch: 3eb67c2e262b0428a56dcd882e7233e1b0cfe67d8b4c0366d3b77b594f79a6b6
    reviewed_at: "2026-05-15T04:11:24Z"
---

# Test Suite Structure

**Project**: DepositMatch CSV-first pilot
**Test Framework**: Vitest plus Playwright for one review-flow smoke path

## Suite Inventory

| Suite | Path | Scope | Runtime | Required |
|-------|------|-------|---------|----------|
| Unit | `tests/unit/` | matching rules, CSV row validation, safe export, telemetry filtering, authorization helpers | under 30s | Yes |
| Integration | `tests/integration/` | CSV import to normalized records, match suggestions, review decisions, audit writes | under 3m | Yes |
| Contract | `tests/contract/` | import, match queue, review decision, export, and problem-details API behavior | under 2m | Yes |
| Security | `tests/security/` | tenant isolation, malicious CSV, telemetry, support access, audit-log controls | under 3m | Yes |
| E2E | `tests/e2e/` | one reviewer import-to-decision smoke journey | under 5m | No for pilot red activity |

## Coverage Mapping

## Contract Tests

| Requirement / Contract | Suite | Test File | Coverage |
|------------------------|-------|-----------|----------|
| `POST /imports` | Contract | `tests/contract/imports.post.test.ts` | success, malformed CSV, unsupported encoding, unauthorized |
| `GET /matches` | Contract | `tests/contract/matches.get.test.ts` | scoped queue, empty queue, unauthorized, cross-client denial |
| `POST /matches/{id}/decision` | Contract | `tests/contract/match-decision.post.test.ts` | accept, reject, stale match, audit failure |
| `GET /exports/review-log` | Contract | `tests/contract/review-log.get.test.ts` | authorized export, empty export, safe CSV encoding |

## Integration Tests

| Flow | Suite | Test File | Coverage |
|------|-------|-----------|----------|
| CSV import normalization | Integration | `tests/integration/import-normalization.test.ts` | parser, repository, validation errors |
| Match suggestion generation | Integration | `tests/integration/match-suggestions.test.ts` | amount/date tolerance, ambiguity, no-match |
| Reviewer decision audit | Integration | `tests/integration/review-audit.test.ts` | accept/reject event persistence |
| Review-log export | Integration | `tests/integration/review-log-export.test.ts` | audit query, safe export, tenant scope |

## Unit Tests

| Rule / Module | Suite | Test File | Coverage |
|---------------|-------|-----------|----------|
| Matching tolerance | Unit | `tests/unit/matching-rules.test.ts` | exact, date tolerance, amount tolerance, ambiguous |
| CSV validation | Unit | `tests/unit/csv-validation.test.ts` | required columns, encoding, malformed row |
| Safe CSV export | Unit | `tests/unit/safe-csv-export.test.ts` | formula prefixes, quoting, nulls |
| Telemetry filtering | Unit | `tests/unit/telemetry-filter.test.ts` | prohibited fields removed |
| Authorization scope | Unit | `tests/unit/authorization-scope.test.ts` | firm/client membership rules |

## Security Tests

| Threat / Control | Suite | Test File | Coverage |
|------------------|-------|-----------|----------|
| TM-I-001 tenant isolation | Security | `tests/security/tenant-isolation.test.ts` | cross-firm and cross-client denial |
| TM-T-001 malicious CSV | Security | `tests/security/csv-formula-neutralization.test.ts` | unsafe cells neutralized at export |
| TM-I-002 restricted telemetry | Security | `tests/security/restricted-telemetry.test.ts` | prohibited values absent from logs/events |
| TM-E-001 support access | Security | `tests/security/support-access.test.ts` | grant required, expiry enforced, audit written |
| Reviewer repudiation | Security | `tests/security/review-audit-log.test.ts` | append-only decision event |

## Test Data

| Asset | Purpose |
|-------|---------|
| Fixtures | valid bank CSV, malformed CSV, unsupported encoding, malicious formula CSV |
| Factories | firm, client, user, import batch, bank transaction, invoice, match suggestion |
| Mocks | identity provider, object storage, clock |

## Execution Commands

```bash
npm test -- tests/unit
npm test -- tests/integration
npm test -- tests/contract
npm test -- tests/security
npx playwright test tests/e2e/reviewer-smoke.spec.ts
```

## Ownership

| Suite | Owner | Review Trigger |
|-------|-------|----------------|
| Unit | implementation owner | Matching, CSV, telemetry, or authorization rule changes |
| Integration | feature owner | Import, matching, audit, or export flow changes |
| Contract | API owner | OpenAPI or API handler changes |
| Security | security lead | Threat model, security architecture, or control changes |
| E2E | product/QA | Reviewer workflow or navigation changes |

## Evidence

| Suite | Evidence Output | Required in CI |
|-------|-----------------|----------------|
| Unit | `coverage/unit/` and test output | Yes |
| Integration | `test-results/integration.xml` | Yes |
| Contract | `test-results/contract.xml` | Yes |
| Security | `test-results/security/` | Yes |
| E2E | Playwright trace on failure | No for pilot red activity |

## Readiness
- [x] Suite boundaries are defined
- [x] Shared test data assets are identified
- [x] All planned suites begin in RED
- [x] Commands, owners, and evidence outputs are recorded
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Test</strong></a> — Define how we know it works. Plans, suites, and procedures that bind specs to implementation.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/03-test/test-suites.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="../../../artifact-types/deploy/deployment-checklist/">Deployment Checklist</a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Test Suites Generation Prompt&#10;&#10;Scope: suite layout under `tests/` — boundaries (contract/integration/unit/E2E), behaviors each suite owns, shared fixtures, and execution commands.&#10;&#10;Related:&#10;- [Test Plan](../test-plan/prompt.md) — project verification strategy these suites realize&#10;- [Story Test Plan](../story-test-plan/prompt.md) — per-story tests that land in these suites&#10;- [Test Procedures](../test-procedures/prompt.md) — writing, running, and maintaining the tests in these suites&#10;&#10;## Reference Anchors&#10;&#10;Use these local resource summaries as grounding:&#10;&#10;- `docs/resources/fowler-practical-test-pyramid.md` grounds suite balance across&#10;  unit, integration, and end-to-end coverage.&#10;- `docs/resources/google-test-sizes.md` grounds runtime and dependency&#10;  expectations for suite grouping.&#10;- `docs/resources/openapi-specification.md` grounds API contract suites where&#10;  interface contracts exist.&#10;&#10;## Storage Location&#10;&#10;`tests/` at the project root&#10;&#10;## Include&#10;&#10;- contract, integration, unit, and E2E boundaries&#10;- the behaviors each suite owns&#10;- required fixtures, factories, or mocks&#10;- any coverage target that matters for this stack&#10;- suite ownership, execution commands, and evidence outputs&#10;&#10;## Keep Out&#10;&#10;- generic TDD teaching text&#10;- oversized code examples&#10;- repeated explanations of why tests come first&#10;&#10;Use template at `workflows/activities/03-test/artifacts/test-suites/template.md`.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: test-suites&#10;---&#10;&#10;# Test Suite Structure&#10;&#10;**Project**: [Project Name]&#10;**Test Framework**: [Framework]&#10;&#10;## Suite Inventory&#10;&#10;| Suite | Path | Scope | Runtime | Required |&#10;|-------|------|-------|---------|----------|&#10;| Unit | `tests/unit/` | [Business rules and pure functions] | [Target] | Yes |&#10;| Integration | `tests/integration/` | [Component and persistence flows] | [Target] | Yes |&#10;| Contract | `tests/contract/` | [API/interface contract] | [Target] | Yes |&#10;| E2E | `tests/e2e/` | [Critical user journeys] | [Target] | [Yes/No] |&#10;| Security | `tests/security/` | [Threat/control checks] | [Target] | [Yes/No] |&#10;&#10;## Coverage Mapping&#10;&#10;## Contract Tests&#10;&#10;| Requirement / Contract | Suite | Test File | Coverage |&#10;|------------------------|-------|-----------|----------|&#10;| [Contract item] | Contract | [file] | [Success, validation, auth, error] |&#10;&#10;## Integration Tests&#10;&#10;| Flow | Suite | Test File | Coverage |&#10;|------|-------|-----------|----------|&#10;| [Flow] | Integration | [file] | [Coordination, persistence, failure] |&#10;&#10;## Unit Tests&#10;&#10;| Rule / Module | Suite | Test File | Coverage |&#10;|---------------|-------|-----------|----------|&#10;| [Rule] | Unit | [file] | [Cases] |&#10;&#10;## Security Tests&#10;&#10;| Threat / Control | Suite | Test File | Coverage |&#10;|------------------|-------|-----------|----------|&#10;| [Threat] | Security | [file] | [Control behavior] |&#10;&#10;## Test Data&#10;&#10;| Asset | Purpose |&#10;|-------|---------|&#10;| Fixtures | [Canonical valid, invalid, and edge payloads] |&#10;| Factories | [Generated test objects] |&#10;| Mocks | [External services or time/network controls] |&#10;&#10;## Execution Commands&#10;&#10;```bash&#10;[unit command]&#10;[integration command]&#10;[contract command]&#10;[security command]&#10;```&#10;&#10;## Ownership&#10;&#10;| Suite | Owner | Review Trigger |&#10;|-------|-------|----------------|&#10;| [Suite] | [Owner] | [When this suite changes] |&#10;&#10;## Evidence&#10;&#10;| Suite | Evidence Output | Required in CI |&#10;|-------|-----------------|----------------|&#10;| [Suite] | [Path/link] | [Yes/No] |&#10;&#10;## Readiness&#10;- [ ] Suite boundaries are defined&#10;- [ ] Shared test data assets are identified&#10;- [ ] All planned suites begin in RED&#10;- [ ] Commands, owners, and evidence outputs are recorded</code></pre></details></td></tr>
</tbody>
</table>
