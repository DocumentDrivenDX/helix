---
ddx:
  id: example.adr.depositmatch.postgresql-system-of-record
  authoring:
    home: repo
  depends_on:
    - example.architecture.depositmatch
---

# ADR-001: Use PostgreSQL as the System of Record

## Problem

DepositMatch must keep imports, source rows, match suggestions, reviewer decisions, exceptions, and audit evidence consistent with each other (PRD P0-1, P0-3, P0-4, P0-5). v1 starts from CSV imports with no external accounting APIs or bank feeds, so auditability and a fast pilot matter more than independent scaling of each data type.

## Decision

We will use PostgreSQL 16 as the single system of record for all DepositMatch v1 data, including audit-log records. Uploaded CSV originals stay in encrypted object storage; PostgreSQL holds their metadata and the normalized rows.

## Why We Chose This

### Over a document database
Flexible import payloads and fewer joins do not outweigh weaker relational integrity across invoices, deposits, matches, and corrections. Audit consistency is the point of the product.

### Over a separate event store plus read models
Event replay is attractive for audit history, but it costs more infrastructure and slows the pilot. Revisit if audit replay needs outgrow relational history.

## Consequences

**Good**: Imports, matches, exceptions, and audit records commit atomically and can be queried together.

**Trade-offs**: High-volume matching or analytics may later need read replicas or separate derived stores. Keep analytics derived and keep raw financial fields out of analytics events.

**Drift signals to watch**: An accepted match without source-row evidence. A partial import commit. A second store quietly becoming a source of truth.

## Concern Impact

- **Affects concerns**: Reinforces `reviewer-auditability`, `csv-import-integrity`, and `financial-data-security`. No practice override.
