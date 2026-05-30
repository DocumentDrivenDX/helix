---
title: "Caching Strategy"
slug: caching-strategy
generated: true
aliases:
  - /reference/glossary/concerns/caching-strategy
---

**Category:** Architecture · **Areas:** data, api

## Description

## Category
architecture

## Areas
data, api

## Boundary

This concern owns **the deliberate use of a cache** — the read/write pattern
(cache-aside / read-through / write-through / write-behind), the **invalidation
and TTL policy**, the **consistency/staleness trade-off** a cached read accepts,
the protection against **stampede / thundering-herd**, and the explicit decision
of **what must not be cached**. It owns *how a copy of data is kept closer/faster
and kept correct-enough*. It does **not** own the performance target the cache
serves, the failure-handling discipline a cache may participate in, or the store
the cache sits in front of. Three neighbors must stay distinct:

- **The performance NFR** (a requirement in the PRD, not a concern) owns the
  **target** — the latency/throughput budget the system must meet. Caching is
  **one means to that end, not the end itself**. The NFR says *p95 read latency
  ≤ X / sustain Y req/s*; this concern says *a read-through cache with a Z-second
  TTL is how we hit it, accepting up-to-Z staleness*. Reference the NFR as the
  thing being satisfied; do **not** restate the target here, and do **not** add a
  cache with no NFR to point at (that is premature caching — see Drift Signals).
- **`resilience`** owns **graceful degradation and failure isolation** —
  timeouts, retries, circuit breakers, bulkheads, fallbacks. A cache **can** act
  as a fallback (serve last-known-good when the origin is down), and a cache miss
  storm can **threaten** resilience (stampede onto a struggling origin), so the
  two compose — but **caching is not resilience**. This concern owns the cache's
  read/write/invalidation behavior; whether a stale-serve-on-origin-failure is an
  accepted degradation mode is a `resilience` decision. Name the overlap; do not
  fold failure-handling policy in here.
- **`relational-data-modeling`** (and the `datastore` slot it runs on) owns the
  **system of record** — the authoritative store the cache sits **in front of**.
  The cache holds a **derived, disposable copy**; the row in the store is the
  truth. This concern never makes the cache authoritative; on any doubt the
  origin wins. Reference the store as the source of truth; do not own the schema.

This concern owns the one thing those do not state: **a cache is a deliberate,
bounded copy with an explicit invalidation/TTL policy and a named staleness
budget — every cache has an answer for how it goes stale, how it is invalidated,
what happens on a miss storm, and what is too correctness-sensitive to cache at
all.**

## Components

- **Cache-aside (lazy)** — the application checks the cache, and on a **miss**
  loads from the origin and populates the cache itself. The cache holds only
  requested keys; the application owns read-population and invalidation. The
  common default; the miss path is where stampede risk lives.
- **Read-through** — reads go **through** the cache, which loads from the origin
  on a miss transparently. The cache (or its client library) owns population, so
  the application's read path is uniform. Behaviorally close to cache-aside; the
  difference is *who* populates.
- **Write-through** — writes go **through** the cache to the origin
  **synchronously**; the cache is updated in the same operation as the store.
  Reads after a write see fresh data; write latency includes both hops. Strong
  cache↔store consistency, slower writes.
- **Write-behind (write-back)** — writes hit the cache and are flushed to the
  origin **asynchronously** later. Fast writes, batched origin load — at the cost
  of a **durability/consistency window** where the cache holds writes the store
  has not yet (data loss risk if the cache dies before flush). The
  highest-consistency-cost pattern; select it only with that window understood.
- **TTL (time-to-live)** — an expiry on each entry that bounds staleness without
  explicit invalidation: the entry is treated as gone after its TTL and reloaded.
  The simplest staleness control; the TTL value **is** the staleness budget.
