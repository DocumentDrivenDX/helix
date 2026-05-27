# Concern: Clean Architecture

## Category
architecture

## Areas
all

## Slot
architecture-style

## Boundary

This concern owns **how the codebase arranges itself as concentric layers
governed by the Dependency Rule, with explicit use-case interactors at the
center of the application** — Robert C. Martin's Clean Architecture. Martin
states it as a synthesis of Hexagonal, Onion, BCE, and DCI; its overriding rule
is *"source code dependencies can only point inwards. Nothing in an inner
circle can know anything at all about something in an outer circle."* It fills
the exclusive `architecture-style` slot (one structuring discipline wins per
project).

Clean is a member of the **dependency-inversion architecture family**; its
slot-siblings `onion-architecture` and `hexagonal-architecture` impose the same
inward-only rule. They are honestly close relatives — the differentiator is
**practical, not dogmatic**:

- **vs `onion-architecture`** — both draw concentric rings with an
  infrastructure-free domain at the center. Clean's distinguishing emphasis is
  the **named, explicit Use Case layer**: application logic is captured as
  **use-case interactors** with their own **input/output boundary interfaces and
  DTOs**, sitting in their own ring between Entities and Interface Adapters.
  Pick Clean over Onion when you want **use cases as first-class, individually
  named units** (one interactor per application operation, request/response
  models at each boundary) — the explicit interactor + boundary-DTO structure is
  the reason to choose it.
- **vs `hexagonal-architecture`** — Hexagonal emphasizes the **symmetry of
  ports/adapters** around a flat core. Clean prescribes a **specific
  four-ring stack** (Entities → Use Cases → Interface Adapters →
  Frameworks/Drivers) and the role of each ring. Pick Clean when the layered
  ring stack and use-case interactors are the organizing idea; pick Hexagonal
  when adapter symmetry/plurality is.
- **vs `classic-layered`** — classic-layered lets the business layer depend
  directly on data-access (no inversion). Clean inverts every inward boundary
  via the Dependency Rule and DTOs.
- **vs `domain-driven-design`** — DDD owns **WHAT** sits in the Entities ring
  (aggregates, invariants, ubiquitous language). Clean owns **HOW** the rings
  are arranged and how use cases drive the entities. They **compose**: DDD's
  model is the Entities ring; Clean keeps it and the use cases
  framework-independent. Reference DDD as the complement; do not restate
  modeling rules.
- **vs `design-patterns-gof` / `enterprise-integration-patterns`** — object-level
  patterns inside a layer and between-system messaging respectively; Clean is
  the macro ring discipline for one deployable.

## Components

- **Entities (innermost ring)** — enterprise-wide business rules: the most
  general, least-likely-to-change business objects. Depend on nothing outside.
  (Their *contents* are governed by `domain-driven-design` when selected.)
- **Use Cases / interactors** — application-specific business rules. Each
  interactor **orchestrates the flow of data to and from the entities** to
  achieve one application operation. Defines its own **input boundary** (the
  interface a controller calls) and **output boundary** (the interface a
  presenter implements), and the **request/response model DTOs** that cross
  them.
- **Interface Adapters** — controllers, presenters, gateways, and view models
  that **convert data** between the format convenient for use cases/entities and
  the format convenient for an external agency (web, DB, UI). Repository
  implementations and ORM mapping live here.
- **Frameworks & Drivers (outermost ring)** — the web framework, the database,
  the UI toolkit, external devices. Mostly glue; the place all volatile detail
  is confined.
- **Boundary interfaces & DTOs** — the input/output boundary interfaces a
  use case declares, and the simple data structures that cross every ring
  boundary.
- **Composition root** — the outermost wiring that constructs concrete
  outer-ring types (controllers, presenters, gateways, framework objects) and
  injects them so inner rings depend only on boundary interfaces.

## Constraints

### The Dependency Rule — source dependencies point only inward

