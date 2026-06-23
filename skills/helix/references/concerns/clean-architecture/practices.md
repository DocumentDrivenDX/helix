# Practices: Clean Architecture

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
