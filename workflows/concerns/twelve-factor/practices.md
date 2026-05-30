# Practices: Twelve-Factor App

These practices make the **per-process operational contract** checkable in
review. They govern **how each deployed process is configured, holds state,
binds, scales, shuts down, and logs** — not how many deployables there are
(`deployment-topology`), not the structure of the telemetry it emits
(`o11y-otel`), and not the runtime that hosts it (`k8s-kind` / the
`deploy-target` filler). Each item is reviewer-checkable: a reviewer can point
at the codebase, the release artifact, or the runbook and confirm or reject it.

## Config and secrets in the environment

- Config that **varies between deploys** (credentials, resource handles,
  hostnames, ports, third-party API keys) MUST come from the **environment**
  (env vars or an injected env), not from code or checked-in per-environment
  config files. Reviewer check: **grep the repo for credential/connection-string
  literals and per-environment config files** — there MUST be none.
- The **open-source litmus test** MUST hold: the codebase could be made public
  right now without leaking any credential.
- Per-deploy config MUST be **granular env vars**, each independent — not a
  single checked-in `production` / `staging` config bundle that grows
  combinatorially.

## Backing services as attached resources

- Every networked dependency (database, cache, queue, SMTP, object store,
  external API) MUST be addressed only through a **config-supplied handle**.
- Code MUST NOT **branch on whether a resource is local or third-party**.
  Reviewer check: swapping a backing service (local DB → managed DB, local SMTP
  → email API) is a **config change with zero code change**.

## Build, release, run separation

- The artifact that runs MUST be an **immutable, uniquely-versioned release** =
  a build + that deploy's config. It MUST NOT be mutated at run time; any change
  is a **new release** with a new version.
- There MUST be **no editing of code or config on a running instance**.
- Dependencies MUST be **explicitly declared in a manifest and isolated**; the
  app MUST NOT rely on system-wide packages leaking in from the host.

## Stateless, share-nothing processes

- A process MUST hold **no sticky local state needed across requests** — no
  in-memory session store assumed to survive, no local-disk state relied on
  between requests, no assumption a follow-up request reaches the same process.
- Persistent and session state MUST live in a **stateful backing service**.
- The app MUST scale **horizontally across share-nothing processes** and MAY
  use distinct process types (web, worker, clock); it MUST NOT daemonize or
  manage PID files itself.

## Port binding

- The app MUST be **self-contained and export its service by binding to a
  port** it controls (ship its own server), with the port supplied by the
  environment — not by being injected into a host webserver container.

## Disposability: fast startup + graceful shutdown

- A process MUST reach ready in **a few seconds** (no multi-minute startup on
  the request path of scaling/deploy).
- A process MUST **handle SIGTERM gracefully**: stop accepting new work, drain
  in-flight work, then exit. Reviewer check: there is explicit SIGTERM/shutdown
  handling, not a hard kill mid-request.
- Worker jobs MUST be **reentrant / idempotent** and **returned to the queue**
  (NACK / auto-requeue) on interruption, so a **sudden death** (crash, kill)
  leaves no corruption or lost work.

## Logs as event streams

- The process MUST write its event stream to **stdout, unbuffered**, and MUST
  **not open, route, or rotate log files itself**. Reviewer check: **no file
  logger / log-rotation config in the app**; log routing and retention are the
  environment's job. (What each line *contains* is `o11y-otel`'s practice.)

## Dev/prod parity

- Dev, staging, and prod MUST use the **same type and version of each backing
  service**. A lightweight local substitute that differs from production (e.g.
  SQLite locally vs Postgres in prod, an in-memory queue vs the real broker) is
  a parity gap and MUST be rejected.

## Admin processes as one-off processes

- Migrations, one-off scripts, and consoles MUST run as **one-off processes
  against an identical release** — same codebase, config, and dependency
  isolation as the long-running processes — not as ad-hoc commands on a
  hand-configured box.

## Stay in your lane (boundary with sibling concerns)

See `concern.md` for the canonical Boundary (vs `deployment-topology`,
`o11y-otel`, `k8s-kind` / the `deploy-target` filler). These practices are
the per-process operational contract — defer to the neighbor named there for
the deployable count and seams, the log/metric/trace schema, and the cluster
/ Helm / image-build mechanics.

## Artifact impact (what selecting this changes)

- **ADR** — records the **config + state + backing-services strategy**: config
  and secrets from the environment, datastore/cache/queue/external services as
  attached resources addressed by config handles, and where persistent/session
  state lives so processes stay stateless. Also notes immutable build/release/run
  and the disposability (SIGTERM, reentrant-jobs) contract.
- **Deployment checklist / runbook** — records the **env-var/secret surface**
  (every config key the process reads), the **SIGTERM/graceful-shutdown
  behavior** and drain timeout, and **how logs are collected** from stdout.
- **Technical design** — records the **process model** (process types and how
  each scales horizontally), the **config surface** (the full set of env vars),
  and the **state strategy** (what lives in backing services vs nothing in the
  process).

## Quality Gates

- **No secret/config literal in the codebase** — all per-deploy config and every
  credential come from the environment; the open-source litmus test holds; no
  checked-in per-environment config bundle.
- **Backing services swappable by config alone** — every networked dependency is
  an attached resource addressed by a config handle; no code branches on
  local-vs-third-party; a swap is a config change with zero code change.
- **Process holds no sticky local state needed across requests** — persistent
  and session state live in a backing service; no in-memory session store, no
  sticky sessions, no local-disk state assumed across requests; scaling is
  horizontal across share-nothing processes.
- **Releases are immutable and build/release/run is separated** — the running
  artifact is a versioned build + config that is never mutated at run time; no
  editing on a live instance; dependencies are declared and isolated.
- **Fast startup + graceful SIGTERM shutdown + crash-safe jobs** — process ready
  in seconds, SIGTERM drains in-flight work then exits, and worker jobs are
  reentrant/idempotent and requeued on interruption.
- **Logs go to stdout as a stream, not files the app rotates** — the process
  emits its unbuffered event stream to stdout and manages no log files or
  rotation; the environment routes the stream.
- **Dev/prod parity on backing services** — dev, staging, and prod use the same
  type and version of each backing service; no lightweight local substitute that
  diverges from production.
- **Admin tasks run as one-off processes on an identical release** — migrations
  and scripts run in the same release as the app, not as ad-hoc commands on a
  bespoke box.
- **No lane bleed** — the contract is not conflated with the deployable count
  (`deployment-topology`), the telemetry structure (`o11y-otel`), or the runtime
  (`k8s-kind` / the `deploy-target` filler).
