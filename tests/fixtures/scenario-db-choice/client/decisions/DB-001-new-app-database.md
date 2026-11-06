---
ddx:
  id: DB-001
  type: decision-brief
  status: draft
  authoring:
    home: repo
  links:
    - {id: component-profile-postgresql-reusable, graph: synaptiq-atlas, kind: evaluates}
    - {id: component-profile-sql-server-reusable, graph: synaptiq-atlas, kind: evaluates}
---

# DB-001: Which database should the new AI-enabled web application use?

## Context

The client runs SQL Server for its existing systems and is starting a
multi-tenant web application with an AI search feature. This brief covers the
database engine for the new application only. Hosting, and the fate of existing
SQL Server systems, are separate decisions and out of scope.

| Bound | Source | Effect on the choice |
|-------|--------|----------------------|
| Tenant data must be isolated at the database tier | Client requirement | Favors options with row-level security |
| The app needs embedding search over its own data | Client requirement | Favors options with a vector type and index |
| The service must survive a node failure with a readable replica | Client requirement | Favors built-in replication with read access |
| Budget is per-application, with no appetite for new per-core licences | Client constraint | Counts licence cost per added core |
| The team knows T-SQL | Current state | Adds ramp-up cost to a new engine |

## Decision

Choose the database engine for the new application. The client's engineering
lead decides.

## Options

- **SQL Server.** The engine already in use. Evidence: SQL Server technology
  brief (component-profile-sql-server-reusable).
- **PostgreSQL.** A separate open-source engine. Evidence: PostgreSQL
  technology brief (component-profile-postgresql-reusable).

## Evaluation

| Criterion | SQL Server | PostgreSQL |
|-----------|------------|------------|
| Row-level security | Filter and block predicates since 2016, in all editions [SQL Server §Access control] | Row security policies since 9.5; owner and pooling pitfalls reported [PostgreSQL §Access control] |
| Vector search | `vector` type GA in 2025; vector index still preview [SQL Server §Vector] | Unknown: the brief does not cover vector search |
| Readable replica | Standard edition: basic availability group, no readable secondary; Enterprise needed [SQL Server §Replication] | Built-in hot standby with read-only queries; replica delay reported [PostgreSQL §Replication] |
| Licence cost per added core | Per-core licence; 2022 list $3,945 Standard and $15,123 Enterprise per 2 cores; 2025 list not published by the maker [SQL Server §Pricing] | None for the software [PostgreSQL §Pricing] |
| Team familiarity | Existing T-SQL skills | Unknown: not researched |

The cost and readable-replica criteria separate the options on the record. The
vector criterion cannot be scored for PostgreSQL because its brief does not
cover it, and SQL Server's vector index is still preview.

## Recommendation

**Recommendation**: PostgreSQL for the new application, on this condition: a
vector-search spike on PostgreSQL meets the application's recall and latency
needs. It avoids new per-core licences and gives a readable replica without
Enterprise edition.

What would change it: a failed vector spike, or a client decision to license
SQL Server Enterprise for other reasons, which removes the cost and replica
advantages.

## Risks and Unknowns

| Risk or unknown | Bears on | Route |
|-----------------|----------|-------|
| PostgreSQL vector search not researched | Vector search | Extend the PostgreSQL brief, then run a spike |
| Team ramp-up from T-SQL | Team familiarity | Plan training; no evidence gathered |
| SQL Server 2025 list price not published on a maker page | Licence cost | Obtain the client's agreement price |

## Evidence

| Reference | Kind | Revision | Used for |
|-----------|------|----------|----------|
| component-profile-sql-server-reusable | Technology brief | pinned at approval | Security, replication, vector, pricing |
| component-profile-postgresql-reusable | Technology brief | pinned at approval | Security, replication, pricing |
