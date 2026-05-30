# Practices: Concurrency Model

These practices govern the **in-process / in-service execution model** — how
concurrent work runs within one service, how its shared mutable state is owned
and protected, and how its concurrency is bounded. They do **not** govern the
broker/channel a worker consumes across a system boundary
(`enterprise-integration-patterns`), the failure-containment guards around the
execution model (`resilience` — breaker, bulkhead, load-shedding), or how many
deployable units / replicas the system ships as (`deployment-topology`). They
reference those concerns at the seam and stay on the execution model.

## Design

- Name the **workload shape** before the model: is the concurrency **I/O-bound**
  (many waits — an event loop fits), **CPU-bound** (parallel compute over shared
  state — threads/parallelism fits), **many coordinating stateful entities**
  (actors / CSP channels fit), an **async pipeline with rate mismatch** (reactive
  streams fit), or **deferred out-of-band work** (a worker/background-job model
  fits)? Record the chosen model and *why it fits the workload*. A deliberate
  **mix** is allowed (e.g. an event-loop request tier offloading CPU work to a
  worker pool) — record each.
- Identify every piece of **shared mutable state** the concurrent paths touch,
  and decide for each: **eliminate** it (immutability / confine to one owner —
  an actor, a single goroutine, the loop thread, thread-local) or **guard** it
  (a lock with a defined acquisition order, an atomic, a channel hand-off).
  State with no concurrent writer needs neither.
- Decide the **bounding strategy** up front: the pool size / semaphore permits /
  bounded-channel capacity / `request(n)` demand that caps in-flight work, and
  the **backpressure or drop strategy** for a producer that can outpace its
  consumer (block / drop / latest / error). There is no "unbounded" default.
- For background/async work, design **idempotency** (a de-dup key or a
  semantically idempotent operation) and **failure visibility** (recorded
  status / reply / callback, plus a dead-letter destination and an alert) before
  building — the job *will* run more than once and *can* fail unseen.
- A material uncertainty about the model (unknown I/O-vs-CPU shape, unknown
  throughput/contention, unproven backpressure behavior) is a `tech-spike` to
  de-risk before committing — not a silent assumption (see
  `workflows/references/concern-resolution.md`).

## Implementation

- Use the **language-runtime** filler's concrete primitives for the chosen model
  (goroutines+channels, asyncio's loop, the actor library, the thread/worker
  pool). Do not hand-roll a second concurrency mechanism alongside it.
- Confine shared state to a single owner where the model offers one (an actor's
  private state, a single goroutine behind a channel, the event-loop thread).
  Where locks are unavoidable, hold them for the shortest critical section and
  acquire multiple locks in a **single consistent order** everywhere.
- On an event loop, keep blocking and CPU-bound work **off the loop** — offload
  to a worker thread/pool — and ensure every `await` is awaited (no dropped
  promise/coroutine).
- Bound every concurrent path: a fixed-size **worker pool** draining a channel/
  queue, a **semaphore** capping in-flight tasks, a **bounded (buffered)
  channel** as the queue, or explicit **`request(n)`** demand on a reactive
  stream. Reclaim every lightweight process — no goroutine left blocked forever,
  every subscription disposed.

## MUST

- **Shared mutable state is eliminated or guarded — never raced.** Every piece of
  state touched by concurrent execution is either immutable / confined to one
  owner, or protected by a lock/atomic/channel hand-off. Unsynchronized
  concurrent mutation is a **data race** — a defect. Verified by a race detector
  (e.g. `-race`, TSan) on the concurrent paths and by review of each shared
  field's ownership.
- **No unbounded concurrency.** Concurrent work is bounded by a pool, semaphore,
  bounded channel, or explicit demand — never one thread/goroutine/actor per
  request/item with no cap, and never an unbounded queue/mailbox/buffer. Verified
  by pointing to the bound (the pool size / permit count / channel capacity) for
  each concurrent path.
