---
title: "Threat Model"
linkTitle: "Threat Model"
slug: threat-model
activity: "Frame"
artifactRole: "supporting"
weight: 24
generated: true
---

## Purpose

Structured analysis of assets, data flows, trust boundaries, STRIDE threats,
risk, mitigations, owners, and verification hooks.

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: example.threat-model.depositmatch
  depends_on:
    - example.security-requirements.depositmatch
    - example.risk-register.depositmatch
  review:
    self_hash: 28c760cff8d40eab543a794535603b0a70e333e9cd808c45c23b885e621e7602
    deps:
      example.risk-register.depositmatch: 4cfb9a77765bfa4a63e8ad9d98a656bb5c9b9bfb5c5569389cb8cf73e8c1c3ba
      example.security-requirements.depositmatch: 2a1f7efe6e55c1edaa67b76e5a11a49be55e4420d9adc456be5482d417312a43
    reviewed_at: "2026-05-15T04:11:24Z"
---

# Threat Model

**Project**: DepositMatch CSV-first reconciliation pilot
**Date**: 2026-05-12

## Executive Summary

**System Overview**: DepositMatch imports bank and invoice CSVs, normalizes
records by firm/client, suggests deposit-to-invoice matches, records reviewer
decisions, tracks exceptions, and exports review logs.

**Key Assets**: Bank deposit records, invoice records, source CSV files,
reviewer decisions, match evidence, exception notes, review-log exports,
support access, and firm/client authorization boundaries.

**Primary Threats**: Cross-firm data exposure, malicious CSV import, tampered
review logs, sensitive data in telemetry/logs, and unauthorized support access.

**Risk Level**: High

## System Description

### Boundaries and Components

**In Scope**: Browser app, API, authentication provider, CSV upload and
validation, import processing, matching service, application database, object
storage for source files, audit log, support access, and export generation.

**Out of Scope**: Bank-feed integrations, accounting-ledger writeback,
automatic approval, and client-facing portals.

**Trust Boundaries**:

- Browser to DepositMatch API
- Auth provider to DepositMatch API
- CSV upload from customer environment into DepositMatch
- API/application services to database and object storage
- Support user access into customer firm data
- Exported review logs leaving DepositMatch

### Components

| Component | Description | Trust Level |
|-----------|-------------|-------------|
| Browser App | Reviewer interface for imports, match review, exceptions, and exports | Customer-controlled client |
| DepositMatch API | Enforces authentication, authorization, validation, and workflow rules | Trusted service |
| Auth Provider | Authenticates firm staff and internal support users | External trusted service |
| Import Processor | Parses CSVs and normalizes records | Trusted service processing untrusted input |
| Matching Service | Suggests matches and confidence/evidence | Trusted service |
| Application Database | Stores normalized records, decisions, exceptions, and metadata | Restricted data store |
| Object Storage | Temporarily stores source CSV files | Restricted data store |
| Audit Log | Stores reviewer/support actions and export history | Restricted audit asset |

### Data Flows

- **External Sources**: Firm staff upload bank deposit and invoice CSVs; auth
  provider returns identity claims.
- **Internal Processing**: API validates files, import processor normalizes
  rows, matching service generates suggestions, reviewer actions update the
  database and audit log.
- **External Destinations**: Reviewers export review logs; support staff may
  view scoped records during approved support sessions.

## Assets

### Data Assets

| Asset | Classification | Confidentiality | Integrity | Availability |
|-------|---------------|-----------------|-----------|--------------|
| Bank deposit records | Restricted financial data | High | High | Medium |
| Invoice records | Restricted business/customer data | High | High | Medium |
| Source CSV files | Restricted financial data | High | Medium | Low |
| Reviewer decisions | Audit record | Medium | High | Medium |
| Review-log exports | Customer/audit record | High | High | Medium |
| Support access logs | Security audit record | Medium | High | Medium |

### System Assets

| Asset | Criticality | Dependencies |
|-------|-------------|--------------|
| Firm/client authorization boundary | Critical | Auth claims, data model, API policy |
| Import validation pipeline | High | Parser, schema validation, object storage |
| Audit log | High | Auth identity, workflow events, database |
| Export generation | Medium | Authorization, audit log, normalized records |

## STRIDE Threat Analysis

