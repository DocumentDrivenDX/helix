# Concern: Multi-Tenancy

## Category
security

Multi-tenancy is categorized as **security**, not architecture, because its
defining failure is a **cross-tenant data leak** — one tenant reading or
mutating another tenant's data. The isolation-model choice (shared schema /
schema-per-tenant / database-per-tenant) is an architecture decision, but the
reason this concern exists and the property it must hold — *tenant isolation is
enforced on every data path* — is a confidentiality/integrity guarantee. Both
AWS (SaaS Lens) and Azure (Architecture Center) frame tenant isolation as a
non-negotiable security boundary that a shared (pooled) model makes *harder*,
not optional. The category reflects what review must protect.

## Areas
data, api

## Boundary

This concern owns **isolation between tenants** — that tenant A can never read
or write tenant B's data, on any path, and the architecture that delivers that
guarantee (which resources are shared vs dedicated). It is composable and does
**not** fill a slot.

For the family ownership table (auth / authorization-model / multi-tenancy /
security-owasp, plus the admin-console and unity-catalog neighbors), and the
ordering invariants (tenant predicate precedes permission; authn precedes
authz), see [README-auth-family.md](../README-auth-family.md).

This concern owns the one thing the rest of the family does not state: **there
is no query path that resolves a record without the tenant predicate, and
tenant identity is derived from the authenticated principal — never from a
client-supplied id alone.** Cross-tenant access is the OWASP Broken Access
Control / IDOR case `security-owasp` names at the umbrella level; this concern
is the tenant-specific, reviewer-checkable refinement.

## Components

- **Isolation model** — the chosen point on the isolation spectrum, recorded in
  an ADR. The spectrum (Azure: shared → isolated; AWS: pool → bridge → silo):
  - **Shared schema, tenant-discriminator column** (pool): one set of tables, a
    `tenant_id` on every tenant-owned row. Highest density / lowest cost;
    weakest physical isolation; the model where a missing predicate leaks data.
  - **Shared schema + row-level security (RLS)**: the database itself enforces
    the `tenant_id` predicate via a session-scoped policy, so a forgotten
    application-side `WHERE tenant_id` cannot leak. Defense in depth on the pool
    model; requires the tenant context to be propagated into the DB session.
  - **Schema-per-tenant**: one database, a schema namespace per tenant.
    Stronger isolation and per-tenant schema customization; schema-migration
    fan-out grows with tenant count.
  - **Database-per-tenant** (silo): a dedicated database (or stamp) per tenant.
    Strongest isolation, per-tenant backup/restore and encryption keys, smallest
    blast radius; highest cost and operational fan-out; needs automated
    provisioning.
  - **Bridge / vertically-partitioned**: mixed — pooled for most tenants,
    siloed for tenants with regulatory or noisy-neighbor requirements.
- **Tenant context** — the resolved tenant identity for the current
  request/unit of work, **derived from the authenticated principal** (session /
  JWT claim), threaded through every layer down to data access. Not a parameter
  a caller may set freely.
- **Tenant-scoped data access** — every read and write of tenant-owned data
  carries the tenant predicate. Ideally enforced in **one place** (a scoped
  repository, query helper, RLS policy, or per-tenant connection) so no
  individual call site can forget it.
- **Tenant resolution** — mapping an incoming request to its tenant (from the
  principal's claim, a subdomain, a path segment, or a tenant→deployment lookup
  table for siloed/sharded deployments) and rejecting requests that resolve to
  no tenant or to a tenant the principal does not belong to.
- **Per-tenant configuration & limits** — tenant-scoped settings, feature
  flags, quotas, and rate limits; the mechanism for noisy-neighbor mitigation
  and per-tenant customization **without** forking infrastructure or schema.
