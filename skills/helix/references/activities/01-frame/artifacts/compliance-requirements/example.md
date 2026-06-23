---
ddx:
  id: example.compliance-requirements.depositmatch
  depends_on:
    - example.opportunity-canvas.depositmatch
  review:
    self_hash: ec7fb87a927f7e53a9c323e9af8ee73d667e4520ab596c130077d332d2783c9f
    deps:
      example.opportunity-canvas.depositmatch: 75303097bfeeed0272bd68f90ef887f9a5e646a1272f9a57ccd0d899ae17497a
    reviewed_at: "2026-05-15T04:11:24Z"
---

# Compliance Requirements

**Project**: DepositMatch CSV-first reconciliation pilot
**Compliance Risk Level**: High
**Date**: 2026-05-12

## Executive Summary

**Applicable Regulations**: FTC Safeguards Rule applicability needs counsel
review; state privacy and breach-notification obligations depend on customer
jurisdictions and data subjects.
**Compliance Scope**: Imported bank deposit records, invoice records, client
business identifiers, reviewer actions, exported review logs, and vendor
handling of pilot data.
**Key Requirements**: Establish financial-data handling controls, keep audit
logs for reviewer decisions, limit access by firm and client, define retention,
and confirm legal applicability before production rollout.

## Applicable Regulations

### FTC Safeguards Rule

- **Jurisdiction**: United States
- **Applicability**: Needs counsel review
- **Assumption**: DepositMatch handles financial customer information for
  bookkeeping firms. Counsel must determine whether DepositMatch, its
  customers, or both are covered directly or through service-provider duties.
- **Key Requirements**: Written information security program, risk-based
  safeguards, access controls, vendor oversight, and evidence of ongoing
  program management if applicable.
- **Penalties**: Regulatory enforcement risk if applicable obligations are not
  met.
- **Timeline**: Confirm applicability before pilot firms upload live client
  financial data.

### State Privacy and Breach Notification Laws

- **Jurisdiction**: U.S. states where pilot firms and their clients operate
- **Applicability**: Needs counsel review
- **Assumption**: The pilot may process personal information if invoice or bank
  records include individual names, contact details, or sole-proprietor data.
- **Key Requirements**: Data minimization, access controls, deletion/retention
  handling, incident response, and breach notification workflows where
  applicable.
- **Penalties**: Varies by jurisdiction.
- **Timeline**: Confirm required notices and incident timelines before pilot.

### Industry Standards

#### NIST Privacy Framework

- **Scope**: Voluntary privacy-risk structure for data processing, governance,
  controls, communication, and protection.
- **Certification Required**: No
- **Key Controls**: Data inventory, processing purpose, access boundaries,
  retention, privacy-risk review, and validation evidence.

## Compliance Requirements Matrix

| Requirement | Reference | Description | Implementation Control | Evidence | Owner | Status |
|-------------|-----------|-------------|------------------------|----------|-------|--------|
| Confirm regulatory applicability | FTC Safeguards Rule / state laws | Determine which obligations apply to DepositMatch and pilot firms. | Counsel review memo before live-data pilot. | Signed review note or issue link | Legal / Compliance | Planned |
| Protect customer financial information | FTC Safeguards Rule candidate obligation | Restrict access to imported financial records and review logs. | Firm-scoped access control, MFA for staff, encrypted storage. | Access-control test results, architecture notes | Engineering | Planned |
| Maintain decision evidence | Contractual / auditability requirement | Preserve reviewer approvals, evidence, and exceptions. | Immutable review log with actor, timestamp, source record, and action. | Test plan and sample audit export | Product / Engineering | Planned |
| Define retention and deletion | State privacy candidate obligation | Remove pilot data when no longer needed or when contract requires it. | Retention policy and deletion procedure by firm/client. | Runbook entry and deletion test | Compliance / Engineering | Planned |
| Manage vendors | FTC Safeguards Rule candidate obligation | Ensure subprocessors protect pilot data. | Vendor list, data processing terms, security review. | Vendor assessment record | Operations | Planned |

