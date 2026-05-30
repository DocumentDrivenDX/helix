---
title: "Classic Layered Architecture"
slug: classic-layered
generated: true
aliases:
  - /reference/glossary/concerns/classic-layered
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

This concern owns **how the codebase layers itself when dependencies are
allowed to point straight down** — the conventional N-tier stack
(**presentation → application/service → domain → data-access**) where each
layer depends directly on the layer beneath it, with **no enforced dependency
inversion**. It fills the exclusive `architecture-style` slot (one structuring
discipline wins per project). It is the **low-ceremony baseline**: it gives a
growing codebase a place for everything without paying for interface
indirection or a composition root.

It does **not** define *what* to model, and it is distinguished from its three
slot-siblings by the **direction of the source-code dependency at the
data-access boundary**:

- **`onion-architecture`**, **`hexagonal-architecture`**, and
  **`clean-architecture`** are the **dependency-inversion family**: each
  declares the persistence/gateway interface in an inner ring and has the
  outer ring implement it, so the business logic depends on nothing concrete.
  Classic-layered is the **odd one out**: its business/domain layer depends
  **directly** on the data-access layer (the dependency points down, not
  inward), so the most important logic is coupled to data-access
  implementation details. That single property — no inverted persistence
  boundary — is what separates this concern from the other three. Pick
  classic-layered when that coupling is an acceptable price for less ceremony.
- **`domain-driven-design`** owns **WHAT** sits in the domain layer —
  aggregates, entities, value objects, invariants, the ubiquitous language.
  Classic-layered owns **HOW** the tiers stack and that calls flow strictly
  through adjacent layers. DDD's tactical patterns are *usable* here, but DDD's
  full payoff (an infrastructure-free domain) wants an inverted boundary, which
  this style does not provide — DDD composes more naturally with the
  dependency-inversion siblings.
- **`design-patterns-gof`** owns object-level collaboration patterns inside a
  layer; **`enterprise-integration-patterns`** owns between-system messaging.
  Classic-layered is the macro stacking rule across one deployable.

## Components

- **Presentation layer** — UI, HTTP controllers/handlers, view models, request
  parsing. The application's entry point; depends on the layer below.
- **Application / service layer** — use-case orchestration and transaction
  boundaries that coordinate domain objects to satisfy a request. Depends on
  the domain and data-access layers below it.
- **Domain / business-logic layer** — the business rules and domain types. In
  this style it depends **downward** on the data-access layer (directly or via
  concrete repository classes), rather than declaring an interface the
  data-access layer implements.
- **Data-access layer (DAL)** — persistence: repositories/DAOs, ORM mapping,
  query code, the database client. The bottom of the stack; depended upon by
  the layers above.
- **(Optional) shared/cross-cutting layer** — logging, config, common types
  referenced by multiple layers. Kept thin to avoid becoming a dependency
  sink.

## Constraints

### Dependencies point downward through adjacent layers

- Each layer depends **only on the layer directly beneath it** (or, where a
  relaxed/open-layer policy is chosen and recorded, on any lower layer). The
  presentation layer talks to the application/domain layer; that layer talks to
  the data-access layer.
- A **lower layer MUST NOT depend on a higher layer** — the data-access layer
  knows nothing about the presentation layer. The dependency graph is acyclic
  and points down.
- The presentation layer **MUST NOT reach past** the application/domain layer
  to call the data-access layer directly, nor touch persistence by other means.
  Each layer has one well-known responsibility and is reached through its
  neighbor.

### No enforced dependency inversion (the defining trade-off)

- This style **accepts** that the domain/business layer depends on data-access
  implementation details. There is **no requirement** that persistence
  interfaces be declared in the domain layer and implemented below — the
  business layer may call concrete repository/ORM types directly. This is the
  deliberate cost of the low-ceremony baseline; if that coupling is
  unacceptable, select a dependency-inversion sibling instead.
- A composition root / DI container is **optional, not required**. Concrete
  lower-layer types may be constructed directly by the layer above.

### Keep behavior in the right layer (avoid the anemic-tier failure)

- Business rules belong in the domain/application layer, **not** smeared into
  presentation controllers or into the data-access layer (logic-in-SQL,
  fat-stored-procedures, fat-controllers). The layers must carry their named
  responsibility, or the structure degrades into spaghetti with extra folders.

## Drift Signals (anti-patterns to reject in review)

- The presentation layer imports / calls the data-access layer directly,
  bypassing the application/domain layer → reach-through; route through the
  adjacent layer
- A lower layer depends on a higher layer (DAL imports a controller / view
  model) → upward dependency; the graph must point down only
- Business rules implemented in controllers or in SQL / stored procedures →
  behavior in the wrong tier; move it to the domain/application layer
- Layers are present in name but one tier holds all the logic (god-service,
  anemic domain with a fat service) → the stacking buys nothing; either
  restore layer responsibilities or reconsider the style
- A persistence interface declared in the domain layer **and** wired through a
  composition root, with a swap-the-datastore requirement → you are paying for
  inversion; that is a dependency-inversion sibling (onion / hexagonal /
  clean), not classic-layered — re-select the slot

## When to use

