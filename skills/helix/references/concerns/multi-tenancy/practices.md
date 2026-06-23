# Practices: Multi-Tenancy

These practices govern **isolation between tenants** — that no code path lets
one tenant reach another's data. For the family ownership table (auth /
authorization-model / multi-tenancy / security-owasp) see
[README-auth-family.md](../README-auth-family.md). Their one job is to make the
**cross-tenant leak** unreachable and **reviewer-checkable**. Each MUST/SHOULD
below is written so a reviewer can confirm or refute it against the diff and
the running system.

## Choose and record the isolation model (Frame / Design)

- Record the **isolation model** in an ADR before building: shared-schema with
  a tenant-discriminator column, shared-schema + row-level security (RLS),
  schema-per-tenant, database-per-tenant, or a bridge (mixed). The ADR MUST
  justify the choice against: isolation strength, cost/tenant density,
  noisy-neighbor risk, per-tenant backup/restore and compliance, blast radius,
  and operational fan-out.
- Identify, during design, the **tenant context source** (which authenticated
  claim or server-validated mapping yields the tenant) and the **single choke
  point** where the tenant predicate is enforced (scoped repository / query
  helper / RLS policy / per-tenant connection).
- In a pooled (shared-schema) model, treat isolation as a **higher** burden, not
  a relaxed one — sharing infrastructure increases cross-tenant risk.

## Tenant context is derived from the principal (Implementation)

- Tenant identity for a request **MUST** be derived from the authenticated
  principal (session / token claim) or a server-validated mapping. It **MUST
  NOT** be taken from a client-supplied id, header, path, or body and trusted on
  its own to grant access.
- A client-supplied tenant value (subdomain, path segment) **MAY** be used only
  after being **validated against** the principal's tenant; a mismatch is
  rejected (403/404).
- A request that resolves to **no tenant**, or to a tenant the principal does
  not belong to, **MUST** be rejected — never served from a default tenant or
  the first matching row.
- The resolved tenant context **MUST** be threaded to the data-access layer
  (and, for RLS, into the database session) — not re-derived ad hoc deep in the
  stack.

## Every data access is tenant-scoped (Implementation)

- Every read and write of tenant-owned data **MUST** carry the tenant predicate.
  **There MUST be no query path that resolves a record by id, slug, name, or any
  other identifier without also constraining it to the caller's tenant.** A
  `findBySlug(slug)` / `getById(id)` that omits the tenant is a defect even if a
  later authorization check passes.
- The tenant predicate **SHOULD** be enforced in **one place** — a tenant-scoped
  repository, a mandatory query filter, an RLS policy, or a per-tenant
  connection — so no individual call site can forget it. Hand-written
  `WHERE tenant_id = ?` repeated at every call site is a drift signal: a future
  query will omit it.
- The tenant predicate **MUST** hold **before** any authorization check is
  meaningful. A permission verified on a record belonging to another tenant is
  still a cross-tenant leak.
- Enumeration/listing endpoints **MUST** be scoped so they return only the
  caller's tenant's rows — counts, search, exports, and aggregates included.

## Cross-tenant isolation is tested (Verification)

- A **negative guard test MUST exist**: tenant A, authenticated as a legitimate
  member of A, attempts to read and to mutate a tenant B record (by id, by slug,
  and via any list/enumeration) and **receives not-found/forbidden — never B's
  data**. This is the guard branch the `verification` evidence gate requires for
  the isolation acceptance criterion; happy-path-green is not done.
- The test **MUST** drive the real data-access path (the choke point), not a
  unit stub that hard-codes the tenant — otherwise it proves nothing about the
  query that ships.
- For an RLS model, a test **SHOULD** confirm that a query issued **without**
  the tenant session context returns zero rows (the database enforces it), so a
  forgotten application-side predicate cannot leak.

## Per-tenant configuration and noisy-neighbor (Implementation)

- Per-tenant settings, feature flags, quotas, and rate limits **MUST** be data
  (tenant-scoped configuration), not forked code or per-tenant schema columns.
- Tenant-level customization **MUST NOT** be implemented by adding columns or
  tables for one tenant, or by forking infrastructure for one tenant — these
  inhibit scale, testing, and updates. Use a tenant-config table / custom-data
  table / feature flags instead.
- Where the pooled model is susceptible to noisy neighbors, per-tenant
  rate-limiting/throttling or quotas **SHOULD** bound one tenant's impact on
  others.

## Tenant lifecycle (Implementation)

- Provisioning a new tenant (its storage/schema/database and first owner)
  **MUST** be repeatable; beyond a handful of tenants it **SHOULD** be automated
  (infrastructure-as-code / a provisioning routine), and the per-tenant
  schema/version **SHOULD** be tracked.
- Offboarding **MUST** be able to export and delete a single tenant's data
  without affecting other tenants.

## Quality Gates

- Isolation model recorded in an ADR with its trade-off justification — not
  defaulted implicitly.
- **No unscoped data-access path**: verifiable in review that every query
  touching tenant-owned data carries the tenant predicate, enforced at a single
  choke point; no `findBy<X>` resolves a record without the tenant constraint.
- Tenant context is **derived from the authenticated principal**; no path trusts
  a client-supplied tenant id alone, and an unresolved/mismatched tenant is
  rejected.
- A **cross-tenant negative guard test** exists and ran green against the real
  data-access path: tenant A cannot read or mutate tenant B's records by id,
  slug, or enumeration (and, under RLS, a context-less query returns zero rows).
- Per-tenant differences are **configuration/data**, not forked schema or
  infrastructure.
- Tenant provisioning is repeatable (automated at scale) and a single tenant's
  data can be exported and deleted without affecting others.
