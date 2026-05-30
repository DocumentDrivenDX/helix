---
title: "Databricks Apps (data/AI app runtime)"
slug: databricks-apps
generated: true
aliases:
  - /reference/glossary/concerns/databricks-apps
---

**Category:** App-Runtime · **Areas:** ui, api, infra

## Description

## Category
app-runtime

## Areas
ui, api, infra

## Slot
deploy-target

## Platform

**Platform-specific (Databricks).** Databricks Apps is Databricks' framework for
building and hosting interactive data/AI applications natively on the Data
Intelligence Platform. HELIX already treats Databricks as a known runtime
ecosystem (the `databricks-genie` install target,
`docs/install/databricks-genie.md`); this concern is the *app-hosting* member of
that family.

## Boundary

This concern owns **how an interactive data/AI app is hosted, identified, and
wired to data on Databricks** — the managed serverless runtime, the app
service-principal identity, OAuth auth, resource bindings, and the rule that
data access flows through Unity Catalog. It must not duplicate its neighbors:

- **`frontend-framework`** (e.g. `react-nextjs`, or a supported Python UI
  framework) owns *what the UI is built with* — components, routing, styling,
  the client experience. Databricks Apps owns *where it runs and how it is
  identified and granted*. The UI framework runs **inside** this runtime; this
  concern does not specify component patterns.
- **Generic `deploy-target`** owns *deploy mechanics for self-hosted infra*
  (containers you operate, a cloud you provision). Databricks Apps is the
  Databricks-specific deploy target: a **managed serverless** runtime that
  eliminates that infra. When this concern fills `deploy-target`, do not also
  stand up parallel self-hosted hosting.
- **`unity-catalog`** owns the **data governance** the app reads through. This
  concern owns *that the app reads through it* (and how the app's identity is
  granted); it does not restate the catalog/grant model.
- **`security-owasp` / `auth`** own application-layer auth semantics. Databricks
  Apps supplies the platform identity layer (app service principal + OAuth,
  on-behalf-of-user authorization); compose, do not duplicate the app's own
  RBAC.

## Components

- **Managed serverless runtime** — the app runs as a **containerized web
  service** on Databricks serverless compute. Each app has its own configuration,
  identity, and isolated runtime; Databricks supplies the hosting (no separate
  infra to provision). Billed per hour of running compute.
- **Supported frameworks** — Python: **Streamlit, Dash, Gradio** (and other
  Python web frameworks such as Flask/FastAPI); JavaScript/Node: **React,
  Angular, Svelte, Express**. The chosen framework fills `frontend-framework`
  and runs inside the runtime.
- **`app.yaml` manifest** — declares the startup **command**, **environment
  variables**, and the **resources** the app binds to (SQL warehouses, model
  serving endpoints, jobs, secrets, Unity Catalog volumes, Genie spaces).
  Dependencies: `requirements.txt`/`pyproject.toml` (Python) or `package.json`
  (Node).
- **App service principal** — Databricks creates a **service principal per app**;
  it is the app's own identity (shared across all users) for resource access.
- **OAuth 2.0 auth + two identity models**:
  - **App authorization** — actions run as the app's **service principal**
    (shared permissions for all users).
  - **User authorization (on-behalf-of)** — the **end user** (who must belong to
    the Databricks account and signs in via SSO) authorizes, so **per-user**
    permissions — including **Unity Catalog grants** — are enforced.
- **Resource bindings** — an app **binds to existing** resources (declared in
  `app.yaml`); it **cannot create** them. Workspace admins review the requested
  permissions at deploy; Databricks enforces **least-privilege**.
- **Data persistence options** — in-memory cache (session-only, lost on
  restart), local filesystem (ephemeral), **Databricks/Unity Catalog tables**
  (persistent), Unity Catalog **volumes**, workspace files, or **Lakebase**
  (managed Postgres) for transactional app state.
- **Networking & isolation** — inherits the workspace's networking protections;
  isolated per-app runtime; encryption in transit and at rest.

