---
ddx:
  id: ADR-007
  type: adr
  authoring:
    home: repo
---

# ADR-007: Confirm the column mapping before validation

## Problem

A wrong column mapping produces plausible but wrong matches.

## Decision

We will ask the reviewer to confirm the mapping before any row is validated.

## Why We Chose This

### Over validating first
A rejected-row count is hard to read when the mapping itself is wrong.

## Consequences

**Good**: Wrong mappings are caught before they reach matching.

**Trade-offs**: One more step per import.

## Assumptions

- Reviewers read the sample rows under each picker: a study showing they skip
  them would invalidate this.

## Validation

**Result**: tested
**Evidence**: Research plan `pilot-reviewer-interviews`, Findings
