# Practices: Unity Catalog (Databricks data governance)

These practices govern **how data and AI assets are registered, granted, and
lineage-tracked on Databricks**. They are the Databricks realization of data
governance; they do not restate the logical data model (`domain-driven-design`)
or application-layer authz (`security-owasp`) — see the boundary in
`concern.md`.

## Requirements (Frame activity)

- Decide the **catalog isolation boundary** up front: catalogs per environment
  (dev/staging/prod), per business unit, or both.
- Identify every dataset, volume, model, and function the product reads or
  writes, and the **groups** that need access to each.

## Design

- Lay out the **three-level namespace** (`catalog.schema.object`) for the
  product's assets; name the metastore/catalog topology in an ADR.
- Decide **managed vs external** per asset — prefer managed; for external data,
  design the **external location + storage credential** rather than raw cloud
  paths or DBFS mounts.
- Design grants as **group-based, least-privilege**: list `USE CATALOG` /
  `USE SCHEMA` plus the specific data privilege (`SELECT`, `MODIFY`,
  `READ VOLUME`, `EXECUTE`, …) each consumer group needs.
- Design **production ownership** as group ownership, and production job/app
  identity as a **service principal**.
- Where row-/column-level access differs by audience, design **row filters** and
  **column masks** instead of forked data copies.

## Implementation

- Register every asset in Unity Catalog — no Hive-metastore / no-isolation
  tables, no DBFS-mount-as-data, no anonymous cloud paths.
- `GRANT` to **groups** (IdP-provisioned via account-level SCIM), never to
  individual users; grant the **narrowest** privilege (no reflexive
  `ALL PRIVILEGES`, no broad `READ FILES`/`WRITE FILES` to end users).
- Create external tables/volumes **beneath** a governed external location, never
  at its root.
- Assign **group ownership** to production catalogs/schemas; run production jobs
  and apps under a **service principal**.
- Apply **row filters** / **column masks** for fine-grained access.
- Let consuming pipelines and apps read through the catalog — no hardcoded cloud
  paths or embedded credentials that bypass grants.

## Testing / Verification

- Verify the namespace: every product asset resolves as
  `catalog.schema.object` (no legacy/Hive/DBFS path).
- Verify access control: a principal **without** the required grant is **denied**
  (negative control), and a principal **with** the grant succeeds — observed,
  not assumed.
- Verify grants are **group-scoped** (no individual-user grants) and production
  assets are **group-owned**.
- Verify **lineage** is captured for the product's key tables (upstream →
  downstream visible in Unity Catalog lineage).

## Boundary with neighbors

- **vs domain modeling (`domain-driven-design`)**: model entities/aggregates in
  the domain concern; register and govern the physical namespace here. Do not
  re-derive the logical model in catalog terms.
- **vs `security-owasp` / app authz**: app-layer auth and catalog grants
  **compose**; neither substitutes for the other. App RBAC does not replace
  `SELECT`/`MODIFY` grants; catalog grants do not replace app authentication.
- **vs `databricks-declarative-pipelines`**: the pipeline declares the dataset;
  this concern owns the grants/ownership/lineage on the result.
- **vs `databricks-apps`**: the app consumes data; this concern owns the rule
  that it consumes **through** Unity Catalog.

## Quality Gates

- All tables, views, volumes, and models the product uses are **registered in
  Unity Catalog** under `catalog.schema.object` — **no unmanaged or anonymous
  data access** (no Hive metastore, no DBFS-mount data, no raw cloud paths).
- Access is granted **explicitly** and **to groups** (not individual users),
  least-privilege (no reflexive `ALL PRIVILEGES`); verified by a **negative
  control** — an ungranted principal is denied.
- **Production** catalogs/schemas are **group-owned** and production jobs/apps
  run under a **service principal**, not a personal identity.
- External data is reached through a governed **external location** (+ storage
  credential), not a DBFS mount or raw cloud path; nothing is created at an
  external location root.
- Fine-grained access (where required) uses **row filters / column masks**, and
  **lineage** is captured for the product's key datasets.
