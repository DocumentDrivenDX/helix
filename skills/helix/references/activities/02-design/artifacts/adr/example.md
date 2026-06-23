---
ddx:
  id: example.adr.depositmatch.postgresql-system-of-record
  depends_on:
    - example.architecture.depositmatch
  review:
    self_hash: d068dcadcfb1b7b4cfa6842e63e078f711128e78d5c2dd7e1666506a7c59d9ad
    deps:
      example.architecture.depositmatch: 64b7297158175ff16812e401fe093f7624b5ba70b11265a7a4bdf324e50a6bff
    reviewed_at: "2026-05-15T04:11:24Z"
---

# ADR-001: Use PostgreSQL as the System of Record

| Date | Status | Deciders | Related | Confidence |
|------|--------|----------|---------|------------|
| 2026-05-12 | Accepted | Product and Engineering | FEAT-001, Architecture | High |

## Context

| Aspect | Description |
|--------|-------------|
| Problem | DepositMatch must preserve imports, source rows, match suggestions, reviewer decisions, exceptions, and audit evidence consistently. |
| Current State | v1 starts from CSV imports and does not use external accounting APIs or bank feeds. |
| Requirements | PRD P0-1 import CSV files; P0-3 require reviewer approval; P0-4 preserve match evidence; P0-5 create exceptions for unmatched deposits. |
| Decision Drivers | Auditability, transactional consistency, simple v1 operations, and fast pilot delivery matter more than independent scaling of each data type. |

## Decision

We will use PostgreSQL 16 as the system of record for DepositMatch v1 data,
including clients, import sessions, source rows, invoices, deposits, match
suggestions, reviewer decisions, exceptions, and audit-log records.

**Key Points**: one transactional store | source-row traceability | no separate
search or document store in v1

## Alternatives

| Option | Pros | Cons | Evaluation |
|--------|------|------|------------|
| PostgreSQL 16 | Strong transactions, relational constraints, straightforward audit queries, mature backups, simple v1 operations | Less specialized for full-text search or high-volume event streaming | **Selected**: best fit for consistency and pilot simplicity |
| Document database | Flexible import payload storage, fewer joins for nested evidence | Harder relational integrity for invoices, deposits, matches, and corrections | Rejected: flexibility is less important than audit consistency |
| Separate event store plus read models | Excellent history and replay model | More infrastructure, more operational complexity, slower pilot delivery | Rejected for v1: event sourcing may be revisited if audit replay needs exceed relational history |

## Consequences

| Type | Impact |
|------|--------|
| Positive | Imports, matches, exceptions, and audit records can commit atomically and be queried together. |
| Negative | Future high-volume matching or analytics may need read replicas or separate derived stores. |
| Neutral | Uploaded CSV originals still live in encrypted object storage; PostgreSQL stores metadata and normalized rows. |

## Risks

| Risk | Prob | Impact | Mitigation |
|------|------|--------|------------|
| Import and match tables grow faster than expected | M | M | Partition or archive import sessions after retention policy is defined; add read replica if reporting load grows. |
| Analytics needs pressure the transactional schema | M | L | Keep analytics derived; do not put raw financial fields into analytics events. |

## Validation

| Success Metric | Review Trigger |
|----------------|----------------|
| 100% of accepted rows used in match evidence include source file, row number, identifier, amount, and date | Any accepted match lacks source-row evidence |
| Import confirmation remains atomic under validation and worker failures | Any partial import commit is observed in testing or production |
| Pilot workload stays below PostgreSQL performance targets | Matching backlog exceeds 100 jobs for 5 minutes repeatedly |

## Supersession

- **Supersedes**: None
- **Superseded by**: None

## Concern Impact

- **Concern selection**: Reinforces `reviewer-auditability`,
  `csv-import-integrity`, and `financial-data-security`.
- **Practice override**: None.

## References

- Architecture: `example.architecture.depositmatch`
- Feature Specification: `example.feature-specification.depositmatch.csv-import`
- PRD requirements: P0-1, P0-3, P0-4, P0-5
