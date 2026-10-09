---
ddx:
  id: example.concerns.depositmatch
  authoring:
    home: repo
  depends_on:
    - example.product-vision.depositmatch
    - example.prd.depositmatch
    - example.principles.depositmatch
---

# Project Concerns

Project Concerns declare active cross-cutting context for DepositMatch. They are
not principles, requirements, ADRs, test plans, or implementation tasks.

## Active Concerns

| Concern | Source | Areas | Why Active | Key Practices |
|---------|--------|-------|------------|---------------|
| `modularity-and-encapsulation` | library; baseline-policy | `areas: all` | Handwritten application source requires deliberate ownership and dependency boundaries. | Architecture maps modules, public APIs, imports, integration ownership, construction and the project boundary-check command. |
| `o11y-otel` | library | `areas: all` | Service signals and agent run diagnostics support API operations and CI failure investigation. | OTel governs telemetry; Contracts own mappings; runner captures safe evidence with quiet console and bounded retrieval. |
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