| ID | Threat | Impact | Likelihood | Risk | Mitigation |
|----|--------|--------|------------|------|------------|
| TM-S-001 | Attacker reuses or spoofs reviewer identity to access firm data | High | Medium | High | Authenticated sessions, MFA for support, session expiry, auth audit logs |
| TM-T-001 | Malicious CSV alters processing or injects spreadsheet formulas into exports | High | Medium | High | CSV validation, formula neutralization, safe export encoding |
| TM-R-001 | Reviewer denies approving or rejecting a match | Medium | Medium | Medium | Actor/timestamp/source-row audit log for every decision |
| TM-I-001 | Reviewer accesses another firm's financial records through ID manipulation | Critical | Medium | High | Firm/client authorization on every query and object access |
| TM-I-002 | Sensitive financial identifiers leak into telemetry or operational logs | High | Medium | High | Restricted telemetry schema, log redaction, security review |
| TM-D-001 | Large or malformed CSV exhausts import resources | Medium | Medium | Medium | File size limits, row limits, background processing limits, failure isolation |
| TM-E-001 | Support user escalates from support access to unrestricted customer data | High | Medium | High | Time-limited grants, least privilege, support audit logs, approval workflow |

ID prefix: S=Spoofing, T=Tampering, R=Repudiation, I=Information Disclosure, D=Denial of Service, E=Elevation of Privilege.

## Risk Assessment

**Scoring**: Impact (1-5) x Likelihood (1-5)

- **Critical (20-25)**: Immediate action required
- **High (15-19)**: Action within 30 days
- **Medium (10-14)**: Action within 90 days
- **Low (1-9)**: Monitor or accept

### Top Risks

| Risk ID | Threat | Impact | Likelihood | Score | Priority |
|---------|--------|--------|------------|-------|----------|
| TM-I-001 | Cross-firm financial data exposure | 5 | 3 | 15 | High |
| TM-T-001 | Malicious CSV tampering or export injection | 4 | 3 | 12 | Medium |
| TM-I-002 | Sensitive data in telemetry/logs | 4 | 3 | 12 | Medium |
| TM-E-001 | Support privilege escalation | 4 | 3 | 12 | Medium |

## Mitigation Strategies

### TM-I-001 - Cross-Firm Financial Data Exposure

- **Controls**: Firm/client scoping in data model, API authorization policy,
  object-storage path controls, negative authorization tests.
- **Timeline**: Before FEAT-001 test completion.
- **Owner**: Engineering Lead
- **Verification**: Authorization tests for cross-firm and cross-client access.

### TM-T-001 - Malicious CSV Tampering

- **Controls**: Validate encoding, size, required columns, parser behavior, and
  export-safe cell formatting.
- **Timeline**: During CSV import design.
- **Owner**: Engineering Lead
- **Verification**: CSV import security tests and export formula-injection
  tests.

### TM-I-002 - Sensitive Data in Telemetry/Logs

- **Controls**: Restricted telemetry schema, log redaction, code review check,
  and test fixture containing prohibited fields.
- **Timeline**: Before pilot analytics are enabled.
- **Owner**: Security Champion
- **Verification**: Telemetry schema review and automated restricted-field
  tests.

### TM-E-001 - Support Access Escalation

- **Controls**: Time-limited support grants, MFA, least privilege, approval
  record, and audit log.
- **Timeline**: Before support access to pilot data.
- **Owner**: Operations Lead
- **Verification**: Support-access workflow test and audit-log review.

## Security Controls Summary

- **Preventive**: Authentication, firm/client authorization, CSV validation,
  encryption, telemetry restrictions, support least privilege.
- **Detective**: Audit logs for reviewer decisions, exports, deletions, and
  support access.
- **Corrective**: Retention/deletion procedure, incident response, access grant
  revocation, source-file deletion.

## Assumptions and Dependencies

- Security Requirements define firm/client authorization, encryption, telemetry,
  input validation, and audit-log requirements.
- Compliance Requirements will confirm live-data obligations before pilot
  onboarding.
