---
ddx:
  id: ADR-003
  type: architecture-decision-record
  status: resolved
  decision_date: 2026-05-18
  depends_on:
    - crm.solution-design
    - ADR-001
---

# ADR-003: Database and ORM Selection

**Status**: Resolved (2026-05-18)

**Context**: The CRM requires durable, ACID-compliant storage for workspace data (contacts, accounts, opportunities, activities, users). The choice of database and ORM impacts:
- Schema migration velocity (migrations are frequent in early products)
- Query performance at scale (200k+ records per workspace)
- Audit trail reliability (GDPR compliance requires immutable change logs)
- Operational simplicity (managed cloud DB vs. self-hosted)
- Backup and disaster recovery complexity

**Options Under Consideration**:

| Option | Pros | Cons | Recommended When |
|--------|------|------|-----------------|
| **PostgreSQL + SQLAlchemy (Python)** | Robust ACID semantics; JSONB for flexible fields; UUID native; great for audit logs; open-source | One more vendor to operate (vs. managed); setup overhead | Python backend chosen; need advanced SQL features (arrays, JSONB, full-text search) |
| **PostgreSQL + Prisma (Node.js)** | Auto-migrations from schema; type-safe query builder; excellent DX; web-friendly | Slightly less mature than SQLAlchemy; Prisma-specific vendor lock-in | Node.js backend; want migrations to be a first-class API, not hand-written SQL |
| **PostgreSQL + GORM (Go)** | Fast, compiled, minimal overhead; excellent for concurrency | Less automatic than Prisma; migration tooling less polished | Go backend; performance critical; team comfortable with explicit code over convention |
| **PostgreSQL + ActiveRecord (Rails)** | Convention over configuration; migrations are first-class; excellent Rails ecosystem | Rails-specific; harder to use outside Rails | Rails backend chosen; team comfortable with convention-driven approach |
| **MySQL 8.0 + Sequelize (Node.js)** | Commodity DB; Sequelize is familiar; lower operational overhead | JSON handling less rich than PostgreSQL; UUID support is newer; audit trail logging is more complex | Simpler operations story is preferred over PostgreSQL features; team knows MySQL well |
| **Firestore / Cloud Datastore (NoSQL)** | Serverless; auto-scaling; no ops; Google-managed | Denormalization required (breaks our normalized schema); audit trail is messy in document DB; harder to implement referential integrity | Team prioritizes zero-ops over schema flexibility; willing to redesign for NoSQL (not recommended given PRD audit requirements) |

## Decision

**Database**: PostgreSQL 15 (AWS RDS recommended for MVP)

**ORM**: SQLAlchemy 2.0+ (async mode via `sqlalchemy.ext.asyncio`)

**Managed vs. Self-Hosted**: Managed (AWS RDS PostgreSQL or equivalent cloud provider)

**Backup Strategy**: Daily automated snapshots with 30-day retention; cross-region backup enabled

**Migration Tooling**: Alembic (SQLAlchemy-native migration framework)

**Audit Log Implementation**: App-level activity table with triggers for critical updates (see rationale below)

### Rationale

**1. PostgreSQL + SQLAlchemy Alignment with ADR-001**

ADR-001 selected Python + FastAPI for the backend. SQLAlchemy is the de facto standard async ORM for Python and integrates seamlessly:
- SQLAlchemy 2.0+ provides async support via `sqlalchemy.ext.asyncio`
- Native async/await patterns align with FastAPI's concurrency model
- Type hints + Pydantic validation match FastAPI's design philosophy
- Proven in production SaaS applications; no stability risk

**2. PostgreSQL Justification**

PostgreSQL provides critical advantages for the CRM workload:
- **ACID Semantics**: Multi-tenant isolation requires serializable transaction support; PostgreSQL's MVCC is production-grade
- **JSONB Support**: Flexible metadata (custom fields, nested structures) without schema redesign; queries via `@>`, `->` operators
- **Array Types**: Perfect for activity tags, record IDs in audit logs; no normalization overhead
- **Full-Text Search**: Future phases (lead scoring, search filters) benefit from built-in FTS; MySQL lacks native support
- **UUID Native**: `uuid-ossp` extension or `gen_random_uuid()` eliminates GUID library dependency
- **Advisory Locks**: For distributed locking if multi-region failover is added post-MVP

