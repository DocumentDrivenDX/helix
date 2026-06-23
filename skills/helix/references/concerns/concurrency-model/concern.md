# Concern: Concurrency Model

## Category

architecture

This is an **architecture** concern, not a quality-attribute one. The
concurrency model is a *structural design decision* — which in-process
execution model the system uses (threads-and-locks, an async/await event loop,
the actor model, CSP channels, reactive streams, or a background worker pool),
how shared mutable state is handled under it, and how concurrent work is
bounded. Those decisions change the shape of the system (its state ownership,
its synchronization points, its bounding strategy) and are recorded in ADRs and
the technical design, exactly like the other architecture concerns
(`onion-architecture`, `enterprise-integration-patterns`, `resilience`). It is
**composable** (no slot): it earns its place only when the system has real
concurrency, parallelism, or background/async processing, and composes with the
language-runtime filler (which fixes the actual primitives) and `resilience`
rather than competing for a position.

## Areas

backend, api

The execution model lives in the service code that runs concurrent work — the
backend logic and the API request handlers that share state, await I/O, spawn
goroutines/actors, or enqueue background jobs. It does not scope to pure UI,
docs, or static-site work, which has no in-process concurrency decision to make.

## Boundary

This concern owns the **in-process / in-service execution model** — *how work
runs concurrently WITHIN one service or process*, how its shared mutable state
is owned and protected, and how its concurrency is bounded. Its vocabulary is
threads/locks/shared-memory, the async/await event loop (single-threaded
cooperative), the actor model (isolated state + message passing), CSP / channels
(goroutines), reactive streams + backpressure, and the worker / background-job
model. Three neighbors must stay distinct:

- **vs `enterprise-integration-patterns` (EIP)** — the load-bearing split is
  **within one process vs across a system boundary over a broker**. EIP owns
  *asynchronous messaging BETWEEN independently-deployed systems* — the channel,
  its delivery guarantee, the router, the dead-letter destination, the wire
  shape that crosses the boundary. THIS concern owns *the execution model
  WITHIN one service*. The seam is sharp at the worker: a background-job
  worker's **concurrency** (how many jobs run at once, the pool/semaphore that
  bounds them, whether the handler is thread-safe) is **here**; the **channel
  the worker consumes from** (its at-least-once guarantee, its DLQ, its
  correlation id) is **EIP**. A queue worker draining an SQS queue: the SQS
  channel and its DLQ are EIP; the worker pool that processes the dequeued
  messages and the shared state those handlers touch are concurrency-model. Do
  **not** restate channel / idempotent-receiver / dead-letter rules here; do
  hand EIP the broker boundary and own the in-process execution that consumes
  it. (Idempotency is shared vocabulary: EIP requires an **Idempotent Receiver**
  because the *channel* redelivers; this concern requires a background job to be
  idempotent because the *worker* may run it more than once on retry — same
  property, different reason, do not duplicate.)
