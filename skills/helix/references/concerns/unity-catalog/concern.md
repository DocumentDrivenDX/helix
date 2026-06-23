# Concern: Unity Catalog (Databricks data governance)

## Category
data-governance

## Areas
data, api, infra

## Platform

**Platform-specific (Databricks).** Unity Catalog is Databricks' unified
governance layer for the lakehouse. This concern is the *specific Databricks
realization* of the generic data-governance discipline — not a generic
data-modeling or access-control concern (see `## Boundary`).

## Boundary

This concern owns **how data and AI assets are governed on Databricks** — the
catalog namespace, the grant model, lineage, and governed external storage. It
is **Databricks' concrete realization** of data governance.

For the auth family (where app-layer `authorization-model` and catalog grants
**compose** — neither substitutes for the other), see
[README-auth-family.md](../README-auth-family.md). For the logical domain
model, defer to `domain-driven-design`: model entities/aggregates there;
register and govern the physical `catalog.schema.object` namespace here.
`databricks-declarative-pipelines` *produces* governed datasets; this concern
owns the grants, ownership, and lineage on the result. `databricks-apps`
*consumes* governed data; this concern owns the rule that an app reads
through Unity Catalog grants, not around them.

## Components

Unity Catalog organizes every governed asset under a **metastore** (the
top-level container, one per region) exposing a **three-level namespace**:
`catalog.schema.object`.

### Namespace — where assets are registered
- **Metastore** — the top-level container; holds catalogs, plus storage
  credentials and external locations directly beneath it.
- **Catalog** — first level; the primary unit of data isolation. Organize by
  environment (dev/staging/prod) and/or business unit.
- **Schema** (database) — second level; groups related objects.
- **Objects** (third level) — **tables** and **views** (tabular), **volumes**
  (governance for non-tabular files), **models** (registered ML models),
  **functions** (UDFs). Tables and volumes are **managed** (Unity Catalog owns
  governance *and* storage lifecycle — preferred) or **external** (governance
  only; data lives at an external location).

### Securable objects & the grant model
Every governed asset is a **securable object** on which privileges are granted
to **users, service principals, or groups**. Privileges are **inherited
downward**: a grant at the catalog level applies to current and future schemas
and objects within it; a schema grant applies to its objects.

Key privileges:
- **`USE CATALOG` / `USE SCHEMA`** — traversal prerequisites; required before
  any data access on objects beneath.
- **`SELECT`** — read a table/view/materialized view.
- **`MODIFY`** — insert/update/delete table data.
- **`READ VOLUME` / `WRITE VOLUME`** — read/write files in a volume.
- **`EXECUTE`** — invoke a function or load a registered model for inference.
- **`BROWSE`** — discover an object and view its metadata (and explore its
  lineage) **without** data access.
- **`CREATE TABLE` / `CREATE SCHEMA` / `CREATE CATALOG` / `CREATE VOLUME` /
  `CREATE FUNCTION` / `CREATE MODEL`** — creation rights at each level.
- **`MANAGE`** — manage privileges, transfer ownership, delete (close to
  ownership, but does not auto-grant data privileges).
- **`ALL PRIVILEGES`** — every applicable privilege (broad; avoid by default).
- **`EXTERNAL USE SCHEMA`** — access tables via external engines over open APIs.

Every securable object has an **owner** (a user, service principal, or — for
production assets — a **group**) who can grant/revoke on it.

### Governed external storage
- **Storage credential** — the cloud identity Unity Catalog uses to reach
  external cloud storage.
- **External location** — a governed path (a credential + a cloud URI) over
  which `READ FILES` / `WRITE FILES` are granted; external tables and external
  volumes are created beneath governed external locations, never at their root.

### Fine-grained access & lineage
- **Row filters** and **column masks** apply row-level and column-level security
  at query time.
- **Data lineage** is captured automatically (table-, column-, and
  notebook/job-level) and aggregated across every workspace attached to the
  metastore; visible to principals with at least `BROWSE`/`SELECT`.
- **Audit logging** records access automatically.

## Constraints

