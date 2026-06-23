# Concern: Domain-Driven Design

## Category
architecture

## Areas
data, api

## Boundary

This concern owns **what to model** — the shape of the domain itself: the
ubiquitous language, the bounded contexts the model lives in, and the
behavior-rich entities, value objects, and aggregates that enforce business
invariants. It does **not** own how the model is layered into the codebase, nor
the catalog of reusable object/integration mechanics. Four neighbors must stay
distinct:

- **`onion-architecture`** (the layering / dependency-inversion concern) owns
  **how** the model is arranged in code: the dependency rule (dependencies point
  inward), which layer the domain, application, and infrastructure live in, and
  why the domain depends on nothing outward. DDD says *aggregates enforce
  invariants and repositories return aggregates*; onion says *the domain layer
  defines the repository interface and infrastructure implements it*. DDD is the
  **content**; onion is the **arrangement**. Reference onion as complementary; do
  **not** restate the dependency rule or layer boundaries here.
- **`design-patterns-gof`** owns general-purpose object-construction and
  collaboration mechanics (factory-method vs abstract-factory, strategy,
  observer, …). DDD's Factory and Domain Event are *domain-modeling roles* with
  business meaning, not the GoF mechanics that may implement them. Name the
  domain role; leave the implementing pattern to that concern.
- **`enterprise-integration-patterns`** owns messaging/integration mechanics
  between systems (channels, routers, message transformation). DDD's domain
  events and eventual consistency *across aggregates* state **what** must
  propagate and **why** (a true invariant lives in one aggregate; cross-aggregate
  rules reconcile eventually); EIP owns the **transport** that carries it.
- **`sample-data`** owns the seed/demo dataset the running product loads. DDD
  defines the aggregates and invariants that dataset must respect; it does not
  generate data.

## Components

- **Ubiquitous language** — one precise, shared vocabulary per bounded context,
  used identically in conversation, specs, and code (type, method, and event
  names). A concept has exactly one meaning inside its context.
- **Bounded contexts + context map** — explicit boundaries where a given model
  and language apply, and the map of how models relate across boundaries
  (shared kernel, customer/supplier, conformist, anti-corruption layer).
- **Subdomain classification** — each part of the problem space labeled **core**
  (the differentiating business value, where modeling effort concentrates),
  **supporting** (necessary but not differentiating), or **generic** (a solved
  problem, buy/adopt rather than model deeply).
- **Anti-corruption layer (ACL)** — a translation boundary that keeps a foreign
  or legacy model from leaking its concepts into this context's model.
- **Entities** — domain objects with a stable identity that persists through
  state changes; equality is by identity, not attribute values.
- **Value objects** — immutable objects defined wholly by their attributes; two
  are equal iff their attributes are equal. Prefer them for descriptive concepts
  (money, date range, address) and hold invariants at construction.
- **Aggregates + aggregate roots** — a consistency cluster of entities and value
  objects treated as one unit. The **root** is the only member external code
  references or loads; it is the gatekeeper that enforces the aggregate's
  invariants. The aggregate boundary is the **transactional consistency
  boundary**.
- **Domain events** — named records of something meaningful that happened in the
  domain (`InvoiceIssued`, `PaymentSettled`), used to propagate changes across
  aggregate boundaries.
- **Repositories** — collection-like interfaces that retrieve and persist
  **whole aggregates** (one repository per aggregate root). They return domain
  aggregates, never persistence/ORM/row types.
- **Domain services** — stateless operations expressing domain logic that has no
  natural home on a single entity or value object (e.g. a transfer spanning two
  accounts). Distinct from application/infrastructure services.
- **Factories** — encapsulate creation of a complex aggregate so it is born in a
  valid, invariant-satisfying state.

## Constraints

### Aggregates enforce invariants in the domain, not at the edges

- A **true invariant** — a business rule that must hold consistently at every
  commit — is enforced **inside the aggregate root**, in the domain layer. It is
  **not** enforced in controllers, request handlers, application services, or the
  database.
- The aggregate root is the only entry point: external code mutates the
  aggregate's internals **through root methods** that guard the invariant, never
  by reaching in and setting fields directly.
