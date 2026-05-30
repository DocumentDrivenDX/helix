# Practices: Enterprise Application Patterns (PoEAA)

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