- **vs `resilience`** — concurrency owns the **execution model**; resilience
  owns **failure handling and stability**. The two overlap on **backpressure**
  and **bounding**, and the split must be explicit: concurrency-model owns
  *how the execution model expresses and propagates demand* — reactive streams'
  `request(n)` pull, a bounded channel that blocks the producer, a worker
  pool/semaphore that caps in-flight work — i.e. **bounding concurrency is the
  normal, steady-state shape of the execution model**. `resilience` owns
  *what the system does when demand exceeds capacity as a failure event* —
  load-shedding at the gateway, the bulkhead that isolates one saturated
  dependency from the rest, the circuit breaker, the timeout. Put plainly:
  a **bounded work pool / semaphore that caps in-flight tasks is
  concurrency-model** (the execution model's native bound); a **bulkhead that
  partitions pools per dependency so one cannot starve the others, and
  load-shedding under overload, are resilience** (failure containment). When the
  question is "how does work run and how is it bounded in steady state", it is
  here; when it is "what happens when a dependency is slow/down or demand floods
  us", it is `resilience`. Do **not** restate breaker/bulkhead/timeout/shed
  machinery here.
- **vs `deployment-topology`** — concurrency owns **in-process** execution (the
  threads, the event loop, the goroutines, the worker pool *inside one
  deployable*); deployment-topology owns **process-level scaling** — how many
  independently deployable units the system ships as and whether you add
  replicas. Scaling out by running more replicas of a stateless service is a
  *topology* decision; choosing an event loop vs a thread pool *inside* each
  replica is *this* concern. They compose: a horizontally-scaled fleet still
  needs an in-process concurrency model per replica. Do **not** restate the
  monolith-vs-microservices / replica-count decision here.

This concern is **non-exclusive** (composable, no slot). It has no `## Slot`
heading.

## Components

The in-process execution models, organized by how each handles concurrent work
and shared state. The language-runtime filler fixes the concrete primitives;
this concern names the model, its sweet spot, and its hazards.

### Threads + locks / shared memory
Multiple threads run over **shared mutable memory**, coordinating through
explicit synchronization (mutexes, semaphores, condition variables, atomics).
The model maps directly to multicore hardware and is the lowest-level,
most-general option.
- **Sweet spot**: CPU-bound parallel work that must share a large in-memory
  data structure; latency-sensitive code where the cost of message-copying is
  unacceptable; the substrate other models are built on.
- **Hazards**: **data races** (two threads touch the same field with at least
  one write, no synchronization — undefined behavior); **race conditions** (the
  result depends on scheduling/interleaving); **deadlock** (two threads each
  hold a lock the other needs — prevented by a consistent global lock-ordering);
  lock contention serializing the very work you parallelized; thread-pool
  exhaustion when blocking work starves the pool. The default mitigation is to
  **eliminate shared mutable state** (immutability, thread-local, confinement)
  before reaching for locks.

### Async / await event loop (single-threaded cooperative)
A **single thread** runs an event loop that interleaves many tasks
**cooperatively**: a task runs until it `await`s an I/O operation, then yields
control back to the loop so another task runs. There is no preemption and (in
the canonical single-loop case) no shared-memory race, because only one task
runs at a time.
- **Sweet spot**: **I/O-bound** workloads with high concurrency — many
  simultaneous connections/requests that spend their time waiting on the
  network, disk, or database (web servers, proxies, API gateways). Cheap
  concurrency without per-connection thread cost.
- **Hazards**: **a blocking or long CPU-bound call stalls the entire loop** —
  one un-yielded computation freezes every other task ("the event loop lie":
  async does not make CPU work concurrent, only I/O waits); **a forgotten
  `await`** leaves a promise/coroutine that never runs (or runs unordered);
  **callback hell / lost error paths** in pre-async-await chaining; **microtask
  flooding** starving macrotasks/timers. CPU-bound work must be offloaded (to a
  worker thread/pool); blocking libraries must not be called on the loop.

### Actor model (isolated state + message passing)
Concurrency is decomposed into **actors**, each owning **private isolated
state** and a **mailbox**. Actors communicate *only* by asynchronous message
passing; an actor processes one message at a time, so its state needs no locks.
Mailbox enqueue/dequeue is atomic, so the classic data race is eliminated by
construction. Erlang/OTP, Akka, and Microsoft Orleans (virtual actors) are the
canonical implementations; supervision hierarchies give a "let it crash"
fault-isolation story and **location transparency** lets actors distribute
across machines.
- **Sweet spot**: large numbers of independent stateful entities coordinating
  (millions of connections/sessions/devices); systems needing fault isolation
  and supervision; workloads that distribute naturally across nodes.
- **Hazards**: **unbounded mailbox growth** — a fast producer outpacing a slow
  actor grows its mailbox until memory is exhausted (the actor model's
  signature failure; needs bounded mailboxes / backpressure); **deadlock by
  cyclic message-wait** (two actors each blocked awaiting the other — isolation
  removes data races, not logical deadlock); **complex multi-actor
  choreography** that is hard to reason about; **at-most-once local / unreliable
  remote** delivery that the design must account for.

### CSP / channels (goroutines)
**Communicating Sequential Processes**: lightweight independent processes
(goroutines) that **share state by communicating** over **channels** rather than
communicate by sharing memory. A `select` multiplexes over several channel
operations. The channel is both the synchronization primitive and the data
conduit; an unbuffered channel is a rendezvous, a buffered channel a bounded
queue.
- **Sweet spot**: pipelines and fan-out/fan-in worker patterns; coordinating
  many lightweight concurrent tasks where the *flow of data* is the natural
  structure; bounded producer/consumer hand-offs (a buffered channel *is* the
  bound).
- **Hazards**: **goroutine leaks** — a goroutine blocked forever on a channel
  nobody will send/receive on, never reclaimed (the silent memory/handle leak);
  **deadlock** when all goroutines are blocked waiting on each other (Go panics
  on total deadlock, but a partial leak is silent); **unbounded goroutine
  spawn** — launching one goroutine per request/item with no pool/limit
  exhausts memory; forgetting to close a channel, or closing it twice. The
  bound is explicit: a worker pool of N goroutines draining one channel, or a
  buffered channel as the queue.

### Reactive streams + backpressure
**Asynchronous stream processing with non-blocking backpressure**: a producer
emits items, and a slow consumer **signals demand** so the producer does not
overwhelm it. The Reactive Streams contract makes this a **pull** model under
the hood (`Subscription.request(n)` — the subscriber asks for as much as it can
handle) even when the surface looks push. Reactor, RxJava (Flowable), and Kotlin
Flow are canonical.
- **Sweet spot**: composing asynchronous data pipelines (transform / filter /
  merge / window) where producer and consumer run at different rates and the
  rate mismatch must be handled in-band; streaming I/O, event processing, and
  glue between async sources.
- **Hazards**: **a hot source with no backpressure strategy overflows** —
  `MissingBackpressureException` / OOM when emissions outpace demand and the
  buffer is unbounded (must choose buffer-with-bound / drop / latest /
  error); **subscription leaks** — never unsubscribing keeps the stream and its
  retained objects alive (a memory leak); steep operator-composition learning
  curve and hard-to-debug stack traces; **cold vs hot** confusion (a cold source
  pulls per-subscriber; a hot source emits regardless and needs a flow-control
  strategy).

### Worker / background-job model
Work the foreground request should not block on is **enqueued** and processed
**out-of-band** by **workers**. The trigger is event-driven, scheduled, or
queue-driven; the worker runs the job asynchronously, with **retries** and a
**poison/dead-letter** path for repeated failure, and **bounded worker
concurrency** so the pool does not exhaust resources. The foreground returns
immediately; the result is communicated back via stored status, a reply, or a
callback.
- **Sweet spot**: slow / spiky / deferred work that must not block the user
  (email/report generation, image processing, third-party calls, scheduled
  maintenance); smoothing load by decoupling acceptance from processing;
  separating a responsive UI from heavy processing.
- **Hazards**: **non-idempotent jobs** double-applying on at-least-once
  redelivery / retry (jobs *will* run more than once); **unbounded worker
  concurrency** — uncapped workers contending for the same resource, or a
  singleton that throws away all scaling; **lost / silent jobs** — fire-and-
  forget with no status, reply, or monitoring, so a failure is undetected;
  **queue saturation** backing up and blocking the system; a poison job blocking
  the queue with no dead-letter path. (The **channel/queue** the worker consumes
  from and its DLQ are `enterprise-integration-patterns`; the **worker pool's
  concurrency, the job's idempotency, and its failure visibility in-process**
  are here.)

### Compact intent table

| Model | Sweet spot | Primary hazard | Bound the concurrency by |
|-------|-----------|----------------|--------------------------|
| Threads + locks / shared memory | CPU-bound parallel work over shared in-memory state | Data race / race condition / deadlock; lock contention | Eliminate/guard shared state; a sized thread pool |
| Async/await event loop | High-concurrency I/O-bound work (servers, proxies) | A blocking/CPU call stalls the whole loop; forgotten `await` | Offload CPU work; never block the loop |
| Actor model | Many isolated stateful entities; fault isolation; distribution | Unbounded mailbox growth; cyclic-wait deadlock | Bounded mailboxes + backpressure |
| CSP / channels | Pipelines, fan-out/fan-in worker coordination | Goroutine leak; deadlock; unbounded goroutine spawn | Worker pool of N; buffered (bounded) channel |
| Reactive streams + backpressure | Async pipelines with producer/consumer rate mismatch | Overflow with no backpressure strategy; subscription leak | `request(n)` demand; bounded buffer / drop strategy |
| Worker / background-job | Slow/spiky/deferred work off the request path | Non-idempotent double-apply; unbounded/lost jobs | Bounded worker pool/semaphore; idempotent + observable jobs |

## Constraints

### A concurrency model is chosen deliberately and recorded
- The system's in-process execution model is a **named, recorded decision** (an
  ADR), not an accident of which library was imported first. Mixing models is
  allowed where each fits its workload (an event-loop web tier handing CPU work
  to a worker pool), but each is a deliberate choice, not drift.
