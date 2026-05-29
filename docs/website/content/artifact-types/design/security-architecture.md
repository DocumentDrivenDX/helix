---
title: "Security Architecture"
linkTitle: "Security Architecture"
slug: security-architecture
activity: "Design"
artifactRole: "supporting"
weight: 17
generated: true
---

## Purpose

Design-level security architecture that maps trust boundaries, controls,
and security decisions to implementation and testing.

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: example.security-architecture.depositmatch
  depends_on:
    - example.security-requirements.depositmatch
    - example.threat-model.depositmatch
    - example.data-design.depositmatch
  review:
    self_hash: eefd2c6eed5574e8d2960a55ec226b7e55bd7b09b6131dc02295047c163f13b7
    deps:
      example.data-design.depositmatch: dc25da87b6288f686dfb11eae276dd334aca0dce4d6cd562c8da70b7f169a7c5
      example.security-requirements.depositmatch: 2a1f7efe6e55c1edaa67b76e5a11a49be55e4420d9adc456be5482d417312a43
      example.threat-model.depositmatch: 28c760cff8d40eab543a794535603b0a70e333e9cd808c45c23b885e621e7602
    reviewed_at: "2026-05-15T04:11:24Z"
---

# Security Architecture

**Scope**: DepositMatch CSV-first pilot
**Status**: draft

## Decision

DepositMatch uses firm/client tenancy as the primary security boundary. Every
restricted record carries `firm_id` and `client_id`; the API enforces those
boundaries on reads, writes, object access, exports, and support sessions.
Source CSVs are treated as untrusted restricted data, normalized into controlled
tables, and deleted according to retention policy. Reviewer decisions are
append-only audit events; the system may suggest matches but cannot accept
them without reviewer action.

## Trust Boundaries

| Boundary | Assets | Trust Change | Control |
|----------|--------|--------------|---------|
| Browser to API | Import files, review queue, decisions | Customer-controlled client to trusted service | Authenticated session, CSRF/API protection, authorization per request |
| Auth provider to API | Identity claims, roles | External trusted identity to app authorization | Token validation, role mapping, session expiry |
| CSV upload to import processor | Source CSV, parsed rows | Untrusted file to trusted processing | Size/encoding/schema validation, formula neutralization |
| API to database/object storage | Restricted financial data | App service to restricted stores | Service credentials, encryption, firm/client scoping |
| Support access to firm data | Customer records and audit logs | Internal user to customer tenant | MFA, approval, time-limited grants, audit log |
| Review-log export leaving system | Audit and financial references | Restricted store to customer-controlled file | Authorization, export audit event, safe CSV encoding |

## Control Mapping

| Threat / Risk | Control | Implementation Surface | Verification |
|---------------|---------|-------------------------|--------------|
| TM-I-001 cross-firm data exposure | Firm/client authorization on every restricted query and object key | API policy, data model, object storage paths | Cross-firm API/UI authorization tests |
| TM-T-001 malicious CSV or formula injection | Validate CSV before normalization and neutralize export cells | Import processor, export generator | CSV validation and export-injection tests |
| TM-I-002 sensitive telemetry/log data | Restricted telemetry schema and log redaction | Logging, analytics, code review checklist | Telemetry restricted-field test |
| TM-E-001 support privilege escalation | Time-limited support grants and MFA | Support access workflow | Support grant and audit-log test |
| Reviewer repudiates decision | Append-only review decision audit events | Review endpoint, audit log table | Audit-log test for actor/timestamp/source refs |

## Identity and Access

- Authentication: Firm staff authenticate through the configured identity
  provider. Internal support users require MFA.
- Authorization: API derives firm/client access from authenticated identity and
  assigned firm/client membership. Authorization is enforced server-side, never
  by trusting client filters.
- Session or token handling: Sessions expire; support grants are time-limited
  and require explicit approval before use.

## Data Protection

- Data at rest: PostgreSQL stores normalized restricted records and audit
  events with encryption enabled. Object storage encrypts temporary source CSVs.
- Data in transit: Browser/API and service/store traffic uses TLS.
- Secrets and key handling: Application credentials and storage keys are kept
  outside source code and rotated through the deployment platform.
- Retention: Source CSVs are deleted after normalization and retention window;
  review logs remain for pilot auditability until export/deletion policy runs.
