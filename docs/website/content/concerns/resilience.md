---
title: "Resilience"
slug: resilience
generated: true
aliases:
  - /reference/glossary/concerns/resilience
---

**Category:** Architecture · **Areas:** api, infra

## Description

## Category

architecture

This is an **architecture** concern, not a quality-attribute one. Resilience is
not a cross-cutting evidence gate that applies to every buildable product (that
is `verification`); it is a set of *structural design decisions* — where to put
timeouts, which dependencies get a circuit breaker, how to partition resources
into bulkheads, what to fall back to when a dependency is down. Those decisions
change the shape of the system (its failure boundaries, its guard wiring, its
fallback paths) and are recorded in ADRs and the technical design, exactly like
the other architecture concerns (`onion-architecture`,
`enterprise-integration-patterns`). It is **composable** (no slot): it earns its
place only when the system has a real failure surface, and composes with the
architecture-style slot and `o11y-otel` rather than competing for a position.

## Areas

api, infra

Resilience guards live where the failure surface is: the service code that makes
outbound calls (`api`) and the infrastructure that hosts dependencies, sets
connection/pool limits, and runs the gateway/mesh (`infra`). It does not scope to
pure UI or docs work.

## Boundary

This concern owns the **stability of synchronous calls across a real failure
surface** — the Nygard *Release It!* stability patterns and the cloud resiliency
patterns (Azure Architecture Center, Netflix Hystrix / resilience4j). Its
vocabulary is timeout, retry-with-backoff-and-jitter, circuit breaker, bulkhead,
fail fast, steady state, backpressure / load shedding, and graceful degradation /
fallback. Three neighbors must stay distinct:

- **vs `enterprise-integration-patterns` (EIP)** — the load-bearing split is
  **synchronous vs asynchronous**. EIP owns the resilience of the **messaging
  channel**: its Idempotent Receiver, Dead Letter Channel, Invalid Message
  Channel, and Guaranteed Delivery make an *async, channel-decoupled* flow
  survive duplicates, poison messages, and broker crashes. THIS concern owns the
  resilience of a **synchronous, in-the-call-path dependency** — the HTTP/gRPC/DB
  call that a request blocks on right now: its timeout, its breaker, its
  bulkhead, its fallback. **Idempotency is shared vocabulary, split by purpose:**
  EIP requires an Idempotent *Receiver* because an at-least-once channel *will*
  redeliver; this concern requires idempotency as the **precondition that makes a
  synchronous retry safe** (you may only auto-retry an operation whose repeat has
  one effect). When the boundary is a queue/broker, reach for EIP; when it is a
  blocking synchronous call, reach for resilience. A retry on a non-idempotent
  synchronous POST and a missing Dead Letter Channel are *different* defects owned
  by *different* concerns — do not duplicate either.
- **vs `verification`** — resilience is the **behavior** (the breaker opens, the
  timeout fires, the fallback serves). `verification` is the **proof it ran** —
  the evidence gate that refuses "done" until the breaker's open/half-open path
  and the timeout were exercised against the running system. This concern *states
  what must be true*; verification *makes you observe it*. Do not restate the
  evidence-gate machinery here; do hand it the guard branches to exercise.
- **vs `o11y-otel`** — you cannot manage a failure you cannot see. `o11y-otel`
  owns the telemetry (RED metrics, traces, structured logs, correlation ids);
  this concern *consumes* it — a circuit breaker's state transitions, a timeout's
  fire rate, and a shed-load count must be observable, but the metric/trace
  plumbing belongs to `o11y-otel`. Compose: emit breaker-state-change and
  timeout/shed events into the o11y pipeline; do not re-specify the pipeline.

This concern is **non-exclusive** (composable, no slot). It has no `## Slot`
heading.

## Components

The stability patterns, organized by what each defends against.