## Constraints

### Databricks hosts the app — no parallel self-hosted infra
- The app runs on the **managed serverless runtime**; this concern fills
  `deploy-target`. Do not provision separate hosting (your own containers,
  cluster, or cloud) for the same app — that defeats the runtime and splits the
  identity/governance model.
- In-memory and local-filesystem state is **ephemeral** (lost on restart);
  durable state goes to Unity Catalog tables/volumes or **Lakebase**, never to
  the app's local disk.

### Identity is the app service principal or the on-behalf-of user — chosen deliberately
- Resource access runs as either the **app service principal** (shared) or the
  **signed-in user** (on-behalf-of). Pick deliberately: use **user
  authorization** when **per-user Unity Catalog grants must be enforced**; use
  the **service principal** only for shared, app-owned actions. Do not silently
  run all data access as the service principal when the product needs per-user
  governance.
- The app **binds to existing** resources via `app.yaml`; it does not create
  resources or self-grant. Requested permissions are admin-reviewed and
  least-privilege.

### Data access flows through Unity Catalog
- The app reads and writes lakehouse data **through Unity Catalog governance**
  (via SQL warehouses / governed tables / volumes), under the appropriate
  identity's grants — **not** around it via hardcoded cloud paths or embedded
  credentials (see `unity-catalog`).

### The UI framework is a separate slot
- The framework (Streamlit/Dash/Gradio/React/…) fills `frontend-framework` and
  composes inside this runtime. This concern owns hosting/identity/data wiring,
  not component patterns.

## Drift Signals (anti-patterns to reject in review)

- A Databricks-targeted app given **its own self-hosted infra** (separate
  cluster/cloud/containers) in parallel → host it on the Databricks Apps
  serverless runtime (this concern fills `deploy-target`)
- Durable app state written to the app's **local filesystem or in-memory cache**
  (lost on restart) → persist to Unity Catalog tables/volumes or Lakebase
- All data access run as the **app service principal** when the product needs
  **per-user** governance → use **user (on-behalf-of) authorization** so Unity
  Catalog grants are enforced per user
- The app reaching data **around Unity Catalog** (hardcoded cloud path, embedded
  credential) → read through governed tables/volumes/SQL warehouse under grants
- Resources expected to be **created by the app** → bind to existing resources in
  `app.yaml`; provision them out of band
- Treating Databricks Apps as the **UI framework** and skipping a real frontend
  framework → fill `frontend-framework` (Streamlit/Dash/Gradio/React/…) inside
  the runtime

## When to use

A product that is an **interactive data or AI application hosted natively on
Databricks** — a dashboard, data/AI tool, or agent UI that lives next to the
lakehouse and serves Databricks-account users. **Selection signal:** the product
targets the Databricks lakehouse / is a data+AI app on Databricks. It fills the
**`deploy-target`** slot (Databricks hosts it); compose with
**`frontend-framework`** (the actual UI framework runs inside the runtime),
**`unity-catalog`** (the data it reads is governed there), and
**`databricks-declarative-pipelines`** (when the data it reads is produced by
declarative ETL). `areas: ui, api, infra` scopes its practices to the UI,
service, and hosting work items.

Do **not** select it for an app hosted off Databricks, or one with no Databricks
account/lakehouse — use the generic `deploy-target` and frontend concerns there.

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- ADR: auth model (app service-principal vs on-behalf-of-user) + durable-state store (UC tables/volumes vs Lakebase)
- TD: managed serverless runtime, app.yaml manifest + resource bindings, identity model, data access via Unity Catalog
- IMPLEMENTATION_PLAN: app.yaml command/env/resource-bindings; bind to existing resources (cannot create)

## ADR References

Record an ADR for the auth model choice (**app service principal vs
on-behalf-of-user**) — it is design-defining for per-user governance — and for
the app's durable-state store (Unity Catalog tables/volumes vs Lakebase). A
material uncertainty (workspace networking, account membership, resource-binding
permissions) is a `tech-spike`, not a silent assumption (see
`workflows/references/concern-resolution.md`).

