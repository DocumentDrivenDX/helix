# Concern: Hexagonal Architecture (Ports & Adapters)

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
