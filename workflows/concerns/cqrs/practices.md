# Practices: CQRS (Command Query Responsibility Segregation)

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
