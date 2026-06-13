---
title: "Twelve-Factor App"
slug: twelve-factor
generated: true
aliases:
  - /reference/glossary/concerns/twelve-factor
---

**Category:** Infrastructure · **Areas:** infra

## Description

## Category

infrastructure

This is **infra**, not architecture. It does not decide internal layering,
dependency direction, or how many deployables the system ships as — it governs
the **per-process operational contract** every deployed process honors so it
can be built, configured, scaled, and disposed of by a cloud platform without
code changes. The decisions it forces (config from the environment, state
externalized, logs to stdout, graceful shutdown) live in the ADR, the
deployment checklist/runbook, and the process-model section of the technical
design — the operational-hygiene layer, not the application-design layer.

## Areas

infra

## Boundary

This concern is the **per-process operational contract** a deployed process
honors so a platform can manage it. It is non-exclusive (no slot) and composes
with three neighbors that must stay distinct:

- **`deployment-topology`** decides **how many deployables the system ships as
  and along which seams they split** (modular monolith vs microservices vs
  serverless). Twelve-factor is **downstream and orthogonal**: it is the
  operational contract **each** of those deployables honors regardless of how
  many there are. One modular monolith and a fleet of microservices both run as
  twelve-factor processes; topology decides the count, twelve-factor decides
  what each process must be. This concern does **not** restate the
  forcing-function / fault-line / distributed-monolith rules.
- **`o11y-otel`** decides **what telemetry to emit and how it is
  structured** — traces, RED metrics, structured-JSON log schema, trace
  context. Twelve-factor decides only the **logs-as-event-streams transport
  rule**: the process writes its event stream to **stdout, unbuffered**, and
  never manages log files, routing, or rotation itself; the execution
  environment captures and routes the stream. The two **compose**: o11y says
  *what each log line contains*, twelve-factor says *where the process puts it*.
  This concern does **not** specify log schema, span naming, or metric names.
- **`k8s-kind`** (and any `deploy-target` filler) is the **runtime that
  consumes a twelve-factor process** — the cluster, Helm charts, image builds,
  the env-var/secret injection, the SIGTERM lifecycle, the port it binds. The
  twelve-factor process is the *thing being deployed*; the deploy-target is the
  *platform deploying it*. A process that honors this contract (config from env,
  port binding, graceful shutdown, stateless, scale-by-process) is the input a
  platform expects; this concern does **not** specify cluster/Helm/image-build
  mechanics. They are designed to fit together.

## Components

The twelve factors, grouped by what each protects:

### Build-time hygiene (codebase, dependencies, build/release/run)

- **Codebase** — one codebase tracked in revision control, **many deploys**.
  One repo per app; multiple apps sharing code do so via declared dependencies,
  not a shared codebase. The same codebase produces every deploy (dev,
  staging, prod), which differ only by config.
- **Dependencies** — dependencies are **explicitly declared** (a manifest) and
  **isolated** (a dependency-isolation tool), so the app never relies on
  system-wide packages leaking in. No implicit reliance on tools existing on
  the host.
- **Build, release, run** — **strictly separate** the three stages. *Build*
  turns code into an executable bundle; *release* combines a build with that
  deploy's config into an immutable, uniquely-versioned artifact; *run* executes
  the release. Releases are immutable and **cannot be mutated at runtime** —
  any change is a new release. Code cannot be changed at run time (no editing
  on the running box).

### Config + resources (config, backing services)

- **Config** — everything that **varies between deploys** lives in the
  **environment** (env vars), not in code or checked-in per-environment config
  files. Credentials, resource handles, and per-deploy hostnames are env vars,
  each orthogonal and independently managed. **Litmus test:** the codebase could
  be made open source at any moment without leaking a single credential. Reject
  grouped `config/production.rb`-style "environments" (combinatorial explosion);
  env vars are granular and per-deploy.
- **Backing services** — every service consumed over the network (database,
  cache, queue, SMTP, object store, third-party API) is an **attached
  resource** referenced only by a config-supplied handle. Local Postgres and
  Amazon RDS are the same kind of resource to the code; swapping one for the
  other is a **config change, not a code change**. No code distinguishes a
  local resource from a third-party one.

### Process model (processes, port binding, concurrency)

