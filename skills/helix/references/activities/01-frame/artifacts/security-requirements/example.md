---
ddx:
  id: example.security-requirements.depositmatch
  depends_on:
    - example.compliance-requirements.depositmatch
    - example.risk-register.depositmatch
    - example.pr-faq.depositmatch
  review:
    self_hash: 2a1f7efe6e55c1edaa67b76e5a11a49be55e4420d9adc456be5482d417312a43
    deps:
      example.compliance-requirements.depositmatch: ec7fb87a927f7e53a9c323e9af8ee73d667e4520ab596c130077d332d2783c9f
      example.pr-faq.depositmatch: 102ec8dcd77efb43d6a73143dc4dbfeb1fc95b0ab516a593166bb8b12dd70686
      example.risk-register.depositmatch: 4cfb9a77765bfa4a63e8ad9d98a656bb5c9b9bfb5c5569389cb8cf73e8c1c3ba
    reviewed_at: "2026-05-15T04:11:24Z"
---

# Security Requirements

**Project**: DepositMatch CSV-first reconciliation pilot
**Date**: 2026-05-12
**Security Champion**: Engineering Lead

## Overview

DepositMatch handles imported bank deposit records, invoice records, reviewer
decisions, and client-scoped exception notes for small bookkeeping firms. The
security goal is to keep financial data isolated by firm and client, preserve
review evidence, and prevent any automated action from bypassing reviewer
approval.

## Required Controls

### Authentication

- Firm staff and internal support users must authenticate before accessing any
  import, match, exception, or review-log data.
- Internal support access must require MFA.
- Acceptance criteria: unauthenticated requests to restricted pages and APIs
  return 401/403; support access without MFA is rejected.

### Authorization

- All records must be scoped by firm and client.
- Reviewers may access only clients assigned to their firm.
- Support access must be explicitly granted, time-limited, and logged.
- Acceptance criteria: authorization tests prove a reviewer cannot read,
  modify, export, or delete another firm's records.

### Data Protection

- Bank deposits, invoices, import files, match evidence, and review logs must
  be encrypted in transit and at rest.
- Source CSV files must be deleted according to the retention policy after
  normalized records are stored or the pilot ends.
- Acceptance criteria: storage configuration shows encryption enabled; deletion
  tests verify source-file disposal.

### Privacy

- Imported fields must be minimized to reconciliation needs.
- Analytics and product telemetry must not include bank account numbers,
  invoice line details, client names, or payer identifiers.
- Acceptance criteria: telemetry schema review confirms restricted fields are
  absent.

### Input Validation

- CSV import must reject files over the configured size limit, unsupported
  encodings, missing required columns, and rows that cannot be parsed safely.
- Acceptance criteria: import validation tests cover malformed CSVs, oversized
  files, formula-injection strings, and missing required fields.

### Logging and Audit

- Accepted matches, rejected suggestions, split deposits, exception ownership,
  exports, deletion requests, and support access must be attributable to an
  authenticated actor and timestamp.
- Logs must not store raw sensitive values when hashes or record references are
  sufficient.
- Acceptance criteria: audit-log tests verify actor, timestamp, action, source
  record reference, and no raw restricted values in operational logs.

## Requirements Matrix

| ID | Requirement | Source | Risk Level | Verification |
|----|-------------|--------|------------|--------------|
| SEC-001 | Enforce firm/client authorization on all financial records. | OWASP ASVS access control, RISK-003 | High | API and UI authorization tests |
| SEC-002 | Encrypt restricted financial data in transit and at rest. | FTC Safeguards candidate obligation | High | Infrastructure review and automated config check |
| SEC-003 | Preserve reviewer decision evidence without allowing automated approval. | PR-FAQ autonomy boundary | High | Workflow tests and audit-log review |
| SEC-004 | Exclude restricted financial data from telemetry. | NIST Privacy Framework, Compliance Requirements | High | Telemetry schema review |
| SEC-005 | Validate CSV imports before processing. | OWASP ASVS input handling, RISK-001 | Medium | Import validation test suite |
| SEC-006 | Log support access and privileged actions. | FTC Safeguards candidate obligation | Medium | Audit-log tests and support-access review |

## Compliance Requirements

**Applicable Regulations**: FTC Safeguards Rule applicability needs counsel
review; state privacy and breach-notification obligations depend on pilot
jurisdictions and data content.

**Applicable Standards**: OWASP ASVS for application-security verification;
NIST Privacy Framework as privacy-risk guidance.

- Security controls must support counsel review by producing evidence for
  access control, encryption, retention, audit logging, and vendor handling.

## Security Risks

### High-Risk Areas

1. **Cross-firm data exposure**: A reviewer or API client accesses another
   firm's records. Mitigation: enforce firm/client authorization in every query
   and test both UI and API boundaries.
2. **Sensitive data leaks into telemetry**: Financial identifiers appear in
   analytics or logs. Mitigation: define a telemetry schema and reject restricted
   fields in code review and tests.
3. **Unapproved match acceptance**: The system accepts or posts a match without
   reviewer approval. Mitigation: require explicit reviewer action and preserve
   audit evidence.

## Security Architecture Requirements

- [ ] Firm/client tenant boundary enforced in data model and service layer
- [ ] Encryption in transit and at rest
- [ ] Restricted telemetry schema
- [ ] Support-access approval and audit trail
- [ ] Dependency vulnerability scanning
- [ ] Backup and recovery tested for review logs and normalized records

## Security Testing Requirements

- [ ] Authorization tests for cross-firm and cross-client access attempts
- [ ] CSV import validation tests
- [ ] Audit-log tests for reviewer and support actions
- [ ] Telemetry restricted-field checks
- [ ] Dependency vulnerability scan in CI
- [ ] Manual security review before live-data pilot

## Assumptions and Dependencies

- Counsel will confirm whether FTC Safeguards requirements apply directly or
  contractually before live financial data is uploaded.
- Pilot research will use anonymized or synthetic sample files until data
  handling requirements are approved.
- Threat Model will analyze abuse paths for CSV import, authorization, support
  access, and review-log export.