Select as the `architecture-style` filler when the product is **thin / CRUD /
forms-over-data**, a **throwaway or short-lived tool**, or a team wants the
**lowest-ceremony baseline** and the direct coupling of business logic to
data-access is an **acceptable trade-off** because the datastore is not
expected to be swapped and the domain is not complex enough to need
isolated testing. This is the honest default when dependency inversion cannot
be justified by changeability or domain complexity (per KISS/YAGNI). One
`architecture-style` filler wins per project; `onion`, `hexagonal`, `clean`,
and classic-layered are the competing fillers — choose a dependency-inversion
sibling instead when you have **non-trivial business logic, swappable
infrastructure, or an isolated-testable-domain requirement**. `areas: all`
because the layering constrains every buildable work item.

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- ADR: classic-layered chosen over inversion siblings; business→data-access coupling accepted
- TD: presentation→application→domain→data-access tiers, dependencies pointing down

## ADR References

Record an ADR when selecting classic-layered over a dependency-inversion
slot-sibling (`onion` / `hexagonal` / `clean`) — the ADR should state that the
business-to-data-access coupling is an accepted trade-off for lower ceremony —
or when an operator overrides the `architecture-style` choice per project.

## Practices by activity

Agents working in any of these activities inherit the practices below via the bead's context digest.

These practices make the **downward layering rule** (each layer depends only on
the layer beneath it; lower layers never depend on higher ones) checkable in
review. They govern **HOW** the codebase stacks its tiers — not **WHAT** sits
in the domain layer (`domain-driven-design` owns aggregates/invariants/
ubiquitous language), not object-level patterns (`design-patterns-gof`), not
between-system messaging (`enterprise-integration-patterns`).

The defining property of this style versus its dependency-inversion siblings
(`onion` / `hexagonal` / `clean`): **the business/domain layer is allowed to
depend directly on the data-access layer.** These practices do not require an
inverted persistence boundary — if review finds the team wants one, the
`architecture-style` selection is wrong and a sibling should fill the slot.

## Discover

- Confirm the product does **not** require a swappable datastore, an
  isolated-testable domain, or multiple symmetric driving adapters — if it
  does, the `architecture-style` is mis-selected; recommend a
  dependency-inversion sibling (`onion` / `hexagonal` / `clean`).
- Per KISS/YAGNI, do NOT introduce repository interfaces, ports, or a DI
  container speculatively under this concern — that ceremony belongs to a
  sibling style that was deliberately selected.

## Frame

- If a relaxed/open-layer policy is adopted (a layer may call any lower layer),
  it MUST be recorded as a deliberate decision; even then, a layer MUST NOT
  call a layer **above** it.
- If the product actually needs a **swappable datastore**, an
  **infrastructure-free testable domain**, or **multiple symmetric driving
  adapters**, the reviewer SHOULD flag that the `architecture-style` selection
  is mismatched and recommend a dependency-inversion sibling, rather than
  bolting partial inversion onto a classic-layered codebase.

## Design

- The code MUST be organized into recognizable layers —
  **presentation → application/service → domain → data-access** — with a
  discoverable mapping from layer to package/module/directory.
- Each layer MUST depend **only on the layer directly beneath it** (closed-layer
  default).
- A lower layer MUST NOT import, reference, or depend on a higher layer (verify
  the import graph: the data-access layer has **zero** edges to the
  presentation or application layers).
- The presentation layer MUST NOT call the data-access layer directly or touch
  persistence by other means; it MUST go through the application/domain layer.
- This style does NOT require persistence interfaces to be declared in the
  domain layer, and does NOT require a composition root. Reviewers MUST NOT
  flag the absence of an inverted persistence boundary as a defect under this
  concern — that absence is the point.

## Build

- Business rules MUST live in the domain/application layer, not in presentation
  controllers and not in the data-access layer (no business logic in SQL,
  stored procedures, or ORM hooks beyond persistence mechanics).
- The data-access layer SHOULD expose persistence operations (repositories /
  DAOs) and contain no business decisions; the presentation layer SHOULD
  contain no business decisions either.

## Test

- Import-graph check: dependencies point **downward only** — no layer imports a
  layer above it; the data-access layer has zero edges to presentation or
  application layers (verify across all layer boundaries).
- Closed-layer check: the presentation layer has **no** dependency edge to the
  data-access layer (it reaches persistence only via the application/domain
  layer); any open-layer exception is recorded.
- Behavior-placement check: no business rules in presentation controllers or in
  SQL/stored procedures; the domain/application layer carries the logic.
- Anti-degradation check: each named layer carries real responsibility — reject
  a "layered" structure where one tier holds all logic (god-service / anemic
  domain) while the others are pass-throughs.
- Selection-fit check: the product does **not** require a swappable datastore,
  an isolated-testable domain, or multiple symmetric driving adapters — if it
  does, the `architecture-style` is mis-selected; recommend a
  dependency-inversion sibling (`onion` / `hexagonal` / `clean`).

## Cross-cutting

### Boundary with sibling concerns

- The **contents** of the domain layer (aggregates, invariants, ubiquitous
  language) are governed by `domain-driven-design`, not here. Verify the model
  sits in the domain layer; do not restate DDD modeling rules.
- Object-level collaboration patterns inside a layer are `design-patterns-gof`;
  between-system integration is `enterprise-integration-patterns`.
  Classic-layered only governs the macro tier-stacking across the codebase.
