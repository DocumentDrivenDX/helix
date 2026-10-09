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
that family. Platform facts below are as of 2026-10-01; re-verify numbers
before a design depends on them.

## Boundary

This concern owns **how an interactive data/AI app is hosted, identified, and
wired to data on Databricks**: the managed serverless runtime and its process
contract, `app.yaml`, the app service principal and on-behalf-of identities,
resource bindings, how the platform resolves dependencies and builds the
frontend, deploy and local-dev mechanics, and the rule that data access flows
through Unity Catalog. It also owns the backend conventions that exist only
because of the hosting contract (one origin, an `/api/*` prefix, a health
route, the SPA served from a static directory with an index fallback), stated
framework-neutrally with FastAPI/uvicorn as the reference implementation. It
must not duplicate its neighbors:

- **`frontend-framework`** (e.g. `react-vite`, `react-nextjs`, or a supported
  Python UI framework) owns *what the UI is built with*: components, routing,
  styling, build configuration. Databricks Apps owns *where it runs, how the
  platform builds it, and how it is identified and granted*. The UI framework
  runs **inside** this runtime; `databricks-appkit-ui` owns the Databricks React
  component layer when selected.
- **`language-runtime`** (`python-uv` for a Python backend) owns
  `pyproject.toml`, `uv.lock`, ruff, pyright, and pytest. This concern owns only
  how the platform resolves those dependencies and what the start command may
  assume. It is not a FastAPI concern; the API contract is `api-style`'s.
- **Generic `deploy-target`** owns *deploy mechanics for self-hosted infra*.
  Databricks Apps is the Databricks-specific deploy target: a **managed
  serverless** runtime that eliminates that infra. When this concern fills
  `deploy-target`, do not also stand up parallel self-hosted hosting.
- **`unity-catalog`** owns the **data governance** the app reads through. This
  concern owns *that the app reads through it* (and how the app's identity is
  granted); it does not restate the catalog/grant model.
- **`security-owasp` / `auth` / `authorization-model`** own hardening, the audit
  policy, and the app's own permission model (see
  [README-auth-family.md](../readme-auth-family/)). Databricks Apps supplies
  the platform identity layer (service principal, on-behalf-of tokens, scopes,
  forwarded headers); compose, do not duplicate the app's own RBAC.
- **`o11y-otel`** owns instrumentation design and **`mcp-server`** owns the MCP
  protocol; this concern owns only where telemetry goes (stdout/stderr, the
  injected OTLP endpoint, Unity Catalog tables) and how an MCP app is hosted
  (streamable HTTP at `/mcp`; an app name starting `mcp-` to appear in AI
  Playground).

## Components

- **Managed serverless runtime**: a containerized web service on Ubuntu 22.04
  with Python 3.11 for pip-resolved apps (uv apps take `requires-python`), Node
  22, and `uv` preinstalled; runs unprivileged (no apt/yum). Billed while
  Running; Stopped, Deploying, and Crashed are not billed.
- **Compute and scale**: Medium (default, 2 vCPU / 6 GB), Large (4 / 12), XLarge
  (12 / 48) via `compute_size`. Horizontal scaling (GA 2026-09-29) runs 1 to 5
  instances with best-effort affinity through the `__Host-databricks-app-router`
  cookie or the `X-Routing-Key` header; scaled apps get no preinstalled Python
  libraries.
- **Limits**: 100 apps per workspace; no source file over 10 MB; app names are
  lowercase letters, digits, and hyphens and, like the URL
  `https://<app>-<workspace-id>.<region>.databricksapps.com`, immutable.
- **`app.yaml`**: `command` (an array) and `env` (`{name, value | valueFrom}`).
  Resources (SQL warehouse, serving endpoint, secret, UC volume or table, Genie
  space, job, experiment, Lakebase) are **attached to the app** in the UI, API,
  or bundle, not declared here; `valueFrom: <resource-key>` resolves each to its
  ID, name, path, secret value, or (Lakebase) endpoint path or host.
