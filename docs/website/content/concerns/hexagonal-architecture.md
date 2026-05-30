---
title: "Hexagonal Architecture (Ports & Adapters)"
slug: hexagonal-architecture
generated: true
aliases:
  - /reference/glossary/concerns/hexagonal-architecture
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

This concern owns **how the codebase isolates its application core behind
explicit ports, with interchangeable adapters plugged in on every side** —
Alistair Cockburn's Ports & Adapters. Its intent (Cockburn): *"Allow an
application to equally be driven by users, programs, automated test or batch
scripts, and to be developed and tested in isolation from its eventual run-time
devices and databases."* It fills the exclusive `architecture-style` slot (one
structuring discipline wins per project).

Hexagonal is a member of the **dependency-inversion architecture family** (its
slot-siblings `onion-architecture` and `clean-architecture` impose the same
inward-only dependency rule). They are honestly close relatives; the
differentiator is **practical, not dogmatic**:

- **vs `onion-architecture` / `clean-architecture`** — Onion and Clean draw
  **concentric rings** and emphasize a layered domain at the center (Clean adds
  named use-case interactors). Hexagonal draws a **flat core with a boundary of
  ports** and emphasizes the **symmetry of the two sides**: the same core is
  reached through **driving (primary) ports** on one side and reaches out
  through **driven (secondary) ports** on the other, and **any number of
  adapters** can plug into one port. Pick hexagonal when the salient fact about
  the system is that **many interchangeable adapters drive or are driven by one
  core** (UI + REST + CLI + tests all drive it; SQL + message bus + third-party
  API are all driven by it) — the port/adapter symmetry is the organizing idea,
  not the internal ring layout of the core.
- **vs `classic-layered`** — classic-layered lets the business layer depend
  directly on data-access (no inversion). Hexagonal inverts every external
  boundary behind a port the core owns.
- **vs `domain-driven-design`** — DDD owns **WHAT** sits in the core
  (aggregates, invariants, ubiquitous language). Hexagonal owns **HOW** the
  core is fenced off behind ports and adapters. They **compose**: DDD's model
  is what lives inside the hexagon; hexagonal keeps it free of devices and
  databases. Reference DDD as the complement; do not restate modeling rules.
- **vs `design-patterns-gof` / `enterprise-integration-patterns`** — those own
  object-level patterns inside a layer and between-system messaging
  respectively. Hexagonal is the macro boundary discipline for one deployable;
  integration adapters are simply driven adapters under it.

## Components

- **Application core (inside the hexagon)** — the technology-agnostic business
  logic and application services. Knows nothing of HTTP, SQL, the UI, or the
  test harness. (Its *contents* are governed by `domain-driven-design` when
  selected.)
- **Ports** — boundary interfaces **defined by and owned by the core**, in the
  core's own terms. A **driving port** (primary) is the API the core offers to
  whoever wants to use it; a **driven port** (secondary) is the interface the
  core requires from the outside (persistence, notification, external service).
  One port can be served by many adapters.
- **Driving / primary adapters (left side)** — adapters that **initiate**
  interaction with the core by calling a driving port: HTTP controllers, a CLI,
  a message-queue consumer, a GUI, **and the test harness**. A test driving the
  core is just another primary adapter substituted for the real UI.
- **Driven / secondary adapters (right side)** — adapters the core **drives**
  through a driven port: the SQL/ORM repository, the message-bus publisher, the
  email/SMS client, the third-party API client. A fake/in-memory store is just
  a driven adapter substituted for the real database.
- **Configuration / composition root** — the outermost wiring that instantiates
  concrete adapters and plugs them into the core's ports at startup
  (configurable dependency). The only place that names concrete adapter types.

## Constraints

### The core owns the ports; dependencies point into the core

- Every external interaction crosses a **port the core defines**. Adapters
  depend on the core's ports; the **core depends on no adapter**. Source-code
  dependencies point **inward, toward the core**, on both sides of the hexagon.
