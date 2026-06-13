---
title: "Enterprise Application Patterns (PoEAA)"
slug: enterprise-application-patterns
generated: true
aliases:
  - /reference/glossary/concerns/enterprise-application-patterns
---

**Category:** Architecture · **Areas:** api, data

## Description

## Category
architecture

## Areas
api, data

## Boundary

This concern owns the **enterprise-application organization patterns** from
Fowler's *Patterns of Enterprise Application Architecture* (PoEAA) — the named,
load-bearing choices for **how domain logic is organized** (Transaction Script,
Domain Model, Table Module, Service Layer) and **how objects move to and from a
data source** (Active Record vs Data Mapper, Unit of Work, Identity Map, Lazy
Load), plus the distribution and session-state patterns that follow from those
choices. It supplies the **mechanics** of the persistence and orchestration
machinery and the canonical trigger for each. It does **not** own the meaning of
the domain, the macro layering of the codebase, or general-purpose OO mechanics.
Three neighbors must stay distinct:

- **`domain-driven-design`** owns the domain **semantics** — aggregates,
  invariants, ubiquitous language, what an entity/value object *means* in the
  business. PoEAA owns the **organization mechanics** that carry that model in
  and out of storage and orchestrate it. The two intersect at two roles and the
  intersection is precisely the boundary:
  - **Repository** — DDD says a repository returns *whole aggregates in domain
    terms*; PoEAA gives the **mediation mechanics** (it sits over a Data Mapper /
    Query Object / Identity Map). DDD = meaning; PoEAA = the persistence machinery
    behind it.
  - **Service Layer** — DDD names *domain services* (logic with no home on one
    entity); PoEAA's Service Layer is the **application boundary / orchestration**
    layer (operations, transaction control, coordination) that drives the domain.
    DDD = domain meaning; PoEAA = the orchestration seam.
  - The **Active-Record-vs-Data-Mapper** decision is **PoEAA's**, and **Data
    Mapper is the mechanism that makes DDD's "persistence must not leak into the
    domain" achievable** — it is the layer that keeps the in-memory domain model
    ignorant that a database exists. Active Record deliberately couples row and
    domain logic and is therefore in tension with that DDD rule (see Constraints).
- **`design-patterns-gof`** owns **general OO mechanics** usable in any program
  (Strategy, Adapter, Observer, …). PoEAA patterns are **enterprise-app-specific**
  layer and data-source patterns. A PoEAA Data Mapper is not a GoF Adapter; a
  PoEAA Unit of Work is not a GoF Memento. When the construct is a generic
  intra-process collaboration, name the GoF mechanic; when it is the enterprise
  app's domain-logic/data-source organization, it is PoEAA's lane.
- **`onion-architecture`** (and its slot-siblings `hexagonal` / `clean` /
  `classic-layered`) owns the **layering structure** — which ring code lives in
  and which way dependencies point. PoEAA owns the **patterns that fill those
  layers**: onion says "the domain declares a repository interface, infrastructure
  implements it"; PoEAA says "that implementation is a Data Mapper over a Unit of
  Work and an Identity Map." Structure vs the patterns inside the structure.
  Reference onion as complementary; do not restate the dependency rule here.

## Components

The PoEAA catalog is large; this concern carries the **enterprise-app-defining
families** — domain-logic organization, data-source architecture, the
object-relational behavioral patterns, and the distribution/session patterns
those choices force. The structural O/R mapping patterns (Foreign Key Mapping,
inheritance mappers, Embedded Value, …) are mechanics an ORM/Data Mapper
implements and are noted only where load-bearing.

- **Domain-logic patterns** — *how* business logic is organized. The choice is
  driven by the **complexity of the business logic**, not by taste:
  Transaction Script (procedural, per-request), Domain Model (behavior-rich
  object web), Table Module (one instance per table, record-set backed), and
  Service Layer (the operation/transaction boundary over any of them).
- **Data-source architectural patterns** — *how* objects reach the database, and
  the **load-bearing Active Record vs Data Mapper** decision (plus the simpler
  Table/Row Data Gateways): does persistence logic live **on** the domain object
  (Active Record) or in a **separate mapper layer** (Data Mapper)?
- **Object-relational behavioral patterns** — the machinery that makes a Data
  Mapper correct and efficient: Unit of Work (track changes, one commit), Identity
  Map (load each object once), Lazy Load (defer loading until needed).
- **Distribution patterns** — what crosses a process boundary efficiently: Remote
  Facade (coarse-grained facade over fine-grained objects), Data Transfer Object
  (carry data across the wire in one round trip).
- **Session-state patterns** — where between-request state lives: Client, Server,
  or Database Session State.

### Intent table (pattern → family → intent → use when)

