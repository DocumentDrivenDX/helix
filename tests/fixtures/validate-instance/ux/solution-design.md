---
ddx:
  id: SD-001
  type: solution-design
  authoring:
    home: repo
---

# Solution Design: SD-001-csv-import

**Feature**: FEAT-001

## Scope

CSV import and column mapping.

## Requirements Mapping

MAP-01 is met by the Mapping Service.

## Solution Approaches

Parse and validate synchronously in the API.

## Domain Model

### Business Rules

- **BR-1** — Required source pair: A draft import is not ready for mapping
  until it has one bank CSV and one invoice CSV.
- **BR-2** — Mapping before import: Accepted rows cannot be committed until
  amount, date and identifier are mapped.
- **BR-3** — Validation before matching: Match suggestions wait until the
  reviewer confirms the import summary.

## System Decomposition

### Component: Mapping Service
- **Purpose**: Check and save column mappings.

## Traceability

| Requirement ID | Component | Design Element | Test Strategy |
|---------------|-----------|----------------|---------------|
| MAP-01 | Mapping Service | Required mapping check | Unit tests |

### Experience Traceability

| Need | Task | Flow | View |
|------|------|------|------|
| Trust imported rows | Import a client's weekly files | UF-001 | UF-001-02-mapping-review |

### Gaps
- [ ] Tell the client which rows failed: no task or view yet; parked.