### Bounding a single call — never wait forever
- **Timeout** — every outbound call to an external dependency (HTTP, gRPC, DB,
  cache, queue client) has a finite deadline on both *connection* and *request*.
  An unbounded call is the root failure: it holds a thread / connection / memory
  while the dependency hangs, and that held resource is what propagates the
  failure inward. Set the timeout from the dependency's latency percentile (e.g.
  p99.9) plus network padding, not an arbitrary round number.
- **Fail Fast** — determine as early as possible whether a request *can* be
  serviced, and if not, reject it immediately rather than doing partial work and
  failing late. Validate inputs and check breaker/resource state up front; a fast
  rejection frees the caller and the resource far sooner than a slow timeout.

### Surviving a flaky dependency — retry and break
- **Retry with exponential backoff + jitter** — for **transient** faults
  (timeout, 503, connection reset), retry, but: (1) only on **idempotent**
  operations; (2) with **exponential backoff** (each attempt waits longer) so a
  recovering dependency is not hammered; (3) with **jitter** (randomness on the
  delay — full or decorrelated) so many clients do not retry in lockstep and
  re-overload it; (4) with a **cap** on attempts and total time, never infinite;
  (5) at **one layer** of the stack only — retries nested at multiple layers
  multiply (3 layers × 3 retries = 27× load). Prefer a **retry budget** (token
  bucket) so retries are bounded as a *fraction* of traffic, not per-call.
- **Circuit Breaker** — a proxy in front of a failing dependency, a state machine
  with three states: **Closed** (calls pass; count recent failures; trip to Open
  when failures exceed a threshold in a window), **Open** (calls fail
  immediately / serve a fallback — no call is made — while a timeout timer runs),
  **Half-Open** (after the timer, a limited number of trial calls probe recovery;
  all-succeed → Closed and reset; any-fail → back to Open and restart the timer).
  The breaker stops a slow/failing dependency from holding resources and
  cascading; Half-Open stops a flood of traffic from re-killing a service that is
  just coming back. The breaker's retry-sensitivity matters: a retry loop *around*
  a breaker must stop retrying when the breaker says the fault is not transient.

### Containing a failure — isolate and degrade
- **Bulkhead** — partition resources (thread pools, connection pools, semaphore
  permits) per dependency / per consumer so that one saturated dependency cannot
  exhaust the shared pool and sink unrelated parts of the system. Named for a
  ship's watertight compartments: a breach floods one compartment, not the hull.
- **Graceful Degradation / Fallback** — when a dependency is down (or its breaker
  is Open), serve a **reduced but useful** response — a cached value, a default, a
  queued-for-later acknowledgement, a feature hidden — rather than failing the
  whole request. The fallback is a deliberate, designed path, not an
  accidental null.

### Protecting the whole system under load — shed and steady
- **Backpressure / Load Shedding** — when inbound demand exceeds capacity, signal
  upstream to slow down (backpressure) or reject excess work early
  (load-shedding / throttling at the gateway), prioritizing high-value traffic.
  Accepting unbounded work you cannot complete converts an overload into a crash.
- **Steady State** — the system can run indefinitely without human intervention:
  every resource that accumulates (logs, temp files, caches, session tables,
  connection pools) has a bounded ceiling and a reclamation mechanism. An
  unbounded accumulation is a guaranteed eventual outage on a timer.

### Anti-patterns (the failures these patterns prevent)
- **Cascading failure** — one slow/failed dependency holds resources, which
  blocks callers, which hold *their* resources, propagating the outage up the
  stack. Timeouts + breakers + bulkheads exist to interrupt this chain.
- **Retry storm** — uncoordinated, uncapped, un-jittered, or multi-layer-nested
  retries amplify load on an already-struggling dependency, turning a blip into an
  outage. Backoff + jitter + cap + single-layer + retry-budget prevent it.
- **Unbounded resource use** — no timeout, no pool cap, no accumulation ceiling;
  the system consumes until it dies. Steady State + bulkheads + timeouts bound it.