| Pattern | Family | Intent | Use when |
|---|---|---|---|
| Transaction Script | Domain logic | Organize business logic as one procedure per request | Logic is simple, mostly independent transactions, little shared behavior — the cheapest start |
| Domain Model | Domain logic | An object web carrying both behavior and data | Business logic is **complex** — many rules, cases, and interactions worth modeling as collaborating objects |
| Table Module | Domain logic | One instance handling the logic for **all rows** of a table, over a record set | Moderate logic with a record-set–centric stack/UI that binds to tabular data |
| Service Layer | Domain logic | An application boundary of operations, owning transaction control and coordination | Multiple clients (UI, API, batch, integration) need the same operations and a single transaction/orchestration seam |
| Table Data Gateway | Data source | One object gating all access to a database **table** | Simple table access, often feeding a Table Module / record set |
| Row Data Gateway | Data source | An object gating a **single record**, with no domain logic | A row needs a persistence-agnostic in-memory stand-in without domain behavior |
| **Active Record** | Data source | A domain object that **wraps a row and adds its own persistence + domain logic** | Domain logic is **simple and maps ~1:1 to tables**; coupling row+logic is an acceptable trade for speed (see Constraints) |
| **Data Mapper** | Data source | A **separate mapper layer** moving data between objects and the DB, each ignorant of the other | The domain model is **rich/independent of the schema** and must stay free of persistence — the enabler of a clean Domain Model and DDD |
| Unit of Work | O/R behavioral | Track all objects touched in a business transaction; coordinate one commit + concurrency | Multiple changes must commit atomically and DB round-trips must be batched (needed by Data Mapper) |
| Identity Map | O/R behavioral | Keep loaded objects in a map so each loads **once** | An object may be fetched repeatedly in one session — correctness (one in-memory identity) and fewer reads |
| Lazy Load | O/R behavioral | An object that defers loading part of its data until first use | Eager-loading a whole graph is wasteful and parts are often unused |
| Query Object | O/R metadata | An object representing a database query in domain terms | Queries are built dynamically and should not be hand-written SQL scattered through the app |
| Remote Facade | Distribution | A coarse-grained facade over fine-grained objects to cut network calls | Fine-grained objects are accessed across a process/network boundary and chatty calls are too costly |
| Data Transfer Object (DTO) | Distribution | Carry data across processes in one object to reduce round trips | Crossing a remote boundary; bundle the fields a client needs into one transfer shape |
| Client Session State | Session | Hold session state on the client | State is small and the server should stay stateless |
| Server Session State | Session | Hold session state on the server (in memory/serialized) | State is large/complex and server affinity is acceptable |
| Database Session State | Session | Hold session state as committed rows in the DB | State must survive restarts/failover and be shared across nodes |

## Constraints

### Match the domain-logic pattern to the complexity (KISS/YAGNI)

- The catalog is a **named menu, not a mandate**. Each pattern is selected against
  a **recorded trigger** (the intent-table row), never reached for because it is
  familiar or sophisticated.
- The domain-logic choice is driven by **how complex the business logic is**.
  **Transaction Script** is the right, cheapest answer for simple, mostly
  independent operations; escalating to a **Domain Model** is justified only when
  the rules/cases/interactions are genuinely complex. Do not stand up a Domain
  Model + Data Mapper + Unit of Work for a thin CRUD surface — that is
  over-engineering. Equally, do not let a Transaction Script accrete sprawling
  conditional logic that has clearly outgrown it.

### Active Record vs Data Mapper is a recorded, load-bearing decision

- The data-source choice is **architectural and must be recorded in an ADR**, not
  defaulted silently by the ORM.
- **Active Record** couples a row and its domain logic in one object. It is a good
  fit when domain logic is **simple and maps closely to the table structure**; it
  becomes a liability as domain logic grows, because business rules get pulled
  toward the table shape and the object cannot evolve independently of the schema.
- **Data Mapper** keeps the domain model **ignorant that a database exists**, with
  a separate mapper layer translating both ways. It is the choice for a **rich
  Domain Model** and is the **mechanism that makes DDD's "persistence must not leak
  into the domain" hold** — it is what lets a repository return aggregates in
  domain terms. It costs more machinery (typically Unit of Work + Identity Map).
- A **rich Domain Model placed on Active Record** is a recurring mismatch: either
  the model bends to the table or persistence leaks into the domain. If DDD is
  also selected, **Data Mapper is the expected data-source pattern**; choosing
  Active Record under DDD requires a recorded justification.

### Unit of Work and Identity Map come with Data Mapper, not à la carte

- When a Data Mapper backs a non-trivial Domain Model, **Unit of Work** (one
  coordinated commit, concurrency resolution) and **Identity Map** (one in-memory
  identity per row per session) are the patterns that make it correct and
  efficient — usually provided by the ORM. Hand-rolling per-object immediate
  writes around a Domain Model reintroduces the problems these patterns solve.

