# Practices: Relational Data Modeling

These practices govern **the relational schema and how it evolves** — its
normalization, keys, constraints, indexes, and migrations. They do **not**
govern the domain model (that is `domain-driven-design`), the domain↔row mapping
mechanics (`enterprise-application-patterns`), or which engine runs the schema
(the `datastore` slot). When a rule references the domain, defer to DDD for the
model; this concern asserts the schema that realizes it.

## Design the schema normalized, denormalize on evidence

- Model each entity as a table normalized to **3NF/BCNF**: every non-key column
  depends on the key, the whole key, and nothing but the key; no repeating
  groups, no partial-key or transitive dependencies. Each fact is stored
  **once**.
- Map relationships to **declared foreign keys**, and choose each relationship's
  referential action (`ON DELETE CASCADE` / `RESTRICT` / `SET NULL`) to match
  the domain's lifecycle — record it in the data-design's relationships table.
  FK boundaries SHOULD mirror the aggregate boundaries DDD defines (a child FK to
  its root; other aggregates referenced by id).
- Any **denormalization** MUST be a recorded decision (ADR) tied to a measured
  read pattern, and MUST name the mechanism that keeps the redundant copy
  consistent (trigger, application write, scheduled refresh). No silent
  duplicated facts.

## Give every table a key and enforce integrity in the schema

- Every table has a **primary key** — a surrogate (generated id / UUID) by
  default; a natural key only when it is stable and never reused; a composite key
  only for genuine compound identity.
- Declare integrity as **database constraints**: **NOT NULL** for required
  columns, **UNIQUE** for business-uniqueness/natural-key rules, **CHECK** for
  range/enumerated/domain rules, **FOREIGN KEY** for every non-orphan-able
  relationship. The application MAY validate too, but a write path that bypasses
  the application MUST NOT be able to persist an inconsistent row.

## Index from the access patterns, not reflexively

- Derive indexes from the data-design's **access-patterns** table: an index for
  each frequent lookup/join/sort key, a unique index backing each UNIQUE
  constraint, and composite indexes whose column order matches the query's
  predicate/sort order.
- Justify **each** index against a query or constraint it serves; remove unused
  or redundant indexes (they cost write throughput and storage) and add the
  missing index on any hot lookup.

## Ship every schema change as a versioned, reversible migration

- Every schema change is a **versioned, ordered migration** committed with the
  code that needs it. The schema is **never** edited by hand out of band, and an
  **already-applied production migration is never edited** — correct forward with
  a new migration.
- Each migration is **reversible** (a tested down-path) unless reversibility is
  genuinely impossible, in which case the **forward-fix path is recorded**.
- A **destructive change** (drop/narrow a column or table, tighten a constraint
  over existing data, rename a live column) MUST follow
  **expand → migrate/backfill → contract**: add the new shape, dual-write /
  backfill existing data, switch reads, and only then remove the old shape in a
  **later** migration — so neither a rollback nor the currently-running version
  strands or breaks data. No destructive change without this plan recorded in the
  implementation-plan.

## Boundary with neighbors

- For **what is modeled** (aggregates, invariants, value objects, ubiquitous
  language) defer to `domain-driven-design`; this concern owns the **schema** that
  persists it. An application-enforced business invariant that belongs inside an
  aggregate stays in the domain — this concern owns only the **structural**
  integrity the schema guarantees.
- For the **domain↔row mapping** (Data Mapper / Active Record / Unit of Work)
  defer to `enterprise-application-patterns`; this concern owns the rows, keys,
  and constraints on the far side of that mapping.
- For the **engine** (Postgres/MySQL/SQLite, its dialect and operational
  profile) defer to the `datastore` slot; the normalization, keys, constraints,
  and migration discipline here hold across any SQL engine.

## Quality Gates

- The data-design records, per entity, a **primary key**, and per relationship a
  **foreign key** with a deliberately chosen `ON DELETE`/`ON UPDATE` action — no
  table without a PK, no non-orphan-able relationship without an FK.
- The schema is **normalized to 3NF/BCNF**, OR every departure is a recorded
  denormalization decision (ADR) naming the read pattern and the consistency
  mechanism for the redundant copy.
- Required/unique/range rules are enforced by **schema constraints** (NOT NULL /
  UNIQUE / CHECK / FK), verifiable that a write bypassing the application cannot
  persist an inconsistent row — not only by application code.
- **Each index traces to an access pattern** (a query it serves or a constraint
  it backs); no unjustified or redundant indexes, no missing index on a
  documented hot lookup.
- Every schema change is a **versioned, ordered migration** committed with the
  code; no hand-applied changes and no edit of an already-applied migration.
- Each migration is **reversible** (tested down-path) or records its
  forward-fix path; a **destructive change** carries an **expand → backfill →
  contract** plan in the implementation-plan, never an in-place break.