- Telemetry: Analytics and operational logs cannot include raw bank account
  numbers, invoice details, payer identifiers, or client names.

## Logging and Monitoring

- Security events: login failures, support grant creation/use, import failures,
  export generation, deletion requests, and authorization denials.
- Alerting: alert on repeated authorization denials, support access outside
  approved windows, and import validation failure spikes.
- Audit trail: reviewer decisions and support access are attributable to actor,
  timestamp, action, firm/client scope, and source record references.

## Residual Risk

- CSV fixture coverage may miss real-world export shapes until Research Plan
  sample intake completes.
- Counsel has not yet confirmed the exact FTC Safeguards and state privacy
  obligations for live-data pilot use.
- Deterministic matching may produce ambiguous suggestions; reviewer approval
  remains the control until match quality is proven.

## Security Test Hooks

- Cross-firm and cross-client authorization tests for every restricted API.
- CSV import security tests for malformed files, unsupported encodings,
  oversized files, and formula-injection strings.
- Telemetry restricted-field test using fixture data with prohibited values.
- Support-access workflow test covering grant creation, expiry, MFA, and audit.
- Audit-log test covering accepted/rejected match decisions and export events.
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Design</strong></a> — Decide how to build it. Capture trade-offs, contracts, and architecture decisions.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/02-design/security-architecture.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="../../../artifact-types/design/technical-design/">Technical Design</a><br><a href="../../../artifact-types/test/test-plan/">Test Plan</a><br><a href="../../../artifact-types/test/security-tests/">Security Tests</a></td></tr>
<tr><th>HELIX documents</th><td><a href="https://github.com/DocumentDrivenDX/helix/blob/main/docs/helix/02-design/security-architecture.md"><code>docs/helix/02-design/security-architecture.md</code></a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Security Architecture Generation Prompt&#10;Document the security architecture patterns, trust boundaries, controls, and&#10;design-level security decisions that shape implementation and testing.&#10;&#10;## Reference Anchors&#10;&#10;Use these local resource summaries as grounding:&#10;&#10;- `docs/resources/owasp-asvs.md` grounds verifiable application security&#10;  controls.&#10;- `docs/resources/owasp-threat-modeling-cheat-sheet.md` grounds trust&#10;  boundaries, data flows, threats, assumptions, and mitigations.&#10;- `docs/resources/nist-privacy-framework.md` grounds privacy-risk controls and&#10;  data-processing constraints.&#10;&#10;## Focus&#10;- Start from security requirements and the threat model.&#10;- Define trust boundaries, control points, identity, data protection, logging,&#10;  monitoring, and residual risk.&#10;- Map threats to controls and controls to tests.&#10;- Keep the artifact at the design level; do not drift into code or deployment&#10;  instructions.&#10;&#10;## Completion Criteria&#10;- Threats and controls are linked.&#10;- Identity and access decisions are explicit.&#10;- Data protection and monitoring decisions are explicit.&#10;- The document is specific enough to guide implementation and testing.&#10;- Residual risks are named instead of hidden.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: security-architecture&#10;---&#10;&#10;# Security Architecture&#10;&#10;**Scope**: [system or subsystem]&#10;**Status**: [draft | complete]&#10;&#10;## Decision&#10;&#10;[Summarize the security architecture approach and the main security controls.]&#10;&#10;## Trust Boundaries&#10;&#10;| Boundary | Assets | Trust Change | Control |&#10;|----------|--------|--------------|---------|&#10;| [name] | [asset] | [how trust changes] | [control] |&#10;&#10;## Control Mapping&#10;&#10;| Threat / Risk | Control | Implementation Surface | Verification |&#10;|---------------|---------|-------------------------|--------------|&#10;| [risk] | [control] | [component or interface] | [test or check] |&#10;&#10;## Identity and Access&#10;&#10;- Authentication:&#10;- Authorization:&#10;- Session or token handling:&#10;&#10;## Data Protection&#10;&#10;- Data at rest:&#10;- Data in transit:&#10;- Secrets and key handling:&#10;&#10;## Logging and Monitoring&#10;&#10;- Security events:&#10;- Alerting:&#10;- Audit trail:&#10;&#10;## Residual Risk&#10;&#10;- [Known risk and why it remains]&#10;&#10;## Security Test Hooks&#10;&#10;- [Test or validation that proves the control exists]</code></pre></details></td></tr>
</tbody>
</table>
