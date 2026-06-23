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