- The model must **fit the workload**: an event loop for I/O-bound concurrency,
  threads/parallel work for CPU-bound, actors/channels for many coordinating
  entities, workers for deferred out-of-band work. Choosing a CPU-parallel
  model for pure I/O waiting (or an event loop for heavy CPU work) is a misuse.

### Shared mutable state is eliminated or guarded — never raced
- Shared mutable state accessed by concurrent execution is **either eliminated**
  (immutability, confinement to one owner — an actor, a single goroutine, the
  event-loop thread, thread-local) **or guarded** by explicit synchronization
  (a lock, an atomic, a channel hand-off). Unsynchronized shared mutation is a
  **data race** — a defect, not a default.
- Where locks are used, a **consistent lock-acquisition order** is defined to
  prevent deadlock; the event-loop thread is **never blocked** by a synchronous
  CPU-bound or blocking call.

### No unbounded concurrency — every concurrent path is bounded
- Concurrent work is **bounded by a pool, a semaphore, a bounded channel, or
  explicit demand (`request(n)`)** — never spawned without limit. Launching one
  thread/goroutine/actor per request or per item with no cap, or an unbounded
  in-memory queue/mailbox/buffer, is an **unbounded-concurrency** defect that
  exhausts memory/threads/handles under load.
- A producer that can outpace its consumer has a **backpressure or bounded-
  buffer** strategy (block / drop / latest / error), chosen deliberately — never
  an unbounded buffer that grows until OOM (the actor-mailbox / reactive-stream
  signature failure).