- **Explicit invalidation** — evicting or updating a key when the underlying data
  changes (on write, or via an event). More precise than TTL but requires knowing
  every write path that affects the key — the hard part of caching ("there are
  only two hard things…").
- **Stampede / thundering-herd protection** — preventing many concurrent misses
  for the same hot key from all hitting the origin at once (on expiry or cold
  start). Mitigations: **single-flight / request coalescing** (one loader, others
  wait), **early/probabilistic refresh** (refresh before expiry), **jittered
  TTLs** (spread expiries), and a brief **negative cache** for known-absent keys.
- **What NOT to cache** — data that must be **always-fresh** (authorization
  decisions, balances/limits used to gate an action, anything where a stale read
  causes an incorrect side effect), **per-request unique** data with no reuse
  (caching it just wastes memory), and **highly volatile** data whose TTL would
  be so short the cache never pays back.

## Constraints

### A cache serves a stated performance NFR — no premature caching

- A cache is added to meet a **named performance target** (a latency/throughput
  NFR in the PRD) against a **real read-heavy hot path or an expensive
  computation**. The decision records *which* path/computation and *which* NFR it
  serves.
- Caching where load is trivial or no NFR is at risk is **premature optimization
  and drift** — it adds an invalidation/staleness problem for no measured gain.
  The cache must point at a target; absent one, do not cache (KISS/YAGNI).

### Every cache has an explicit invalidation/TTL and staleness policy

- Each cached dataset has a **stated invalidation policy** — a TTL, explicit
  invalidation on write, or both — and a **named staleness budget**: the maximum
  staleness a read may serve, justified as acceptable for that data.
- The **consistency trade-off is explicit**: the read/write pattern chosen
  (cache-aside / read-through / write-through / write-behind) implies a
  consistency level, and that level is recorded against the data's tolerance for
  staleness. Write-behind's durability/consistency window in particular is named
  and accepted, never stumbled into.

### Correctness-sensitive reads are not cached behind a stale copy

- Data where a stale read causes an **incorrect decision or side effect** —
  authorization/permission checks, balances or quotas that gate an action,
  anything requiring **read-your-write** correctness — is **not served from a
  cache that can be stale**. Either it is not cached, or it uses a
  strongly-consistent pattern (write-through with synchronous invalidation) whose
  freshness is proven.
- The cache is **never the system of record**: it holds a derived, disposable
  copy, and on eviction/failure the origin is the truth. Nothing of record lives
  only in the cache.

### Hot keys are protected from stampede

- A hot key's expiry or a cold start **does not** let many concurrent misses
  dogpile the origin. A stampede mitigation is in place for hot keys —
  single-flight/coalescing, early/probabilistic refresh, jittered TTLs, and/or a
  negative cache for known-absent keys — so cache behavior does not become an
  origin-overload (and, by extension, a resilience) problem.

## Drift Signals (anti-patterns to reject in review)

- A cache added with **no performance NFR it serves** and no measured hot path →
  premature caching; remove it or tie it to a target (point at the NFR)
- A cache with **no invalidation policy and no TTL** (entries never go stale or
  never refresh correctly) → state a TTL and/or explicit invalidation + a
  staleness budget
- **Stale-read-sensitive** data (authz decision, balance/quota gating an action,
  read-your-write requirement) served from a cache that can be stale → do not
  cache it, or use a proven strongly-consistent pattern
- The cache **treated as the source of truth** (data of record lives only in the
  cache; origin not authoritative on a miss/eviction) → the store is the truth;
  the cache is a disposable copy
- **Write-behind chosen** with its durability/consistency window unstated /
  unaccepted (silent data-loss risk if the cache dies before flush) → name and
  accept the window, or choose write-through
- A **hot key with no stampede protection** (every concurrent miss hits the
  origin) → add single-flight/coalescing, early refresh, jittered TTL, or a
  negative cache
- Caching **per-request-unique or trivially-cheap** data → no reuse and no
  payback; do not cache
- A cache positioned as the project's **resilience** mechanism (rather than a
  performance means) → caching ≠ resilience; record the failure-handling decision
  under `resilience` and let the cache compose as an optional fallback

## When to use

A product with a **real read-heavy hot path or an expensive computation where
some staleness is tolerable** — a frequently-read dataset behind a clear
latency/throughput NFR, an expensive aggregate/derived view recomputed on every
request, a hot lookup that dominates load. High autonomy auto-selects this
concern for such products (see `workflows/references/concern-resolution.md`). It
is composable (no slot); `areas: data, api` scope its practices to the
data-access and service layers. Compose with the **performance NFR** (the target
the cache serves), **`resilience`** (the cache may act as a fallback; failure
policy lives there), and **`relational-data-modeling`** / the **`datastore`**
slot (the system of record the cache sits in front of).

Do **NOT** select it when **correctness needs always-fresh reads** (a domain
dominated by authorization decisions, balances/quotas gating actions, or strict
read-your-write requirements where a stale read is a bug), or when **load is
trivial** and no performance NFR is at risk. Adding a cache there buys an
invalidation/staleness problem for no gain — **premature caching is a drift**
(KISS/YAGNI).

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- ADR: cache pattern + invalidation/TTL policy + named staleness budget + consistency trade-off + what is not cached
- TD: read/write pattern (cache-aside/read-through/write-through/write-behind), stampede protection on hot keys
- TEST_PLAN: invalidation/staleness behavior + stampede protection (single-flight) on a hot key

## ADR References

