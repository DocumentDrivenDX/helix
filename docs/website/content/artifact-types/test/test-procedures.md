---
title: "Test Procedures"
linkTitle: "Test Procedures"
slug: test-procedures
activity: "Test"
artifactRole: "supporting"
weight: 13
generated: true
---

## Purpose

Repeatable operator procedures for running planned tests, capturing evidence,
and applying pass/fail rules consistently.

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: example.test-procedures.depositmatch
  depends_on:
    - example.test-plan.depositmatch
    - example.story-test-plan.depositmatch.upload-csv
    - example.security-tests.depositmatch
  review:
    self_hash: 3eb67c2e262b0428a56dcd882e7233e1b0cfe67d8b4c0366d3b77b594f79a6b6
    deps:
      example.security-tests.depositmatch: 00be76c876686ebff233fc3829f9df5f6458132e61f4f3d4a9243c7b3f017be8
      example.story-test-plan.depositmatch.upload-csv: ea5f25266c2652513d7c3623b18bb3b8f9ac0058379e1edcfe305107bdf6a11e
      example.test-plan.depositmatch: ba055b639a94e62d3b24f3a7ca270f78c3f17f6bae78b936d399291225d7976f
    reviewed_at: "2026-05-15T04:11:24Z"
---

# Test Procedures

## Scope

- Tests covered: DepositMatch CSV import, match review, tenant isolation,
  restricted telemetry, and audit-log behavior for the pilot.
- Operators: implementation agent, reviewer, and CI.
- Out of scope: production load testing, full penetration testing, browser
  compatibility matrix, and manual UAT scripts.

## Prerequisites

- [ ] Node dependencies installed with `npm ci`.
- [ ] Test database created and migrated.
- [ ] Fixture set loaded from `tests/fixtures/depositmatch/`.
- [ ] Two firm tenants and two clients available through factories.
- [ ] CI stores JUnit XML and coverage output as build artifacts.

## Procedures

### Contract Tests

1. Review the OpenAPI contract for imports, match queue, review decisions, and
   exports.
2. Add one contract test file per endpoint under `tests/contract/`.
3. Cover success, validation, authorization, and problem-details error paths.
4. Run the test before implementation and confirm it fails for the expected
   missing behavior.

### Integration Tests

1. Use the real parser, matcher, database repositories, and audit-log writer.
2. Mock only external identity-provider calls and object storage.
3. Load fixture CSVs through the same import service used by production code.
4. Verify normalized rows, suggested matches, reviewer decisions, and audit
   events in one flow.

### Unit Tests

1. Isolate deterministic matching rules, CSV row validation, safe CSV export,
   telemetry filtering, and authorization policy helpers.
2. Use table-driven cases for date tolerance, amount tolerance, unsupported
   encodings, malformed rows, and formula-risk prefixes.
3. Keep each assertion tied to one business or security rule.

### Security Tests

1. Seed Firm A and Firm B through factories.
2. Run tenant-isolation, formula-neutralization, telemetry, support-access, and
   review-audit tests from the security test matrix.
3. Confirm every failing security test blocks the build.

## Execution

### Local

```bash
npm test -- tests/unit
npm test -- tests/integration
npm test -- tests/contract
npm test -- tests/security
```

### CI

CI runs all suites on pull requests. A pull request cannot merge while any
contract, integration, unit, or security suite fails.

## Evidence Capture

| Procedure | Evidence | Location |
|-----------|----------|----------|
| Unit tests | Test output and coverage report | `coverage/unit/` |
| Integration tests | JUnit XML and fixture logs | `test-results/integration.xml` |
| Contract tests | JUnit XML | `test-results/contract.xml` |
| Security tests | JUnit XML and malicious fixture output | `test-results/security/` |
| CI gate | CI run URL | Pull request checks |

## Pass/Fail Rules

| Procedure | Pass | Fail |
|-----------|------|------|
| Unit tests | All deterministic rule cases pass | Any rule case fails or requires network/time dependency |
| Integration tests | Import-to-review flow produces expected records and audit events | Data mismatch, missing audit event, or fixture cannot be reproduced |
| Contract tests | API responses match contract and error schema | Status, schema, or authorization behavior diverges |
| Security tests | Threat controls behave as specified | Cross-tenant data leak, unsafe export, telemetry leak, or missing audit event |
| CI gate | Required suites pass and artifacts publish | Any required suite fails or evidence artifact is missing |

## Quality Checklist

- [x] Test names describe behavior
- [x] Tests are independent and deterministic
- [x] Assertions are specific
- [x] Managed fixtures or factories are used

## Troubleshooting