- An aggregate must be modifiable in any business-required way with its
  invariants fully consistent within a **single transaction**.

### Vernon's aggregate design rules (defaults, not absolutes)

These are the well-known rules from *Implementing Domain-Driven Design*; treat
them as defaults that a deviation must justify (record it in an ADR):

1. **Model true invariants in consistency boundaries** — put inside one
   aggregate exactly what must stay transactionally consistent, and no more.
2. **Design small aggregates** — prefer a root entity plus value objects;
   resist god aggregates that pull in everything reachable. Large-cluster
   aggregates do not scale and become a contention nightmare.
3. **Reference other aggregates by identity** — hold another aggregate's
   **id**, not a direct object reference. This keeps the boundary crisp and
   prevents a single transaction from quietly mutating two aggregates.
4. **Update other aggregates with eventual consistency** — when a command on one
   aggregate must trigger rules on another, do it **outside** the transaction via
   a domain event, not by enlarging the transaction to span both.

The corollary rule: **modify only one aggregate per transaction.** A transaction
that commits changes to two aggregate roots is a design smell pointing at a
mis-drawn boundary.

### Persistence must not leak into the domain

- Repositories return and accept **aggregates**; ORM entities, row structs,
  query builders, ResultSets, and database column names **never** appear in the
  domain model's public surface.
- The domain model is expressed in domain terms (the ubiquitous language), not
  in storage terms. Persistence concerns conform to the model, not the reverse.
  (How this is enforced via dependency inversion is `onion-architecture`'s
  business; this concern only asserts the leak must not happen.)

### No anemic domain model

- Behavior lives **with the data it guards**. Entities and value objects expose
  domain methods that enforce rules — not just public getters/setters with all
  logic drained into procedural "manager"/"service" classes.
- Validation, calculation, and state-transition rules for an aggregate belong on
  that aggregate, not in a handler that sets its fields from the outside.

### Language and boundaries are explicit

- Each bounded context has a named, documented ubiquitous language; the same
  word does not mean two things inside one context, and a model is not silently
  reused across contexts.
- Cross-context model translation goes through an **anti-corruption layer**; a
  foreign model is not absorbed wholesale into this context.

## Drift Signals (anti-patterns to reject in review)

- Entities/value objects that are bags of getters and setters with logic in
  separate "service"/"manager" classes → **anemic domain model**; move behavior
  onto the aggregate it guards
- An aggregate that transitively pulls in large object graphs / everything
  reachable → **god aggregate**; split it, reference the rest by identity
- A transaction that commits two or more aggregate roots → mis-drawn boundary;
  keep the true invariant in one aggregate, reconcile the rest eventually
- A direct object reference to another aggregate's internals → replace with a
  reference by identity
- An invariant checked in a controller/handler/route instead of inside the
  aggregate → move enforcement into the domain
- ORM entities / row types / query objects appearing in the domain's public
  surface or returned from a repository → **persistence leaking into the
  domain**; the repository must deal in aggregates
- The same term meaning different things in one context, or one model copied
  across contexts with no ACL → tighten the ubiquitous language / introduce a
  bounded-context boundary
- Value-object concepts (money, date range, email) modeled as bare primitives
  with rules scattered at call sites → introduce the value object and hold its
  invariant at construction

## When to use

Any **domain-rich business application** — one with non-trivial business
entities that carry **invariants, lifecycle, and relationships** (invoicing,
CRM, ordering, billing, scheduling, ledgers, …). High autonomy auto-selects this
concern for such products (see `workflows/references/concern-resolution.md`).
It is composable (no slot); `areas: data, api` scopes its practices to the
domain and service layers. Compose with **`onion-architecture`** (which arranges
the model into layers), with the tech-stack concern (which fixes the language),
and with `sample-data` (whose seed must respect the aggregates' invariants). Do
**not** select it for pure presentation/marketing sites, thin CRUD-only
admin tools with no business rules, or libraries with no domain.

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- ADR: bounded-context map + subdomain classification + aggregate boundaries
- TD: aggregates/value-objects/repositories/domain-services/factories model
- DATA_DESIGN: schema mirrors aggregate boundaries; cross-aggregate refs by identity

## ADR References
