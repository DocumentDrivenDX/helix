# Concern: Deployment Topology

## Category
architecture

## Areas
infra, api

## Boundary

This concern owns **one ADR-recorded decision: how many independently
deployable units the system ships as, and — if more than one — along which
boundaries they are split**. It is the choice along the spectrum from a
**modular monolith** (one deployable, module boundaries enforced in-process)
through **microservices** (many independently deployable services) to
**serverless / FaaS** (event-driven functions as the deployment unit). It is a
single non-exclusive decision-guide concern with a strong default
(**modular-monolith**), not a slot of competing members — the choice is one
decision, and the alternatives differ in *how many deployables and when to
split*, not in distinct rich vocabularies. Four neighbors must stay distinct:

- **`onion-architecture` / `architecture-style`** owns the **internal layering
  and dependency direction of ONE deployable** — which way source-code
  dependencies point inside a single buildable unit. Deployment-topology owns
  **how many deployables there are and where the seams between them fall**. They
  **compose**: a modular monolith is one Onion-layered deployable with enforced
  module boundaries; each microservice is itself internally layered by the
  `architecture-style` filler. This concern does **not** restate the Dependency
  Rule or ring layout.
- **`enterprise-integration-patterns`** owns **how services communicate once
  split** — channels, messages, routers, delivery guarantees across a real
  system boundary. Deployment-topology owns the **decision to create that
  boundary at all**; once you have two deployables that must talk
  asynchronously, EIP governs the transport. This concern does **not** restate
  channel / idempotency / dead-letter rules; it decides *whether the boundary
  exists*, EIP decides *how messages cross it*.
- **`k8s-kind`** (and any `deploy-target` filler) owns the **runtime that hosts
  the deployables** — the cluster, Helm charts, image builds, the local kind
  workflow. Deployment-topology owns the **count and shape of what gets
  deployed onto that runtime**, not the orchestration mechanics. One modular
  monolith and a fleet of microservices can both run on Kubernetes; the
  topology decision is upstream of the runtime choice.
- **`domain-driven-design`** owns the **bounded contexts** that, when a split is
  justified, become the *fault lines* a topology split follows. DDD names the
  contexts; deployment-topology decides whether each context is an in-process
  module or an out-of-process deployable. A split that cuts across a bounded
  context (a "distributed monolith") is the failure mode this concern exists to
  prevent.

## Components

- **The deployable unit** — the thing that ships and scales as one: the single
  process/artifact of a modular monolith, a microservice, or a serverless
  function. Choosing the topology is choosing the count and granularity of
  these units.
- **Module boundaries (in a modular monolith)** — internal seams enforced by the
  language/module system (package visibility, separate schemas per module, an
  explicit module API) so the single deployable stays decomposable. These are
  the same fault lines a future split would follow — drawn first, in-process,
  where they are cheap to move.
- **Service boundaries (in microservices)** — the out-of-process seams: each
  service is **independently deployable**, owns its **own data** (no shared
  database reached across the boundary), and communicates only over its
  published contract.
- **Function + trigger (in serverless / FaaS)** — a **stateless**, event-driven
  unit invoked by a trigger (HTTP, queue, schedule, event), with all state held
  in external services (database, object store, cache, queue), and a managed
  runtime that scales to zero.
- **The split fault line** — the boundary a split follows: a **bounded context**
  (`domain-driven-design`), never an arbitrary technical layer. The decision
  record names which fault line each deployable sits on.
- **The microservice premium prerequisites** — the operational capabilities a
  multi-deployable topology *demands before it pays off*: **automated
  deployment**, **observability/monitoring** (`o11y-otel`), **distributed-data
  discipline** (per-service data, eventual consistency, designing for partial
  failure), and the integration transport (`enterprise-integration-patterns`).

## Constraints

### Monolith first — the default is one modular deployable

- The default topology is a **modular monolith**: one deployable with module
  boundaries enforced in-process. **Do not start a new project with
  microservices**, even when you are confident it will eventually be large
  enough to warrant them (Fowler, *MonolithFirst*). The majority of systems
  should be one modular application (Fowler, *MicroservicePremium*; Newman:
  microservices "should not be the default choice").
- The decision to ship more than one deployable is **recorded in an ADR** with
  the specific forcing function that justifies paying the premium. Splitting by
  default, or "because microservices", is the anti-pattern.

### The split needs a forcing function, not a hunch

