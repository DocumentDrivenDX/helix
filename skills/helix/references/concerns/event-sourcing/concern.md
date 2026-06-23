# Concern: Event Sourcing

## Category
architecture

## Areas
data

## Boundary

This concern owns **how a slice of state is persisted as truth** — the decision
to store the full, ordered sequence of state-changing **events** in an
append-only log and treat that log as the authoritative system of record,
deriving current state by **replaying** it. It owns the event store, replay /
rehydration, snapshots, projections/read models, idempotent application, and
event schema evolution. It does **not** own what the domain model is, how the
codebase layers itself, or how messages move between systems. Four neighbors
must stay distinct:

- **`domain-driven-design`** owns **what** is modeled — the aggregates, value
  objects, invariants, and ubiquitous language, and the fact that an aggregate
  **emits domain events** when something meaningful happens. Event sourcing is
  one way to **persist** those emitted events *as the source of truth* and
  rehydrate the aggregate from them. Compose: the aggregate root is still the
  invariant gatekeeper (DDD's rule), and command handling still loads → mutates
  → persists one aggregate per transaction; ES only changes *how* that
  aggregate is loaded and saved (replay an eventstream, append new events). Do
  **not** restate aggregate/invariant rules here — reference DDD.
- **`enterprise-integration-patterns`** owns moving messages **between** systems
  or bounded contexts (channels, routers, transformation, delivery). A **stored
  domain event is not an integration message**: ES is a persistence/state model
  **within** one context; EIP is the transport across contexts. One can publish
  the other (an event handler may emit an integration event onto a channel), but
  the eventstream that is the source of truth and the wire message that fans out
  to other systems are different artifacts. Reference EIP for the transport; do
  not own it.
- **`onion-architecture`** owns **how** the codebase layers and which way
  dependencies point. The **event store is an outer-ring infrastructure
  adapter** that implements a persistence interface (an event-store / repository
  port) declared by an inner layer in domain terms. ES says *the log is the
  truth and the aggregate rehydrates from it*; onion says *the inner ring
  declares the port and the outer ring implements it*. Do not restate the
  dependency rule — reference onion for the arrangement.
- **`sample-data`** owns the seed/demo dataset. For an event-sourced slice the
  governed seed is expressed as **events appended to the store** (not rows
  inserted into a current-state table), so projections rehydrate from a
  realistic event history; ES defines that the seed is events, `sample-data`
  governs the dataset's variety and edge cases.

**CQRS is the frequent companion, not owned here.** Event sourcing pairs
naturally with **CQRS** — the write side appends events; the read side serves
queries from projections built off the eventstream. This concern owns the
**event log as source of truth and its projections**; it does **not** own the
full command/query segregation discipline. Name CQRS as the companion; do not
claim to define it.

## Components

- **Event** — an immutable record of something that **happened**, named in the
  past tense (`SeatsReserved`, `OrderCanceled`, `EmailOpened`), carrying the
  data and **business intent** of the change. Intent-focused events
  (`TwoSeatsReserved`) are worth more than state-snapshot events
  (`RemainingSeatsChanged to 42`) — the latter degrade the store to a meaningless
  change log.
- **Event store** — the append-only log that is the **system of record / source
  of truth**. Each entity has its own ordered **eventstream**; the store
  supports append + read-by-stream and, ideally, optimistic-concurrency append.
  (It is *not* a message broker — Kafka et al. fan events out but lack
  per-entity stream reads and optimistic concurrency; see Drift Signals.)
- **Rehydration (replay)** — deriving an entity's current state by **replaying
  its eventstream** from the start (or from a snapshot) and applying each event
  in order. Current state is **derived, never the stored authority**.
- **Snapshot** — a serialized cache of an entity's state at a point in its
  stream, taken every *N* events, so rehydration loads the latest snapshot and
  replays only the tail. A snapshot is an **optimization, not the truth** — it
  is always regenerable from the eventstream.
- **Projection / read model (materialized view)** — a read-optimized view built
  by an event handler consuming the stream. It is **disposable and rebuildable
  from the event log alone**; there is no editing a projection in place — a
  change means replaying from event zero forward. This is the CQRS read side.
- **Event handler / consumer** — listens for events and updates a projection,
  triggers a side effect, or publishes an integration event. Delivery is
  typically **at-least-once**, so handlers must be **idempotent**.
- **Compensating event** — the *only* way to "undo" or correct: append a new
  event that reverses a prior one (`ReservationCanceled` compensating
  `SeatsReserved`). The original event stays; history records the reversal.
- **Event version + upcaster** — a version identifier on each event and a
  transformation that converts an older event schema to the current one **during
  deserialization on replay**, leaving stored events unchanged.

## Constraints

### The event log is the source of truth — stored events are immutable and append-only

- The event store is the **authoritative system of record**. State changes are
  recorded **only** by appending a new event; stored events are **never updated
  or deleted in place**.
- **Current state is derived by replaying events, not stored as the authority.**
  Any current-state representation (in memory, a row, a cache) is a *derived
  view* that can be discarded and rebuilt from the log.
- A correction or reversal is a **new compensating event appended** to the
  stream, never an edit of the offending event. (In-place rewrite of stored
  events undermines the audit trail and is a last-resort migration only.)

### This is not a plain audit log — the log IS the state

- In a plain CRUD-plus-audit system, current state lives in a table and the log
  is a **side record** of what happened. In event sourcing the relationship is
  inverted: the **log is the primary store and current state is the side
  view** derived from it. There is no authoritative current-state table behind
  the log.

### Projections are derived, rebuildable, and eventually consistent

- Every projection / read model is **rebuildable from the event log alone** —
  delete it and replay the stream to reconstruct it. Nothing of record lives
  only in a projection.
- Projections are **eventually consistent** with the write side: there is a
  delay between appending an event and a projection reflecting it. The system
  (and its consumers) must be designed to tolerate that window; ES does not offer
  read-your-write consistency across the projection boundary.

### Event application is idempotent; events are ordered and versioned

- Event handlers / projection updates are **idempotent** — processing the same
  event twice yields the same state and fires a side effect at most once
  (track the last processed sequence number, or design naturally-repeatable
  mutations). At-least-once delivery makes this mandatory, not optional.
- Per-entity event **order** is significant and preserved; concurrent appends to
  one stream are arbitrated by **optimistic concurrency** (reject-on-conflict,
  reload, retry), not by overwriting.
- Each event carries a **version**; schema evolution is handled by **upcasting**
  older versions to the current one on replay (and/or tolerant deserialization
  for additive changes), so application code handles only the latest shape while
  stored events stay immutable.

### Personal data vs. immutability

- The append-only, immutable store conflicts with deletion mandates (right to be
  forgotten). Design for it: keep personal data **outside** the eventstream
  referenced by id (delete independently), or **crypto-shred** (per-subject key,
  delete the key). Do not plan to delete events to satisfy erasure.

## Drift Signals (anti-patterns to reject in review)

- A stored event is updated or deleted in place to "fix" or change state →
  immutability violation; append a **compensating event** instead
- Current state persisted as the authority with the events kept only as a side
  audit log → that is CRUD-plus-audit, **not** event sourcing; if ES is selected,
  the log must be the source of truth
- A snapshot (or cache) treated as the authority / not regenerable from the
  stream → snapshot is an optimization; the eventstream remains the truth
- A projection holding data of record that cannot be rebuilt by replaying the
  log → make the projection fully rebuildable from events; nothing of record
  lives only in a read model
- Editing a projection in place to "correct" it instead of replaying → rebuild
  the projection from event zero
- Event handler that is not idempotent (double-applies on redelivery, fires a
  side effect twice) → make application idempotent (sequence tracking / safe
  mutations)
- Events with no version and no upcasting path → add a version + upcaster so
  schema can evolve without rewriting stored events
- State-snapshot events (`XChangedTo42`) instead of intent events
  (`TwoSeatsReserved`) → capture business intent, not just the resulting value
- A message broker (Kafka, …) used as the event store → use a real event store
  for the per-entity stream-of-record + optimistic concurrency; the broker is a
  distribution layer, not the system of record
- Event sourcing applied to thin reference/lookup CRUD with no history
  requirement → over-engineering; use current-state storage (see When to use)

## When to use

Select for the **slice(s) of a domain where the sequence of changes is itself
valuable** — where audit/history is a hard requirement, temporal queries
("state as of date X", "how did we get here") matter, or the change stream *is*
the product: **ledgers and financial transactions, order/booking lifecycles,
activity timelines, and lead/engagement event streams** (e.g. a per-lead
timeline ingesting open / click / bounce events is a strong fit — the events are
the asset). It also fits when you must avoid conflicting updates under high write
contention, or when the app already emits events naturally.

It is a **non-exclusive, composable** concern (no slot) and is **scoped per
domain slice, not whole-product** — apply it to the parts that benefit (the
payment ledger, the order pipeline) and use plain current-state storage
elsewhere; "don't event-source everything." `areas: data` scopes its practices
to data-layer work items. Compose with `domain-driven-design` (aggregates emit
the events ES persists), `onion-architecture` (the event store is an outer-ring
adapter behind an inner port), **CQRS** (the projections are the read side), and
`sample-data` (the seed is events appended to the store).

Do **NOT** select it for **thin CRUD / forms-over-data with no history
requirement**, mostly-static reference or lookup data (catalogs, config),
prototypes / short-lived tools where the schema-evolution and projection
investment never pays back, systems that require strong read-your-write
consistency and real-time views (projections are eventually consistent), or
teams with no event-driven experience adopting it blind. There, current-state
storage is the simpler, correct choice (KISS/YAGNI).

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- ADR: event-sourcing for the named slice + event store + snapshot/upcasting + eventual-consistency window
- TD: event store, rehydration/replay, projections/read-models, idempotent handlers, upcasters
- DATA_DESIGN: append-only eventstream as system of record; projections are rebuildable views
- TEST_PLAN: replay rebuilds state; idempotent handler (no double-apply); compensating-event correction

## ADR References

Record an ADR when selecting event sourcing for a given domain slice (it is a
costly-to-reverse persistence decision), naming the slice, the
audit/history/temporal justification, the event store choice, the
snapshot/upcasting strategy, and the projections and their eventual-consistency
window.