- **Processes** — the app executes as **one or more stateless,
  share-nothing processes**. Any data that must persist goes to a stateful
  backing service. **No sticky state** held in process memory or local disk
  across requests — no in-memory session store assumed to survive, no reliance
  on a request hitting the same process (no sticky sessions).
- **Port binding** — the app is **completely self-contained** and exports its
  service by **binding to a port** itself (it ships its own HTTP server), rather
  than being injected into a runtime webserver container. The port is supplied
  by the environment; one app's exported service can be another's backing
  service.
- **Concurrency** — scale **out via the process model**: handle diverse
  workloads with multiple process *types* (web, worker, clock) and scale each
  type **horizontally** by running more processes. Processes do not daemonize or
  write PID files; rely on the platform's process manager.

### Lifecycle + parity (disposability, dev/prod parity, logs, admin processes)

- **Disposability** — processes are **disposable**: **fast startup** (a few
  seconds to ready) so scaling and deploys are nimble, and **graceful shutdown
  on SIGTERM** — stop accepting new work, drain in-flight work, exit. Workers
  return unfinished jobs to the queue (NACK / auto-requeue) and **all jobs are
  reentrant/idempotent**, so the app is also **robust against sudden death**
  (crash-only): an unexpected kill leaves no corruption.
- **Dev/prod parity** — keep dev, staging, and prod **as similar as
  possible**, closing the **time gap** (deploy in hours, not weeks), the
  **personnel gap** (authors operate what they ship), and the **tools gap** —
  most importantly, use the **same type and version of each backing service**
  across all environments (no SQLite-in-dev / Postgres-in-prod substitution).
