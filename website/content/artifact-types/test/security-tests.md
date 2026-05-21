---
title: "Security Tests"
linkTitle: "Security Tests"
slug: security-tests
activity: "Test"
artifactRole: "supporting"
weight: 12
generated: true
---

## Purpose

Security verification matrix that maps material threats and controls to
executable tests, evidence, and residual-risk decisions.

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: example.security-tests.depositmatch
  depends_on:
    - example.security-requirements.depositmatch
    - example.threat-model.depositmatch
    - example.security-architecture.depositmatch
    - example.tech-spike.depositmatch
  review:
    self_hash: 00be76c876686ebff233fc3829f9df5f6458132e61f4f3d4a9243c7b3f017be8
    deps:
      example.security-architecture.depositmatch: eefd2c6eed5574e8d2960a55ec226b7e55bd7b09b6131dc02295047c163f13b7
      example.security-requirements.depositmatch: 2a1f7efe6e55c1edaa67b76e5a11a49be55e4420d9adc456be5482d417312a43
      example.tech-spike.depositmatch: 0002d693fd2ec90fdba7005bf51eb0c34ff454274bc969ae3d1b2d9f699561e9
      example.threat-model.depositmatch: 28c760cff8d40eab543a794535603b0a70e333e9cd808c45c23b885e621e7602
    reviewed_at: "2026-05-15T04:11:24Z"
---

# Security Tests

**Project**: DepositMatch CSV-first pilot
**Date**: 2026-05-12

## Scope

- Threats covered: cross-firm data exposure, malicious CSV input, sensitive
  telemetry leakage, support privilege escalation, and reviewer repudiation.
- Required setup: two firm tenants, two client accounts, restricted fixture CSVs,
  support user with MFA, and malicious CSV fixture set from SPIKE-001.
- Out of scope: full penetration test, production WAF tuning, bank SSO
  certification, and exhaustive spreadsheet-version coverage.

## Test Matrix

| Threat / Control | Test ID | Test | Expected Result | Evidence |
|------------------|---------|------|-----------------|----------|
| TM-I-001 firm/client isolation | SEC-001 | Authenticated Firm A user requests Firm B import, match, export, and object URLs | 403 or not found; no Firm B data returned | API test output |
| TM-T-001 malicious CSV | SEC-002 | Import fixture CSVs with formula prefixes and export review log | Import succeeds or rejects safely; exported cells are neutralized | Fixture test output |
| TM-I-002 restricted telemetry | SEC-003 | Run import/review flow with prohibited values and inspect logs/events | No bank account numbers, invoice details, payer IDs, or client names in telemetry | Log assertion output |
| TM-E-001 support access | SEC-004 | Attempt support access without grant, with active grant, and after expiry | Denied, allowed, denied; all attempts audited | Workflow test output |
| Reviewer repudiation | SEC-005 | Accept and reject suggested matches through review endpoint | Append-only audit event contains actor, timestamp, action, firm/client, and source refs | DB assertion output |

## Tooling

```yaml
sast:
  tool: semgrep
  trigger: pull_request
dast:
  tool: not_in_pilot_scope
  target: none
dependency_scan:
  tool: npm_audit
```

## Key Test Cases

### SEC-001: Firm and Client Isolation

**Steps**: Seed Firm A and Firm B with separate clients and imports. Authenticate
as Firm A. Request Firm B import, match queue, export URL, and object key.
**Expected**: Every request is denied or hidden. No response body contains Firm B
record data.
**Pass Criteria**: Automated API test fails if any restricted response includes
another firm or client identifier.

### SEC-002: CSV Formula Neutralization

**Steps**: Import malicious fixture CSVs containing formula-risk prefixes. Export
the review log. Inspect exported cells.
**Expected**: Source records remain restricted; exported cells are neutralized as
text.
**Pass Criteria**: Fixture test fails if any exported cell begins with an unsafe
formula prefix after decoding.

### SEC-003: Restricted Telemetry

**Steps**: Run import and review flow with fixture values marked prohibited for
telemetry. Capture application logs and analytics events.
**Expected**: Telemetry includes event type, status, firm/client scope, and
record counts only.
**Pass Criteria**: Log assertion fails on raw account numbers, payer names,
invoice details, or client names.

## Abuse Cases

| Abuse Case | Test | Expected Control | Evidence |
|------------|------|------------------|----------|
| User changes `client_id` in API request body | SEC-001 | Server-side authorization ignores client-supplied scope | API test output |
| Reviewer uploads a CSV with spreadsheet formulas | SEC-002 | Export boundary neutralizes risky values | Fixture test output |
| Support user opens client data without approval | SEC-004 | Request is denied and audited | Workflow test output |

