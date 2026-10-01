# Practices: Databricks Apps (data/AI app runtime)

These practices govern **hosting, identity, and data wiring** for an interactive
data/AI app on the Databricks managed serverless runtime. They do not govern UI
component patterns (that is the `frontend-framework` filler) or the catalog/grant
model (`unity-catalog`) — see the boundary in `concern.md`.

## Requirements (Frame activity)

- Confirm the product is hosted **natively on Databricks** and its users belong to the Databricks account (SSO).
- Decide the **identity per data path**: on-behalf-of for anything that reads or writes user data, the app service principal only for shared or bulk app-owned work. This is design-defining; record it.
- Identify the **resources** the app needs (SQL warehouse, serving endpoint, job, secret, Unity Catalog volume or table, Genie space, Lakebase) and which groups own them; the app attaches them, it cannot create them.
- List the on-behalf-of **scopes** each feature needs; the minimal set becomes `user_api_scopes`.
- Name the target workspaces per environment (dev, staging, prod) and who holds `CAN_MANAGE`.
- Flag any requirement that depends on an open spike in `concern.md` (long requests, uploads, SSE/WebSocket, health probing) as a `tech-spike`, not an assumption.

## Design

- Design one origin: the backend serves every route under `/api/*`, `/api/health`, and the SPA build from a static directory with an `index.html` fallback.
- Design the backend as stateless across 1 to 5 instances: sessions, uploads, and job state in Lakebase or Unity Catalog; caches per instance and keyed per user.
- Design the **durable-state store** as Unity Catalog tables/volumes or **Lakebase** (managed Postgres), never the app's local disk or memory.
- Design data access to flow **through Unity Catalog** (SQL warehouse, governed tables, volumes) under the chosen identity's grants; route heavy work to SQL warehouses, Jobs, or Model Serving.
- Design `app.yaml`: an array `command` and an `env` list whose resource and secret values all come from `valueFrom`.
- Design the deploy as a bundle (`resources.apps.<key>` with `resources`, `user_api_scopes`, `compute_size`, `permissions`) run from CI.
- Choose a compute size from the measured load, not by default; Medium is the platform default.

## Implementation

- Ship `pyproject.toml` + `uv.lock` and no `requirements.txt` in the app directory; declare every runtime library, including the web server (toolchain rules are `python-uv`'s).
- Start the server with an array `command` that binds `0.0.0.0:$DATABRICKS_APP_PORT` (e.g. `["uvicorn", "backend.main:app"]`, which the `UVICORN_*` shims bind correctly); no literal port.
- Put a root `package.json` whose install covers the frontend's build dependencies and whose `build` script writes the SPA into the backend's static directory; keep `pnpm-lock.yaml` in sync when using pnpm.
- Read the on-behalf-of token from `x-forwarded-access-token` per request and pass it to the SQL connector or SDK client; never log, print, or persist it.
- Use the SDK `Config()` (which reads `DATABRICKS_CLIENT_ID` / `DATABRICKS_CLIENT_SECRET`) for service-principal calls.
- Write a structured audit record for each action taken on behalf of a user (who, what, which resource), without the token (policy per `auth`).
- Return errors through a global handler with no stack traces to clients.
- Handle SIGTERM: stop accepting work and exit within 15 s; keep startup light; defer slow work.
- Log to stdout/stderr only; enable telemetry to Unity Catalog for any app scaled past one instance.
- Persist durable state to Unity Catalog tables/volumes or Lakebase; mint a fresh Lakebase credential for each new pooled connection.
- In CI, authenticate with workload identity (GitHub OIDC is the documented path) and run `bundle validate`, `bundle deploy`, `bundle run <app_key>`, then poll for `RUNNING`.

## Testing / Verification

- Verify the app **runs on the Databricks serverless runtime** (deployed app URL reachable, `/api/health` answers), not a self-hosted stand-in, observed rather than assumed.
- Verify the on-behalf-of path on the **deployed** app: a user **without** the Unity Catalog grant is **denied** (negative control) and a granted user succeeds; `run-local` does not inject the token, so it cannot prove this.
- Verify durable state **survives a restart and a redeploy** (it is in Unity Catalog or Lakebase, not memory).
- Verify deep links: a non-API path returns the SPA, and an unknown `/api/*` path returns a JSON 404.
- Verify the CI deploy ran `bundle run` and the app reached `RUNNING` on the new code.
- Use `databricks apps run-local` for header-driven paths only; it injects the forwarded identity headers and runs the command locally.

## Quality Gates

- The app is **hosted on the Databricks Apps managed serverless runtime** (no parallel self-hosted infra); the deployed URL and `/api/health` respond.
- No `requirements.txt` in the app directory; `uv.lock` is committed and current.
- `app.yaml` uses array syntax, no literal port, and no secret in `value:`.
- **Data access flows through Unity Catalog** under a deliberate identity; for per-user governance, a user without the grant is **denied** on the deployed app (negative control).
- No token appears in logs, and `user_api_scopes` lists only scopes a feature uses.
- Durable state lives in **Unity Catalog tables/volumes or Lakebase** and survives a restart.
- The app **binds to existing** resources with **least-privilege** permissions; it creates no resources and embeds no credentials.
- CI deploys run `bundle run` after `bundle deploy` and wait for `RUNNING`.
- No source file exceeds 10 MB.