- **Logs** — treat logs as **event streams**: the process writes its
  unbuffered event stream to **stdout** and never concerns itself with routing,
  storage, or rotation. The execution environment captures and routes the
  stream. (Structure and content of those events are `o11y-otel`'s concern.)
- **Admin processes** — run admin/management tasks (migrations, one-off
  scripts, REPL/console) as **one-off processes against an identical release**:
  same codebase, same config, same dependency isolation as the long-running
  processes — not as ad-hoc commands on a hand-configured box.

## Constraints

### Config and secrets live in the environment, never in the codebase

- Everything that varies between deploys is supplied by the **environment**
  (env vars or an injected env). **No credential, hostname, port, or
  per-deploy literal is committed** to the repo — the open-source litmus test
  must hold. Grouped checked-in per-environment config files (a
  `production`/`staging` config set in the repo) are rejected in favor of
  granular per-deploy env vars.

### Backing services are swappable by config alone

- Every networked dependency is an **attached resource** addressed only through
  a config-supplied handle. Code MUST NOT branch on whether a resource is local
  or third-party. Swapping a backing service (local DB → managed DB, local SMTP
  → email API) MUST be possible with a **config change and zero code change**.

### Processes are stateless and share-nothing

- No state needed across requests is held in process memory or on local disk.
  Persistent state goes to a backing service. The app MUST NOT assume sticky
  sessions, an in-process cache that survives a restart, or that a follow-up
  request reaches the same process. Scaling is horizontal across share-nothing
  processes.

### Build, release, run are separated and releases are immutable

- The artifact that runs is an **immutable, versioned release** (a build + that
  deploy's config). It MUST NOT be mutated at run time; any change is a new
  release with a new version. No editing code or config on a running instance.

### Disposable: fast startup, graceful SIGTERM shutdown, crash-safe

- Processes start in seconds and shut down gracefully on **SIGTERM** (refuse new
  work, drain in-flight, exit). Worker jobs are **reentrant/idempotent** and
  returned to the queue on interruption, so a sudden kill never corrupts state.

### Logs stream to stdout; the process does not manage log files

- The process writes its event stream to **stdout, unbuffered**, and does
  **not** open, route, or rotate log files itself. Log routing/retention is the
  environment's job. (What each line contains is `o11y-otel`.)

### Dev/prod parity — same backing services across environments

- Dev, staging, and prod use the **same type and version of each backing
  service**. A lightweight local substitute that differs from production (e.g.
  SQLite locally, Postgres in prod) is a parity gap to reject.

### Admin tasks run as one-off processes on an identical release

- Migrations and one-off scripts run in the **same release** (code + config +
  dependency isolation) as the app's long-running processes — not as commands
  hand-run against a bespoke environment.

## Drift Signals (anti-patterns to reject in review)

- A credential, hostname, port, or per-deploy value **committed to the repo**
  (or a checked-in `config/production.*`) → fails the open-source litmus test;
  move it to the environment
- Code that **branches on local-vs-third-party** for a backing service, or a
  service that cannot be swapped without a code change → make it an attached
  resource addressed by a config handle
- **Sticky state in process memory / local disk** assumed across requests
  (in-process session store, sticky sessions, a cache that must survive a
  restart) → externalize to a backing service; make processes share-nothing
- A **mutated running instance** (code/config edited in place) or a release
  that is not immutable + versioned → rebuild a new release; never mutate at run
  time
- **No SIGTERM handling** (process killed mid-request, jobs lost on shutdown),
  slow startup, or **non-idempotent jobs** that corrupt on re-run → add graceful
  drain + reentrant jobs
- The app **writing/rotating its own log files** instead of streaming to stdout
  → emit the unbuffered event stream to stdout; let the environment route it
- A **different backing service in dev than prod** (SQLite vs Postgres, an
  in-memory queue vs the real broker) → align type and version across
  environments
- A migration / admin task run as an **ad-hoc command on a hand-configured box**
  rather than a one-off process on an identical release → run it in the release
- Twelve-factor rules conflated with the **topology** (`deployment-topology` —
  how many deployables) or the **runtime** (`k8s-kind` — the platform) → keep
  them separate; this concern is the per-process contract

## When to use

Select for **any deployed long-running service or app** — anything that runs as
a process a platform manages and that has config and/or backing services. The
contract is what lets that process be deployed, configured, scaled, and disposed
of without code changes.

**Skip** for artifacts with no per-process operational contract to honor:
**libraries** (consumed in-process, no deploy/config/backing-services surface),
**static / marketing sites** (no running process, no config in the environment),
and **CLIs with no config or backing services** (a one-shot tool with nothing to
externalize). A CLI or tool that *does* read config and talk to backing services
is a deployed-process-like surface and may select it.

It **composes** (no slot) with `deployment-topology` (which decides how many
deployables each honor this contract), `o11y-otel` (which structures the events
this concern streams to stdout), and `k8s-kind` / the `deploy-target` filler
(the runtime that consumes the twelve-factor process). `areas: infra` scopes its
practices to the infrastructure / process-contract work items.

### Selection signal (verbatim — propose for concern-resolution)

> Select **twelve-factor** for any **deployed service or app** — anything that
> runs as a platform-managed process and has config and/or backing services. It
> is the **per-process operational contract** each deployable honors: config and
> secrets supplied from the environment (open-source litmus test holds), backing
> services as attached resources swappable by config alone, stateless
> share-nothing processes, immutable build/release/run separation, fast startup
> with graceful SIGTERM shutdown and reentrant jobs, logs streamed to stdout
> (the process never rotates its own files), the same backing services across
> dev/staging/prod, and admin tasks run as one-off processes on an identical
> release. Do **not** select it for a **library**, a **static/marketing site**,
> or a **CLI with no config or backing services** — there is no per-process
> contract to honor. It composes with `deployment-topology` (how many
> deployables), `o11y-otel` (the event structure it streams), and `k8s-kind` /
> the `deploy-target` filler (the runtime that consumes the process); it does
> not decide any of those.

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- ADR: config + state + backing-services strategy (env-sourced config, attached resources, stateless processes), build/release/run + disposability
- TD: process model (stateless share-nothing, port binding, concurrency), logs to stdout, graceful SIGTERM, admin-as-one-off
- IMPLEMENTATION_PLAN: deployment checklist/runbook — env-var config, dev/prod parity, immutable releases, migrations as one-off processes

## ADR References

Selecting this concern **forces ADR content**: the ADR MUST record the
**config + state + backing-services strategy** — where config and secrets come
from (the environment / injected env, never the repo), which datastore/cache/
queue/external services are **attached resources** addressed by config handles
and therefore swappable, and the **state strategy** that keeps processes
stateless (where persistent and session state live). It MUST also note the
**build/release/run** discipline (immutable versioned releases) and the
**disposability** contract (graceful SIGTERM, reentrant jobs). A material
uncertainty (an unproven backing-service choice, an undecided secrets source) is
a `tech-spike`, not a silent gap (see
`workflows/references/concern-resolution.md`).

## Practices by activity

Agents working in any of these activities inherit the practices below through runtime work context, such as a DDx bead context digest.

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