Record an ADR when introducing a cache: the **read-heavy hot path or expensive
computation** and the **performance NFR** it serves; the **pattern** chosen
(cache-aside / read-through / write-through / write-behind) and **why**; the
**invalidation policy + TTL** and the **named staleness budget** the data
tolerates; the **consistency trade-off** accepted (and, for write-behind, the
durability/consistency window); the **stampede protection** for hot keys; and
**what is deliberately not cached** because it must stay fresh. A material
uncertainty about whether the hot path truly needs a cache to hit the NFR is a
`tech-spike` (measure first), not a silent assumption (see
`workflows/references/concern-resolution.md`).

## Practices by activity

Agents working in any of these activities inherit the practices below via the bead's context digest.

These practices govern **the deliberate use of a cache** — its read/write
pattern, invalidation/TTL policy, staleness budget, stampede protection, and the
explicit decision of what not to cache. They do **not** restate the performance
target (that is a PRD **performance NFR** — the cache serves it), the
failure-handling policy a cache may participate in (`resilience`), or the schema
of the store the cache fronts (`relational-data-modeling` / the `datastore`
slot). A cache is always a derived, disposable copy; the origin is the truth.

## Discover

- Add a cache **only** to meet a named **performance NFR** against a **real
  read-heavy hot path or an expensive computation**. Record *which* path /
  computation and *which* NFR the cache serves. No NFR and no measured hot path
  means no cache — premature caching buys an invalidation/staleness problem for
  no gain (KISS/YAGNI).
- Before caching an expensive computation, confirm the cost is real (measured),
  not assumed; a material uncertainty is a `tech-spike`, not a silent cache.

## Frame

- Choose the read/write pattern deliberately and record **why** in the ADR:
  - **cache-aside (lazy)** / **read-through** for read-heavy data tolerant of
    bounded staleness (the difference is who populates on a miss);
  - **write-through** when reads after a write must be fresh (strong cache↔store
    consistency, slower writes);
  - **write-behind** only when write latency dominates AND the
    **durability/consistency window** (the cache holds writes the store does not
    yet — data-loss risk if the cache dies before flush) is **named and
    accepted**.
- Record the **consistency trade-off** the chosen pattern implies against the
  data's tolerance for staleness — never stumble into write-behind's window.
- Record in the ADR **what is deliberately not cached** (and why it must stay
  fresh).

## Design

- Each cached dataset has an explicit **invalidation policy** — a TTL, explicit
  invalidation on write, or both — and a **named staleness budget** (the maximum
  staleness a read may serve), justified as acceptable for that data. The TTL
  value **is** the staleness budget when TTL is the only control.
- When using explicit invalidation, identify **every write path** that affects a
  cached key and invalidate/update on each; a missed write path is a stale-read
  bug. Record the cache **keys** and their TTLs in the technical-design.
- Data where a stale read causes an **incorrect decision or side effect** —
  authorization/permission checks, balances or quotas that gate an action,
  anything needing **read-your-write** — is **not** served from a cache that can
  be stale. Either it is not cached, or it uses a strongly-consistent pattern
  (write-through with synchronous invalidation) whose freshness is proven.
- The cache is **never the system of record**: nothing of record lives only in
  the cache; on a miss, eviction, or cache failure the **origin is the truth**.

## Build

- For each hot key, ensure expiry or cold start does **not** dogpile the origin:
  apply **single-flight / request coalescing** (one loader, others wait),
  **early / probabilistic refresh** (refresh before expiry), **jittered TTLs**
  (spread expiries), and/or a brief **negative cache** for known-absent keys.
- Treat a miss storm as a real failure mode: where serving stale-on-origin-down
  is desired, record that as a `resilience` degradation decision — the cache
  composes as a fallback, it is not itself the resilience mechanism.

## Test

- Every cache **traces to a performance NFR and a real read-heavy hot path or
  expensive computation**; no cache exists without a target it serves (no
  premature caching).
- Each cached dataset has a **stated invalidation policy** (TTL and/or explicit
  invalidation) and a **named staleness budget**; no cache with entries that
  never go stale or never refresh.
- The **read/write pattern** is recorded with its **consistency trade-off**; if
  write-behind, its **durability/consistency window** is named and accepted.
- **Correctness-sensitive reads** (authz, balances/quotas gating an action,
  read-your-write) are **not** served from a stale-capable cache; verifiable that
  such data is uncached or strongly-consistent.
- The cache is **not the system of record** — on miss/eviction/failure the origin
  is authoritative; nothing of record lives only in the cache.
- **Hot keys have stampede protection** (single-flight, early refresh, jittered
  TTL, or negative cache); a hot-key expiry does not dogpile the origin.
- **What is deliberately not cached** (and why it must stay fresh) is recorded in
  the ADR.

## Cross-cutting

### Boundary with neighbors

See `concern.md` for the canonical Boundary (vs the performance NFR,
`resilience`, `relational-data-modeling` / `datastore`). The cache is a
performance/staleness mechanism — defer failure-handling policy to
`resilience` and the schema of the system of record to the data-modeling /
store neighbors.
