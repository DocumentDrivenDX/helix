---
title: "Clean Architecture"
slug: clean-architecture
generated: true
aliases:
  - /reference/glossary/concerns/clean-architecture
---

**Category:** Architecture · **Areas:** all

## Description

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

## Practices by activity

Agents working in any of these activities inherit the practices below via the bead's context digest.

These practices make Martin's **Dependency Rule** ("source code dependencies
can only point inwards; nothing in an inner circle knows anything about an outer
circle") and its **explicit use-case interactors** checkable in review. They
govern **HOW** the codebase arranges its rings and boundaries — not **WHAT**
sits in the Entities ring (`domain-driven-design` owns aggregates/invariants/
ubiquitous language), not object-level patterns (`design-patterns-gof`), not
between-system messaging (`enterprise-integration-patterns`). Where DDD is also
selected, its model is exactly the Entities ring described here.

The differentiator versus the sibling dependency-inversion styles (`onion` /
`hexagonal`): Clean review additionally checks for **named use-case interactors
with input/output boundary interfaces** and **request/response DTOs at every
boundary** — not just inward-pointing dependencies.

## The four rings and the Dependency Rule

- Code MUST be organized into concentric rings —
  **Entities → Use Cases → Interface Adapters → Frameworks/Drivers** — with a
  discoverable mapping from ring to package/module/directory.
- Source-code dependencies MUST point **only inward**: any ring may depend on a
  more central ring; **no ring may depend on a ring further out** (verify the
  import graph across all ring boundaries).
- The **Entities ring MUST import nothing** from Use Cases, Interface Adapters,
  or Frameworks/Drivers. The **Use Cases ring MUST import only Entities** — no
  framework, ORM, web, or outer-ring package (verify both inner rings' import
  graphs have zero edges outward).

## Explicit use-case interactors

- Each application operation MUST be expressed as a **named use-case interactor**
  in the Use Cases ring, not as logic scattered into controllers or entities.
  The interactor is the unit that orchestrates entities to satisfy a request.
- Each interactor MUST declare its **input boundary** (the interface a
  controller calls to invoke it) and, where it returns a result for
  presentation, an **output boundary** (the interface a presenter implements).
  These boundary interfaces are declared **in the inner ring**, implemented
  outward.

## Dependency inversion at every inward boundary

- When an inner ring needs an outer capability (persistence, presentation,
  external service), the inner ring MUST **declare the boundary interface** and
  the outer ring MUST **implement** it. Controllers call the input boundary;
  presenters implement the output boundary; gateways/repositories implement the
  persistence boundary the use case declares.
- Inner-ring code MUST depend only on these boundary interfaces, never on a
  concrete controller, presenter, gateway, ORM, or framework type, and MUST NOT
  `new`/construct or `import` one.
- Concrete outer-ring types MUST be **injected at runtime by the composition
  root** (the only place that names concrete framework/DB/controller types).

## DTOs cross boundaries; entities and framework objects do not

- Only **simple request/response data structures the inner ring owns** may cross
  a ring boundary. **Entities MUST NOT be passed outward across a boundary**, and
  **ORM rows / framework request/response objects MUST NOT be passed inward** —
  translate at the boundary (controller maps to a request DTO; presenter maps a
  response DTO to a view model).

## Keep entities and use cases independent

- The Entities and Use Cases rings SHOULD be **buildable/exercisable with the
  Frameworks/Drivers ring absent** — substituting fakes for each boundary
  interface should compile and run. (Writing those tests is the `testing`
  concern; this practice only requires the boundary seams to exist.)

## Match the discipline to the product (avoid over-engineering)

- Apply the full four-ring + interactor + boundary-DTO structure only when the
  **selection signals** in `concern.md` hold — a larger/longer-lived system that
  wants explicit named use cases. For thin CRUD with no real application logic,
  the interactor + per-boundary-DTO ceremony is over-engineering — prefer
  `classic-layered` (or `onion` if you want inversion without named
  interactors), recorded as the `architecture-style` choice.
- Per KISS/YAGNI, do NOT manufacture an interactor + input/output boundary +
  request/response DTO for an operation that is a trivial pass-through with no
  application logic, unless it is needed to keep the boundary testable in
  isolation.

## Boundary with sibling concerns

- The **contents** of the Entities ring are governed by `domain-driven-design`,
  not here. Verify the model sits in the Entities ring with inward-only
  dependencies; do not restate DDD modeling rules.
- Object-level collaboration patterns inside a layer are `design-patterns-gof`;
  between-system integration is `enterprise-integration-patterns`. Clean governs
  only the macro ring/boundary structure across the codebase.

## Quality Gates

- Import-graph check: the Entities ring has **zero** outward edges; the Use
  Cases ring imports **only** Entities (no framework/ORM/web/outer-ring edges).
- Ring-direction check: every cross-boundary dependency points **inward**; no
  ring depends on a more-outer ring (verify across all ring boundaries).
- Use-case check: each application operation is a **named interactor** in the
  Use Cases ring with declared input (and, where applicable, output) boundary
  interfaces; application logic is not scattered into controllers or entities.
- Boundary-ownership check: persistence/output-boundary interfaces are declared
  by the inner ring (the use case) and implemented in Interface Adapters — not
  declared alongside their implementation in the outer ring.
- DTO-crossing check: only request/response DTOs the inner ring owns cross ring
  boundaries; no entity is passed outward and no ORM row / framework object is
  passed inward (translation present at each boundary).
- Wiring check: concrete framework/DB/controller/presenter types are named only
  in the composition root; inner rings reference only boundary interfaces.
- Selection-fit check: the system's size/longevity justifies explicit
  interactors + per-boundary DTOs; the four-ring ceremony is not wrapped around a
  thin-CRUD app (else re-select `classic-layered`, or `onion` for inversion
  without named interactors).