- A multi-deployable topology is justified only by a concrete forcing function:
  **independent scaling** of a part with a materially different load profile,
  **team autonomy** (separate teams needing independent deploy cadence), or a
  system **genuinely too complex to manage as one deployable** (Fowler — "don't
  even consider microservices unless you have a system that's too complex to
  manage as a monolith"). Absent such a function, the split is cost without
  payoff (KISS/YAGNI).

### Pay the microservice premium before splitting, not after

- Multiple deployables introduce a distributed system: **automated deployment,
  monitoring, dealing with failure, and eventual consistency** become
  mandatory, not optional (Fowler, *MicroservicePremium*; Newman lists automated
  deployment as a baseline prerequisite). A split made before these capabilities
  exist produces an unoperable distributed system.

### Split along bounded contexts; each service owns its data

- A split follows **bounded-context fault lines** (`domain-driven-design`), and
  each resulting service **owns its own data** — no second deployable reaches
  into the first's database. Sharing a database across a service boundary, or
  cutting the boundary across a context, produces a **distributed monolith**:
  the operational cost of microservices with the coupling of a monolith, the
  worst of both. Cross-service communication goes over a contract / channel
  (`enterprise-integration-patterns`), not a shared table.

### Boundaries are hard to get right early — keep them cheap to move

- Stable service boundaries are very hard to identify up front; "any refactoring
  of functionality between services is much harder than it is in a monolith"
  (Fowler). Draw the boundaries first as **in-process module seams** where they
  are cheap to move, let them stabilize under real usage, then **peel services
  off the edge** of the monolith one bounded context at a time (Newman: turn a
  single module into a service and see how it works) — rather than committing to
  out-of-process boundaries before they are proven.

### Serverless is event-driven and stateless — design for it

- A serverless/FaaS unit is **stateless**: no state survives between invocations;
  all state lives in external services. It is **event/trigger-driven** and
  scales to zero. Designing a function that assumes warm in-memory state, a
  long-lived connection, or sub-cold-start latency under sporadic traffic is a
  misuse.
- Serverless fits **variable/spiky or scale-to-zero workloads** (webhook
  handlers, event processors, scheduled jobs, glue) where its trade-offs are
  acceptable. It is a **poor fit** for latency-sensitive hot paths that cannot
  absorb **cold-start** spikes, long-running or CPU-intensive work (e.g. video
  encoding) that hits execution-time limits, and workloads needing persistent
  connections (e.g. WebSockets against short function timeouts). The real
  lock-in risk is the **surrounding managed services (data, queues), not the
  function code** — isolate provider SDKs behind a port (`onion-architecture`).

## Drift Signals (anti-patterns to reject in review)

- A new / greenfield project started directly on microservices with no recorded
  forcing function → default to a modular monolith; record the premium-justifying
  reason before splitting (Fowler *MonolithFirst*)
- Multiple deployables introduced with **no automated deployment, no
  observability, and no distributed-data discipline** in place → the microservice
  premium was not paid; the system is an unoperable distributed system
- Two services sharing one database, or one service reaching into another's
  tables → **distributed monolith**; each service owns its data, talk over a
  contract/channel (`enterprise-integration-patterns`)
- A service boundary drawn across a bounded context (a single context split
  across deployables, or one deployable spanning several unrelated contexts) →
  realign the split to bounded-context fault lines (`domain-driven-design`)
- A monolith with **no internal module boundaries** ("big ball of mud") defended
  as "we'll split later" → enforce module seams in-process now; an
  un-modularized monolith cannot be peeled apart later
- A serverless function holding in-memory state across invocations, or assuming a
  warm start / persistent connection on a sporadic-traffic path → make it
  stateless; reconsider topology if cold-start or timeout limits are violated
- "We chose microservices/serverless" with no ADR recording the forcing function
  and the premium-readiness → record the decision, or revert to the default
- The topology decision conflated with the runtime (`k8s-kind`) or the internal
  layering (`architecture-style`) → separate them; this concern decides only the
  count and seams of deployables

## When to use

Select for **any buildable product** that must decide how it deploys — which is
nearly all of them. The concern's job is mostly to **defend the default**: ship
one **modular monolith** with enforced internal module boundaries, and split
into microservices or adopt serverless only when a recorded forcing function
(independent scaling, team autonomy, or complexity that genuinely exceeds a
single deployable) justifies the premium. Do **not** apply its splitting
machinery to a library, a static/marketing site, a CLI, or a throwaway tool —
those are single artifacts with no topology decision to make; record the trivial
default and move on (KISS/YAGNI).

It is **composable** (no slot): the topology decision sits alongside the
`architecture-style` filler (which layers each deployable internally),
`domain-driven-design` (which supplies the bounded-context fault lines a split
follows), `enterprise-integration-patterns` (which governs communication once
split), `k8s-kind` / the `deploy-target` filler (the runtime the deployables run
on), and `o11y-otel` (the observability the premium demands). `areas: infra,
api` scopes its practices to the infrastructure and service-contract work items
where the deployable count and its seams are decided.

### Selection signal (verbatim — propose for concern-resolution)

> Select **deployment-topology** for every buildable product that ships a
> running system. Its default stance is **modular-monolith**: one deployable
> with enforced internal module boundaries. Keep the default unless a recorded
> forcing function — **independent scaling of a part with a materially different
> load profile, independent team-autonomy/deploy-cadence, or complexity that
> genuinely exceeds a single deployable** — justifies paying the microservice
> premium (automated deployment, observability, distributed-data discipline).
> Adopt **serverless/FaaS** only for variable/scale-to-zero, event-driven
> workloads that can absorb cold-start latency and run statelessly. Do **not**
> select it for a library, static site, CLI, or throwaway tool — there is no
> topology decision to make; record the trivial single-artifact default. The
> split, when justified, follows bounded-context fault lines and each service
> owns its data.

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- ADR: deployable count + split topology, forcing function, microservice-premium readiness, bounded-context fault lines
- TD: deployable units, module/service boundaries, per-service data ownership, function+trigger for serverless

## ADR References

Record an ADR for **any topology other than the modular-monolith default**, and
for the default itself when a reader might expect microservices. The ADR MUST
name: the chosen topology, the **specific forcing function** that justifies it
(scaling / team autonomy / complexity), evidence the **microservice premium**
(automated deployment, observability, distributed-data discipline) is paid, and
the **bounded-context fault lines** each deployable sits on. A material
uncertainty about the topology (unknown load profile, unproven boundaries) is a
`tech-spike`, not a silent split (see
`workflows/references/concern-resolution.md`).