## Evidence

| Test ID | Command / Review | Result | Evidence Location |
|---------|------------------|--------|-------------------|
| SEC-001 | `npm test -- security/tenant-isolation.test.ts` | Red until API policy exists | `test-results/security/tenant-isolation.xml` |
| SEC-002 | `npm test -- security/csv-formula-neutralization.test.ts` | Red until export helper exists | `test-results/security/csv-formula-neutralization.xml` |
| SEC-003 | `npm test -- security/restricted-telemetry.test.ts` | Red until logging filter exists | `test-results/security/restricted-telemetry.xml` |
| SEC-004 | `npm test -- security/support-access.test.ts` | Red until support grant flow exists | `test-results/security/support-access.xml` |
| SEC-005 | `npm test -- security/review-audit-log.test.ts` | Red until audit events exist | `test-results/security/review-audit-log.xml` |

## Residual Risk

| Risk | Reason Not Fully Covered | Owner | Follow-Up |
|------|--------------------------|-------|-----------|
| Spreadsheet behavior varies outside tested tools | Pilot fixture coverage is intentionally narrow | Security lead | Expand fixtures after pilot sample intake |
| FTC/state privacy interpretation may change required controls | Counsel review is pending | Product/legal | Update compliance requirements after review |
| DAST is not configured for pilot | No stable deployed test environment yet | Engineering lead | Add DAST when staging environment exists |

## Done

- [x] High-risk threats mapped to tests
- [x] Applicable controls covered
- [x] Tests are executable and deterministic
- [x] Evidence and residual risk are recorded
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="/reference/glossary/activities/"><strong>Test</strong></a> — Define how we know it works. Plans, suites, and procedures that bind specs to implementation.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/03-test/security-tests.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="/artifact-types/test/test-plan/">Test Plan</a><br><a href="/artifact-types/iterate/security-metrics/">Security Metrics</a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Security Tests Generation
Create concise, project-specific security tests that map threats and security requirements to executable checks.

## Reference Anchors

Use these local resource summaries as grounding:

- `docs/resources/owasp-asvs.md` grounds verifiable application security
  controls.
- `docs/resources/owasp-wstg.md` grounds concrete web and API security test
  scenarios.
- `docs/resources/owasp-threat-modeling-cheat-sheet.md` grounds traceability
  from threats and mitigations to verification.

## Focus
- Cover the highest-risk threats first.
- Use a small threat-to-test matrix rather than broad prose.
- Include only the fixtures, setup, tooling, and controls that this stack actually needs.
- Treat scanner output as evidence, not as a substitute for threat-specific
  tests.

## Completion Criteria
- Relevant threat coverage is explicit.
- Expected failures and pass criteria are clear.
- The output is usable in the Red activity.
- Residual risks are named with an owner or follow-up.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---
ddx:
  id: security-tests
---

# Security Tests

**Project**: [Project Name]
**Date**: [Creation Date]

## Scope

- Threats covered: [Threat IDs or control names]
- Required setup: [Environments, accounts, fixtures]
- Out of scope: [What this suite does not test]

## Test Matrix

| Threat / Control | Test ID | Test | Expected Result | Evidence |
|------------------|---------|------|-----------------|----------|
| [Threat] | [SEC-001] | [Test case] | [Expected behavior] | [Command/output/review] |

## Tooling

```yaml
sast:
  tool: [tool]
  trigger: [when it runs]
dast:
  tool: [tool]
  target: [environment]
dependency_scan:
  tool: [tool]
```

## Key Test Cases

### SEC-TC-001: [Name]

**Steps**: [Minimal reproducible steps]
**Expected**: [Expected result]
**Pass Criteria**: [What proves the control works]

### SEC-TC-002: [Name]

**Steps**: [Minimal reproducible steps]
**Expected**: [Expected result]
**Pass Criteria**: [What proves the control works]

## Abuse Cases

| Abuse Case | Test | Expected Control | Evidence |
|------------|------|------------------|----------|
| [Abuse case] | [Test ID] | [Control behavior] | [Evidence] |

## Evidence

| Test ID | Command / Review | Result | Evidence Location |
|---------|------------------|--------|-------------------|
| [SEC-001] | [command or review step] | [pass/fail] | [path/link] |

## Residual Risk

| Risk | Reason Not Fully Covered | Owner | Follow-Up |
|------|--------------------------|-------|-----------|
| [Risk] | [Reason] | [Owner] | [Issue/artifact] |

## Done

- [ ] High-risk threats mapped to tests
- [ ] Applicable controls covered
- [ ] Tests are executable and deterministic
- [ ] Evidence and residual risk are recorded</code></pre></details></td></tr>
</tbody>
</table>
