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
