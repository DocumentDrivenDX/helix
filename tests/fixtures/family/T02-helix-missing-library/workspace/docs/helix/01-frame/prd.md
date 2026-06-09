---
library_type: library:prd
status: draft
---

# PRD: Inventory Reconciliation Service

## Problem

Warehouse counts and ledger counts diverge by ~2% monthly, costing
roughly $40k/quarter in write-offs.

## Goals

1. Reconcile inventory daily, not monthly.
2. Surface divergences over $500 within 15 minutes.

## Non-goals

- Replacing the existing WMS.
- Real-time per-SKU tracking below the case level.