### Every governed asset is registered and explicitly granted
- All tables, views, volumes, models, and functions live in the
  `catalog.schema.object` namespace under a Unity Catalog metastore — **no
  unmanaged or anonymous data access** (no legacy Hive-metastore / no-isolation
  tables, no DBFS mounts standing in for governed data).
- Access is granted **explicitly** via the privilege model; there is no implicit
  open access. `USE CATALOG`/`USE SCHEMA` plus the specific data privilege
  (`SELECT`, `MODIFY`, `READ VOLUME`, …) are all required.

### Grant to groups, least-privilege, group ownership for production
- Grant privileges to **groups, not individual users** (groups provisioned from
  the IdP via account-level SCIM).
- Grant the **narrowest** privilege that satisfies the need; avoid
  `ALL PRIVILEGES` and broad `READ FILES`/`WRITE FILES` on external locations to
  end users.
- **Production** catalogs and schemas are **owned by a group**, never an
  individual — and production jobs run under a **service principal**, not a
  personal identity.

### Prefer managed; govern external storage through external locations
- Prefer **managed** tables and volumes (full governance + storage lifecycle).
- External data is reached only through a governed **external location** built
  on a **storage credential**; do not create external tables/volumes at an
  external location's root, and do not mount storage to DBFS that is also used as
  an external location.

### Isolate by catalog; fine-grained access at the data layer
- Use the **catalog** as the primary isolation boundary (per environment /
  business unit).
- Apply **row filters** and **column masks** for row-/column-level access rather
  than forking copies of data per audience.

### Data-layer governance is not replaced by app-layer authz
- Unity Catalog grants are the **data-layer** control and compose with — never
  substitute for — application-layer authentication/authorization
  (`security-owasp`). An app reading lakehouse data does so **through** Unity
  Catalog (see `databricks-apps`), not around it.

## Drift Signals (anti-patterns to reject in review)

- A table/view/volume/model accessed outside the `catalog.schema.object`
  namespace — legacy Hive metastore, raw DBFS mount, anonymous path → register
  it in Unity Catalog and grant explicitly
- Privileges granted to **individual users** instead of groups → grant to
  IdP-provisioned groups
- `ALL PRIVILEGES` (or broad `READ FILES`/`WRITE FILES` on an external location)
  handed to end users → grant the narrowest privilege that satisfies the need
- A **production** catalog/schema **owned by an individual**, or a production job
  running under a personal identity → group ownership + service-principal job
  identity
- External table/volume created at an external location **root**, or DBFS mount
  doubling as an external location → create beneath a governed external location;
  remove the overlapping mount
- Row-/column-level access solved by forking per-audience data copies → use row
  filters / column masks
- App- or pipeline-side code reaching data around the catalog (hardcoded cloud
  path, direct credential) instead of through Unity Catalog grants → route data
  access through the catalog

## When to use

Any product whose **data and AI assets live in the Databricks lakehouse** and
must be governed — registered, access-controlled, and lineage-tracked through
Unity Catalog. This is the data-governance member of the Databricks platform
family; select it together with `databricks-apps` (when the product is a
Databricks-hosted app) and/or `databricks-declarative-pipelines` (when ETL runs
as declarative pipelines). It is composable (no slot); `areas: data, api, infra`
scopes its practices to the data, service, and infrastructure work items.

Do **not** select it for a product that does not store data in Databricks — use
the generic data-governance / data-modeling concerns there instead.

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- ADR: metastore/catalog layout (isolation boundaries), managed-vs-external, group/ownership model for production
- TD: assets registered in catalog.schema.object; data access through Unity Catalog grants, not around them
- DATA_DESIGN: namespace placement, grant model, row filters/column masks, governed external locations

## ADR References

Record an ADR for the metastore/catalog layout (isolation boundaries:
per-environment vs per-business-unit), the managed-vs-external decision for the
product's data, and the group/ownership model for production assets. A material
uncertainty (workspace/metastore topology, external-storage credentials,
cross-region constraints) is a `tech-spike`, not a silent assumption (see
`workflows/references/concern-resolution.md`).
