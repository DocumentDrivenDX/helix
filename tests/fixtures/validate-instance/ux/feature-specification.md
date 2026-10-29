---
ddx:
  id: FEAT-001
  type: feature-specification
  authoring:
    home: repo
---

# Feature Specification: FEAT-001 — CSV Import and Column Mapping

## Problem Statement

A silent mapping error makes plausible matches point at the wrong row.

## Functional Areas

| Area | User question or job | Feature responsibility |
|------|----------------------|------------------------|
| Mapping | Does DepositMatch understand these columns? | Require amount, date and identifier mappings. |

## Task Model

| Task | Goal | Users | Needs | Rules | Realized by | Key |
|------|------|-------|-------|-------|-------------|-----|
| Import a client's weekly files | The import is confirmed and ready to match | Reconciliation lead | Trust imported rows | BR-1, BR-2, BR-3 | import weekly files, UF-001 | import-weekly-files |

## Requirements

MAP-01. The system must require mappings for amount, date and identifier.

## Edge Cases and Error Handling

- A saved mapping that names a missing column must be repaired before import.

## Success Metrics

- 95% of valid imports reach the summary without support.

## Constraints and Assumptions

- CSV is the only v1 ingestion path.

## Out of Scope

- Bank feed integration.