### Background and async work is idempotent and observable
- A background job runs **at least once** and may run **more than once** (retry,
  redelivery); every state-mutating job is therefore **idempotent** —
  reprocessing yields one effect, not a double-apply. (This is the in-process
  twin of EIP's Idempotent Receiver; the channel guarantee that *causes* the
  redelivery is EIP.)
- Background/async work's **failure is observable**: a job has a recorded
  outcome (status, reply, or callback) and its repeated failure has a
  destination (a dead-letter path) and an alert — never fire-and-forget with no
  way to detect a lost or failed job.

### Cooperative tasks never starve the loop; processes never leak
- On an async/await event loop, **no task blocks the loop**: blocking I/O and
  CPU-bound work are offloaded; every `await` is actually awaited (no dropped
  promise/coroutine).
- Lightweight processes (goroutines/coroutines/subscriptions) are **reclaimed**:
  none is left blocked forever on a channel/signal that will never come, and
  every subscription is disposed. A leaked process/subscription is a steady-
  state defect (overlaps `resilience` steady-state; the leak's *cause* — the
  unreaped goroutine, the never-disposed subscription — is owned here).

## Drift Signals (anti-patterns to reject in review)

- **Shared mutable state mutated by concurrent threads with no synchronization**
  (a field read+written from two threads, no lock/atomic) → data race; eliminate
  the sharing or guard it
- **Locks acquired in inconsistent order** across call paths → deadlock risk;
  define and enforce a global lock-ordering
- **A blocking or long CPU-bound call on the event-loop thread** (a sync DB
  call, a tight compute loop in an `async` handler) → it stalls every task;
  offload it to a worker pool