| Problem | Likely Cause | Fix |
|---------|--------------|-----|
| Tenant-isolation test passes too early | Factory data reused the same firm/client IDs | Seed distinct tenants and assert identifiers differ |
| CSV fixture fails locally only | Spreadsheet-generated fixture changed encoding | Restore canonical fixture from repository |
| Audit-log assertion is flaky | Test reads before transaction commit | Assert through service boundary or wait for committed event |
| Telemetry test reports false positive | Test logger includes fixture setup data | Scope capture to application events only |

## Handoff

- [x] Required tests are written and failing
- [x] CI is configured
- [x] Test docs are complete
- [x] Evidence and pass/fail rules are recorded
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Test</strong></a> — Define how we know it works. Plans, suites, and procedures that bind specs to implementation.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/03-test/test-procedures.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="../../../artifact-types/test/test-suites/">Test Suites</a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Test Procedures Generation Prompt&#10;&#10;Scope: procedures for writing, running, and maintaining tests — per-type writing rules, execution commands, validation checks, and evidence capture.&#10;&#10;Related:&#10;- [Test Plan](../test-plan/prompt.md) — project verification strategy these procedures execute&#10;- [Story Test Plan](../story-test-plan/prompt.md) — per-story tests these procedures apply to&#10;- [Test Suites](../test-suites/prompt.md) — suite layout these procedures operate on&#10;&#10;## Reference Anchors&#10;&#10;Use these local resource summaries as grounding:&#10;&#10;- `docs/resources/google-test-sizes.md` grounds different execution&#10;  expectations for small, medium, and large tests.&#10;- `docs/resources/fowler-practical-test-pyramid.md` grounds the balance between&#10;  fast focused tests and fewer broad confidence tests.&#10;- `docs/resources/cucumber-executable-specifications.md` grounds procedures for&#10;  acceptance examples when behavior needs shared language.&#10;&#10;## Storage Location&#10;&#10;`docs/helix/03-test/test-procedures.md`&#10;&#10;## Include&#10;&#10;- per-test-type writing rules only where they differ&#10;- local and CI execution commands&#10;- validation and quality checks&#10;- the common failure modes worth documenting&#10;- evidence capture and pass/fail rules&#10;&#10;Use template at `workflows/activities/03-test/artifacts/test-procedures/template.md`.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: test-procedures&#10;---&#10;&#10;# Test Procedures&#10;&#10;## Scope&#10;&#10;- Tests covered: [suite names, story IDs, risks, or acceptance criteria]&#10;- Operators: [who runs or reviews the procedures]&#10;- Out of scope: [tests or environments not covered here]&#10;&#10;## Prerequisites&#10;&#10;- [ ] Test framework configured&#10;- [ ] CI pipeline ready&#10;- [ ] Test data and mocks prepared&#10;&#10;## Procedures&#10;&#10;### Contract Tests&#10;&#10;1. Review the API or interface contract.&#10;2. Add one file per endpoint or command.&#10;3. Cover success, validation, auth, and error paths.&#10;4. Verify the test fails before implementation exists.&#10;&#10;### Integration Tests&#10;&#10;1. Review dependencies and data flow.&#10;2. Use the smallest realistic mix of real and mocked services.&#10;3. Cover coordination and failure handling.&#10;&#10;### Unit Tests&#10;&#10;1. Isolate business rules and edge cases.&#10;2. Keep each test focused on one behavior.&#10;3. Confirm the test fails for the right reason.&#10;&#10;## Execution&#10;&#10;### Local&#10;```bash&#10;npm test&#10;npm test -- --coverage&#10;npm test -- --watch&#10;```&#10;&#10;### CI&#10;&#10;Run the same suite on push and PRs. Block merges on failure.&#10;&#10;## Evidence Capture&#10;&#10;| Procedure | Evidence | Location |&#10;|-----------|----------|----------|&#10;| [Procedure] | [Command output, CI run, screenshot, review note] | [Path/link] |&#10;&#10;## Pass/Fail Rules&#10;&#10;| Procedure | Pass | Fail |&#10;|-----------|------|------|&#10;| [Procedure] | [Observable passing condition] | [Blocking failure condition] |&#10;&#10;## Quality Checklist&#10;&#10;- [ ] Test names describe behavior&#10;- [ ] Tests are independent and deterministic&#10;- [ ] Assertions are specific&#10;- [ ] Managed fixtures or factories are used&#10;&#10;## Troubleshooting&#10;&#10;| Problem | Likely Cause | Fix |&#10;|---------|--------------|-----|&#10;| Passing too early | Implementation or weak assertions | Recheck expectations |&#10;| Poor failure messages | Test is too broad | Split the test |&#10;| Flaky results | Time, state, or external deps | Remove dependency or isolate state |&#10;&#10;## Handoff&#10;&#10;- [ ] Required tests are written and failing&#10;- [ ] CI is configured&#10;- [ ] Test docs are complete&#10;- [ ] Evidence and pass/fail rules are recorded</code></pre></details></td></tr>
</tbody>
</table>
