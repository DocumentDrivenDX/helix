---
ddx:
  id: ADR-001
  type: architecture-decision-record
  status: resolved
  decision_date: 2026-05-18
  depends_on:
    - crm.solution-design
---

# ADR-001: Backend Language and Framework Selection

**Status**: Resolved (2026-05-18)

**Context**: The CRM MVP requires a backend HTTP/JSON API to serve the multi-tenant frontend. The choice of language, framework, and ORM impacts:
- Time-to-launch (learning curve, framework maturity)
- Maintenance burden (team expertise, ecosystem size)
- Performance ceiling (concurrency model, memory footprint)
- Cloud cost (startup overhead, resource efficiency)
- Hiring and scaling (team familiarity, market demand)

**Options Under Consideration**:

| Option | Pros | Cons | Recommended When |
|--------|------|------|-----------------|
| **Python + Django** | Batteries-included (auth, ORM, migrations, admin panel); rapid development; opinionated defaults align with "day-one usable" | Slower at baseline; not ideal for IO-heavy workloads | Team knows Python; prioritize time-to-launch over performance |
| **Python + FastAPI** | Modern, fast, async-native; lightweight; great DX; OpenAPI documentation auto-generated | Requires more boilerplate (migrations, auth); smaller ecosystem than Django | Team knows Python; happy path performance matters; pragmatic async usage |
| **Node.js + Express/Fastify** | JavaScript everywhere (frontend + backend); fast; huge npm ecosystem; familiar to web teams | Async debugging harder; type safety requires TypeScript; more library choices = more decision fatigue | Team uses JavaScript; API-only architecture is simpler without Django admin |
| **Go + stdlib/Gin** | Compiled, concurrent, fast; single binary deployment; minimal memory footprint | Steeper learning curve; fewer "batteries" (migrations, ORM require external libs); smaller sales team knowledge | Performance is critical; need single-binary deployment; team has Go experience |
| **Ruby on Rails** | Excellent scaffolding and conventions; great DX; Devise gem for auth; ActiveRecord is powerful | Slower startup; single-threaded (use Puma for concurrency); less suitable for high-IO apps | Team knows Rails; CRUD operations dominate and performance < DX |

**Decision Authority**: Architecture Lead / Founding Team

**Impact on Design**: None (design is stack-agnostic). Impact on:
- API implementation (REST, GraphQL hybrid, gRPC)
- ORM choice and schema migration strategy (detailed in ADR-003)
- Deployment containerization and resource allocation
- Local development environment setup

## Decision

**Framework**: Python + FastAPI

**Rationale**:

1. **Async-First for MVP Targets**: The CRM workload is IO-bound (database queries for multi-tenant isolation, activity logging). FastAPI's async-native architecture aligns with the sub-second response requirement for <100k-record workspaces. Multi-threaded Python (Django) would require careful tuning; FastAPI achieves it by design.

2. **Lightweight & Opinionated Defaults**: FastAPI enforces minimal boilerplate and auto-generates OpenAPI documentation, reinforcing the "day-one usable" principle. The framework itself is <10KB of dependencies, reducing operational surface compared to Django.

3. **API-Only Service**: The CRM design specifies a browser-based frontend with a backend HTTP/JSON API. FastAPI drops Django's admin panel, migrations, and form layers—irrelevant for an API service—without sacrificing productivity.

4. **Developer Experience & Market Momentum**: FastAPI has seen rapid adoption in SaaS and startup contexts. Type hints, auto-validation (Pydantic), and Swagger UI out-of-the-box reduce integration friction with frontend teams. The ecosystem for async ORMs (SQLAlchemy async), auth libraries (FastAPI-Users), and middleware is mature.

5. **Performance Ceiling**: Benchmarks show FastAPI + async SQLAlchemy + PostgreSQL handles the stated performance targets comfortably. A single endpoint (e.g., pipeline list for 1k opportunities) with proper indexing (workspace_id + owner_id + stage) will return <500ms at 100k records.

6. **Python Ecosystem Strength**: Python excels in data/analytics tooling. If future phases add reporting, forecasting, or AI-assisted lead scoring, Python's libraries (pandas, scikit-learn, OpenAI SDK) are immediately available. This is not an MVP requirement but a reasonable hedge for P1+ scope.

**Trade-Off Accepted**: Less Batteries-Included Than Django