- **A forgotten `await`** / a promise or coroutine created and dropped → it may
  never run or runs unordered; await it or schedule it explicitly
- **One thread/goroutine/actor spawned per request or per item with no pool or
  cap** → unbounded concurrency; bound it with a pool/semaphore/bounded channel
- **An unbounded mailbox / channel buffer / reactive buffer** that grows under a
  fast producer → choose a bounded buffer + backpressure/drop strategy
- **A hot reactive source with no backpressure strategy** →
  overflow/OOM; apply `request(n)` demand or a bounded buffer/drop operator
- **A goroutine blocked forever on a channel nobody services**, or a
  never-disposed subscription → process/subscription leak; ensure reclamation
- **A background job that is not idempotent** (a retry double-charges /
  double-sends / double-inserts) → make it idempotent (in-process twin of EIP's
  Idempotent Receiver)
- **Fire-and-forget background work with no status, reply, or monitoring** → a
  failed/lost job is undetectable; make the outcome observable with a
  dead-letter + alert path
- **A circuit breaker / bulkhead / load-shedding rule restated here** → that is
  `resilience` (failure containment); this concern owns the steady-state
  execution model and its bound
- **The broker channel / DLQ / delivery guarantee a worker consumes restated
  here** → that is `enterprise-integration-patterns`; own the worker pool and
  job idempotency, hand EIP the channel

## When to use

Select for any product with **real in-process concurrency, parallelism, or
background/async processing, or high throughput**: a server handling many
concurrent connections, CPU-bound parallel work over shared state, many
coordinating stateful entities, async data pipelines with producer/consumer rate
mismatch, or **background/queued/scheduled work processed by workers**. A
platform that runs an I/O-bound request tier *and* offloads slow work to a
bounded worker pool is a **strong** fit — and it composes with
`enterprise-integration-patterns` (which owns the queue the workers consume) and
`resilience` (which owns failure containment around them).

Do **not** select it for a **thin synchronous request/response CRUD app** with
no background processing, no parallelism, and no high-throughput requirement — a
handler that reads a row and returns it has no in-process concurrency decision to
make, and naming an execution model there is cost without payoff (KISS/YAGNI).
Also skip it for a static/marketing site or a purely sequential single-shot CLI.
The framework/runtime's default request-per-handler model is enough until there
is concurrent work, shared mutable state, or out-of-band processing to govern.

It is composable (no slot); `areas: backend, api` scopes its practices to the
service and request-handler work items where the execution model lives. Compose
with the **language-runtime** filler (which fixes the concrete primitives —
goroutines, asyncio, the actor library, the thread pool), the
**architecture-style** slot (the execution model sits in the service core /
outer-ring adapters), **`enterprise-integration-patterns`** (the queue/channel a
worker consumes), **`resilience`** (the failure containment — bulkhead, breaker,
load-shedding — around the execution model), and **`o11y-otel`** (which carries
pool-saturation, queue-depth, and job-outcome signals so concurrency is
observable).

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- ADR: in-process execution model (threads/event-loop/actors/CSP/reactive/worker) + bounding strategy + (if async) job idempotency/failure-visibility
- TD: state ownership/synchronization, bounded concurrency (pool/semaphore/bounded-channel/backpressure), worker model
- TEST_PLAN: no unbounded concurrency, idempotent background jobs (no double-apply on retry), no leaked processes

## ADR References

Selecting concurrency-model **forces** a specific ADR: the **concurrency model
and its bounding strategy** — which in-process execution model the system uses
(threads-and-locks / event loop / actors / CSP channels / reactive streams /
worker pool, or a deliberate mix per workload), how **shared mutable state** is
owned and protected under it, and how concurrent work is **bounded** (the
pool/semaphore/bounded-channel/backpressure strategy) so there is no unbounded
concurrency. For products with background/async processing the ADR also records
the **job idempotency and failure-visibility** approach. A material uncertainty
about the model (unknown workload shape — I/O-bound vs CPU-bound, unknown
throughput/contention profile, unproven backpressure behavior) is a `tech-spike`
to de-risk before committing, not a silent assumption (see
`workflows/references/concern-resolution.md`).
