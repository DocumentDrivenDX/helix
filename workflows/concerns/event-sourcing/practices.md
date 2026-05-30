# Practices: Event Sourcing

These practices govern **persisting a slice of state as an append-only log of
events that is the source of truth**, deriving current state by replay. They do
**not** govern what the domain model is (`domain-driven-design`), how the code
layers (`onion-architecture`), or how messages move between systems
(`enterprise-integration-patterns`). When a rule references the aggregate, defer
to DDD for the modeling; this concern asserts how that aggregate is persisted
and rehydrated. Apply these **per domain slice** that selected event sourcing —
not to every entity in the product.

## Decide the slice before applying

- Confirm the slice **earns** event sourcing: a hard audit/history requirement,
  temporal queries, value-bearing change streams (ledger, lifecycle, activity /
  engagement timeline), or high write-contention conflict avoidance. If it is
  thin CRUD with no history need, mostly-static reference data, or a short-lived
  prototype, do **not** event-source it — use current-state storage (record the
  decision; "don't event-source everything").
- Name the **aggregate / entity** whose eventstream this is (its boundary is the
  DDD aggregate's — defer to `domain-driven-design`), the **event store**, the
  **projections** to build, and the **eventual-consistency window** consumers
  must tolerate. Record the selection in an ADR.

## Model events as immutable, intent-bearing facts

- Events are **named in the past tense** and capture **business intent**, not
  just a resulting value: `TwoSeatsReserved` / `OrderCanceled`, MUST NOT be
  `RemainingSeatsChangedTo42`. State-snapshot events reduce the store to a
  meaningless change log.
- An event, once appended, is **immutable**: its data MUST NOT be updated or its
  record deleted. (Schema *shape* may evolve via versioning/upcasting — that does
  not mutate stored events; see below.)
- Each event carries a **version** identifier (in the envelope or the type name)
  so consumers can select handling logic and upcasters can transform it.

## Append-only store as the source of truth

- The event store is the **authoritative system of record**. A state change is
  recorded **only** by **appending** a new event — never by an in-place
  update/delete of a stored event.
- **Current state is derived by replaying events, not stored as the authority.**
  Do NOT keep an authoritative current-state table behind the log; any
  current-state representation is a derived, disposable view.
- To undo or correct, **append a compensating event** (`ReservationCanceled`
  compensating `SeatsReserved`); the original event stays. In-place rewrite of
  stored events is a last-resort migration only, recorded as an ADR deviation —
  not a routine correction.
- Per-entity event **order** is preserved; concurrent appends to one stream are
  arbitrated by **optimistic concurrency** (reject-on-conflict → reload →
  reevaluate → retry), never by overwriting.

## Rehydrate from the stream; snapshot only as a cache

- Derive an entity's current state by **replaying its eventstream** in order and
  applying each event. The command path is: load (replay) → run business logic
  on the aggregate → append new events.
- Where replay cost is material, take a **snapshot** every *N* events and
  rehydrate from the latest snapshot + the tail of events after it. A snapshot
  is an **optimization, not the truth** — it MUST be regenerable from the
  eventstream, and the eventstream remains authoritative.

## Build projections that are rebuildable and idempotent

- Every projection / read model is **rebuildable from the event log alone** —
  deleting it and replaying the stream reconstructs it. Nothing of record lives
  **only** in a projection.
- Do **not** edit a projection in place to correct it; a change to a projection
  means **replaying from event zero forward**.
- Projection updates / event handlers are **idempotent** — at-least-once
  delivery means the same event can arrive twice; processing a duplicate MUST
  yield the same state and fire any side effect at most once. Track the last
  processed sequence number per consumer, or design inherently repeatable
  mutations.
- Treat projections as **eventually consistent** with the write side; design the
  UI/consumers for the lag. Do not assume read-your-write across the projection
  boundary.

## Evolve event schema by versioning + upcasting

- Handle schema evolution **without mutating stored events**:
  - **Tolerant deserialization** for additive, non-breaking changes (ignore
    unknown fields, default missing ones).
  - **Upcasting** for breaking changes — a transform from an older version to the
    current one applied **on replay/deserialization**, chainable so application
    code handles only the latest shape. Stored events stay unchanged.
- In-place migration (rewriting stored events to the new schema) breaks
  immutability and the audit trail — last resort, ADR-recorded.

## Handle personal data under immutability

- Plan erasure up front: keep personal data **outside** the eventstream
  (referenced by id, deletable independently) or **crypto-shred** (per-subject
  key, delete the key). Do NOT plan to delete events to satisfy a
  right-to-be-forgotten request.

## Boundary with neighbors

See `concern.md` for the canonical Boundary (vs `domain-driven-design`,
`enterprise-integration-patterns`, `onion-architecture`, `sample-data`, and
the **CQRS** companion). Idempotent application of events here is the same
property `enterprise-integration-patterns` requires of consumers under
at-least-once delivery — defer there for the channel-delivery rule, apply it
here to projection/read-model updates. The event store is a real event store
(per-entity stream reads + optimistic concurrency), not a message broker
standing in as the system of record.

## Quality Gates

- Stored events are **immutable and append-only** — verifiable that no code path
  performs an in-place update or delete of a stored event; corrections are
  compensating events.
- The **event log is the source of truth**: current state is **derived by
  replaying events**, not stored as the authority (no authoritative
  current-state table behind the log; snapshots are a cache, regenerable from the
  stream).
- **Projections are rebuildable from the event log alone** — deleting a
  projection and replaying reconstructs it; nothing of record lives only in a
  projection.
- **Event application is idempotent** (duplicate delivery yields the same state /
  at-most-once side effect) and **events carry a version** with an upcasting (or
  tolerant-deserialization) path so schema evolves without rewriting stored
  events.
- Per-entity event **order is preserved** and concurrent appends are arbitrated
  by **optimistic concurrency**, not overwrite.
- Projections are treated as **eventually consistent**; consumers tolerate the
  window (no read-your-write assumption across the projection boundary).
- Event sourcing is **scoped to the slice that earns it** (audit/history/temporal
  /value-bearing stream); thin-CRUD / static-reference slices use current-state
  storage instead.