### Compact intent table

| Pattern | Defends against | Applies when |
|---------|-----------------|--------------|
| Timeout | A hung dependency holding a thread/connection forever | Any outbound call to an external dependency |
| Fail Fast | Doing partial work then failing late, wasting resources | A request can be cheaply known un-serviceable up front |
| Retry + backoff + jitter | A transient blip failing a request that would succeed on a 2nd try | The fault is transient AND the operation is idempotent |
| Circuit Breaker | Cascading failure / cost of repeatedly calling a known-down dependency | A dependency fails in a way that takes time to recover |
| Bulkhead | One saturated dependency exhausting a shared pool and sinking the rest | Multiple dependencies/consumers share a finite resource pool |
| Graceful Degradation / Fallback | A single dependency outage failing the whole request | A reduced-but-useful response exists (cache, default, defer) |
| Backpressure / Load Shedding | Accepting more work than capacity, crashing under overload | Inbound demand can exceed what the system can complete |
| Steady State | An unbounded accumulation running the system out of a resource | Anything accumulates over time (logs, temp, caches, sessions) |

## Constraints

### Every outbound call to an external dependency is bounded
- Every synchronous call that leaves the process to an external dependency
  (HTTP/gRPC/DB/cache/queue-client) has a **timeout** on connection and request.
  An unbounded outbound call is a defect, not a default — it is the seed of every
  cascading failure.

### Retries are safe, bounded, and single-layer — or they are a storm
- A synchronous operation is auto-retried **only if it is idempotent** (its
  repeat has exactly one effect). A retry on a non-idempotent mutation
  (a plain POST/charge/create with no idempotency key) is a defect.
- Retries use **exponential backoff + jitter**, a **cap** on attempts and total
  elapsed time (never infinite), and happen at **one layer** of the stack.
  Prefer a **retry budget** (token bucket) bounding retries as a fraction of
  traffic. Lockstep, uncapped, or multi-layer-nested retries are a **retry
  storm** — rejected.
- Retry handles **transient** faults; a fault the breaker has classified as
  non-transient stops the retry loop.

### A flaky / slow dependency is guarded by a circuit breaker
- A dependency that fails in a way taking time to recover is fronted by a
  **circuit breaker** with explicit Closed/Open/Half-Open behavior, a failure
  threshold, and a reset timeout. While Open, calls fail fast or serve a
  fallback — they do not hit the dependency. Half-Open probes recovery with
  limited trial traffic, never a flood.

### Failures are contained, not propagated
- Resources are **bulkheaded** (per-dependency pools/permits) so one saturated
  dependency cannot exhaust the shared pool and cascade. A single shared
  unbounded pool for all dependencies is a cascade waiting to happen.
- A dependency outage **degrades gracefully** to a designed fallback (cache /
  default / defer / hidden feature) where one exists, rather than failing the
  whole request. The fallback is intentional, not an accidental null.

### The system protects itself under load and runs in steady state
- Under overload the system **sheds or throttles** excess work (load-shedding /
  backpressure), prioritizing high-value traffic, rather than accepting unbounded
  work it cannot complete.
- Every accumulating resource has a **bounded ceiling and reclamation** (steady
  state): logs rotate, temp is cleaned, caches evict, pools cap. An unbounded
  accumulation is a scheduled outage.

### Resilience is earned, not flat
- These guards are warranted **in proportion to the failure surface**. A system
  with external dependencies and distributed/synchronous calls earns them; a
  thin in-process CRUD app with no real failure surface does not. Wrapping an
  in-memory function call in a circuit breaker is cost without payoff
  (KISS/YAGNI) — the breaker exists for a *remote* dependency that can be slow or
  down.

## Drift Signals (anti-patterns to reject in review)

