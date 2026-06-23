# Concern: Onion Architecture

## Category
architecture

## Areas
all

## Slot
architecture-style

## Boundary

This concern owns **how the codebase layers itself and which way its
source-code dependencies point** — the application's dependency structure. It
fills the exclusive `architecture-style` slot (one structuring discipline wins
per project); its slot-siblings are other whole-codebase structuring styles
(`hexagonal`, `clean`, `classic-layered`). It does not define *what* to model
and it does not own object-level design patterns:

- **`domain-driven-design`** owns **WHAT** sits at the center — aggregates,
  entities, value objects, invariants, the ubiquitous language. Onion owns
  **HOW** the layers are arranged and which direction dependencies are inverted.
  They **compose**: DDD's domain model is exactly what lives in Onion's core,
  and Onion is the dependency discipline that keeps that model
  infrastructure-free. This concern references DDD as the complement; it does
  **not** restate aggregate/invariant/ubiquitous-language modeling rules.
- **`design-patterns-gof`** owns **object-level** collaboration patterns
  (factory, strategy, observer) inside a layer. Onion is the **macro** layering
  rule across the whole codebase, not a catalog of object patterns.
- **`enterprise-integration-patterns`** owns **between-system** messaging and
  integration. Onion governs the dependency structure **within** one
  deployable; integration adapters are simply outer-ring code under it.

Onion is one named member of the **dependency-inversion architecture family**
(Cockburn's Hexagonal / Ports-and-Adapters and Martin's Clean Architecture are
its close relatives — all three impose the same inward-only dependency rule).
Picking this concern picks **Onion's vocabulary and ring layout**; the family
constraints below hold for whichever sibling fills the slot.

## Components

- **Domain model core** — the innermost ring: entities, value objects, and
  domain logic that model truth for the organization. Depends on nothing
  outside itself. (Its *contents* are governed by `domain-driven-design` when
  that concern is also selected.)
- **Domain services** — behavior that spans multiple domain objects but is
  still pure domain logic, sitting just outside the core model.
- **Application services** — the application-specific orchestration (use
  cases / workflows) that drives the domain to satisfy a request. **Declares**
  the interfaces (repositories, gateways, notifiers) it needs from the outside
  world.
- **Interfaces declared by inner layers** — repository / gateway / port
  abstractions expressed in the inner rings in domain terms, stating what the
  core *needs*, not how it is provided.
- **Outer ring (infrastructure / UI / tests)** — persistence, HTTP controllers
  and handlers, message/queue clients, external-service clients, the UI, and
  the test harness. This ring **implements** the inner interfaces and is wired
  in at composition time. Everything replaceable as a "detail" lives here.
- **Composition root** — the single outermost place (entrypoint / DI container
  / `main`) that constructs concrete outer-ring implementations and injects
  them into the inner layers at runtime.

## Constraints

### The Dependency Rule — dependencies point only inward

- Source-code dependencies cross ring boundaries **only toward the center**.
  Any code may depend on something more central; nothing may depend on
  something further out. All coupling is toward the core.
- The **domain model core depends on nothing** outside itself — not on a
  framework, an ORM, a web library, a database driver, or an outer-ring
  package. It is coupled only to itself.
- The **database/UI/framework are external details**, not the foundation. The
  database is not the center; it is plugged into the outer ring.

### Dependency inversion across the boundary

- **Inner layers declare interfaces; outer layers implement them.** The
  abstraction (the port / repository interface) is owned by the inner ring in
  domain terms; the concrete adapter (the SQL repository, the HTTP client)
  lives in the outer ring and implements that interface.
- Concrete outer-ring implementations are **injected at runtime** by the
  composition root, never constructed by or `import`-ed into inner-ring code.
- Data crossing a boundary is expressed in **inner-layer terms** (domain
  objects or simple DTOs the inner layer owns) — outer-ring shapes (ORM rows,
  framework request objects) do not leak inward.

### Direction of control vs. direction of dependency

- Control flows **inward** at request time (a controller calls an application
  service) and the result flows back out, while the **source-code dependency**
  still points inward (the controller depends on the application service, never
  the reverse). Dependency inversion is what reconciles the two.

### Testability is the payoff, not an add-on

- Because the core depends only on interfaces, the domain and application
  layers are **exercisable without infrastructure** — substitute a fake/stub
  adapter for the real one at the boundary. (How those tests are written is the
  `testing` concern's call; Onion only guarantees the seam exists.)

## Selection signals (when this slot filler fits — and when it is over-engineering)

Onion (and its family) earns its layering cost when the structure pays for
itself:

- **Select Onion** for products with **non-trivial business logic** that
  deserves to live free of infrastructure, **swappable infrastructure or
  adapters** (the datastore, an external provider, or the delivery mechanism is
  expected to change or be doubled), and a need for a **testable, isolated
  domain**. Long-lived domain-driven systems are the canonical fit; it composes
  naturally with `domain-driven-design`.
- **Do NOT select Onion** for **thin CRUD** or a forms-over-data app with
  little behavior, a throwaway / short-lived tool, or a small team unfamiliar
  with the discipline. There, the ring ceremony and interface indirection is
  **over-engineering** — choose the simpler `classic-layered` filler (or no
  explicit `architecture-style`) instead. Per KISS/YAGNI, layering you cannot
  justify by changeability or domain complexity is cost without payoff.

## Drift Signals (anti-patterns to reject in review)

- An inner-ring file `import`s an infrastructure/framework/ORM package →
  Dependency Rule violation; depend on an inner-layer interface and inject the
  implementation
- A repository/gateway interface declared in the outer ring (or in the same
  package as its SQL implementation) → declare it in the inner layer, implement
  it outside
- An application service `new`s up a concrete database/HTTP client directly →
  inject it via the composition root against the inner interface
- A controller/handler that the domain or application layer depends on →
  dependency points the wrong way; controllers depend on application services,
  never the reverse
- ORM rows / framework request objects passed into the domain core → translate
  to domain objects / inner DTOs at the boundary
- Full ring ceremony wrapped around a thin CRUD app with no real domain logic →
  over-engineering; reconsider the `architecture-style` selection

## When to use

Select as the `architecture-style` filler when the product has **non-trivial
domain logic, swappable infrastructure, or a testable-domain requirement** (see
Selection signals). One `architecture-style` filler wins per project; Onion,
`hexagonal`, `clean`, and `classic-layered` are the competing fillers. Compose
with `domain-driven-design` (which governs the core's contents) and with the
tech-stack concern (whose package/module system enforces the import graph).
`areas: all` because the dependency rule constrains every buildable work item.

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- ADR: Onion chosen for the architecture-style slot over its siblings
- TD: ring layout, inner-declared ports, outer-ring adapters, composition root

## ADR References

Record an ADR when selecting Onion over a slot-sibling (`hexagonal` / `clean` /
`classic-layered`), or when an operator overrides the `architecture-style`
default per project.
