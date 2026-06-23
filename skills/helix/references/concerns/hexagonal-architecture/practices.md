# Practices: Hexagonal Architecture (Ports & Adapters)

These practices make Cockburn's Ports & Adapters discipline checkable in
review: **every external interaction crosses a port the application core owns,
adapters depend on the core (never the reverse), and any port can host more
than one adapter.** They govern **HOW** the codebase fences its core behind
ports — not **WHAT** sits in the core (`domain-driven-design` owns
aggregates/invariants/ubiquitous language), not object-level patterns
(`design-patterns-gof`), not between-system messaging
(`enterprise-integration-patterns`). Where DDD is also selected, its model is
exactly what lives inside the hexagon.

The differentiator versus the sibling dependency-inversion styles (`onion` /
`clean`): hexagonal review focuses on the **symmetry of driving and driven
ports** and the **plurality of adapters per port**, not on an internal
concentric ring layout.

## Discover

- Apply full ports-and-adapters only when the **selection signals** in
  `concern.md` hold — **multiple symmetric driving and/or driven adapters**
  around one core. For a thin CRUD app with one UI and one datastore and no
  prospect of a second adapter, the port ceremony is over-engineering — prefer
  `classic-layered`, recorded as the `architecture-style` choice.
- Per KISS/YAGNI, do NOT introduce a port for a boundary that has exactly one
  adapter and no realistic prospect of a second, **unless** the port is needed
  to keep the core driveable/testable in isolation.

## Design

- Code MUST be organized into an **application core** plus **adapters**, with a
  discoverable mapping from core / driving-adapter / driven-adapter to
  package/module/directory.
- Every external interaction MUST cross a **port defined in the core**, in the
  core's own terms. Adapters MUST depend on the core's ports; the **core MUST
  NOT import or reference any adapter, framework, transport, or driver** (verify
  the core package's import graph has zero edges to adapter/framework packages).
- A **driven (secondary) port** — the interface for persistence or an external
  system — MUST be declared **in the core** and implemented in a secondary
  adapter. The port interface MUST NOT live in the adapter's package.
- **Driving (primary) adapters** (HTTP, CLI, queue consumer, GUI, test harness)
  MUST call the core only through **driving ports**. **Driven (secondary)
  adapters** (SQL/ORM, message bus, email, third-party clients) MUST be invoked
  by the core only through **driven ports**.
- Adapters MUST NOT depend on other adapters — a driving adapter MUST NOT reach
  into a driven adapter directly; both talk only to the core through ports
  (verify the import graph: no adapter-to-adapter edges).
- Each port MUST be **adapter-plural by construction**: it MUST be possible to
  attach a second adapter (a test harness on a driving port; an in-memory fake
  on a driven port) without modifying the core. A port whose single
  implementation is hard-wired is a defect.
- Data crossing a port MUST be expressed in the **core's own terms** (core
  objects / DTOs the core owns). Transport shapes (HTTP request/response
  objects, ORM rows) MUST be translated **inside the adapter** and MUST NOT
  cross the port into the core.

## Build

- Concrete adapters MUST be instantiated and wired to the core's ports **at
  configuration time by the composition root** — the only place that names
  concrete adapter types. The core MUST NOT construct or `import` a concrete
  adapter.
- Swapping an adapter (different datastore, CLI instead of HTTP) MUST require
  changes only in that adapter and the wiring, never in the core.
- The core SHOULD be **exercisable through ports with no real devices or
  databases present** — driven by a test (primary) adapter and backed by fake
  (secondary) adapters. (Writing those tests is the `testing` concern; this
  practice only requires the port seams to exist on both sides.)

## Test

- Import-graph check: the application core has **zero** dependency edges to any
  adapter, framework, transport, or driver package.
- Driven-port ownership check: every persistence/external-system interface is
  declared in the core and implemented in a secondary adapter; no driven-port
  interface lives in an adapter package.
- Adapter-isolation check: **no adapter-to-adapter** dependency edge exists —
  every adapter depends only on the core's ports.
- Adapter-plurality check: at least one port demonstrably hosts a second adapter
  (e.g. the test harness as a driving adapter and/or an in-memory fake as a
  driven adapter); no port is hard-wired to a single implementation.
- Wiring check: concrete adapter types are named only in the composition root;
  the core references only ports.
- Boundary-translation check: no transport shapes (HTTP request objects, ORM
  rows) cross a port into the core — translation happens in the adapter.
- Selection-fit check: multiple symmetric driving/driven adapters justify the
  port ceremony; ports-and-adapters is not wrapped around a single-UI,
  single-datastore thin-CRUD app (else re-select `classic-layered`).

## Cross-cutting

### Boundary with sibling concerns

- The **contents** of the core are governed by `domain-driven-design`, not here.
  Verify the model sits inside the hexagon behind ports; do not restate DDD
  modeling rules.
- Object-level collaboration patterns inside a layer are `design-patterns-gof`;
  between-system integration is `enterprise-integration-patterns` (its messaging
  endpoints are driven adapters under this concern). Hexagonal governs only the
  macro port boundary across the codebase.
