# Practices: Domain-Driven Design

These practices govern **what the domain model is** — its language, boundaries,
and behavior-rich building blocks. They do **not** govern how the model is
layered into the codebase (that is `onion-architecture`), nor the reusable
object/integration mechanics that may implement a role (`design-patterns-gof`,
`enterprise-integration-patterns`). When a rule below references layering, defer
to onion for the *how*; this concern asserts the *what*.

## Discover

- Classify the area's **subdomain** as core / supporting / generic. Concentrate
  modeling effort on **core**; do not deeply model a **generic** subdomain that a
  bought/adopted solution already solves.

## Frame

- Name the **bounded context(s)** the work lives in, and the **ubiquitous
  language** of each: the precise domain terms for the concepts, used identically
  in specs, type names, methods, and events. A term MUST NOT mean two different
  things inside one context.
- When this context consumes a foreign or legacy model, translate it through an
  **anti-corruption layer** — the foreign concepts MUST NOT leak into this
  context's model.
- Each Vernon rule is a **default**; a deliberate deviation MUST be recorded in
  an ADR with its justification.

## Design

- Model concepts with **identity and lifecycle** as **entities** (equality by
  identity); model descriptive, replaceable concepts (money, quantity, date
  range, email, address) as **immutable value objects** (equality by attributes),
  with their invariant held **at construction**.
- Behavior MUST live **with the data it guards**: an entity/value object exposes
  domain methods that enforce its rules. **No anemic domain model** — do not drain
  all logic into procedural "service"/"manager" classes leaving getters/setters
  behind.
- Use a **factory** when constructing a complex aggregate so it is born valid;
  use a **domain service** (stateless) only for logic that genuinely has no home
  on a single entity or value object (e.g. an operation spanning two aggregates).
- Draw the **aggregate boundary** around exactly the true invariant — the rule
  that MUST stay transactionally consistent — and **no more**. The aggregate
  boundary IS the transactional consistency boundary.
- **Design small aggregates** (default: a root entity + value objects). Resist
  pulling in every reachable association — that is a god aggregate.
- The **aggregate root** is the only member external code references or loads,
  and the only entry point for mutation: change internals **through root methods**
  that enforce the invariant, never by setting fields from outside.
- **Reference other aggregates by identity** (hold their id), not by direct
  object reference.
- **Modify only one aggregate per transaction.** When a command on one aggregate
  must affect another, publish a **domain event** and reconcile with **eventual
  consistency** outside the transaction — do not enlarge the transaction to span
  both roots.

## Build

- **Repositories return and accept aggregates** — one repository per aggregate
  root. ORM entities, row structs, query builders, ResultSets, and raw column
  names MUST NOT appear in the domain model's public surface or cross a
  repository boundary into the domain.
- The model is expressed in the **ubiquitous language**, not in storage terms;
  persistence conforms to the model, not the reverse. (The dependency-inversion
  mechanism that makes this hold is `onion-architecture`'s practice.)
- Every true invariant is checked **inside the aggregate**, in the domain layer
  — **not** in a controller, request handler, route, or application service, and
  **not** delegated to a database constraint as the sole guard.
- An application service / handler coordinates (load aggregate → call a root
  method → save via repository); it MUST NOT contain the business rule itself.

## Test

- Each work item's bounded context and ubiquitous language are named; domain
  type/method/event names match that language (no synonym drift, no term with two
  meanings in one context).
- Aggregates enforce their invariants **in the domain layer** — verifiable that
  no invariant is checked only in a controller/handler/route or only as a DB
  constraint.
- **No anemic domain model**: entities/value objects expose behavior; logic is
  not drained into procedural service classes leaving bare getters/setters.
- Each transaction modifies **exactly one** aggregate root; cross-aggregate
  effects go through a domain event + eventual consistency (or a recorded ADR
  deviation).
- Aggregates reference other aggregates **by identity**, not by direct object
  reference; aggregates are small (root + value objects by default).
- **Repositories return aggregates**; no persistence/ORM/row types appear in the
  domain's public surface or cross a repository boundary into the domain.
- Descriptive concepts with invariants (money, ranges, identifiers) are modeled
  as immutable value objects, not bare primitives with rules scattered at call
  sites.

## Cross-cutting

### Boundary with neighbors

- For **layering** (where domain/application/infrastructure live, the dependency
  rule, who defines the repository interface) defer to `onion-architecture`; do
  not restate it here.
- A DDD **Factory** / **Domain Event** is a domain role; the GoF mechanic or the
  messaging transport that implements it belongs to `design-patterns-gof` /
  `enterprise-integration-patterns`. Name the domain role; do not specify the
  mechanic here.