- The first release excludes bank feeds, ledger writeback, automatic approval,
  and client-facing portals.
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Frame</strong></a> — Define what the system should do, for whom, and how success will be measured.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/01-frame/threat-model.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="../../../artifact-types/design/solution-design/">Solution Design</a><br><a href="../../../artifact-types/test/test-plan/">Test Plan</a></td></tr>
<tr><th>Referenced by</th><td><a href="../../../artifact-types/design/adr/">ADR</a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Threat Modeling Prompt&#10;Enumerate threats by STRIDE category and assign mitigation owners.&#10;&#10;## Traceability chain&#10;&#10;This artifact&#x27;s place in the security triangle: **threats -&gt; STRIDE +&#10;mitigation owners**.&#10;- See `security-requirements` for the testable controls that mitigate each&#10;  threat.&#10;- See `compliance-requirements` for the regulations those mitigations satisfy.&#10;&#10;## Reference Anchors&#10;&#10;Use these local resource summaries as grounding:&#10;&#10;- `docs/resources/owasp-threat-modeling-cheat-sheet.md` grounds assets, data&#10;  flows, trust boundaries, STRIDE, assumptions, and mitigation mapping.&#10;- `docs/resources/owasp-asvs.md` grounds mapping threat mitigations into&#10;  verifiable security controls.&#10;&#10;## Focus&#10;- Define boundaries, assets, and trust changes first.&#10;- Analyze threats with STRIDE and assign each one a mitigation owner.&#10;- Cross-reference the control(s) in `security-requirements` that mitigate the&#10;  threat rather than restating control text.&#10;- Keep risk scoring and mitigation ownership explicit.&#10;- Treat missing boundaries, unclear assets, or unstated assumptions as findings.&#10;- Do not author control acceptance criteria. Cross-reference&#10;  `security-requirements`.&#10;- Do not analyze regulatory applicability. Cross-reference&#10;  `compliance-requirements`.&#10;&#10;## Completion Criteria&#10;- The threat surface is clear and threats are categorized by STRIDE.&#10;- Each high-risk threat has a named mitigation owner and a cross-reference to&#10;  the mitigating control in `security-requirements`.&#10;- Important threats are prioritized.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: threat-model&#10;---&#10;&#10;# Threat Model&#10;&#10;**Project**: [Project Name]&#10;**Date**: [Creation Date]&#10;&#10;## Executive Summary&#10;&#10;**System Overview**: [Brief description]&#10;**Key Assets**: [Primary assets needing protection]&#10;**Primary Threats**: [Top 3-5 threats]&#10;**Risk Level**: [Critical/High/Medium/Low]&#10;&#10;## System Description&#10;&#10;### Boundaries and Components&#10;**In Scope**: [Systems, components, data flows included]&#10;**Out of Scope**: [What is not covered]&#10;**Trust Boundaries**: [Where trust levels change]&#10;&#10;### Components&#10;| Component | Description | Trust Level |&#10;|-----------|-------------|-------------|&#10;| [Component] | [Description] | [Level] |&#10;&#10;### Data Flows&#10;- **External Sources**: [Data entering the system]&#10;- **Internal Processing**: [How data moves within]&#10;- **External Destinations**: [Where data exits]&#10;&#10;## Assets&#10;&#10;### Data Assets&#10;| Asset | Classification | Confidentiality | Integrity | Availability |&#10;|-------|---------------|-----------------|-----------|--------------|&#10;| [Asset] | [Level] | [Criticality] | [Criticality] | [Criticality] |&#10;&#10;### System Assets&#10;| Asset | Criticality | Dependencies |&#10;|-------|-------------|--------------|&#10;| [Asset] | [Level] | [Dependencies] |&#10;&#10;## STRIDE Threat Analysis&#10;&#10;For each STRIDE category (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege):&#10;&#10;| ID | Threat | Impact | Likelihood | Risk | Mitigation |&#10;|----|--------|--------|------------|------|------------|&#10;| TM-X-001 | [Threat] | [Level] | [Level] | [Level] | [Control] |&#10;&#10;ID prefix: S=Spoofing, T=Tampering, R=Repudiation, I=Information Disclosure, D=Denial of Service, E=Elevation of Privilege.&#10;&#10;## Risk Assessment&#10;&#10;**Scoring**: Impact (1-5) x Likelihood (1-5)&#10;- **Critical (20-25)**: Immediate action required&#10;- **High (15-19)**: Action within 30 days&#10;- **Medium (10-14)**: Action within 90 days&#10;- **Low (1-9)**: Monitor or accept&#10;&#10;### Top Risks&#10;| Risk ID | Threat | Impact | Likelihood | Score | Priority |&#10;|---------|--------|--------|------------|-------|----------|&#10;| [ID] | [Threat] | [1-5] | [1-5] | [Score] | [Level] |&#10;&#10;## Mitigation Strategies&#10;&#10;### [Risk ID] - [Title]&#10;- **Controls**: [Preventive, detective, corrective actions]&#10;- **Timeline**: [When to implement]&#10;- **Owner**: [Who is responsible]&#10;- **Verification**: [Security test, design review, or audit evidence]&#10;&#10;## Security Controls Summary&#10;&#10;- **Preventive**: [Authentication, authorization, encryption, input validation]&#10;- **Detective**: [Logging, monitoring, intrusion detection]&#10;- **Corrective**: [Incident response, backup/recovery, patching]&#10;&#10;## Assumptions and Dependencies&#10;- [List assumptions and external dependencies]</code></pre></details></td></tr>
</tbody>
</table>
