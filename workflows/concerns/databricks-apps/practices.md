# Practices: Databricks Apps (data/AI app runtime)

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