### Distribution patterns apply only at a real remote boundary

- **Remote Facade** and **DTO** earn their place **only when a process/network
  boundary is actually crossed**. Introducing DTOs and coarse facades inside a
  single process — where fine-grained calls are free — is ceremony, not a feature.
  (First Law of Distributed Objects: don't distribute your objects.)

### Mechanics, not domain meaning or layering

- PoEAA supplies **organization mechanics**. When the construct carries business
  meaning (an aggregate, an invariant, the ubiquitous-language name), that is
  `domain-driven-design`. When it concerns which layer code lives in and the
  dependency direction, that is `onion-architecture`. When it is a generic OO
  collaboration, that is `design-patterns-gof`. Do not stretch a PoEAA pattern to
  cover any of the three.

## Drift Signals (anti-patterns to reject in review)

- A full **Domain Model + Data Mapper + Unit of Work** stack wrapped around a thin
  CRUD surface with no real business logic → over-engineering; a Transaction
  Script (or Active Record) fits the complexity
- A **Transaction Script** that has accreted sprawling validation/calculation
  branches and duplicated rules → it has outgrown the pattern; refactor toward a
  Domain Model
- The **Active Record vs Data Mapper** choice made implicitly by the ORM with **no
  ADR** → record it; an architectural data-source decision is not a default
- A **rich Domain Model riding on Active Record** — business rules bending to the
  table shape, or SQL/row concerns leaking into domain objects → mismatch; use a
  Data Mapper (especially under DDD)
- ORM rows / row gateways / Active Record instances surfacing as the domain's
  public types under DDD → persistence leaking into the domain (DDD's rule), which
  the Data Mapper exists to prevent
- A Domain Model on a Data Mapper with **per-object immediate writes** and no Unit
  of Work / Identity Map → reintroduces N+1 writes, lost-update races, and
  duplicate in-memory identities the behavioral patterns solve
- **DTOs / Remote Facades introduced inside a single process** with no remote
  boundary → distribution ceremony; pass domain objects directly
- A PoEAA pattern standing in for **domain meaning** (`domain-driven-design`),
  **macro layering** (`onion-architecture`), or a **generic OO mechanic**
  (`design-patterns-gof`) → route it to the owning concern
- A pattern named but not realized (a "Service Layer" that is one passthrough
  method; a "Repository" that returns raw rows) → align the name with the
  mechanic, or drop it

## When to use

Select this concern for **enterprise applications with non-trivial persistence
and a domain-logic-to-data-source mapping to make** — products where the team
must decide how business logic is organized (Transaction Script vs Domain Model)
and how objects reach storage (**Active Record vs Data Mapper**), and live with
the Unit-of-Work / Identity-Map / Lazy-Load machinery that follows. It is a
**non-exclusive reference concern** (no slot, fills no exclusive position);
`areas: api, data` scopes its practices to the domain-logic and data-source
layers. Compose it with `domain-driven-design` (domain semantics — Data Mapper is
how its persistence-isolation rule is met), with `onion-architecture` (the
layering these patterns fill), with `design-patterns-gof` (generic OO mechanics),
and with the tech-stack/ORM concern (which provides Unit of Work, Identity Map,
and the mapper).

Do **not** select it for **thin CRUD** admin tools, glue scripts, or read-only /
marketing content, where a Transaction Script or plain Active Record is the right
answer and the Domain-Model/Data-Mapper machinery is cost without payoff
(KISS/YAGNI).

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- ADR: domain-logic organization (Transaction Script/Domain Model) + data-source pattern (Active Record vs Data Mapper)
- TD: data-source layer (mapper/Unit-of-Work/Identity-Map), Service Layer boundary, distribution/session-state placement
- DATA_DESIGN: how the chosen pattern maps domain objects to the schema

## ADR References

Selecting this concern forces these decisions to be recorded:

- **Domain-logic organization** — Transaction Script vs Domain Model (vs Table
  Module), justified by the assessed complexity of the business logic.
- **Data-source pattern** — **Active Record vs Data Mapper**, the load-bearing
  decision; under `domain-driven-design`, Data Mapper is expected and choosing
  Active Record requires a recorded justification.
- Where a non-trivial Domain Model is on a Data Mapper, note the **Unit of Work /
  Identity Map** provision (typically the ORM) and any **distribution** boundary
  that introduces Remote Facade / DTO and the **session-state** placement.

These propagate into the **technical-design** (the data-source layer + the
domain-logic organization) and the **data-design** (how the chosen pattern maps
objects to the schema).

## Practices by activity

Agents working in any of these activities inherit the practices below through runtime work context, such as a DDx bead context digest.

These practices govern **how domain logic is organized** and **how objects move
to and from a data source** in an enterprise application — the load-bearing
PoEAA choices and the machinery they pull in. They sit beside
`domain-driven-design` (domain semantics — what the model *means*),
`onion-architecture` (the layering these patterns fill), and `design-patterns-gof`
(generic OO mechanics); they do not restate those concerns. Their job is to keep
the **domain-logic and data-source patterns matched to the actual complexity,
recorded, and not over-built** (KISS/YAGNI).

## Discover

- The domain-logic pattern MUST be chosen against the **assessed complexity of
  the business logic**: **Transaction Script** for simple, mostly independent
  operations; **Domain Model** when the rules, cases, and interactions are
  genuinely complex; **Table Module** only when a record-set–centric stack/UI
  justifies it.
- You SHOULD start with the **simplest** organization the logic warrants and
  refactor *toward* a Domain Model when complexity actually arrives — not stand up
  a Domain Model speculatively for a thin surface.
- A **Service Layer** SHOULD be introduced only when **multiple clients** (UI,
  API, batch, integration) need the same operations or a single
  transaction/orchestration seam is required — not as a reflexive passthrough over
  a single caller.
- The **session-state** placement (client / server / database) SHOULD be a
  recorded choice driven by state size, statelessness/affinity needs, and
  survive-restart requirements — not an accident of the framework.

## Frame

- The chosen domain-logic organization MUST be recorded in an ADR.
- The **Active Record vs Data Mapper** decision MUST be made explicitly and
  **recorded in an ADR** — it MUST NOT be left as an implicit ORM default.
- Choose **Active Record** when domain logic is **simple and maps closely to the
  table structure** and coupling row + logic is an acceptable trade. Choose **Data
  Mapper** when the domain model is **rich and must stay independent of the
  schema/persistence**.
- When `domain-driven-design` is also selected, **Data Mapper is the expected
  data-source pattern** — it is the mechanism that keeps the domain model ignorant
  of the database and lets repositories return aggregates in domain terms.
  Choosing Active Record under DDD MUST be justified in the ADR.

## Design

- A rich Domain Model MUST NOT be placed on Active Record such that business rules
  bend to the table shape or SQL/row concerns leak into domain objects.
- The **technical-design** reflects the chosen data-source layer + domain-logic
  organization, and the **data-design** reflects how that pattern maps objects to
  the schema.
- **Remote Facade** and **Data Transfer Object** MUST be introduced only at a real
  **process/network boundary**; they MUST NOT be added inside a single process
  where fine-grained calls are free.

## Build

- When a Data Mapper backs a non-trivial Domain Model, **Unit of Work** (one
  coordinated commit + concurrency resolution) and **Identity Map** (one in-memory
  identity per row per session) MUST be provided — normally by the ORM, not
  hand-rolled as per-object immediate writes.
- **Lazy Load** SHOULD be used where eager-loading a whole graph is wasteful, with
  attention to N+1 read patterns.

## Test

- The **domain-logic organization** (Transaction Script vs Domain Model vs Table
  Module) is recorded in an ADR and matches the assessed complexity — no Domain
  Model + Data Mapper + Unit of Work wrapped around a thin CRUD surface, and no
  Transaction Script left to accrete sprawling rules it has outgrown.
- The **Active Record vs Data Mapper** decision is recorded in an ADR (not an
  implicit ORM default); under `domain-driven-design`, Data Mapper is used or
  Active Record is explicitly justified.
- No **rich Domain Model on Active Record** with rules bending to the table, and
  no ORM rows / Active Record instances surfacing as the domain's public types
  under DDD (persistence not leaking into the domain).
- A Domain Model on a Data Mapper is backed by **Unit of Work + Identity Map**
  (typically the ORM) — not per-object immediate writes that reintroduce N+1
  writes, lost updates, or duplicate in-memory identities.
- **Remote Facade / DTO** appear only where a real remote boundary is crossed —
  no distribution ceremony inside a single process.
- The **technical-design** reflects the chosen data-source layer + domain-logic
  organization, and the **data-design** reflects how that pattern maps objects to
  the schema.
- Every pattern present is named to match the mechanic actually implemented (no
  one-method "Service Layer", no row-returning "Repository") and routes domain
  meaning, macro layering, and generic OO mechanics to their owning concerns.

## Cross-cutting

### Staying in your lane

- When a construct carries **business meaning** (an aggregate, an invariant, a
  ubiquitous-language name), the domain semantics belong to
  `domain-driven-design`; PoEAA describes only the persistence/orchestration
  **mechanics**. For **Repository** and **Service Layer**, name the domain meaning
  per DDD and let this concern own the persistence/orchestration machinery.
- The patterns here fill layers; **which layer code lives in and the dependency
  direction** belong to `onion-architecture` and MUST NOT be restated. A **generic
  intra-process OO collaboration** is `design-patterns-gof`, not a PoEAA pattern.