- **Platform environment**: `DATABRICKS_APP_NAME`, `DATABRICKS_WORKSPACE_ID`,
  `DATABRICKS_HOST`, `DATABRICKS_APP_PORT`, the service principal's
  `DATABRICKS_CLIENT_ID` / `DATABRICKS_CLIENT_SECRET`, shims such as
  `UVICORN_PORT` and `UVICORN_HOST=0.0.0.0`, `OTEL_*` when telemetry is on, and
  `PG*` for the first Lakebase resource. Forwarded headers: `X-Forwarded-User`,
  `X-Forwarded-Email`, `X-Forwarded-Preferred-Username`, `X-Forwarded-Host`,
  `X-Real-Ip`, `X-Request-Id`, and `x-forwarded-access-token`.
- **Two identities**: the **app service principal** (one per app, shared by all
  users; the SDK `Config()` reads its credentials) and **on-behalf-of** user
  authorization through `x-forwarded-access-token`, under which Unity Catalog
  row filters and column masks apply. Scopes are granted per app in
  `user_api_scopes` (e.g. `sql`, `files`, `genie`, `postgres`); admins can
  restrict them (`allowedAppsUserApiScopes`); the token works only in the app's
  own workspace.
- **Build hook**: a root `package.json` triggers `pnpm install --frozen-lockfile`
  (when `pnpm-lock.yaml` exists) or `npm install`, the Python install,
  `npm run build`, then `command`.
- **Deploy and local dev**: workspace folder (`databricks sync` + `databricks
  apps deploy`), Git source, or bundles (`resources.apps.<key>`).
  `databricks apps run-local` injects the forwarded identity headers but **not**
  `x-forwarded-access-token`.
- **Logs, telemetry, network**: stdout/stderr only, one instance per view, lost
  when compute stops; telemetry (GA 2026-09-18) writes `otel_logs`, `otel_spans`,
  and `otel_metrics` to Unity Catalog. Egress needs `pypi.org`,
  `files.pythonhosted.org`, `registry.npmjs.org`, `*.databricksapps.com`, and
  `*.amazonaws.com` allowed.
- **Databricks' primary scaffold** is AppKit (TypeScript, the `@databricks/appkit`
  Node server) via `databricks apps init`. HELIX ships no concern for the AppKit
  Node server; a project that chooses it records an ADR.

## Constraints

### The process honors the platform contract
- Bind `0.0.0.0:$DATABRICKS_APP_PORT`; never hard-code a port. A bare
  `uvicorn module:app` binds correctly through the `UVICORN_*` shims.
- `command` is not run through a shell; only `$DATABRICKS_APP_PORT` is
  substituted, so every other value comes from `env`.
- Exit within 15 s of SIGTERM. Keep startup light; defer slow work (installs,
  migrations, external calls).
- Serve cleartext HTTP behind the platform's TLS-terminating proxy; never
  terminate TLS in the app.
- Log to stdout/stderr, never to files; a scaled app turns on telemetry, because
  each Logs view shows one instance.

### One origin: the app process serves the SPA and the API
- Every backend route lives under `/api/*`; the SPA build is served from a static
  directory with an `index.html` fallback for other paths; an unknown `/api/*`
  path returns a JSON 404, never `index.html`.
- Expose `/api/health` as the liveness route by convention.
- Reference implementation: the official `nodejs-fastapi-hello-world-app`
  template (FastAPI + uvicorn, `StaticFiles(html=True)` at `/`, Vite
  `outDir: ../backend/static`). Cite its shape, not its code: its pins are dated
  and its catch-all route is unreachable behind the static mount.

### Dependencies resolve through uv; no `requirements.txt`
- A `requirements.txt` present **takes precedence**: the platform then uses pip,
  Python 3.11, and its preinstalled libraries. Without it, `pyproject.toml` +
  `uv.lock` install through uv with nothing preinstalled; Databricks recommends
  uv for all Python apps.
- A Python app ships `pyproject.toml` + `uv.lock` (owned by `python-uv`) and no
  `requirements.txt` anywhere in the app directory. Declare every runtime
  library, including the web server.
- The frontend builds on the platform through the root `package.json` `build`
  script. The install step runs against that root file, so it carries the
  frontend's build dependencies (the template's shape, `vite build frontend`) or
  its `build` script installs the frontend's own `package.json` first; a
  `pnpm-lock.yaml` stays in sync with `package.json`.

