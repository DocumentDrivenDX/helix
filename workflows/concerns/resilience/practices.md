# Practices: Resilience

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