- An outbound call to an external dependency with **no timeout** (relying on the
  client library's default-infinite) → bound it; an unbounded call seeds
  cascading failure
- A **retry on a non-idempotent** synchronous mutation (plain POST/charge with no
  idempotency key) → retry only idempotent ops, or add an idempotency key
- Retries with **no backoff, no jitter, no cap**, or **nested across layers** →
  retry storm; add backoff+jitter+cap and retry at one layer / a retry budget
- A known-flaky dependency called directly in the request path with **no circuit
  breaker** → front it with a breaker; cap the blast radius of its slowness
- A circuit breaker present but its **Open/Half-Open behavior is never tested**
  (only the happy path) → exercise the open + recovery paths (hand to
  `verification`)
- **One shared unbounded pool** for all dependencies, so one saturated dependency
  starves the rest → bulkhead per dependency
- A dependency outage **fails the whole request** when a cached/default/deferred
  fallback was available → add a designed graceful-degradation path
- The system **accepts unbounded inbound work** under overload and crashes →
  shed/throttle excess, apply backpressure, prioritize high-value traffic
- An **unbounded accumulation** (logs/temp/cache/sessions never reclaimed) →
  steady-state violation; bound and reclaim it
- Breaker trips / timeouts / shed-load **invisible** (no metric, no event) →
  compose with `o11y-otel` so failures are observable
- A circuit breaker / bulkhead / retry wrapped around an **in-process** call with
  no remote failure surface → KISS/YAGNI; remove it

## When to use

Select for any product with a **real failure surface**: it makes **synchronous
calls to external dependencies** (a third-party API, a remote database/cache, a
payment or auth provider, another service in a distributed system) where that
dependency can be slow, flaky, or down and the call sits **in the request path**.
A platform that fans out to several downstream services, integrates a third-party
provider synchronously, or has a dependency whose outage must not take the whole
system down is a **strong** fit.

Do **not** select it for a **thin in-process CRUD app** with no external
synchronous dependency, a static/marketing site, a single-process library, or any
system with **no real failure surface** — there the timeout/breaker/bulkhead
machinery is cost without payoff (KISS/YAGNI). An in-memory function call is not a
failure surface.

It is composable (no slot); `areas: api, infra` scopes its practices to the
service and infrastructure work items where the guards live. Compose with the
**architecture-style** slot (the guards sit at the outer-ring / adapter boundary
where calls leave the process), **`enterprise-integration-patterns`** (which owns
the *async-channel* resilience — DLQ, idempotent receiver — to this concern's
*synchronous-call* resilience), and **`o11y-otel`** (which carries the breaker /
timeout / shed-load signals so failures are observable).

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- ADR: failure-handling strategy — per-dependency timeout/breaker/bulkhead/retry/fallback policy
- TD: timeout + circuit-breaker + bulkhead + graceful-degradation guards at the outbound-call boundary
- TEST_PLAN: breaker open/half-open + timeout-fire + fallback paths exercised, not just happy path

## ADR References

Selecting resilience **forces** a specific ADR: the **failure-handling
strategy** — which dependencies are in the request path, which get a **circuit
breaker** (with threshold + reset behavior) and/or a **bulkhead**, what the
**timeout** policy is per dependency, the **retry** policy (backoff/jitter/cap,
which operations are idempotent enough to retry), and the **fallback /
degradation** behavior when each guarded dependency is down. The chosen failure
modes and guard placement are design-defining decisions, recorded in an ADR — not
left implicit. A material uncertainty about a dependency's failure behavior
(unknown latency distribution, unknown idempotency guarantees, unknown recovery
time) is a `tech-spike` to de-risk before committing the strategy, not a silent
assumption (see `workflows/references/concern-resolution.md`).

## Practices by activity

Agents working in any of these activities inherit the practices below via the bead's context digest.

These practices govern the **stability of synchronous calls across a real
failure surface** — the Nygard *Release It!* stability patterns and the cloud
resiliency patterns (timeout, retry-with-backoff-and-jitter, circuit breaker,
bulkhead, fail fast, steady state, backpressure / load shedding, graceful
degradation). They govern the **in-the-call-path** dependency: the HTTP / gRPC /
DB / cache call a request blocks on now. They do **not** govern async-channel
resilience (`enterprise-integration-patterns` owns the Dead Letter Channel,
Idempotent Receiver, and Guaranteed Delivery for a broker-decoupled flow), they
do not re-specify the evidence gate (`verification` owns proving the guards ran),
and they do not re-specify telemetry plumbing (`o11y-otel` owns the
metrics/traces these guards emit into). They reference those concerns at the seam.

## Design

- **Map the failure surface first.** Enumerate every synchronous outbound call
  that leaves the process to an external dependency (third-party API, remote
  DB/cache, payment/auth provider, sibling service). For each, record its
  expected latency, its failure modes, its recovery time, and whether the
  operation is **idempotent**. This map drives every guard below; a dependency
  not on the map has no guard.
- **Pick the guards per dependency, deliberately.** Decide which dependencies get
  a **circuit breaker** (those that fail in ways that take time to recover),
  which need a **bulkhead** (those sharing a finite pool with others), what the
  **timeout** is (from the dependency's latency percentile + padding), and the
  **retry** policy (only for transient + idempotent, with backoff/jitter/cap).
  Record the choices — these are the ADR's failure-handling strategy.
- **Design the fallback for each guarded dependency.** State what a degraded-but-
  useful response is when the dependency is down / its breaker is Open — a cached
  value, a default, a deferred acknowledgement, a hidden feature — or record
  explicitly that no fallback exists and the request fails fast.
- **Decide load protection.** Where inbound demand can exceed capacity, decide the
  backpressure / load-shedding / throttling policy and what high-value traffic is
  prioritized.
- A material uncertainty about a dependency (unknown latency distribution,
  unknown idempotency guarantee, unknown recovery behavior) is a `tech-spike` to
  de-risk before committing the strategy — not a silent assumption (see
  `workflows/references/concern-resolution.md`).

## Implementation

- Place the guards at the **boundary where the call leaves the process** — the
  outer-ring adapter / client wrapper under the architecture-style slot — so the
  domain calls a guarded interface and is unaware of the breaker/retry mechanics.
- Wire each guard's state change into the **`o11y-otel`** pipeline: breaker
  open/half-open/close transitions, timeout fires, retry attempts, and
  shed-load / throttle events are emitted as metrics/events with the correlation
  id, so a failure is observable rather than silent.
- Prefer a battle-tested library (resilience4j, Polly, a service-mesh sidecar,
  the SDK's standard/adaptive retry mode) over hand-rolled guard logic where one
  exists for the stack — hand-rolled backoff/jitter and breaker state machines are
  a common source of subtle storms.

## MUST

- **Every synchronous outbound call to an external dependency has a timeout** on
  both connection and request. No reliance on a client library's default-infinite
  timeout. An unbounded outbound call is rejected.
- **A synchronous operation is auto-retried only if it is idempotent.** A retry on
  a non-idempotent mutation (a plain POST / charge / create with no idempotency
  key) is rejected; either make it idempotent (idempotency key / dedup) or do not
  retry it.
- **Retries use exponential backoff + jitter, a cap, and one layer.** Every retry
  policy has exponential backoff, jitter (full or decorrelated), a maximum attempt
  count, and a maximum total elapsed time — never infinite. Retries happen at a
  **single layer** of the stack, not nested across layers. Lockstep / uncapped /
  multi-layer-nested retries are a retry storm — rejected.
- **A flaky / slow dependency in the request path is fronted by a circuit
  breaker** with explicit Closed → Open → Half-Open behavior, a failure threshold
  over a window, and a reset timeout. While Open, calls fail fast or serve the
  fallback — they do **not** reach the dependency. Half-Open admits only limited
  trial traffic, never a flood.
- **A retry loop around a breaker is breaker-sensitive** — it stops retrying when
  the breaker signals the fault is not transient, rather than retrying into an
  Open breaker.
- **Resources are bulkheaded per dependency** where multiple dependencies /
  consumers share a finite pool — one saturated dependency must not exhaust the
  shared pool and starve the rest. A single shared unbounded pool for all
  dependencies is rejected.
- **Every accumulating resource has a bounded ceiling and reclamation** (steady
  state): logs rotate, temp is cleaned, caches evict, pools cap, growing tables
  are pruned/archived. An unbounded accumulation is rejected.
- **Guard activity is observable** — breaker trips, timeout fires, and
  shed-load / throttle events emit a metric/event (composed with `o11y-otel`),
  not a silent swallow.

## SHOULD

- **Prefer a retry budget (token bucket)** that bounds retries as a fraction of
  total traffic over per-call retry counts, so a broad outage cannot multiply load
  even within the cap.
- **Fail fast** — validate inputs and check breaker / resource availability up
  front and reject un-serviceable requests immediately, rather than doing partial
  work and failing late.
- **Degrade gracefully** — when a guarded dependency is down, serve the designed
  fallback (cache / default / deferred / hidden feature) rather than failing the
  whole request, where a useful reduced response exists.
- **Shed load / apply backpressure under overload** — reject or throttle excess
  inbound work at the edge / gateway and prioritize high-value traffic, rather
  than accepting unbounded work the system cannot complete.
- **Set timeouts from latency percentiles** (e.g. p99.9 + network padding) rather
  than arbitrary round numbers, so the timeout reflects the dependency's real
  behavior.
- **Use a per-resource breaker** where one logical dependency has independent
  providers (e.g. DB shards) so a problem in one does not trip access to the
  healthy ones.

## Boundary with neighbors

See `concern.md` for the canonical Boundary (vs `enterprise-integration-patterns`,
`verification`, `o11y-otel`). These practices stay on synchronous-call
stability; defer to the neighbor named there for async-channel resilience
(EIP), the evidence gate that proves the guards ran (`verification`), and the
telemetry pipeline that carries breaker/timeout/shed signals (`o11y-otel`).

## Quality Gates

- **Every outbound call to an external dependency has a timeout** — verified by
  inspecting each client/adapter (no default-infinite), with the timeout derived
  from the dependency's latency rather than an arbitrary value.
- **Retries use backoff + jitter and only on idempotent operations** — verified
  by inspecting each retry policy: exponential backoff present, jitter present, a
  cap on attempts and total time present, retry confined to one layer, and the
  retried operation idempotent (idempotency key / read-only / dedup). No retry on
  a non-idempotent mutation.
- **A circuit breaker guards each flaky dependency, and its open/half-open
  behavior is tested** — verified by an exercise (handed to `verification`) that
  forces failures until the breaker **opens** (calls then fail fast / serve the
  fallback without hitting the dependency), waits the reset timeout, and confirms
  **half-open** admits limited trial traffic and **closes** on recovery. A breaker
  whose only exercised path is the happy (Closed) path fails this gate.
- **Resources are bulkheaded per dependency** — verified that no single shared
  unbounded pool backs all dependencies; a saturated dependency does not starve
  the others.
- **Each guarded dependency has a tested fallback (or a recorded fail-fast)** —
  with the breaker Open, the request serves the designed degraded response or
  fails fast as recorded, never hangs or returns an accidental null.
- **Under overload the system sheds / throttles** rather than accepting unbounded
  work — verified by driving demand past capacity and observing excess rejected /
  throttled with high-value traffic prioritized.
- **No unbounded accumulation (steady state)** — every accumulating resource
  (logs, temp, caches, sessions, pools, growing tables) has a recorded ceiling and
  reclamation.
- **Guard activity is observable** — breaker trips, timeout fires, and shed-load
  events appear as metrics/events in the `o11y-otel` pipeline, not silent.
