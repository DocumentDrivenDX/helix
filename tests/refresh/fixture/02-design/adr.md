---
ddx:
  id: ADR-001
classification: INCOMPLETE
---

# ADR-001: Sample Decision

| Date | Status | Deciders |
|------|--------|----------|
| 2026-01-15 | Accepted | Architecture team |

## Context

The system needs to choose a caching strategy for frequently accessed data.

## Decision

We will use Redis as the primary caching layer with in-memory fallback.

## Alternatives

- Memcached: simpler but less flexible
- In-memory only: fast but limited by process memory

## Consequences

- Improved latency for read operations
- Added dependency on Redis infrastructure
