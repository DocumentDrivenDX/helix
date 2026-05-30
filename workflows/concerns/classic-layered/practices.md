# Practices: Classic Layered Architecture

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
