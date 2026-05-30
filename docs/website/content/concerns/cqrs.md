---
title: "CQRS (Command Query Responsibility Segregation)"
slug: cqrs
generated: true
aliases:
  - /reference/glossary/concerns/cqrs
---

**Category:** Architecture · **Areas:** data, api

## Description

## Category
architecture

## Areas
data, api

## Boundary

This concern owns **the decision to model writes and reads with two separate
models inside one bounded context** — a **write model** that handles *commands*
(state-changing operations carrying business intent and invariants) and one or
more **read models** that serve *queries* (denormalized, query-shaped
projections returning DTOs with no domain logic). It owns the **read/write
split** itself, the **command-handling path vs. the query-serving path**, the
**projection / read-model** that feeds queries, and the **consistency model**
between the two (synchronous same-store vs. eventually-consistent separate
stores). It does **not** own what the domain model is, how a slice of state is
persisted as truth, or how a service exposes itself on the wire. Three neighbors
must stay distinct:

- **`event-sourcing`** owns **how a slice of state is persisted as truth** — an
  append-only log of events as the authoritative system of record, replay /
  rehydration, snapshots, and event schema evolution. CQRS and event sourcing
  are a **frequent companion pair but each is independently adoptable**: CQRS
  needs no event log (the write model can be a normal current-state store, and
  the read model a separate read schema or replica), and event sourcing needs no
  command/query segregation (you can replay a stream into one model). When they
  compose, the **event store IS the write model / source of truth and the
  projections ARE the read side** — but those projection / replay / immutability
  rules are `event-sourcing`'s; do **not** restate them here. This concern owns
  only the **read-from-write separation discipline and its consistency model**.
