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
<tr><th>Activity</th><td><a href="/reference/glossary/activities/"><strong>Frame</strong></a> — Define what the system should do, for whom, and how success will be measured.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/01-frame/threat-model.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="/artifact-types/design/solution-design/">Solution Design</a><br><a href="/artifact-types/test/test-plan/">Test Plan</a></td></tr>
<tr><th>Referenced by</th><td><a href="/artifact-types/design/adr/">ADR</a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Threat Modeling Prompt
Document the project threat model with enough detail to drive mitigations.

## Reference Anchors

Use these local resource summaries as grounding:

- `docs/resources/owasp-threat-modeling-cheat-sheet.md` grounds assets, data
  flows, trust boundaries, STRIDE, assumptions, and mitigation mapping.
- `docs/resources/owasp-asvs.md` grounds mapping threat mitigations into
  verifiable security controls.

## Focus
- Define boundaries, assets, and trust changes first.
- Analyze threats with STRIDE and map them to controls.
- Keep risk scoring and mitigation ownership explicit.
- Treat missing boundaries, unclear assets, or unstated assumptions as findings.

## Role Boundary

Threat Model is not Security Requirements or Security Architecture. It explains
what can go wrong and where. Security Requirements state what controls must be
true; Security Architecture places those controls in the design.

## Completion Criteria
- The threat surface is clear.
- Important threats are prioritized.
- Mitigations are concrete.
- High-risk threats have owners and verification hooks.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---
ddx:
  id: threat-model
---

# Threat Model

**Project**: [Project Name]
**Date**: [Creation Date]

## Executive Summary

**System Overview**: [Brief description]
**Key Assets**: [Primary assets needing protection]
**Primary Threats**: [Top 3-5 threats]
**Risk Level**: [Critical/High/Medium/Low]

## System Description

### Boundaries and Components
**In Scope**: [Systems, components, data flows included]
**Out of Scope**: [What is not covered]
**Trust Boundaries**: [Where trust levels change]

### Components
| Component | Description | Trust Level |
|-----------|-------------|-------------|
| [Component] | [Description] | [Level] |

### Data Flows
- **External Sources**: [Data entering the system]
- **Internal Processing**: [How data moves within]
- **External Destinations**: [Where data exits]

## Assets

### Data Assets
| Asset | Classification | Confidentiality | Integrity | Availability |
|-------|---------------|-----------------|-----------|--------------|
| [Asset] | [Level] | [Criticality] | [Criticality] | [Criticality] |

### System Assets
| Asset | Criticality | Dependencies |
|-------|-------------|--------------|
| [Asset] | [Level] | [Dependencies] |

## STRIDE Threat Analysis

For each STRIDE category (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege):

| ID | Threat | Impact | Likelihood | Risk | Mitigation |
|----|--------|--------|------------|------|------------|
| TM-X-001 | [Threat] | [Level] | [Level] | [Level] | [Control] |

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
| [ID] | [Threat] | [1-5] | [1-5] | [Score] | [Level] |

## Mitigation Strategies

### [Risk ID] - [Title]
- **Controls**: [Preventive, detective, corrective actions]
- **Timeline**: [When to implement]
- **Owner**: [Who is responsible]
- **Verification**: [Security test, design review, or audit evidence]

## Security Controls Summary

- **Preventive**: [Authentication, authorization, encryption, input validation]
- **Detective**: [Logging, monitoring, intrusion detection]
- **Corrective**: [Incident response, backup/recovery, patching]

## Assumptions and Dependencies
- [List assumptions and external dependencies]</code></pre></details></td></tr>
</tbody>
</table>
