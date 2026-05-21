---
ddx:
  id: example.concerns.depositmatch
  depends_on:
    - example.product-vision.depositmatch
    - example.prd.depositmatch
    - example.principles.depositmatch
  review:
    self_hash: 34738dd02d95489bcc3c00b5be15b630ae9fb15ab4f99f45d0ec1ecd1d3f1c6e
    deps:
      example.prd.depositmatch: c9c24e1694af4548a6deaad8d92059e365da110148bd9adc44d8640dff9770a4
      example.principles.depositmatch: bb37a1addd5c152f068dd5c416b6a4ae217847242d0d1b7f9e64406b671de0ed
      example.product-vision.depositmatch: 8abbb2fcb552b536f07829f57d91ef3ae8dbf52a6066955222e83d196b59b5ae
    reviewed_at: "2026-05-15T04:11:24Z"
---

# Project Concerns

Project Concerns declare active cross-cutting context for DepositMatch. They are
not principles, requirements, ADRs, test plans, or implementation tasks.

## Active Concerns

| Concern | Source | Areas | Why Active | Key Practices |
|---------|--------|-------|------------|---------------|
| `csv-import-integrity` | project-local | `area:ui`, `area:api`, `area:data` | CSV import is the only v1 ingestion path, and bad mappings would corrupt review trust. | Validate required columns, preserve source row identity, save per-client mappings, and reject ambiguous files before matching. |
| `financial-data-security` | project-local | `area:api`, `area:data`, `area:infra` | Deposit and invoice data include customer financial records. | Encrypt customer financial data at rest, exclude financial fields from analytics, and keep audit logs access-controlled. |
| `reviewer-auditability` | project-local | `area:ui`, `area:api`, `area:data` | Trust depends on visible evidence, reviewer attribution, and reversible corrections. | Show evidence before acceptance, record reviewer and timestamp, preserve correction history, and avoid destructive edits. |
| `a11y-wcag-aa` | library | `area:ui` | Reviewers may work through dense queues for long sessions. | Use accessible table controls, keyboard review actions, visible focus states, and non-color-only confidence indicators. |

## Project Overrides

| Concern | Practice | Override | Authority |
|---------|----------|----------|-----------|
| `a11y-wcag-aa` | Generic form and page guidance | Apply WCAG AA patterns specifically to reconciliation queues, import mapping tables, and exception triage controls. | Needs ADR before launch if queue interaction patterns diverge from standard controls. |

## Area Labels

This project uses the following area labels for concern scoping:

- `area:ui` — reviewer workspace, import mapping, match review, exception queue
- `area:api` — upload, matching, review, exception, export endpoints
- `area:data` — deposit, invoice, match, evidence, exception, audit storage
- `area:infra` — hosting, secrets, backups, deployment, monitoring
- `area:testing` — import fixtures, matching confidence checks, audit-log verification

## Concern Conflicts

| Conflict | Resolution |
|----------|------------|
| `csv-import-integrity` vs. reviewer speed | Reject bad files early. Do not let speed bypass validation that protects source-row identity. |
| `financial-data-security` vs. reviewer-auditability | Keep audit trails complete, but redact financial fields from analytics and restrict audit-log access. |
| `a11y-wcag-aa` vs. dense queue efficiency | Preserve keyboard speed and visual density only when focus, labels, and non-color indicators remain accessible. |
