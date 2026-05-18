---
ddx:
  id: ADR-001
  depends_on:
    - recipe-app-prd
  status: draft
---

# ADR-001: Use SQLite for Initial Database

| Date | Status | Deciders | Related | Confidence |
|------|--------|----------|---------|------------|
| 2026-05-01 | Proposed | Product, Engineering | FEAT-recipe-share | Medium |

## Context

| Aspect | Description |
|--------|-------------|
| Problem | Need to select initial database for recipe storage (users, recipes, ratings, comments) |
| Current State | No database selected; feature specs assume persistence layer |
| Requirements | Support ≤ 100 concurrent users; launch MVP within 6 months; minimize ops overhead |
| Decision Drivers | Simplicity vs. scalability; infrastructure cost; engineering team familiarity |

## Decision

We will use SQLite for the initial launch, with a planned migration to PostgreSQL post-launch when concurrent user demand exceeds SQLite's write-lock constraints.

**Key Points**: SQLite requires zero devops | Single-file backup | Free tier databases support SQLite | Easy migration to Postgres later

## Alternatives

| Option | Pros | Cons | Evaluation |
|--------|------|------|------------|
| PostgreSQL | Scales to millions of users; multi-writer safe; proven in production | Requires managed DB service ($10-50/mo); more complex initial setup | Rejected: overspend for MVP |
| Firebase/Firestore | Serverless; auto-scales; no ops | Vendor lock-in; limited query flexibility; data export friction | Rejected: lock-in risk for future |
| **SQLite** | Zero ops; free; perfect for MVP; single-file backup | Single-writer (locks on write); not suitable for concurrent edits at scale | **Selected: minimum viable for ≤100 users, clear upgrade path** |

## Consequences

| Type | Impact |
|------|--------|
| Positive | No database service cost; faster initial development; entire DB in single file; easy testing |
| Negative | Write operations serialize (queuing at contention points); max ~10-20 writes/sec; not suitable for high-concurrency workloads |
| Neutral | Single database instance per environment (dev, staging, prod); backups via file copy |

## Risks

| Risk | Prob | Impact | Mitigation |
|------|------|--------|------------|
| Write contention causes timeouts | Medium | Medium | Monitor write latency in staging; plan Postgres migration trigger if ≥ 5 concurrent writes observed |
| Database file corruption on disk full | Low | High | Implement disk space monitoring; plan recovery procedure; documented in runbook |
| Single-server failure loses all data | Low | High | Daily backups to S3; recovery RTO ≤ 1 hour |

## Validation

| Success Metric | Review Trigger |
|----------------|----------------|
| 100 concurrent users without write-timeout errors | Reconsider when user load exceeds 200 concurrent |
| Write latency p99 < 200ms | Reconsider when p99 exceeds 500ms |
| Zero corruption incidents in first 6 months | Reconsider if corruption occurs |

## Supersession

- **Supersedes**: None
- **Superseded by**: None (planned: ADR-002 or similar for Postgres migration)

## Concern Impact

No active project concerns overridden. This is a database selection decision, not a practice override.

## References

- PRD §Technical Context: Database requirement
- FEAT-recipe-share: Feature depending on persistent storage
- Planned: Migration guide (TBD) for upgrading to PostgreSQL

## Review Checklist

- [x] Context names specific problem
- [x] Decision statement is actionable
- [x] At least two alternatives evaluated
- [x] Each alternative has concrete pros and cons
- [x] Selected option's rationale explains why it wins
- [x] Consequences include both positive and negative
- [x] Negative consequences have mitigations
- [x] Risks specific with probability and impact
- [x] Validation section defines success metrics
- [x] Review triggers define reconsideration conditions
- [x] Concern impact complete
- [x] Consistent with governing PRD requirements
