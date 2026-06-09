---
title: "Monitoring Setup — `ddx-server`"
slug: monitoring-setup
weight: 950
activity: "Deploy"
source: "05-deploy/monitoring-setup.md"
generated: true
---
# Monitoring Setup — `ddx-server`

## Service Summary

- Service: `ddx-server` (loopback `127.0.0.1:7743` by default; opt-in
  Tailscale exposure via `tsnet`).
- Signals that matter most: server liveness, worker pool health, bead-queue
  depth (open / ready / blocked), claim freshness (orphan-recovery health),
  and provider-call success rate.

## Metrics Collection

| Category | Metrics | Notes |
|----------|---------|-------|
| Application | Worker count (healthy / unhealthy), in-flight executions, recent execution success / failure counts, average execution duration | From `ddx server workers list --json`; emitted to `.ddx/exec-runs.jsonl` for historical reads |
| System | Process memory (RSS), CPU, file-descriptor count, `.ddx/agent-logs/` disk usage | Operator workstation `top` / `du -sh`; not actively scraped |
| Business | Bead queue depth by status (`open`, `in_progress`, `blocked`, `closed` over the last 24h), close rate | From `ddx bead list --status <s> --json`; surfaced via `ddx bead status` |
| Custom | Orphan-recovery sweeps performed, claims released, stale-claim age distribution | Computed from `events[]` arrays during `ddx bead status` |

## Alerting Rules

| Alert | Condition | Action |
|-------|-----------|--------|
| Server unhealthy | `GET /healthz` returns non-200 for 2 consecutive checks | Operator notification: `ddx-server down` (no automated paging — single-operator service) |
| All workers unhealthy | `ddx server workers list --json` reports zero healthy workers for 60s | Operator-visible: `ddx bead status` and `ddx server workers list` show the failure |
| Queue blocked depth growing | `ddx bead list --status blocked --json` count grows by ≥3 in the same `ddx work` cycle | Operator-visible warning in `ddx bead status`; surfaces as backlog drift |
| Stale claims exceed threshold | Any `claimed-at` older than the DDx orphan threshold (default 7200s) without a recovery sweep | Next `ddx work` cycle should sweep; if it doesn't, operator runs `ddx bead unclaim` manually |
| Provider error spike | `>5` consecutive provider 4xx/5xx responses in `.ddx/agent-logs/` | Operator-visible: tail of agent log; check API key + provider status |

## Dashboards

| Dashboard | Must Show |
|-----------|-----------|
| Operations | `GET /healthz` status; worker pool size and health; in-flight executions; latest provider errors |
| Business | Bead counts by status; close rate over the last 24h; focused-epic state; ready-queue depth |
| Technical | `.ddx/agent-logs/` disk usage; recent execution evidence size in `.ddx/exec-runs.d/`; tracker file size and last-modified timestamp |

In practice the "dashboards" surface for a single-operator developer
service is `ddx bead status` plus `ddx server workers list`. There is no
Grafana / Datadog setup; alerting is operator-driven.

## Logs and Tracing

### Logging

- Required fields (per agent-execution log entry): `timestamp`,
  `level`, `service`, `run-id`, `bead-id`, `message`. Provider names
  appear; provider request bodies and API keys never appear.
- Retention: `.ddx/agent-logs/` is gitignored runtime state. Operators
  prune on their own schedule; HELIX does not auto-rotate.
- Authoritative execution audit: `.ddx/exec-runs.jsonl` (one record per
  agent run) plus the per-run evidence directory under
  `.ddx/exec-runs.d/<run-id>/`. These are durable and committed when
  appropriate.

### Tracing

- Critical journeys: `ddx work` cycle → bead claim → `ddx bead execute`
  dispatch → provider call → result capture → bead update / close.
- Sampling: 100% — every agent run produces a durable execution record
  by design. Sampling is not configurable; the audit trail is the
  product.

## Health Checks

| Check | Endpoint or Mechanism | What It Verifies |
|-------|-----------------------|------------------|
| Liveness | `GET http://127.0.0.1:7743/healthz` | Process is running and responsive on the loopback bind |
| Readiness | `ddx server workers list --json` (returns ≥1 healthy worker) | Worker pool is healthy and capable of executing |
| Tracker integrity | `ddx bead list --status open --json` exits 0 | `.ddx/beads.jsonl` is parseable and locks acquire cleanly |
| Provider connectivity | `ddx bead execute --dry-run <ready-bead>` | API key resolves; provider TLS handshake succeeds |

## SLI/SLO Tracking

| Indicator | SLI | SLO |
|-----------|-----|-----|
| Availability | (`/healthz` 200 responses) / (total checks) over a 24h operator session | ≥99% during active sessions |
| Execution success | (Closed beads with `status: closed`) / (Total claimed beads) over a `ddx work` cycle | ≥80% (the rest are blockers, supersessions, or stop-for-guidance — all valid outcomes) |
| Tracker durability | (Cycles with no torn writes) / (Total cycles) | 100% (any tear is a release-blocker bug) |

### Error Budget

Because this is a developer-local service, the "error budget" is not
formal. The operator stops the service and investigates whenever any SLI
above degrades; there is no auto-escalation.

## Incident Response

### Response Entry Points

- Primary owner or schedule: The operator running `ddx-server`.
- Secondary owner or schedule: HELIX maintainers via the repo issue
  tracker for reproducible bugs in the service itself.
- Immediate containment actions: `ddx server stop` is always safe — claims
  are durable in `.ddx/beads.jsonl` and orphan recovery picks up stale
  claims on next run.
- Existing runbook links: [`runbook.md`](/artifacts/runbook/) — the canonical
  incident-response surface.

### Routing

- Primary: Operator on the workstation.
- Secondary: HELIX maintainers (issue tracker).
- Escalation: Model-provider support for provider-side outages.