- The core MUST NOT import or reference any adapter, framework, transport, or
  driver. It is expressed entirely in its own terms behind its ports.
- A driven port (the interface for persistence/external systems) is **declared
  in the core** and **implemented by a secondary adapter** outside it — never
  the reverse, and the port interface MUST NOT live in the adapter's package.

### Symmetry of the two sides

- **Driving adapters call the core; the core calls driven adapters through
  driven ports.** Primary adapters depend on the core's driving ports; the core
  depends on its own driven ports (which secondary adapters implement). Neither
  side reaches across to the other — adapters never depend on adapters.
- A port is **adapter-plural by design**: the architecture must permit more than
  one adapter per port (real UI + test harness on a driving port; real DB +
  in-memory fake on a driven port) without changing the core.

### Configurable dependency at the boundary

- Concrete adapters are **selected and wired at configuration time** by the
  composition root, not constructed inside the core. Swapping an adapter (a
  different datastore, a CLI in place of HTTP) MUST require changes only in that
  adapter and the wiring, never in the core.
- Data crossing a port is expressed in the **core's own terms** (core
  objects / simple DTOs the core owns); transport shapes (HTTP requests, ORM
  rows) are translated **in the adapter**, never leaked across the port.

### Testability is the headline payoff

- Because every boundary is a port, the core is **driven and observed entirely
  through ports** — drive it with a test (primary) adapter and back it with
  fake (secondary) adapters, with no real devices or databases present. (How
  those tests are written is the `testing` concern; hexagonal only guarantees
  the port seams exist on both sides.)

## Drift Signals (anti-patterns to reject in review)

- The application core imports an adapter, framework, transport, or driver
  package → boundary violation; depend on a port the core owns and wire the
  adapter at configuration time
- A driven-port interface (repository/gateway) declared in the adapter package
  rather than the core → declare it in the core, implement it in the secondary
  adapter
- An adapter that depends on another adapter (HTTP controller reaching into the
  SQL repository directly) → adapters talk only to the core through ports, never
  to each other
- A port that structurally cannot host a second adapter (the "real" impl is
  hard-wired, no test harness can substitute) → the port/adapter seam is fake;
  restore the configurable dependency
- Transport shapes (HTTP request objects, ORM rows) passed through a port into
  the core → translate in the adapter; the port speaks the core's terms
- Concrete adapter types named anywhere but the composition root → move wiring
  to the composition root
- Full ports-and-adapters ceremony around a thin CRUD app with one UI and one
  datastore and no second adapter in sight → over-engineering; reconsider the
  `architecture-style` selection (likely `classic-layered`)

## When to use

Select as the `architecture-style` filler when the salient structural fact is
**multiple symmetric driving and/or driven adapters around one core**: the same
application is (or will be) driven by **several entry points** — UI **and** a
public API **and** a CLI/batch job **and** the test harness — and/or it talks to
**several interchangeable external systems** (datastore, message bus,
third-party services) that may be doubled or swapped. The port/adapter symmetry
and adapter-plurality are the reason to choose hexagonal over its ring-drawing
siblings. Prefer **`onion`/`clean`** instead when the organizing concern is a
**layered/concentric domain** (and, for `clean`, explicit use-case
interactors) rather than adapter symmetry; prefer **`classic-layered`** for
thin/CRUD where inversion is not worth it. One `architecture-style` filler wins
per project. Compose with `domain-driven-design` (core contents) and the
tech-stack concern (package system enforcing the import graph). `areas: all`
because the port boundary constrains every buildable work item.

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- ADR: Hexagonal chosen for architecture-style slot; the driving/driven adapters justifying port symmetry
- TD: core, driving/driven ports, primary/secondary adapters, composition root

## ADR References

Record an ADR when selecting hexagonal over a slot-sibling
(`onion` / `clean` / `classic-layered`) — the ADR should name the multiple
driving/driven adapters that justify the port symmetry — or when an operator
overrides the `architecture-style` choice per project.

## Practices by activity

Agents working in any of these activities inherit the practices below via the bead's context digest.

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