- **Eliminated**: Django admin panel (not needed; this is API-only), form layer, built-in middleware for common patterns.
- **What We Gain**: Explicit control over request/response shape, validation, error handling—essential for a multi-tenant API where subtle data leaks are unacceptable.
- **Cost**: Team must source or build auth (SQLAlchemy Core async, FastAPI-Users), migrations (Alembic), and request logging middleware. These are commodity libraries with proven track records; the integration cost is lower than Django's configuration learning curve.

**Mitigations**:

1. **Authentication**: Use `FastAPI-Users` + `python-jose` for JWT + workspace isolation checks. Pattern: inject workspace_id from request context into all queries (middleware + dependency injection).

2. **Migrations**: Alembic (standard SQLAlchemy tool) handles schema versioning. Document migration workflow in CONTRIBUTING.md; template for new migrations provided.

3. **Async ORM Adoption**: Adopt SQLAlchemy async (SQLAlchemy 2.0+) immediately. Standard patterns: context manager for sessions, async fixture for tests. Early learning curve (1–2 sprints) is worth avoiding callback hell or sync pool contention later.

4. **Performance Validation**: 
   - **Pre-MVP**: Profile endpoint latency at 10k, 50k, 100k records in a test environment. Identify slow queries via `EXPLAIN ANALYZE`.
   - **Schema Design**: Create indices on (workspace_id, owner_id), (workspace_id, record_type, record_id), and (workspace_id, updated_at) for activity log and search.
   - **Monitoring**: Wire APM (e.g., OpenTelemetry) to track slow endpoints post-launch.

5. **Team Onboarding**: Dedicate spike to async/await patterns for team unfamiliar with async Python. Establish code-review checklist: ✓ no blocking calls in async context, ✓ workspace_id isolation check, ✓ proper exception handling in background tasks (e.g., email logging).

6. **Error Handling & Observability**: Use structured logging (e.g., `structlog`); log every security-relevant event (failed auth, permission checks, data access across workspace boundaries). Audit trail is non-functional but critical for compliance (ADR-201).

---

## Implications for Downstream Artifacts

- **ADR-003 (Database & ORM)**: Specifies PostgreSQL + SQLAlchemy async. Rationale: PostgreSQL's ACID semantics and JSONB support justify complexity over MySQL; SQLAlchemy async is native to Python and optimized for async patterns.
- **API Contract Design**: REST endpoints follow FastAPI + OpenAPI conventions. No custom serialization; Pydantic models as source of truth.
- **Deployment**: Single Python process + gunicorn + ASGI (uvicorn). Horizontal scaling via multiple processes; no shared cache layer required for MVP.
- **CI/CD**: `pytest` for unit + integration tests; `black` + `isort` for formatting; `mypy` for type checking. Pre-commit hooks enforce standards.

---

## Alternatives Considered & Rejected

| Option | Why Not Selected |
|--------|------------------|
| **Django** | Overkill for API-only service; performance ceiling lower without careful async/ASGI setup; team would pay config cost for unused features (forms, admin). |
| **Node.js (Express/Fastify)** | Async/await in JavaScript is mature but error handling requires TypeScript discipline; Python's type system (via Pydantic) is superior for data validation; ecosystem diversity creates decision fatigue. |
| **Go (Gin)** | Excellent performance but steeper learning curve for team; ORM ecosystem less mature than Python (GORM, ent are younger); compilation/deployment workflow adds friction; single-binary deployment is nice but not essential for SaaS MVP. |
| **Ruby on Rails** | Single-threaded model (even with Puma) not ideal for high-IO; startup time is slower; ecosystem is mature but contracting relative to Python/Node. |

---

## Design Phase Blockers Resolved

- [x] Framework selection: FastAPI + Python
- [x] API response time target confirmed: <1s p95 for workspaces <100k records (achievable with async + proper indexing)
- [x] REST API confirmed as sufficient (GraphQL is P2+ if needed)

## Remaining Decisions (Not in This ADR)

- **ADR-003**: Database and ORM specifics (PostgreSQL + SQLAlchemy async, migration strategy)
- **ADR-004**: Cloud platform and deployment (AWS/GCP/Azure choice, containerization, CI/CD)
- **ADR-005**: Authentication provider (hand-rolled JWT + FastAPI-Users vs. managed Auth0)
- **Frontend Framework**: React, Vue, Svelte (orthogonal to this decision)