### Identity is the app service principal or the on-behalf-of user — chosen deliberately
- Use **on-behalf-of** for anything that reads or writes user data, so Unity
  Catalog grants, row filters, and column masks apply per user; use the **app
  service principal** only for shared or bulk app-owned work.
- Request minimal `user_api_scopes`; never print, log, or persist a token; write
  a structured audit record of actions taken on behalf of users (policy per
  `auth`).
- Lakebase on-behalf-of access needs the `postgres` scope and a Postgres role per
  user.

### Resources are bound; secrets come through `valueFrom`
- The app **binds to existing** resources; it creates none and self-grants
  nothing. Secrets never appear in `value:`.
- An existing Lakebase `database` resource is not switched to `postgres`; that
  creates separate roles and breaks data access.

### Bundle targets are the committed per-environment config layer
- This concern is the **exception** to `twelve-factor`'s "Ops handles (hostnames,
  endpoints) and secrets never appear in committed files": a bundle's `targets:`
  (per-target `variables`, `workspace.host`, warehouse/catalog/schema names) is
  a committed per-environment file the platform consumes directly, so
  non-secret ops handles may live there, reviewed like code. Per-target values
  reach the app through resource bindings (`${var.*}` feeding
  `resources.apps.<key>.resources`, read via `valueFrom`); `app.yaml` is one
  file for every target, so it holds only target-independent literals.
- Secrets still never appear in `value:`; they come through `valueFrom` secret
  resources. Credentials and tokens stay out of `databricks.yml` entirely
  (CI authenticates by workload identity).
- The app still reads its config through the `language-runtime` concern's one
  typed config object; resource bindings and `app.yaml` `env` are just the
  injection path into it.

### Stateless across instances
- Sessions, uploads, and job state live in Lakebase, Unity Catalog tables, or
  volumes, never instance memory or disk (lost on restart, redeploy, and
  scaling); in-process caches are per instance and keyed per user.

### A deploy is done when the app restarted
- Production deploys run bundles from CI with workload identity (GitHub OIDC is
  the documented path, `DATABRICKS_AUTH_TYPE: github-oidc`): `bundle validate`,
  `bundle deploy`, `bundle run <app_key>`, then poll for `RUNNING`. Deploy alone
  keeps old code serving.
- Each environment has its own workspace; users get `CAN_USE`, and `CAN_MANAGE`
  is limited to the deployer and trusted developers.

### Open spikes
Record each, and any other material uncertainty (workspace networking, account
membership, resource-binding permissions), as a `tech-spike` before a design
depends on it (see `workflows/references/concern-resolution.md`):
- **Build devDependencies**: docs put build tools in `dependencies`; official
  templates build with `vite` in `devDependencies`.
- **Proxy limits**: request timeout, body size, SSE, WebSocket, and idle
  shutdown are undocumented.
- **uv start command**: whether `command: ["uv", "run", ...]` works with only
  `pyproject.toml` and `uv.lock`, and receives `$DATABRICKS_APP_PORT`.
- **run-local with uv**: `--prepare-environment` installs a legacy library list
  and `requirements.txt` only.
- **OBO scope names**: the auth docs and the AppKit template name scopes
  differently (`genie` vs `dashboards.genie`).
- **Health contract**: whether the platform probes any path.
- **H2C**: the best-practices page says the proxy needs HTTP/2 cleartext
  support, while the reference uvicorn server speaks HTTP/1.1 only.

## Drift Signals (anti-patterns to reject in review)

- A Databricks-targeted app given **its own self-hosted infra** → host it on the
  Databricks Apps serverless runtime
- Heavy data processing in a request handler → a SQL warehouse, Job, or Model
  Serving endpoint
- A literal port, a shell-string `command`, or `$VARS` in it → array syntax,
  `$DATABRICKS_APP_PORT`, values through `env`
- TLS termination in the app, or SIGTERM ignored → plain HTTP behind the proxy;
  exit within 15 s