- **`domain-driven-design`** owns **what is modeled** — the aggregates, value
  objects, invariants, and ubiquitous language. **CQRS's write model IS the DDD
  aggregate**: a command loads an aggregate, calls a root method that guards the
  invariant, and persists it (DDD's rule, unchanged). CQRS applies **per bounded
  context** — the context decides whether its read and write needs diverge
  enough to warrant two models. Do **not** restate aggregate / invariant /
  one-aggregate-per-transaction rules here — defer to DDD for the command model's
  shape; this concern only asserts that **queries bypass that model** and read
  from a separate projection.
- **`api-style`** owns **the synchronous request/response interface a service
  EXPOSES on the wire** — REST/GraphQL/gRPC/RPC, the contract, error shape, and
  versioning. **CQRS's read/write split is an INTERNAL structuring of the
  service, not the wire interface**: a single REST/GraphQL surface can sit in
  front of a CQRS-structured service (a `POST` routed to a command handler, a
  `GET` served from a read model), and the command/query DTOs are **not** the
  wire contract. Do **not** conflate "command vs. query" (internal model split)
  with "mutation vs. safe verb" (wire semantics) — reference `api-style` for the
  exposed contract; do not own it.

**Artifact impact — selecting CQRS forces specific document changes** (see also
*When to use*): an **ADR** records the read/write-split decision *and* the
**consistency model** chosen (synchronous shared-store vs. eventually-consistent
separate-store); the **technical-design** must show **separate command and query
models**, the **projection / read-model**, and **how eventual consistency is
handled** (the staleness window, how the read side is updated, idempotent
projection updates where async); the **data-design** must show the read schema
(denormalized / materialized view / replica) distinct from the write schema and
how they stay in sync. Selecting CQRS without these changes is drift.

## Components

- **Command** — a request to **change state**, named for the **business task /
  intent** (`BookHotelRoom`, `RateProduct`), not a low-level field mutation
  (`SetReservationStatusToReserved`). A command can be rejected (it expresses an
  intent that may fail validation/invariants); it does **not** return query data.
- **Command handler** — accepts a command, loads the **write model** (the DDD
  aggregate), invokes a domain method that enforces the invariant, and persists.
  This is the full command-processing stack: input validation, business
  validation, transactional integrity. Commands are often dispatched
  **asynchronously via a queue** (not required, but common).
- **Write model** — the model **optimized for updates and transactional
  integrity**, holding domain logic and invariants. It IS the
  `domain-driven-design` aggregate (defer there for its shape).
- **Query** — a request to **read state** that **never alters data** and returns
  a **DTO / read-shaped view object**, not a domain aggregate.
- **Read model / projection (materialized view)** — the model **optimized for
  queries**: denormalized, query-shaped, **no domain logic or validation
  stack**, returning DTOs for the presentation layer. May be a separate read
  schema in the same store, a read replica, a document store, or (when composed
  with event sourcing) a projection built off the event stream.
- **Query handler / read-side service** — serves a query straight from the read
  model with no business logic; the read side is deliberately thin.
- **Projection updater / synchronization mechanism** — the path that keeps the
  read model current with the write model: a synchronous same-transaction update
  (shared store), or an **asynchronous** publish-update-event → apply-to-read-
  model path (separate stores) — the latter is **eventually consistent** and its
  handlers must be **idempotent**.
- **Consistency model** — the explicit, recorded choice between **synchronous**
  (read model updated in the write transaction — strongly consistent, simpler,
  same store) and **eventually consistent** (read model updated out-of-band —
  scalable, separately storable, but stale-read window). This choice is the
  decision the ADR captures.

## Constraints

### Two models: the write side and the read side are deliberately separate

- The model used to **change** state (commands → write model) is **distinct**
  from the model used to **read** state (queries → read model). They are not one
  model serving both purposes within the CQRS-selected context.
- A **command** changes state and returns **no query data**; a **query** returns
  data and **never changes state**. An operation is one or the other, not both
  (a method that both mutates and returns the mutated view conflates the sides).

### The write model holds the logic; the read model holds none

- The **write model** carries the **full command-processing stack** — input
  validation, business validation, invariants — and is the DDD aggregate (defer
  to `domain-driven-design` for its shape and one-aggregate-per-transaction
  rule).
- The **read model returns DTOs / view objects with no domain logic** — no
  invariants, no business rules, no validation stack. It is denormalized and
  query-shaped, optimized for retrieval, and **queries bypass the domain model**
  rather than loading aggregates to read from them.

### Commands express business intent, not low-level mutations

- Commands are named for the **business task** (`BookHotelRoom`,
  `SubmitOrder`), capturing user intent and aligning with business processes —
  **not** anemic field setters (`SetStatusReserved`). Command granularity is
  chosen to **reduce conflicting concurrent requests** in collaborative
  domains.

### The consistency model is an explicit, recorded decision

- Whether the read model is updated **synchronously** (same store / same
  transaction — strongly consistent) or **asynchronously** (separate store,
  publish-and-project — **eventually consistent**) is a **deliberate, ADR-
  recorded** choice, not an accident of implementation.
- When the read model is **eventually consistent**, the system and its consumers
  are **designed for the staleness window**: there is no read-your-write
  guarantee across the read/write boundary, the UI accounts for acting on
  possibly-stale reads, and the projection-update handlers are **idempotent**
  (a published update may be delivered more than once).

### Separate stores must be kept in sync — and that path is fallible

- When read and write use **separate data stores**, a defined mechanism keeps
  them in sync (commonly: the write side publishes an event the read side
  consumes). Because a message broker and a database usually **cannot enlist in
  one distributed transaction**, the sync path must tolerate failures,
  duplicates, and retries (idempotent application) — this is an accepted cost of
  the separation, not a bug to wish away.

### CQRS is scoped per bounded context, not applied whole-system

- CQRS is applied to the **specific bounded context(s) whose read and write
  needs genuinely diverge** — not as a top-level architecture for the entire
  system. Contexts that are simple CRUD keep a single model. (Greg Young: CQRS
  is *not* a top-level pattern; Fowler: apply it to bounded contexts that need
  it, not whole systems.)

## Drift Signals (anti-patterns to reject in review)

- A **single shared model** serving both commands and queries inside a context
  that was selected for CQRS → there is no segregation; either split the models
  or drop the CQRS claim for that context
- A **query that mutates state**, or a **command that returns the queried view
  object** → commands and queries are conflated; keep each pure (command changes
  state, returns no data; query returns data, changes nothing)
- The **read model carrying domain logic / invariants / a validation stack** →
  the read side must be a thin DTO/projection with no business rules; logic lives
  in the write model
- The **read side loading write-model aggregates to read from them** (rehydrate
  an aggregate just to project a field) → queries should read the denormalized
  read model, not the command model
- **Separate read and write stores with no defined synchronization path**, or a
  sync path assumed transactional with the broker → define the
  publish-and-project path and make it idempotent / failure-tolerant
- **Eventual consistency assumed away** — UI/consumers built as if a read
  reflects a just-issued write immediately (read-your-write across the boundary)
  → design for the staleness window, or choose the synchronous consistency model
  and record that choice
- A **non-idempotent projection updater** (double-applies an update event,
  double-fires a side effect) → make read-model updates idempotent
- **Anemic, field-mutation commands** (`SetXTo3`) instead of intent-bearing
  business-task commands → name commands for the business task
- **CQRS applied across the whole system** / to thin-CRUD contexts that do not
  need it → over-engineering (Fowler's "risky complexity"); scope it to the
  bounded context whose read/write needs diverge, leave simple CRUD as one model
- **CQRS selected but the ADR / technical-design / data-design unchanged** (no
  recorded split, no consistency model, no read schema) → the selection forces
  those artifact changes; their absence is drift (see *When to use*)

## When to use

Select for the **specific bounded context(s) where the read and write models
genuinely diverge** — where one model serving both sides has become an awkward,
overloaded compromise. The signals (Young / Fowler / Azure):

- **Collaborative domains** — many users read and modify the same data
  concurrently, and command-level granularity reduces merge conflicts.
- **Task-based UIs** — the UI guides the user through tasks/processes (book,
  approve, cancel) that map to **intent-bearing commands** rather than generic
  CRUD field edits.
- **Strongly asymmetric read vs. write shape or scale** — reads and writes have
  very different shapes or load (e.g. read-heavy with complex query shapes), so
  each side benefits from being **scaled and schema-optimized independently**.
- **Complex domains** where the command-side business logic and the query-side
  presentation needs have diverged enough that one model serves neither well.

It is a **non-exclusive, composable** concern (no slot) and is **scoped per
bounded context, not whole-product** — apply it to the context(s) that earn it
and keep a single model everywhere else. `areas: data, api` scopes its practices
to the data-layer and service-layer work items. **Compose** with
`domain-driven-design` (the write model IS the aggregate; CQRS applies per
bounded context), with `event-sourcing` (the event store becomes the write
model / source of truth and the projections the read side — frequent companion,
neither requires the other), and with `api-style` (a single exposed wire surface
fronts the internal read/write split).

**Selecting CQRS forces artifact changes:** an **ADR** for the read/write-split
decision *and* the consistency model (synchronous vs. eventually consistent);
the **technical-design** for the separate command/query models, the projection /
read-model, and the eventual-consistency handling; and the **data-design** for
the distinct read schema and the write→read synchronization. Selecting it
without these is drift.

Do **NOT** select it for a **simple CRUD context** — where the data is read the
same way it is written, an information base updated and read through one model
fits well, and a plain CRUD model + a conventional API is the simpler, correct
choice. Fowler's caution applies directly: *for most systems CQRS adds risky
complexity*; it is **difficult to use well** and should be applied only to the
bounded contexts that need it, never reflexively to a whole system (KISS/YAGNI).

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- ADR: read/write-split decision + consistency model (synchronous shared-store vs eventually-consistent separate-store)
- TD: separate command/query models, projection/read-model, eventual-consistency handling (staleness, idempotent updates)
- DATA_DESIGN: read schema (denormalized/materialized view/replica) distinct from write schema + write→read sync
- TEST_PLAN: idempotent projection updater + read-side reflects committed writes within the staleness window

## ADR References

Record an ADR when selecting CQRS for a given bounded context. It is a
structural decision with a standing consistency cost, so the ADR names: the
**bounded context** the split applies to; the **decisive signal** (collaborative
domain / task-based UI / divergent read-write shape or scale / complex domain);
the **consistency model** chosen — **synchronous shared-store** (strongly
consistent, simpler) vs. **eventually-consistent separate-store** (scalable,
stale-read window) — and, if eventually consistent, the **synchronization path**
(how the read model is updated) and the **staleness window** consumers must
tolerate; whether it **composes with `event-sourcing`** (event store as write
model) and with the relevant `api-style` surface; and the contexts that
deliberately remain **single-model CRUD**. A material uncertainty about whether
the read/write needs truly diverge is a `tech-spike`, not a silent assumption
(see `workflows/references/concern-resolution.md`).

## Practices by activity

Agents working in any of these activities inherit the practices below via the bead's context digest.

These practices govern **separating the write model (commands) from the read
model(s) (queries) within a bounded context, and managing the consistency
between them**. They do **not** govern what the domain model is
(`domain-driven-design` — the write model IS the aggregate), how state is
persisted as truth (`event-sourcing` — the event log and its replay/projection
rules), or how the service exposes itself on the wire (`api-style` — the
read/write split is internal, not the contract). When a rule references the
aggregate, defer to DDD; when it references the event store / projections as the
source of truth, defer to event sourcing. Apply these **per bounded context**
that selected CQRS — not to every context in the product.

## Discover

- Confirm the context **earns** CQRS: a **collaborative** domain (many concurrent
  writers), a **task-based UI** (intents map to commands), **divergent read vs.
  write shape/scale**, or a genuinely **complex** domain where one model serves
  neither side. If it is simple CRUD read the same way it is written, do **NOT**
  apply CQRS — use a single model (record the decision; Fowler: CQRS adds risky
  complexity, it is difficult to use well).

## Frame

- Choose and **record the consistency model in an ADR**: **synchronous**
  (read model updated in the write transaction — strongly consistent, simpler,
  same store) vs. **eventually consistent** (read model updated out-of-band,
  separate store — scalable, but a stale-read window). Name the **bounded
  context**, the **decisive signal**, and (if eventually consistent) the
  **synchronization path** and the **staleness window** consumers must tolerate.
- A **synchronous** consistency model (read model updated in the write
  transaction, same store) is the simpler choice when strong read-after-write is
  required; prefer it unless the asymmetry/scale signal justifies the
  eventually-consistent separation. Whichever is chosen MUST match the ADR.
- The selection MUST drive the artifacts: the **technical-design** SHOULD show
  separate command/query models, the projection/read-model, and the
  eventual-consistency handling; the **data-design** SHOULD show the read schema
  distinct from the write schema and how they stay in sync.

## Design

- The model handling **commands** (state changes) MUST be **distinct** from the
  model serving **queries** (reads) within the CQRS-selected context — not one
  model doing both.
- A **command** MUST change state and return **no query data**; a **query** MUST
  return data and **never** change state. An operation is one or the other — a
  method that mutates *and* returns the mutated view conflates the sides.
- Queries MUST read from the **read model / projection**, NOT by loading
  write-model aggregates to read fields off them.
- The **write model** carries the full command-processing stack — input
  validation, business validation, invariants — and IS the
  `domain-driven-design` aggregate (defer there: a command loads the aggregate,
  calls a root method that guards the invariant, persists; one aggregate per
  transaction).
- The **read model MUST return DTOs / view objects with no domain logic** — no
  invariants, no business rules, no validation stack. It is denormalized and
  query-shaped, optimized for retrieval.
- Commands MUST be named for the **business task / intent** (`BookHotelRoom`,
  `RateProduct`, `SubmitOrder`), capturing user intent — NOT anemic field
  setters (`SetReservationStatusToReserved`).
- Command **granularity SHOULD be chosen to reduce conflicting concurrent
  requests** in collaborative domains (a command scoped to a meaningful task
  conflicts less than a coarse "save everything").

## Build

- When the read model is **eventually consistent**, the UI/consumers MUST be
  designed for the **staleness window**: no read-your-write assumption across the
  read/write boundary; acting on a possibly-stale read is handled deliberately
  (re-validate on the command side, optimistic UI with reconciliation, etc.).
- When read and write use **separate stores**, a defined synchronization path
  MUST keep them in sync (commonly: the write side publishes an update event the
  read side consumes). Because a broker and a database usually cannot enlist in
  one distributed transaction, the path MUST tolerate failures, duplicates, and
  retries.
- Projection / read-model update handlers MUST be **idempotent** — applying the
  same update event twice yields the same read-model state and fires any side
  effect at most once.

## Test

- CQRS is **scoped to the bounded context(s) that earn it** (collaborative /
  task-based UI / divergent read-write shape-or-scale / complex domain);
  simple-CRUD contexts use a single model — verifiable that CQRS is not applied
  whole-system or to thin CRUD.
- **Commands and queries are segregated and pure** within the context: no command
  returns query data, no query mutates state, and queries read the **read model**
  rather than loading write-model aggregates.
- The **write model holds the logic** (validation + invariants, as the DDD
  aggregate) and the **read model holds none** (denormalized DTO/projection, no
  domain logic) — verifiable that no business rule lives in the read side.
- Commands are **named for the business task** (intent-bearing), not anemic field
  setters.
- The **consistency model is recorded in an ADR** (synchronous shared-store vs.
  eventually-consistent separate-store) and the implementation matches it.
- When **eventually consistent**, consumers tolerate the **staleness window** (no
  read-your-write assumption across the boundary) and the **projection updater is
  idempotent** and failure/duplicate-tolerant; separate stores have a defined
  synchronization path.
- Selecting CQRS is reflected in the artifacts: the **ADR** (split + consistency
  model), the **technical-design** (separate command/query models + projection +
  eventual-consistency handling), and the **data-design** (read schema distinct
  from write schema + sync path) — verifiable that the selection is not silent
  drift.

## Cross-cutting

### Boundary with neighbors

See `concern.md` for the canonical Boundary (vs `domain-driven-design`,
`event-sourcing`, `api-style`). Idempotent projection updates here are the
same property `enterprise-integration-patterns` requires of consumers under
at-least-once delivery — defer there for the cause, apply it here to the
read-model update path. When composed with event sourcing, the event store
becomes the write model / source of truth and the projections the read side;
the immutability/replay/rebuild rules are `event-sourcing`'s — not restated
here.
