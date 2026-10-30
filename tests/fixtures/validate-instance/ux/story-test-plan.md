---
ddx:
  id: STP-002
  type: story-test-plan
  authoring:
    home: repo
---

# Story Test Plan: STP-002-confirm-column-mappings

## Story Reference

**User Story**: [[US-002-confirm-column-mappings]]
**Technical Design**: [[TD-002-confirm-column-mappings]]

## Scope and Objective

**Goal**: Prove the reviewer confirms or fixes the mapping before validation.

## Acceptance Criteria Test Mapping

| AC ID | Acceptance Criterion (Given/When/Then) | New or Existing Test(s) to Create or Run | Asserted Behavior (what the test verifies) | AC-ID Citation (`@covers`) | Test Level | File or Command | Setup / Data | Notes |
|-------|----------------------------------------|----------------------------------|--------------------------------------------|----------------------------|------------|-----------------|--------------|-------|
| US-002-AC1 | Given a saved mapping, when Maya opens mapping review, then it is preselected | `prefills_saved_mapping` | Each picker shows the saved column | `@covers US-002-AC1` | E2E | `pnpm test:e2e -- mapping` | Saved Acme mapping | |
| US-002-AC2 | Given amount is unmapped, when Maya confirms, then the missing field is named | `names_missing_field` | Inline error names amount; picks kept | `@covers US-002-AC2` | E2E | `pnpm test:e2e -- mapping` | Invoice file without amount | |

## Executable Proof

```bash
pnpm test:e2e -- mapping
```

## Data and Setup

| Need | Required For | Source / Strategy |
|------|--------------|-------------------|
| Acme CSV fixtures | All tests | `tests/fixtures/acme/` |

## Build Handoff

**Done When**
- [ ] Every in-scope acceptance criterion has passing evidence

## Journey Scenarios

| Journey | Path | AC IDs | Test | File or Command |
|---|---|---|---|---|
| import weekly files | UF-001: Upload files → Confirm mapping → Columns complete → Continue to summary → Confirm import | US-001-AC1, US-002-AC1, US-003-AC1 | `imports_weekly_files` | `pnpm test:e2e -- import-journey` |

## UX Coverage

| Pattern | Disposition | AC IDs or Reason | Evidence |
|---|---|---|---|
| navigation | not-applicable | Mapping review adds no navigation destination | none |
| keyboard-overlays | not-applicable | No dialog or overlay in this slice | none |
| async-actions | covered | US-002-AC2 | 2026-10-28 · `pnpm check:a11y --route /imports/mapping` · CI artifact `ui-check`, kept 400 days |
| forms | covered | US-002-AC1, US-002-AC2 | 2026-10-28 · `pnpm check:a11y --route /imports/mapping` · CI artifact `ui-check`, kept 400 days |
| data-states | not-applicable | Column loading is covered by STP-001 | none |
| destructive-actions | not-applicable | Nothing is deleted in this slice | none |