- **A producer that can outpace its consumer has a bounded buffer + a chosen
  overflow strategy** (block / drop / latest / error) — never an unbounded buffer
  that grows until OOM. (The actor-mailbox and reactive-stream signature
  failure.)
- **The event-loop thread is never blocked** by a synchronous CPU-bound or
  blocking call; such work is offloaded to a worker pool. No `await` is dropped.
- **Every state-mutating background job is idempotent** — reprocessing the same
  job yields one effect, not a double-apply (no double charge / send / insert).
  Verified by running the same job twice and observing one effect. (In-process
  twin of EIP's Idempotent Receiver.)
- **Background/async work's outcome and failure are observable** — a recorded
  status / reply / callback, a dead-letter destination for repeated failure, and
  an alert. Never fire-and-forget with no way to detect a lost or failed job.
- **Locks are acquired in a single consistent order** across all call paths, to
  prevent deadlock; lightweight processes and subscriptions are **reclaimed**
  (no goroutine blocked forever, every subscription disposed).

## SHOULD

- **Prefer eliminating shared mutable state over guarding it** — immutability,
  confinement to one owner (actor / single goroutine / loop thread), or
  thread-local — reaching for locks only when sharing is genuinely required.
- **Prefer the model that matches the workload** — an event loop for I/O-bound
  concurrency, parallelism for CPU-bound, actors/channels for many coordinating
  entities, a worker pool for deferred work — over forcing one model onto an
  ill-fitting workload.
- **Prefer a bounded (buffered) channel or a fixed worker pool as the queue**
  over an ad-hoc unbounded in-memory list, so the bound is structural, not
  hoped-for.
- **Carry concurrency signals into telemetry** (compose with `o11y-otel`):
  pool/queue saturation, queue depth, mailbox/buffer size, job outcomes and
  retry counts — so saturation and lost jobs are visible before they become an
  incident.
- **Hand failure-containment to `resilience`** — a bulkhead partitioning pools
  per dependency, load-shedding under overload, a breaker/timeout around a
  remote call — rather than open-coding those here; this concern owns the
  steady-state bound, resilience owns the overload/failure response.

## Boundary with neighbors

See `concern.md` for the canonical Boundary (vs `enterprise-integration-patterns`,
`resilience`, `deployment-topology`). These practices stay on the in-process
execution model; reach to the neighbor named there for channel/DLQ rules
(EIP), bulkhead/breaker/load-shedding (`resilience`), or replica/deployable
count (`deployment-topology`).

## Quality Gates

- Shared mutable state on every concurrent path is eliminated or guarded; a race
  detector (`-race` / TSan) runs clean on the concurrent code, and each shared
  field has a named owner or guard (no unsynchronized concurrent mutation).
- No unbounded concurrency: every concurrent path has a stated bound — a pool
  size, semaphore permit count, bounded-channel capacity, or `request(n)`
  demand. No "one per request/item with no cap" and no unbounded
  queue/mailbox/buffer.
- A producer that can outpace its consumer has a bounded buffer and a recorded
  overflow strategy (block / drop / latest / error), verified by driving the
  producer faster than the consumer and observing the bound hold (no OOM).
- The event loop is never blocked: no synchronous CPU-bound or blocking call runs
  on the loop thread (offloaded to a pool), and no `await` is dropped — verified
  by review and a loop-latency check under load.
- Every state-mutating background job is idempotent, verified by **running the
  same job twice and observing exactly one effect**.
- Background/async work is observable: each job has a recorded outcome and a
  dead-letter + alert path for repeated failure — verified by failing a job and
  observing it land in the dead-letter destination (not silently lost).
- Locks are acquired in a single consistent order (review), and no lightweight
  process or subscription leaks (no goroutine blocked forever on an unserviced
  channel; every subscription disposed).
- The chosen concurrency model and its bounding strategy are recorded in an ADR;
  the model fits the workload shape (I/O-bound vs CPU-bound vs entity
  coordination vs deferred work).
