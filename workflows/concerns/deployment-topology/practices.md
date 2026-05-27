# Practices: Deployment Topology

These practices make the **topology decision** (how many independently
deployable units, and where their seams fall) checkable in review. They govern
**how many deployables and where the boundaries are** — not the internal
layering of any one deployable (`architecture-style` / `onion-architecture`),
not how services talk once split (`enterprise-integration-patterns`), and not
the runtime that hosts them (`k8s-kind` / the `deploy-target` filler). The
default stance is **modular-monolith**; most of the review work is confirming
the default was kept or that a split was justified and the premium paid.

## Decide and record the topology

- The product MUST have a **recorded topology decision** (ADR) naming whether it
  ships as a modular monolith, microservices, or serverless/FaaS. The default
  is **modular-monolith**; any other choice MUST cite a specific forcing
  function.
- For any topology other than the modular-monolith default, the ADR MUST name:
  the **forcing function** (independent scaling / team autonomy / complexity
  exceeding one deployable), evidence the **microservice premium is paid**
  (automated deployment, observability, distributed-data discipline), and the
  **bounded-context fault lines** each deployable sits on.
- A library / static site / CLI / throwaway tool MUST record the trivial
  single-artifact default and apply none of the splitting machinery.

## Default: ship a modular monolith with enforced module boundaries

- A monolith MUST have **internal module boundaries enforced by the
  language/module system** (package visibility, per-module schema, an explicit
  module API) — not a "big ball of mud" defended as "split later". An
  un-modularized monolith cannot be peeled apart and is a defect.
- Module boundaries MUST follow **bounded-context fault lines**
  (`domain-driven-design`), so they are the same seams a future split would
  follow — drawn first in-process where they are cheap to move.
- The monolith SHOULD stay one deployable until a recorded forcing function
  justifies splitting; boundaries are matured in-process before any service is
  peeled off the edge.

## If split into microservices: independence and data ownership

- Each service MUST be **independently deployable** — deployable without
  lock-step release of another service.
- Each service MUST **own its own data**. No service reaches into another
  service's database/tables; cross-boundary access goes over the published
  contract or a channel (`enterprise-integration-patterns`). A shared database
  across a service boundary is a **distributed monolith** and MUST be rejected.
- A service boundary MUST sit on a **bounded context** — not an arbitrary
  technical layer, and never cutting a single context across deployables.
- The microservice premium MUST be **in place before the split ships**:
  automated deployment, observability/monitoring (`o11y-otel`), and an explicit
  distributed-data / partial-failure strategy (eventual consistency, designed
  failure handling). A split without these is rejected.

## If serverless / FaaS: stateless, event-driven, workload-fit

- Each function MUST be **stateless** — no state carried in-memory across
  invocations; all state lives in external services (database, object store,
  cache, queue). A function relying on warm in-memory state is a defect.
- Functions MUST be invoked by an explicit **trigger** (HTTP, queue, schedule,
  event) and MUST tolerate **cold starts** and the platform's execution-time /
  connection limits.
- Serverless MUST only be chosen for workloads that fit it: variable / spiky /
  scale-to-zero, event-driven work that can absorb cold-start latency. It MUST
  NOT be chosen for latency-sensitive hot paths that cannot absorb cold-start
  spikes, long-running / CPU-intensive work that hits execution-time limits, or
  workloads needing persistent connections (e.g. WebSockets).
- Provider-specific SDKs (functions and the managed data/queue services they
  use) SHOULD be isolated behind a port (`onion-architecture`) so the
  real lock-in surface — the surrounding managed services — is contained.

## Stay in your lane (boundary with sibling concerns)

- Do **not** review the internal layering of a deployable here — that is
  `architecture-style` / `onion-architecture`. Verify only the count and seams
  of deployables.
- Do **not** review channel / idempotency / dead-letter / delivery-guarantee
  rules here — that is `enterprise-integration-patterns`, which applies once a
  split creates a boundary.
- Do **not** review cluster / Helm / image-build mechanics here — that is
  `k8s-kind` / the `deploy-target` filler. The topology decision is upstream of
  the runtime.

## Quality Gates

- A **recorded topology decision** (ADR) exists; the default is
  modular-monolith and any other choice cites a specific forcing function plus
  evidence the microservice premium is paid.
- A **monolith has enforced internal module boundaries** following
  bounded-context fault lines — no un-modularized "big ball of mud".
- **No distributed monolith**: every service is independently deployable and
  owns its own data; no shared database or cross-boundary table access; every
  service boundary sits on a bounded context.
- The **microservice premium is in place before any multi-deployable split
  ships**: automated deployment, observability, distributed-data discipline.
- Every **serverless function is stateless and trigger-driven**, fits a
  variable/scale-to-zero event-driven workload, and tolerates cold-start and
  execution-time limits; provider SDKs are isolated behind a port.
- The topology decision is **not conflated** with internal layering
  (`architecture-style`), inter-service communication
  (`enterprise-integration-patterns`), or the runtime (`k8s-kind`).
