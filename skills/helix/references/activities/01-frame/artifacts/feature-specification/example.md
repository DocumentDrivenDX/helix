---
ddx:
  id: example.feature-specification.depositmatch.csv-import
  depends_on:
    - example.product-vision.depositmatch
    - example.prd.depositmatch
    - example.principles.depositmatch
    - example.concerns.depositmatch
  review:
    self_hash: d85530eb091209cf9989c9cac3bc1f1063358a5b79964ca0e5e7a384fa77c44a
    deps:
      example.concerns.depositmatch: 34738dd02d95489bcc3c00b5be15b630ae9fb15ab4f99f45d0ec1ecd1d3f1c6e
      example.prd.depositmatch: c9c24e1694af4548a6deaad8d92059e365da110148bd9adc44d8640dff9770a4
      example.principles.depositmatch: bb37a1addd5c152f068dd5c416b6a4ae217847242d0d1b7f9e64406b671de0ed
      example.product-vision.depositmatch: 8abbb2fcb552b536f07829f57d91ef3ae8dbf52a6066955222e83d196b59b5ae
    reviewed_at: "2026-05-15T04:11:24Z"
---

# Feature Specification: FEAT-001 - CSV Import and Column Mapping

**Feature ID**: FEAT-001
**Status**: Specified
**Priority**: P0
**Owner**: Product and Engineering

## Overview

CSV Import and Column Mapping implements the PRD requirement to import bank
deposit CSV files and invoice export CSV files for a client. The feature gives
reviewers a dependable way to bring source data into DepositMatch while
preserving the source-row identity needed for matching evidence and audit logs.

## Ideal Future State

Maya uploads bank and invoice exports for a client, confirms the saved column
mapping, and sees a clean import summary before matching begins. If a file is
ambiguous or missing required columns, DepositMatch explains the issue before
any rows enter the review queue. Source rows remain traceable through matching,
exceptions, reports, and corrections.

## Problem Statement

- **Current situation**: Reviewers reconcile deposits from bank exports,
  invoice exports, spreadsheets, and email notes.
- **Pain points**: CSV layouts differ by client and system. A silent mapping
  error can make match suggestions look plausible while pointing to the wrong
  source row.
- **Desired outcome**: Reviewers can import valid files quickly and trust that
  invalid files stop before they pollute the matching workflow.

## Functional Areas

| Area | User question or job | Feature responsibility |
|------|----------------------|------------------------|
| Upload | Can I provide the bank and invoice files for this client? | Accept CSV files and associate them with one client and import session. |
| Mapping | Does DepositMatch understand the columns in these files? | Require mappings for amount, date, identifier, and source-specific optional fields. |
| Validation | Are these files safe to import? | Detect missing columns, duplicate source identifiers, malformed dates, and invalid amounts before import. |
| Import Summary | What happened during import? | Show accepted rows, rejected rows, warnings, and saved mappings. |
| Traceability | Can every later match point back to source data? | Preserve file identity, row number, source identifier, and normalized values. |

## Requirements

### Functional Requirements by Area

#### Upload

UP-01. The system must accept one bank deposit CSV and one invoice export CSV
for a selected client and import session.

UP-02. The system must reject non-CSV files before parsing.

#### Mapping

MAP-01. The system must require mappings for amount, date, and source
identifier in both bank and invoice files.

MAP-02. The system must save a confirmed mapping for reuse on the next import
for the same client and source type.

MAP-03. The system must let the reviewer adjust a saved mapping before rows
are imported.

#### Validation

VAL-01. The system must reject an import when required mapped columns are
missing from either file.

VAL-02. The system must reject rows with invalid amounts, invalid dates, or
duplicate source identifiers within the same file.

VAL-03. The system must show rejected rows with the source row number and a
plain-language reason.

#### Import Summary

SUM-01. The system must show accepted row count, rejected row count, warning
count, and saved mapping status before the reviewer proceeds to matching.

SUM-02. The system must not create match suggestions until the reviewer
confirms the import summary.

#### Traceability

TRC-01. The system must preserve source file name, import session, row number,
source identifier, normalized amount, and normalized date for every accepted
deposit and invoice row.

TRC-02. The system must make preserved source-row fields available to match
evidence, exception records, and reconciliation exports.

### Acceptance Criteria

| Requirement | Scenario | Given | When | Then |
|-------------|----------|-------|------|------|
| UP-01 | Valid bank and invoice exports | Maya selected Acme Dental and chose two valid CSV files | She uploads both files | DepositMatch opens mapping review for the import session |
| MAP-02 | Reused client mapping | Acme Dental has a saved bank mapping | Maya uploads the same source type next week | The saved mapping is preselected and editable before import |
| VAL-01 | Missing required column | The invoice file lacks a mapped amount column | Maya confirms the mapping | The import is rejected before rows are accepted |
| VAL-03 | Row-level validation error | A bank row has `12OO.00` in the amount column | Maya validates the file | The row is rejected with its source row number and reason |
| SUM-02 | Reviewer has not confirmed summary | Validation completed with accepted and rejected rows | Matching would otherwise begin | No match suggestions are created until Maya confirms the summary |
| TRC-02 | Accepted row appears in evidence | A deposit row was accepted during import | Maya later reviews a suggested match | Match evidence includes the source file, row number, amount, date, and identifier |

### Non-Functional Requirements

- **Performance**: Validate and summarize files totaling 10,000 rows in under
  5 seconds on the supported production environment.
- **Security**: Do not send raw financial row values to analytics or logging
  systems.
- **Reliability**: Import confirmation must be atomic; either all accepted rows
  for the session are recorded with traceability fields or none are.
- **Usability**: All validation errors must identify the file, row number, and
  field in plain language.

## User Stories

- [US-001 - Upload CSV files for a client](../user-stories/US-001-upload-csv-files.md)
- [US-002 - Confirm or adjust column mappings](../user-stories/US-002-confirm-column-mappings.md)
- [US-003 - Review import validation results](../user-stories/US-003-review-import-validation.md)

## Edge Cases and Error Handling

- **Duplicate source identifiers**: Reject duplicate identifiers within the
  same file and show each duplicate row.
- **Locale-specific amounts**: Reject ambiguous amount formats unless the
  mapping defines the decimal and thousands separators.
- **Partial upload**: If only one file is uploaded, keep the import session in
  draft and do not validate matching readiness.
- **Saved mapping drift**: If a saved mapping references a missing column,
  require the reviewer to repair the mapping before import.

## Success Metrics

- 95% of valid pilot-firm CSV import sessions reach the import summary without
  support intervention.
- 100% of accepted rows used in match evidence include file name, row number,
  source identifier, amount, and date.
- Fewer than 1% of import sessions require mapping correction after reviewer
  confirmation.

## Constraints and Assumptions

- CSV import is the only v1 ingestion path.
- Pilot firms can provide sample bank and invoice exports before launch.
- Source files may contain customer financial data and must follow the
  `financial-data-security` concern.

## Dependencies

- **Other features**: FEAT-002 Match Suggestion Review depends on accepted
  deposits and invoices from this feature.
- **External services**: None for v1.
- **PRD requirements**: P0-1 import CSV files; P0-4 preserve match evidence;
  P0-5 create exceptions for unmatched deposits.

## Out of Scope

- Bank feed integration.
- Accounting platform API sync.
- Automatic correction of malformed CSV values.
- Matching deposits to invoices before the reviewer confirms import summary.