## Practices by activity

Agents working in any of these activities inherit the practices below via the bead's context digest.

These practices govern **hosting, identity, and data wiring** for an interactive
data/AI app on the Databricks managed serverless runtime. They do not govern UI
component patterns (that is the `frontend-framework` filler) or the catalog/grant
model (`unity-catalog`) — see the boundary in `concern.md`.

## Requirements (Frame activity)

- Confirm the product is hosted **natively on Databricks** and its users belong
  to the Databricks account (SSO).
- Decide the **auth model**: app service principal (shared) vs on-behalf-of-user
  (per-user Unity Catalog grants). This is design-defining — record it.
- Identify the **resources** the app needs (SQL warehouse, model serving
  endpoint, jobs, secrets, Unity Catalog volumes/tables, Genie space) and which
  groups own them.

## Design

- Choose the **UI framework** (Streamlit/Dash/Gradio/Flask/FastAPI or
  React/Svelte/Express) — it fills `frontend-framework` and runs inside the
  runtime.
- Design the **`app.yaml`**: startup command, environment variables, and the
  **resource bindings** (bind to **existing** resources; the app cannot create
  them).
- Design the **durable-state store** as Unity Catalog tables/volumes or
  **Lakebase** (managed Postgres) — never the app's local disk or in-memory
  cache.
- Design data access to flow **through Unity Catalog** (SQL warehouse / governed
  tables / volumes) under the chosen identity's grants.

## Implementation

- Deploy to the **managed serverless runtime** — no separate self-hosted infra.
- Declare dependencies in `requirements.txt`/`pyproject.toml` (Python) or
  `package.json` (Node); declare command, env, and resources in `app.yaml`.
- Use **on-behalf-of-user** authorization where per-user governance matters; use
  the **app service principal** only for shared, app-owned actions.
- Persist durable state to Unity Catalog tables/volumes or Lakebase; treat
  in-memory/local-filesystem state as ephemeral.
- Read/write lakehouse data **through Unity Catalog** — no hardcoded cloud paths
  or embedded credentials.
- Request **least-privilege** resource permissions (admin-reviewed at deploy).

## Testing / Verification

- Verify the app **runs on the Databricks serverless runtime** (deployed app
  URL reachable), not a self-hosted stand-in — observed, not assumed.
- Verify the chosen **auth model** behaves correctly: under on-behalf-of-user,
  a user **without** a Unity Catalog grant is **denied** the data (negative
  control); a granted user succeeds.
- Verify durable state **survives an app restart** (it is in Unity
  Catalog/Lakebase, not in-memory).
- Verify the app **binds to existing** resources (no create-on-deploy) and
  permissions are least-privilege.

## Boundary with neighbors

See `concern.md` for the canonical Boundary (vs `frontend-framework`, generic
`deploy-target`, `unity-catalog`, `security-owasp` / `auth`). Composition in
the Databricks family: this concern hosts; `databricks-declarative-pipelines`
produces the data; `unity-catalog` governs it — each owns its piece, none
restates the others.

## Quality Gates

- The app is **hosted on the Databricks Apps managed serverless runtime** (no
  parallel self-hosted infra); the deployed app URL is reachable.
- A real **UI framework** fills `frontend-framework` and runs inside the runtime
  (the app is not "Databricks Apps as the UI").
- **Data access flows through Unity Catalog** under a deliberate identity (app
  service principal vs on-behalf-of-user); for per-user governance, a user
  without the grant is **denied** (negative control).
- Durable state lives in **Unity Catalog tables/volumes or Lakebase** and
  survives a restart — not in-memory/local-filesystem.
- The app **binds to existing** resources via `app.yaml` with **least-privilege**
  permissions (admin-reviewed); it creates no resources and embeds no
  credentials.
