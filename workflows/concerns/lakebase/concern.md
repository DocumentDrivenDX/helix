# Concern: Lakebase (managed Postgres on Databricks)

## Category
tech-stack

## Areas
data, api, infra

## Slot
datastore

## Platform

**Platform-specific (Databricks).** Lakebase is Databricks' managed PostgreSQL
service (Lakebase Autoscaling "projects"). It is the `datastore` filler of the
`databricks-apps` profile in `slots.yml`. Platform facts below are as of
2026-10-31; re-verify numbers before a design depends on them.

## Boundary

This concern owns **the transactional Postgres store an app keeps its own
state in on Databricks**: the project/branch/compute model, how environments
map to branches, high availability and recovery, connection credentials, and
which data belongs in Lakebase rather than Unity Catalog. It must not duplicate
its neighbors:

- **`relational-data-modeling`** owns schema design, keys, constraints,
  normalization, and migrations as a practice. This concern owns only what
  Lakebase changes about running them.
- **`databricks-apps`** owns attaching Lakebase to an app as a resource, the
  injected `PG*` variables, `valueFrom`, the app service principal, and the
  on-behalf-of `postgres` scope. This concern owns what the app does with the
  connection.
- **`unity-catalog`** owns governance of lakehouse data, including tables
  synced into Lakebase. Governed firm data is read through Unity Catalog; this
  concern does not make Lakebase a second copy of it.
- **`language-runtime`** (`python-uv`) owns the driver and pool libraries.

## Components

- **Project**: the unit of a Lakebase database; Postgres 16, 17 (default), or
  18 chosen at creation. Extensions include `vector` (pgvector).
- **Branches**: copy-on-write children of a parent branch, isolated while
  sharing storage. Every project has a default `production` branch; one branch
  per project can be **protected** (no delete, reset, or archive). A child can
  be **reset** to its parent's current state (a full overwrite; not for a root
  branch or a branch with children). Branches can **expire** (1 hour to 30 days,
  or never); an expiring branch is billed only for changed data.
- **Computes**: each branch has its own endpoint, scaled independently, with
  autoscaling and scale-to-zero (resumes in a few hundred milliseconds; session
  state such as temp tables, prepared statements, and advisory locks is lost on
  suspend).
- **High availability**: 1 primary plus 1–3 secondaries in different
  availability zones with automatic failover; requires scale-to-zero off.
  Committed transactions are durable in the storage layer before
  acknowledgement, so failover preserves them. Readable secondaries are exposed
  through a `-ro` connection string.
- **Recovery**: instant restore creates a branch from any point in the history
  window; disaster recovery replicates to a secondary workspace in another
  region with manual failover.
- **Credentials**: OAuth tokens from `generate_database_credential` expire after
  one hour (checked at login only); a non-owner identity needs a Postgres role
  created through the `databricks_auth` extension; native passwords are off by
  default.
- **Synced tables**: Unity Catalog tables synced into Lakebase for low-latency
  reads.

## Constraints

### Lakebase holds the app's own state, not a copy of governed data
- Sessions, drafts, workflow state, locks, job queues, and app-owned content
  live here. Data mastered elsewhere (governed lakehouse tables, an identity or
  entitlement source) is referenced by id and read live, or synced read-only
  from Unity Catalog; it is never cached as a second source of truth.
- Entitlement decisions are never answered from Lakebase rows the app wrote.

### Environments are branches
- Production is the protected `production` branch with high availability on.
- QA and dev are child branches reset from their parent before a release
  rehearsal; pull-request and CI databases are expiring branches.
- A branch of production contains production data. Non-production branches
  holding regulated or confidential data are created from masked data or kept
  in a separate project, and access to them is restricted.

### Connections are credentialed per connection
- Mint a fresh OAuth credential for each new pooled connection; never store a
  long-lived password or token in configuration.
- Pool connections and assume a pooled connection may meet a resumed or
  failed-over compute: retry connect, and do not depend on session-level state
  surviving.

### Schema changes are versioned
- Migrations are versioned in the repository and run once per release,
  expand-then-contract, so old and new app versions run side by side; a pull
  request runs its migrations against its own branch first.

### Availability is configured, not assumed
- Production that claims zero data loss on node failure and automatic failover
  runs with high availability (scale-to-zero off) and at least two secondaries
  when the `-ro` endpoint must survive a failover.
- A recovery-point claim for a region loss names the DR configuration and its
  manual failover runbook.

## Drift Signals (anti-patterns to reject in review)

- Durable app state in instance memory, local disk, or append-only Delta tables
  for read-modify-write data → Lakebase
- A Lakebase table that copies governed records, entitlements, or document
  bodies → reference by id and read through Unity Catalog or the source
- A static database password in config or a token reused past its hour → mint
  per connection
- Dev, QA, or preview pointing at the production branch → a child branch
- Production on a single compute while the SLA claims automatic failover →
  enable high availability
- Hand-run schema changes, or migrations first run in production → versioned
  migrations, exercised on a branch in CI
- Advisory locks or temp tables relied on across a scale-to-zero suspend →
  table-based locks with expiry

## When to use

A product hosted on Databricks (`deploy-target: databricks-apps`) that needs a
transactional, shared, durable store for its own state across stateless
instances. It is the `datastore` default of the `databricks-apps` profile.
Compose with **`relational-data-modeling`** (schema practice),
**`unity-catalog`** (governed data stays there), and **`databricks-apps`**
(resource binding and identity).

Do **not** select it for analytical or append-only data (Delta tables under
`unity-catalog`), or for a product not hosted on Databricks.

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- DATA_DESIGN: which state lives in Lakebase and which data is only referenced
- TD: branch-per-environment map, credential minting and pooling, migration path
- Deployment/runbook: high-availability setting, restore and DR procedure

## ADR References

Selecting this concern needs no ADR; `concerns.md` records it. Write an ADR only
when the project deviates from a constraint here.
