---
library_type: library:adr
status: accepted
---

# ADR 0001: Pick Postgres for primary store

## Context

We need a primary OLTP store. Candidates: Postgres, MySQL, CockroachDB.

## Outcome

Postgres 16, single-writer, with logical replication to a read replica.
(Note: this section uses the alias "Outcome" instead of canonical "Decision".)

## Consequences

- Familiar to the team; no new ops burden.
- Logical replication adds operational complexity vs single-node.
- Vertical scaling ceiling near 32 vCPU before sharding required.