Trade-off accepted: PostgreSQL is more complex to operate than MySQL, but managed RDS eliminates most DevOps burden.

**3. Async ORM Choice (SQLAlchemy over Django ORM)**

Rejecting Django ORM (requires Django framework; we use FastAPI):
- SQLAlchemy is framework-agnostic; works with FastAPI's lightweight model
- Async mode critical: standard Django ORM is not async-friendly; sync pool would bottleneck under load
- Alembic migrations are hand-written (explicit control for complex schemas), not auto-generated (better for audit compliance)

**4. Managed RDS for MVP Simplicity**

Rationale for RDS:
- MVP timeline prioritizes launch over ops expertise
- RDS handles replication, backups, patching; we focus on schema and queries
- Cost impact minimal at MVP scale (<100GB data); single-instance RDS is ~$30/month for 15GB storage, t4g.medium compute
- Multi-region failover and read replicas are P2+ (not MVP scope)

Backup strategy:
- Daily automated snapshots (RDS default)
- 30-day retention (sufficient for GDPR compliance audits)
- Cross-region backup enabled (disaster recovery; <1 hour RTO acceptable for MVP)

**5. Migration Strategy: Alembic + Explicit Hand-Written Migrations**

Chosen: **Alembic** (hand-written, explicit migrations)

Why not auto-migrations (Prisma-style)?
- Hand-written migrations force explicit schema review (compliance requirement)
- Audit trail: each migration is a git commit with rationale (required for regulatory audits)
- Data migrations (e.g., backfill `updated_by` during auth refactor) are explicit, testable
- Alembic integrates with SQLAlchemy; no vendor lock-in (Prisma is Node-only)

Process:
```bash
# Generate migration skeleton (inspects current models)
alembic revision --autogenerate -m "add user.email_verified"

# Edit generated migration (always review before merge)
# Apply in development
alembic upgrade head

# Production deployment: run during blue-green transition
# (zero-downtime via online schema migration tools post-MVP if needed)
```

**6. Audit Log Implementation: Dual-Layer (App + Database Triggers)**

Chosen: **Hybrid approach**
- **App-level activity table** (primary): Every user action (create contact, update account) logged as `Activity` record with `user_id`, `workspace_id`, `action`, `entity_type`, `entity_id`, `changes` (JSONB)
- **Database triggers** (secondary): On `accounts`, `opportunities`, `contacts` tables, auto-populate `updated_at` and `updated_by` for compliance audits

Why both?
- App-level logs are queryable, filterable, and human-readable (UI dashboards)
- Database triggers ensure immutability (no app-level tampering possible)
- Compliance audits require both layers: business event trail + database change trail

**7. Scope Constraints (MVP)**

- No sharding, partitioning, or multi-region replication (single PostgreSQL instance sufficient for <1M records per workspace)
- No data archival or pruning (full retention for audit compliance)
- Connection pooling via PgBouncer (post-MVP if connection limits hit; not needed at MVP load)

### Integration with ADR-001

ADR-001 specified:
> "ADR-003 (Database & ORM): Specifies PostgreSQL + SQLAlchemy async. Rationale: PostgreSQL's ACID semantics and JSONB support justify complexity over MySQL; SQLAlchemy async is native to Python and optimized for async patterns."

✅ This ADR fully implements that specification.

### Open Questions Resolved

- ✅ **Managed vs. Self-Hosted?** → RDS (managed) for MVP; self-hosted evaluation in Phase 2 if cost is blocker
- ✅ **RPO Requirement?** → Daily snapshots (24-hour RPO); sufficient for MVP, lower-cost than PITR
- ✅ **Compliance Audits?** → Yes (GDPR article 17, deletion audit trail). Implemented via app-level activity table + database triggers
- ✅ **Zero-Downtime Migrations?** → Out of scope for MVP. Blue-green deployment handles schema compatibility; multi-version support via Alembic branches (Phase 2)
- ✅ **Data Volume Growth?** → Projected <1M records in first 12 months; single-instance RDS t4g.large sufficient through Series A

### Remaining Decisions (Not in This ADR)

- **ADR-004**: Cloud platform and containerization (AWS/GCP/Azure choice)
- **ADR-005**: Authentication provider (hand-rolled JWT vs. Auth0)
- **Connection Pooling Strategy** (PgBouncer vs. application-level pooling; post-MVP)
- **Read Replicas** (analytics workload isolation; P2+)

