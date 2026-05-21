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