## Data Classification and Handling

| Data Type | Classification | Regulations | Handling Requirements |
|-----------|----------------|-------------|----------------------|
| Bank deposit records | Restricted financial data | FTC Safeguards candidate, state privacy if personal data appears | Encrypt at rest and in transit, firm-scoped access, audit access. |
| Invoice records | Restricted business/customer data | State privacy if personal data appears | Minimize fields, encrypt, retain per pilot agreement. |
| Reviewer decisions | Internal audit record | Contractual/auditability | Preserve actor, timestamp, evidence, and outcome. |
| Client contact/follow-up notes | Confidential customer data | State privacy if personal data appears | Limit access, redact where possible, retention limit. |

### Data Retention

| Data Type | Retention Period | Legal Basis | Disposal Method |
|-----------|------------------|-------------|-----------------|
| Pilot import files | 90 days after pilot end unless contract requires shorter | Pilot agreement | Secure deletion from object storage and derived records. |
| Review logs | 1 year or customer contract term | Auditability and support | Export to customer, then delete per retention policy. |
| Support/debug records | 30 days | Operational troubleshooting | Delete logs and attachments after support window. |

## Applicability Gaps

| Question | Why It Matters | Owner | Due Date |
|----------|----------------|-------|----------|
| Is DepositMatch directly covered by the FTC Safeguards Rule or only contractually bound as a service provider? | Determines required compliance program scope before live-data pilot. | Legal Counsel | Before pilot onboarding |
| Which pilot jurisdictions create privacy or breach-notification duties? | Determines incident timelines, notices, and data subject handling. | Compliance Officer | Before pilot onboarding |
| Can imported CSVs include consumer personal information? | Determines classification, minimization, and deletion requirements. | Product Lead | During pilot intake |

## Privacy Requirements

### Data Subject Rights (if applicable)

| Right | Implementation | Response Time |
|-------|----------------|---------------|
| Access/export | Firm admin can export review logs and source records for a client. | Contract-defined |
| Deletion | Firm admin requests deletion by firm/client/import batch. | Contract-defined |
| Correction | Firm reviewer corrects matches through explicit review actions. | In product workflow |

### Privacy Impact Assessment

- **Data Types**: Bank deposit records, invoices, reviewer decisions, client
  notes.
- **Purpose**: Match deposits to invoices, preserve evidence, and route
  exceptions.
- **Legal Basis**: Customer contract and pilot agreement; counsel to confirm
  privacy-law basis where personal information is present.
- **Risk Level**: High because financial records may include sensitive customer
  or client information.

## Incident Response and Reporting

### Breach Notification Requirements

| Regulation | Authority Notification | Individual Notification | Timeline |
|------------|----------------------|------------------------|----------|
| FTC Safeguards Rule candidate | Counsel to confirm | Counsel to confirm | Confirm before pilot |
| State breach laws | Depends on jurisdiction | Depends on jurisdiction | Confirm before pilot |

## Compliance Risk Assessment

| Risk | Impact | Likelihood | Risk Level | Mitigation |
|------|--------|------------|------------|------------|
| Live financial data uploaded before applicability review | Regulatory and contractual exposure | Medium | High | Require counsel signoff before live-data pilot. |
| CSVs contain personal data outside expected fields | Privacy obligations expand unexpectedly | Medium | High | Field minimization, sample-data intake, and data classification review. |
| Vendor terms do not cover pilot data | Contractual compliance gap | Low | Medium | Complete vendor assessment before production-like pilot. |

## Implementation Plan

- [ ] Complete legal applicability review for FTC Safeguards and pilot
  jurisdictions.
- [ ] Define restricted-data handling requirements for bank deposits, invoices,
  and reviewer logs.
- [ ] Add firm/client access boundaries, encryption, and audit logging to
  Security Requirements.
- [ ] Document retention/deletion procedures in the Runbook.
- [ ] Add compliance evidence checks to the Test Plan.
