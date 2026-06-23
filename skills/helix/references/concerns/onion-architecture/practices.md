# Practices: Onion Architecture

These practices make the **Dependency Rule** (source-code dependencies point
only inward, toward the domain) checkable in review. They govern **HOW** the
codebase layers and inverts dependencies — not **WHAT** sits in the core
(`domain-driven-design` owns aggregates/invariants/ubiquitous language), not
object-level patterns (`design-patterns-gof`), not between-system messaging
(`enterprise-integration-patterns`). Where DDD is also selected, its domain
model is exactly what lives in the core ring described here.

## Discover

- Apply the full ring layering only when the **selection signals** in
  `concern.md` hold (non-trivial domain logic, swappable infrastructure, or a
  testable-domain requirement). For **thin CRUD / forms-over-data** with little
  behavior, the ring ceremony is over-engineering — prefer the
  `classic-layered` slot filler, recorded as the `architecture-style` choice.
- Per KISS/YAGNI, do not introduce an interface for a boundary that has exactly
  one implementation and no realistic prospect of a second **unless** it is
  needed to keep the domain testable in isolation.

## Design

- The code MUST be organized into concentric rings — **domain model core →
  domain services → application services → outer ring (infrastructure / UI /
  tests)** — with a discoverable mapping from ring to package/module/directory.
- Source-code dependencies MUST point **only inward**: any ring may depend on a
  more central ring; **no ring may depend on a ring further out** (verify the
  import graph).
- The **domain layer MUST import nothing** from infrastructure, framework, ORM,
  web, or any outer-ring package (verify the domain package's import graph has
  zero edges to those packages).
- Control may flow inward and results flow back out, but the **source-code
  dependency still points inward** — a controller/handler depends on an
  application service; the application/domain layers MUST NOT depend on the
  controller.
- Interfaces the core needs (repositories, gateways, ports, notifiers) MUST be
  **declared in the inner layer** (domain or application) in domain terms, and
  **implemented in the outer ring**. The interface and its concrete
  implementation MUST NOT live in the same outer-ring package.
- Inner-layer code MUST depend on these interfaces, never on the concrete
  outer-ring class. Inner code MUST NOT `new`/construct or `import` a concrete
  infrastructure implementation directly.
- Data crossing a boundary MUST be expressed in **inner-layer terms** — domain
  objects or DTOs the inner layer owns. ORM rows, framework request/response
  objects, and other outer-ring shapes MUST NOT leak into the domain or
  application layers; translate at the boundary.

## Build

- Concrete outer-ring implementations MUST be **injected at runtime by the
  composition root** (the entrypoint / DI container / `main`). The composition
  root is the **only** place that names concrete infrastructure types.
- The domain and application layers SHOULD be **buildable/exercisable without
  any infrastructure present** — substituting a fake/stub adapter for each
  inner-layer interface should compile and run. (Writing those tests is the
  `testing` concern's job; this practice only requires the seam to exist.)
- The database, UI, and framework MUST be treated as **replaceable details** in
  the outer ring — swapping one (a different datastore, a different web
  framework) SHOULD require changes only in the outer ring and the composition
  root, not in the core.

## Test

- Import-graph check: the domain layer has **zero** dependency edges to
  infrastructure / framework / ORM / web / outer-ring packages.
- Every cross-boundary dependency points **inward**; no inner ring depends on a
  more-outer ring (verify the import graph across all ring boundaries).
- Every infrastructure adapter **implements an interface declared in an inner
  layer**; no inner-layer code constructs or imports a concrete infrastructure
  implementation.
- Controllers/handlers depend on application services, **never the reverse**.
- Concrete infrastructure types are named only in the **composition root**;
  inner layers reference only the interfaces.
- No outer-ring shapes (ORM rows, framework request objects) appear in the
  domain or application layers — boundary translation is present.
- The `architecture-style` selection fits the product: ring layering is not
  wrapped around a thin-CRUD app (else re-select `classic-layered`).

## Cross-cutting

### Boundary with sibling concerns

- The **contents** of the core (aggregates, entities, value objects,
  invariants, ubiquitous language) are governed by `domain-driven-design`, not
  here. Do not restate DDD modeling rules in Onion review; do verify the model
  sits in the core ring with inward-only dependencies.
- Object-level collaboration patterns inside a layer are `design-patterns-gof`;
  between-system integration is `enterprise-integration-patterns`. Onion only
  governs the macro dependency structure across the codebase.