- `requirements.txt` beside `pyproject.toml`, or a library used because pip
  preinstalled it → delete it; declare everything in `pyproject.toml`
- API routes outside `/api/*`, or unknown `/api/*` paths answered with
  `index.html` → `/api/*` prefix and a JSON 404
- Durable state in **memory or local disk**, or assumed instance affinity →
  Lakebase, Unity Catalog tables, or volumes
- All data access run as the **service principal** when the product needs
  **per-user** governance → on-behalf-of with `x-forwarded-access-token`
- A token logged or stored, or broad `user_api_scopes` → log user and action
  only; request the minimal scopes
- A secret in `value:` → `valueFrom: <secret-resource-key>`
- Resources expected to be **created by the app** → attach existing resources
- The app reaching data **around Unity Catalog** → governed tables, volumes, or a
  SQL warehouse under grants
- Log files on local disk → stdout/stderr, plus telemetry when scaled
- `bundle deploy` without `bundle run`, or dev and prod in one workspace → run
  and poll for `RUNNING`; a workspace per environment
- An OBO path called tested because it passed under `run-local` → verify it on
  the deployed app

## When to use

A product that is an **interactive data or AI application hosted natively on
Databricks**: a dashboard, data/AI tool, or agent UI that lives next to the
lakehouse and serves Databricks-account users. **Selection signal:** the product
targets the Databricks lakehouse / is a data+AI app on Databricks. It fills the
**`deploy-target`** slot (Databricks hosts it); compose with
**`frontend-framework`** (`react-vite` for a React SPA served by a Python
backend), **`python-uv`** (the backend toolchain), **`unity-catalog`** (the
data it reads is governed there), **`databricks-appkit-ui`** (Databricks-styled
React components), and **`databricks-declarative-pipelines`** (when the data it
reads is produced by declarative ETL). `areas: ui, api, infra` scopes its
practices to the UI, service, and hosting work items.

Do **not** select it for an app hosted off Databricks, or one with no Databricks
account/lakehouse — use the generic `deploy-target` and frontend concerns there.

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- ADR: auth model per data path (app service principal vs on-behalf-of) + durable-state store (UC tables/volumes vs Lakebase) + deploy path (bundles from CI)
- TD: process contract (port, SIGTERM, no TLS), one-origin `/api/*` + static SPA serving, uv dependency resolution, `app.yaml` env + `valueFrom` bindings, stateless instances
- IMPLEMENTATION_PLAN: `app.yaml` command/env, bundle resources and `user_api_scopes`, CI `bundle deploy` + `bundle run`, the open spikes the design depends on
- TEST_PLAN: deployed-app checks for on-behalf-of denial (negative control), restart survival, SIGTERM exit, `/api/health`

## Local Diagnostic Capture

The prohibition on application-owned log files applies to the deployed app.
A development/CI runner may capture safe stdout/stderr locally under `o11y-otel`
and own rotation/retention. Preserve the platform's supported collection route
and verify it does not ingest the same event twice; local evidence does not
establish shared production retention.

## Practices by activity

Agents working in any of these activities inherit the practices below through runtime work context, such as a DDx bead context digest.

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
- Declare per-environment non-secret values in the committed `databricks.yml`: `targets.<t>.workspace.host`, and warehouse/catalog/schema as target `variables` that feed resource bindings (read via `valueFrom`); literal `value:` only for non-resource, non-secret handles such as catalog/schema names. This is the documented exception to `twelve-factor`'s no-committed-ops-handles rule. Secrets stay `valueFrom`.
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
- Code shape is gated by `code-shape-ceilings` (complexity, function, and file-size ceilings; editing-time and pre-commit hooks), which this concern does not restate.

## Local Agent Diagnostics

Compose with `o11y-otel` for schema, correlation, privacy, console filtering and
receiver proof. The deployed app keeps the platform stdout/stderr or supported
managed telemetry route; it does not rotate local log files. A development/CI
runner may capture safe output locally and own rotation/retention. Validate one
canonical export/ingestion route; enabling file ingestion and SDK export for the
same event requires tested deduplication. Instrumentation choice remains OTel's
concern, not a new Databricks logging schema.