- **Tenant lifecycle** — provisioning (bootstrap a new tenant's storage /
  schema / database, ideally automated) and offboarding (export and delete a
  tenant's data, decommission its dedicated resources).

## Constraints

### Every data access is tenant-scoped — no unscoped path exists

- Every query that touches tenant-owned data carries the **tenant predicate**.
  There is **no query path that resolves a record by id, slug, name, or any
  other identifier without also constraining it to the caller's tenant**. A
  lookup like `findBySlug(slug)` that omits the tenant is a cross-tenant leak
  even if a downstream authorization check passes.
- Prefer enforcing the predicate in **one choke point** (a tenant-scoped
  repository / query layer, database RLS, or a per-tenant connection) over
  trusting every call site to remember it. Isolation must be a property of the
  data-access path, not of careful per-query discipline.

### Tenant identity comes from the principal, never the client alone

- The tenant for a request is **derived from the authenticated principal** (the
  session or token claim), or from a server-validated mapping. A
  client-supplied tenant id, header, or path segment is **never trusted on its
  own** to grant access — at most it is validated *against* the principal's
  tenant.
- A request that resolves to no tenant, or to a tenant the principal does not
  belong to, is **rejected** (404/403), not silently served from a default or
  the first matching row.

### The isolation model is chosen deliberately and recorded

- The point on the isolation spectrum is an explicit decision recorded in an
  ADR, justified against isolation strength, cost/density, noisy-neighbor risk,
  per-tenant backup/restore and compliance needs, blast radius, and operational
  fan-out — not defaulted implicitly.
- In a **pooled** (shared-schema) model the isolation burden is **higher**, not
  lower: sharing infrastructure increases the chance of cross-tenant access, so
  enforcement must be more diligent, not relaxed.

### Cross-tenant isolation is tested, not assumed

- A **negative guard test exists**: tenant A, properly authenticated, cannot
  read or mutate tenant B's records — by id, slug, or any enumeration — and
  receives a not-found/forbidden, not B's data. This is the guard branch the
  verification evidence gate requires for the isolation acceptance criterion.

### Tenant lifecycle is a first-class flow

- Provisioning a new tenant (its storage/schema/database and first owner) is
  repeatable and, beyond a handful of tenants, **automated** — manual per-tenant
  setup does not scale and drifts.
- Offboarding can **export and delete** a single tenant's data without
  affecting others.

## Drift Signals (anti-patterns to reject in review)

- A data-access path that resolves a record by id/slug/name **without a tenant
  predicate** → cross-tenant leak; scope the query to the principal's tenant
- Tenant id taken from a **client-supplied** header/path/body and trusted to
  grant access → derive tenant from the authenticated principal; validate any
  client value against it
- Tenant scoping written **ad hoc per query** with no choke point → a call site
  will eventually forget it; centralize in a scoped repository / RLS / per-tenant
  connection
- An **authorization** check standing in for isolation (permission verified on a
  record that belongs to another tenant) → the tenant predicate must hold first;
  authorization is intra-tenant
- **No negative test** that tenant A cannot reach tenant B's data → add the
  cross-tenant guard test
- Isolation model **defaulted implicitly** with no ADR weighing cost vs
  isolation vs blast radius → record the decision
- **Per-tenant schema/column customization or forked infrastructure** for one
  tenant → use per-tenant configuration / feature flags / a custom-data table;
  forking inhibits scale, testing, and updates
- Manual, un-automated per-tenant provisioning at scale → automate; track each
  tenant's deployment/schema version

## When to use

Any **multi-tenant / SaaS / account-isolated product** — anything where
multiple tenants (customers, organizations, accounts, workspaces) share the
system and one tenant's data must never be reachable by another. High autonomy
auto-selects this concern for such products (see
`workflows/references/concern-resolution.md`). Do **not** select it for
single-tenant or single-user tools, anonymous public sites, or libraries with
no tenant concept. It is composable (no slot); `areas: data, api` scope its
practices to the data-access and service layers. Compose with **`auth`**
(authn/identity — who you are, distinct from isolation), **`authorization-model`**
(what you may do within a tenant), **`security-owasp`** (cross-tenant access is
Broken Access Control / IDOR), and **`domain-driven-design`** (tenant is part of
the model and the aggregate's identity).

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- ADR: tenant isolation model (shared-schema/+RLS/schema-per-tenant/db-per-tenant/bridge) + tenant resolution + lifecycle
- TD: tenant-context propagation from the principal; tenant-scoped data-access choke point
- DATA_DESIGN: tenant discriminator + scoping (or per-schema/per-db isolation)
- TEST_PLAN: negative cross-tenant guard — tenant A cannot reach tenant B by id/slug

## ADR References

Projects record an ADR when choosing the isolation model (shared-schema +
discriminator / + RLS / schema-per-tenant / database-per-tenant / bridge),
justified against isolation strength, cost/density, noisy-neighbor risk,
per-tenant backup/restore and compliance, blast radius, and operational fan-out;
and when defining tenant resolution (claim / subdomain / path / tenant→deployment
mapping) and the tenant lifecycle (provisioning + offboarding).