- Source-code dependencies cross ring boundaries **only toward the center**.
  Nothing in an inner ring may name, import, or know anything about an outer
  ring — not a class, function, variable, or data format declared outside.
- The **Entities ring depends on nothing** outside itself. The **Use Cases
  ring** depends only on Entities. Frameworks, the database, and the UI are
  outermost **detail**, never depended on by inner rings.

### Crossing a boundary inward uses Dependency Inversion

- When control must flow from an inner ring out to an outer one (a use case
  needs to persist, or to present a result), the inner ring **declares a
  boundary interface** and the outer ring **implements** it — so the source
  dependency still points inward. Use cases declare input/output boundaries;
  controllers call the input boundary, presenters implement the output boundary,
  gateways implement the persistence boundary.

### Use cases are explicit and first-class

- Application logic is expressed as **named use-case interactors**, one per
  application operation, not scattered into controllers or entities. The
  interactor is the unit that orchestrates entities to satisfy a request.

### Data crossing boundaries are simple structures

- Only **simple data structures / DTOs** cross ring boundaries — request and
  response models the inner ring owns. **Entities, ORM rows, and framework
  objects MUST NOT be passed across a boundary**; passing an entity outward, or
  a database row / framework request object inward, violates the Dependency
  Rule. Translate at the boundary.

### Independence is the payoff

- The architecture yields a system **independent of frameworks, UI, and
  database, and testable without them** — entities and use cases are
  exercisable with the outer rings absent. (How tests are written is the
  `testing` concern; Clean only guarantees the boundary seams exist.)

## Drift Signals (anti-patterns to reject in review)

- An inner ring (Entities or Use Cases) imports a framework / ORM / web /
  outer-ring package → Dependency Rule violation; depend on a boundary interface
  and inject the implementation
- Application logic living in controllers or entities instead of in a named
  use-case interactor → use cases are not first-class; extract the interactor
- An entity, ORM row, or framework request/response object passed **across a
  ring boundary** → only request/response DTOs the inner ring owns may cross;
  translate at the boundary
- A persistence/gateway or output-boundary interface declared in the Interface
  Adapters ring (with its implementation) instead of being declared by the use
  case it serves → declare the boundary in the inner ring, implement it outward
- A presenter or controller that a use case or entity depends on → dependency
  points the wrong way; inner rings depend only on boundary interfaces
- Concrete framework/DB/controller types named outside the composition root →
  move wiring to the composition root
- Full four-ring + interactor + boundary-DTO ceremony around a thin CRUD app
  with no real application logic → over-engineering; reconsider the
  `architecture-style` selection (likely `classic-layered`)

## When to use

Select as the `architecture-style` filler for **larger or longer-lived systems
that want application logic captured as explicit, individually named use-case
interactors** with request/response DTOs at every boundary, framework/DB/UI
confined to the outermost ring, and the full Dependency Rule enforced. The
explicit interactor + boundary-DTO structure is the reason to choose Clean over
its siblings. Prefer **`onion`** when you want the same concentric
domain-centric inversion but **without** the ceremony of named interactors and
per-boundary DTOs; prefer **`hexagonal`** when **adapter symmetry/plurality** is
the organizing concern rather than the ring stack; prefer **`classic-layered`**
for thin/CRUD where inversion is not worth it. One `architecture-style` filler
wins per project. Compose with `domain-driven-design` (Entities-ring contents)
and the tech-stack concern (package system enforcing the import graph).
`areas: all` because the Dependency Rule constrains every buildable work item.

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- ADR: Clean chosen for architecture-style slot; interactor/boundary-DTO ceremony justified by size/longevity
- TD: Entities/Use-Cases/Interface-Adapters/Frameworks rings, interactors, boundary DTOs, composition root

## ADR References

Record an ADR when selecting Clean over a slot-sibling
(`onion` / `hexagonal` / `classic-layered`) — the ADR should justify the
explicit-use-case-interactor ceremony by system size/longevity — or when an
operator overrides the `architecture-style` choice per project.
