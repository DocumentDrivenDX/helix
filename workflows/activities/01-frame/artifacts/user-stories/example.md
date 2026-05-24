---
ddx:
  id: example.user-story.depositmatch.upload-csv
  depends_on:
    - example.feature-specification.depositmatch.csv-import
  review:
    self_hash: b87b259be7a0ac9a75516d5868742aed44b6af05ab12d10aa4535a3cae24e9b6
    deps:
      example.feature-specification.depositmatch.csv-import: d85530eb091209cf9989c9cac3bc1f1063358a5b79964ca0e5e7a384fa77c44a
    reviewed_at: "2026-05-24T23:28:08Z"
---

# US-001: Upload CSV Files for a Client

**Feature**: FEAT-001 - CSV Import and Column Mapping
**Feature Requirements**: UP-01, UP-02
**Priority**: P0
**Status**: Approved

## Story

**As a** Maya, the reconciliation lead
**I want** to upload bank and invoice CSV files for one client
**So that** I can start weekly reconciliation from the client's current source
data without rebuilding the import context by hand.

## Context

Maya receives weekly bank and invoice exports from each client she manages. This
story covers the first step of FEAT-001: associating one bank deposit CSV and
one invoice export CSV with the selected client and import session. It exercises
UP-01 and UP-02 only; mapping, validation, and import summary behavior are
covered by follow-on stories.

## Walkthrough

1. Maya opens Acme Dental's reconciliation workspace and chooses to start a new
   import session.
2. DepositMatch shows bank deposit and invoice export upload controls for Acme
   Dental.
3. Maya selects `acme-bank-2026-05-08.csv` and
   `acme-invoices-2026-05-08.csv`.
4. DepositMatch accepts both CSV files, associates them with the Acme Dental
   import session, and opens the mapping review step.

## Acceptance Criteria

- [ ] **US-001-AC1** — Given Maya is viewing Acme Dental, when she uploads one
  valid bank CSV and one valid invoice CSV, then DepositMatch creates one draft
  import session for Acme Dental and opens mapping review.
- [ ] **US-001-AC2** — Given Maya is viewing Acme Dental, when she uploads a PDF
  instead of a CSV for either required file, then DepositMatch rejects the file
  before parsing and keeps the import session in draft.
- [ ] **US-001-AC3** — Given Maya has uploaded both required CSV files, when the
  files are accepted, then the import session records the client, file names,
  upload time, and source type for each file.

## Edge Cases

- **Wrong file type**: Reject non-CSV files before parsing and identify which
  file slot failed.
- **Missing second file**: Keep the import session in draft until both bank and
  invoice files are present.
- **Client changed mid-upload**: Associate accepted files only with the client
  selected at upload confirmation time.

## Test Scenarios

| Scenario | AC ID | Input / State | Action | Expected Result |
|----------|-------|---------------|--------|-----------------|
| Happy path | US-001-AC1 | Client `Acme Dental`; files `acme-bank-2026-05-08.csv` and `acme-invoices-2026-05-08.csv` | Maya uploads both files | Draft import session is created for Acme Dental and mapping review opens |
| Wrong file type | US-001-AC2 | Client `Acme Dental`; bank file `statement.pdf`; invoice file `acme-invoices-2026-05-08.csv` | Maya uploads both files | PDF is rejected before parsing; session remains draft |
| Missing invoice file | US-001-AC2 | Client `Acme Dental`; bank file only | Maya uploads the bank file | Bank file is attached to draft session; mapping review does not open |

## Dependencies

- **Stories**: None.
- **Feature Spec**: FEAT-001 - CSV Import and Column Mapping.
- **Feature Requirements**: UP-01, UP-02.
- **External**: Browser file upload support; no external APIs for v1.

## Out of Scope

- Column mapping.
- Row-level validation.
- Match suggestion generation.
- Saving accepted rows into the review queue.
