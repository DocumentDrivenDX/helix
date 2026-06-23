# Practices: Caching Strategy

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
