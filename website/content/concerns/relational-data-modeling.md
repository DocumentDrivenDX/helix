---
title: "Relational Data Modeling"
slug: relational-data-modeling
generated: true
aliases:
  - /reference/glossary/concerns/relational-data-modeling
---

**Category:** Architecture · **Areas:** data

## Description

## Category
architecture

## Areas
data

## Boundary

This concern owns **the relational schema itself** — the tables, columns, and
their types; primary and foreign keys; the constraints that enforce
integrity (NOT NULL / UNIQUE / CHECK / referential actions); the normalization
level and any deliberate denormalization; the indexing strategy; and the
**migration discipline** by which that schema evolves. It owns *how structured
data is shaped and kept correct in a relational store*. It does **not** own the
domain model, the persistence-mapping mechanics, or which engine the rows live
in. Four neighbors must stay distinct:

- **`domain-driven-design`** owns **the domain model** — aggregates, entities,
  value objects, invariants, and the ubiquitous language. This concern owns the
  **relational realization** of that model: the schema the aggregate is
  persisted into. The two compose tightly — an **aggregate boundary is the
  natural transactional consistency boundary, and a foreign-key boundary often
  mirrors it** (a child row's FK to its aggregate root, with the rest referenced
  by id, echoing DDD's "reference other aggregates by identity"). DDD says *what
  must stay consistent*; this concern says *which columns, keys, and constraints
  realize that in tables*. Do **not** restate aggregate/invariant rules here —
  reference DDD; state the schema.
- **The `datastore` slot** owns **which relational engine** the schema runs on
  (Postgres / MySQL / SQLite / …) and its operational profile. This concern is
  **engine-agnostic schema design** — it assumes a relational store but does not
  pick one. Engine-specific features (a particular RLS syntax, a partitioning
  dialect) belong to the chosen datastore; the normalization, keys, constraints,
  and migration discipline here hold across any SQL engine. Reference the slot
  for the engine; own the schema.
- **`enterprise-application-patterns`** (Data Mapper / Active Record / Unit of
  Work / Identity Map) owns **how the domain object maps to and from the
  schema** — the mapping layer and its mechanics. This concern owns the **schema
  on the far side of that mapping**: the mapper translates domain↔rows; this
  concern decides what those rows, keys, and constraints *are*. Name the mapping
  pattern as the neighbor; do not specify the schema's shape there.
- **`event-sourcing`** owns **append-only event-log persistence** as the source
  of truth for a slice. This concern is its alternative: **current-state
  relational storage** where the row *is* the truth, mutated in place under
  constraints. For an event-sourced slice the schema here governs only the
  **projections / read models** (which are themselves relational tables), not the
  log. Pick one model per slice; do not own the event log here.

This concern owns the one thing those do not state: **the relational schema is a
deliberate, constraint-enforced, versioned artifact — normalization and keys are
chosen on purpose, integrity is enforced by the database not just the
application, and every schema change ships as a reversible, versioned migration
with no destructive change made without a plan.**

## Components

- **Normalization level** — the schema is normalized to **3NF/BCNF by default**:
  every non-key column depends on the key, the whole key, and nothing but the
  key; no repeating groups (1NF), no partial-key dependencies (2NF), no
  transitive dependencies (3NF), no non-trivial dependency on a non-superkey
  (BCNF). Each fact lives in exactly one place.
- **Deliberate denormalization** — any departure from the normalized default
  (duplicated columns, a derived/aggregate column, a wide read table) is a
  **recorded decision** tied to a measured read pattern, naming how the
  redundant copy is kept consistent (trigger, application write, scheduled
  refresh). Denormalization-by-accident is drift.
- **Primary keys** — every table has a primary key. A **surrogate key**
  (generated id / UUID) is the default; a natural key is used only when it is
  stable and never reused. Composite keys model genuine compound identity
  (e.g. a join table), not convenience.
- **Foreign keys + referential integrity** — relationships are expressed as
  **declared foreign keys**, and the referential action (`ON DELETE
  CASCADE` / `RESTRICT` / `SET NULL`) is chosen deliberately per relationship to
  match the domain's lifecycle. An orphan-able relationship with no FK is a
  defect, not an optimization.
- **Constraints** — integrity rules live in the schema: **NOT NULL** for
  required columns, **UNIQUE** for natural-key and business-uniqueness rules,
  **CHECK** for domain/range/enumerated-value rules, and FK constraints for
  referential integrity. The database is a guard, not a dumb bucket the
  application alone polices.
- **Indexing strategy** — indexes are chosen from the **access patterns**, not
  sprinkled reflexively: an index for each frequent lookup/join/sort key, a
  unique index backing each UNIQUE constraint, composite indexes ordered by
  selectivity, and a deliberate decision about covering vs. lookup. Every index
  is justified against a query; unused/redundant indexes are removed.
- **Migrations** — every schema change is a **versioned, ordered migration**
  checked in with the application code, applied in sequence, and **reversible**
  (a tested down-path) unless reversibility is impossible and a forward-fix is
  recorded instead. Migrations are **forward-only in production** (roll forward
  with a new migration; do not edit an applied one). A destructive change (drop
  column/table, narrow a type, tighten a constraint over existing data) carries
  an **expand-then-contract plan** and a backfill, not an in-place break.

## Constraints

### Normalized by default; denormalization is a recorded decision

- Schemas are normalized to **3NF/BCNF** unless a specific, measured read
  pattern justifies otherwise. Each fact is stored once; update anomalies from
  duplicated facts are a design defect.
- Any **denormalization** is deliberate and recorded (an ADR), tied to the read
  pattern it serves, and **names the mechanism that keeps the redundant copy
  consistent**. "We denormalized for speed" with no measurement and no
  consistency mechanism is drift, not a decision.

### Integrity is enforced in the schema, not only in the application

- Required-ness (**NOT NULL**), uniqueness (**UNIQUE**), value/range/enum rules
  (**CHECK**), and relationships (**FOREIGN KEY**) are declared as **database
  constraints**. The application may also validate, but the database is the
  backstop — a path that bypasses the application must not be able to write
  inconsistent rows.
- Every table has a **primary key**; every relationship that must not orphan has
  a **declared foreign key** with a deliberately chosen `ON DELETE`/`ON UPDATE`
  action. (Application-enforced invariants that belong inside an aggregate stay
  in the domain — that is `domain-driven-design`'s rule; this constraint is about
  the *structural* integrity the schema itself guarantees.)

### Indexes follow access patterns and are justified

- Each index traces to a **query or constraint** it serves (a frequent
  lookup/join/sort, or a UNIQUE/PK it backs). Composite-index column order
  matches the query's predicate/sort order.
- Indexes are not free: each one costs write throughput and storage. An index
  with no supporting query is removed; a missing index on a hot lookup is a
  defect surfaced against the access patterns in the data-design.

### Migrations are versioned, reversible, and forward-only in production

- Every schema change is a **versioned, ordered migration** committed with the
  code that needs it; the schema is never edited by hand out of band.
- Migrations are **reversible** — a tested down-path exists — unless
  reversibility is genuinely impossible, in which case the forward-fix path is
  recorded. An applied production migration is **never edited**; correction is a
  new migration (forward-only).
- A **destructive change is never made without a plan**: dropping or narrowing a
  column/table, tightening a constraint over existing data, or renaming a live
  column goes through **expand → migrate/backfill → contract** (add the new
  shape, dual-write/backfill, switch reads, then remove the old shape in a later
  migration), so a rollback never strands data and a deploy never breaks the
  running version.

## Drift Signals (anti-patterns to reject in review)

- The same fact stored in two tables/columns with **no recorded denormalization
  decision and no consistency mechanism** → normalize, or record the
  denormalization + its sync mechanism (ADR)
- A relationship modeled by a bare id column with **no foreign key** (orphan-able
  data) → declare the FK and choose its `ON DELETE` action deliberately
- A table with **no primary key**, or a mutable/reusable natural key used as the
  PK → add a surrogate PK (or a stable natural key that is never reused)
- Required/unique/range rules enforced **only in application code**, with the
  schema allowing inconsistent rows on a bypass path → add NOT NULL / UNIQUE /
  CHECK constraints in the schema
- Indexes added reflexively (or none at all) with **no link to an access
  pattern** → justify each index against a query; drop unused, add the missing
  hot-path index
- A schema change applied **by hand / not as a versioned migration**, or an
  already-applied migration **edited in place** → ship the change as a new
  ordered, reversible migration; correct forward
- A **destructive change made in one step** (drop/narrow/tighten over existing
  data) with no expand-contract + backfill plan → break it into
  expand → backfill → contract so neither rollback nor the running version
  strands or breaks data
- An irreversible migration with **no recorded forward-fix path** → record how a
  bad deploy is recovered before shipping it

## When to use

Any product that **persists structured / relational data** in a SQL store —
entities with stable shape and relationships (users, accounts, orders,
invoices, line items, memberships, …). High autonomy auto-selects this concern
for such products (see `workflows/references/concern-resolution.md`). It is
composable (no slot); `areas: data` scopes its practices to data-layer work
items. Compose with **`domain-driven-design`** (the aggregates this schema
realizes — FK boundaries often mirror aggregate boundaries), the **`datastore`**
slot (the engine the schema runs on), **`enterprise-application-patterns`** (the
mapper between domain and rows), and **`event-sourcing`** (for slices stored as
an event log instead — this concern then governs only their relational
projections).

Do **NOT** select it for **schemaless / document-only** products where there is
no relational schema to design (a pure key-value or document store with no
relational integrity), or for products with **no persistence at all**
(stateless tools, pure computation, static sites). There, there is no relational
schema, keys, or migrations to govern (KISS/YAGNI).

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- ADR: normalization level + deliberate denormalization (read pattern + consistency mechanism), key choices, migration discipline
- TD: schema-enforced integrity (NOT NULL/UNIQUE/CHECK/FK), indexing from access patterns
- DATA_DESIGN: tables/columns/types, primary + foreign keys, normalization, indexes
- IMPLEMENTATION_PLAN: versioned reversible migrations; destructive changes via expand→backfill→contract

## ADR References

Record an ADR for the relational design decisions that are costly to reverse:
the **normalization level** and any **deliberate denormalization** (with the
read pattern that justifies it and the mechanism that keeps the redundant copy
consistent); significant **key choices** (surrogate vs. natural, composite
identity); and the **migration discipline** for destructive changes (the
expand-then-contract / backfill plan, and the forward-fix path for any
irreversible migration). A material uncertainty about whether the read/write
shape truly needs denormalization is a `tech-spike`, not a silent assumption
(see `workflows/references/concern-resolution.md`).

## Practices by activity

Agents working in any of these activities inherit the practices below via the bead's context digest.

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
