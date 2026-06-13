---
title: "Runbook — `ddx-server`"
slug: runbook
weight: 970
activity: "Deploy"
source: "05-deploy/runbook.md"
generated: true
---

> **Example from HELIX's own docs.** This generated page comes from `docs/helix/`. Use it to see the method in practice; start with the [artifact-type catalog](/artifact-types/) for reusable templates. Historical plans and reports may describe retired architecture.

# Runbook — `ddx-server`

## Service Summary

- Service or component: `ddx-server` — the long-running platform service
  that owns the bead tracker (`.ddx/beads.jsonl`), agent worker pool, and
  execution evidence under `.ddx/exec-runs.d/`.
- Primary function: Accept `ddx bead execute` / `ddx work` dispatch from
  HELIX skills, run the resulting model-provider calls, and persist
  execution records that HELIX consumes during review.
- Business impact if degraded: `ddx work` and `ddx bead execute` cannot
  advance the bead queue. Existing claims may go stale (orphan-recovery
  threshold default 7200s) but no data is lost — `.ddx/beads.jsonl` is
  durable on disk under git.
- Ownership team: HELIX maintainers (this is a developer-local service; the
  operator running it is the on-call).
- On-call rotation: N/A — single-operator service. The operator is expected
  to be present when `ddx-server` is running.
- Environments covered: One per repo working tree. The default deployment
  is `systemd --user` on the operator's workstation, listening on
  `127.0.0.1:7743`.

## Operator Entry Points

| Situation | First dashboard, log, or query | First command or check | Owner |
|-----------|--------------------------------|------------------------|-------|
| `ddx work` reports `BLOCKED` with no obvious bead-side cause | `ddx bead status` | `ddx server workers list` and `curl -fsS http://127.0.0.1:7743/healthz` | Operator |
| Agent dispatch hangs or times out | `.ddx/agent-logs/<latest>` | `ddx server workers list` then `ddx server stop` / `ddx server start` | Operator |
| Tracker writes appear torn or out of order | `git diff -- .ddx/beads.jsonl` | `ddx bead list --status in_progress --json` to find unreleased claims | Operator |
| Port 7743 is in use at startup | `ss -lntp '( sport = :7743 )'` | Identify the conflicting process; kill it or change the bind port | Operator |
| Model-provider auth errors | `.ddx/agent-logs/<latest>` | `echo "${OPENROUTER_API_KEY:0:8}…"` to verify env, then re-source rc | Operator |

## Dependencies and Failure Boundaries

| Dependency or boundary | Why it matters | Failure signal | Fallback or escalation |
|------------------------|----------------|----------------|------------------------|
| Model provider (OpenRouter, Anthropic, etc.) | Every agent call routes here | 4xx/5xx in agent logs; `ddx bead execute` exits with provider error | Switch provider via env (`OPENROUTER_API_KEY` → `ANTHROPIC_API_KEY` etc.); operator-driven |
| `.ddx/beads.jsonl` on local filesystem | Tracker durability | `ddx bead list` errors; corrupt-JSON parse failures | Restore from git: `git checkout .ddx/beads.jsonl` after stopping the server |
| Loopback port 7743 | Local control-plane access | Bind failure on startup | Kill conflicting process; or set `DDX_SERVER_PORT` to a free port and update `ddx server start` config |
| `~/.ddx/` user-state dir | Server-managed state outside the repo | Permission errors at startup | Verify ownership; recreate if missing (state is reproducible from repo) |
| Tailscale (`tsnet`) sidecar (opt-in) | Remote control-plane access | Tailscale connectivity errors | Service still works on loopback; tailnet failure is non-blocking |

## Alert Triage

| Alert or symptom | Likely causes | Immediate checks | Stop and escalate when |
|------------------|---------------|------------------|------------------------|
| `ddx work` repeatedly returns `NEXT_ACTION: WAIT` | No ready beads; or queue-drain gate is blocking on missing context | `ddx bead ready --json`; `ddx bead status`; check focused-epic state | Beads exist as ready but workers idle — restart `ddx-server` |
| `ddx server workers list` shows zero healthy workers | Server crashed; or all workers wedged on a long model call | Check `.ddx/agent-logs/<latest>`; check `systemctl --user status ddx-server` | Crash loops more than 3x — capture logs and stop, do not restart blindly |
| `claimed-at` ages exceed DDx orphan threshold (default 7200s) | Worker died without `--unclaim`; orphan recovery not yet swept | Wait for next sweep, or run `ddx bead unclaim <id>` manually after confirming the worker is dead | Recovery does not free the claim — investigate before forcing |
| Provider 401/403 spikes | API key revoked, expired, or rate-limited | `echo "${OPENROUTER_API_KEY:0:8}…"`; provider dashboard | Key is valid but provider rejects — escalate to provider support |
| Tracker file shows torn writes | Concurrent direct edit during a live run | `git diff .ddx/beads.jsonl`; check `events[]` for the affected bead | The bead `events[]` log does not match observable state — restore from git |

## Common Incident Procedures

### Stuck Claim After Worker Death

- Trigger: `ddx bead list --status in_progress` shows a bead with stale
  `claimed-at` (older than the orphan threshold) and the recorded
  `claimed-pid` is no longer running.
- Immediate actions:
  1. Confirm the PID is dead: `ps -p <claimed-pid>` returns nothing.
  2. Capture the bead state: `ddx bead show <id> --json > /tmp/<id>-stuck.json`.
  3. Run `ddx bead unclaim <id>` to release the claim.
- Validation:
  - `ddx bead show <id>` reports `status: open` and no claim metadata.
  - `ddx work` resumes and either reclaims or skips per the queue ordering.
- Escalate to: N/A (operator-only service).

### Tracker File Corruption

- Trigger: `ddx bead list` exits non-zero with a JSON parse error, or
  `git diff -- .ddx/beads.jsonl` shows a malformed line.
- Immediate actions:
  1. Stop the server: `ddx server stop`.
  2. Capture evidence: `cp .ddx/beads.jsonl /tmp/beads-corrupt.jsonl`.
  3. Restore from git: `git checkout .ddx/beads.jsonl`.
  4. Replay any lost work by inspecting recent agent logs and re-issuing
     `ddx bead update` calls if needed.
- Validation:
  - `ddx bead list --status open --json | jq length` returns the expected
    count.
  - `ddx bead status` shows a coherent queue.
- Escalate to: HELIX maintainers via repo issues if corruption is
  reproducible.

### Provider Auth Failure

- Trigger: Agent logs show repeated 401 / 403 from the model provider.
- Immediate actions:
  1. Verify the env var is set in the server's environment:
     `systemctl --user show-environment | grep -i api_key` (presence only —
     never echo the value).
  2. Re-source the operator rc file or `direnv reload` and restart the
     server: `ddx server stop && ddx server start`.
  3. If the key is genuinely expired, rotate at the provider, update the
     env, and restart.
- Validation:
  - One successful `ddx bead execute --dry-run` against any ready bead.
- Escalate to: Provider support if the key is valid but rejected.

## Rollback and Recovery

### Rollback Entry Conditions

- A `ddx-server` upgrade caused crash loops on startup.
- A schema-incompatible bead was written by a newer DDx version and the
  current `ddx bead` cannot parse it.

### Rollback Procedure

1. Stop the running server: `ddx server stop`.
2. Reinstall the previous DDx version (operator's preferred path —
   typically `mise` or `asdf`).
3. If the tracker file was rewritten by the newer version, restore the
   previous tracker state: `git checkout HEAD~1 -- .ddx/beads.jsonl`
   (after capturing the current file for forensics).
4. Restart: `ddx server start`.

### Recovery Validation

- `curl -fsS http://127.0.0.1:7743/healthz` returns `200 OK`.
- `ddx server workers list` shows at least one healthy worker.
- `ddx work --dry-run` produces a coherent next-action summary against
  the current queue.

## Routine Operations

| Operation | Trigger or cadence | Command or workflow | Verification |
|-----------|--------------------|---------------------|--------------|
| Orphan-claim sweep | Automatic on each `ddx work` cycle | Internal — no operator action required | `ddx bead list --status in_progress` shows no claims older than the DDx orphan threshold |
| `.ddx/agent-logs/` rotation | Operator discretion (logs are gitignored runtime state) | Manual: prune older than 30 days | Disk usage in `.ddx/agent-logs/` stays bounded |
| Worker pool restart | After provider config or env change | `ddx server stop && ddx server start` | One successful execute against a ready bead |
| API-key rotation | When provider issues a new key | Update env in operator rc; restart server | Single dry-run against a ready bead succeeds |

If no recurring operational tasks exist beyond these, no other periodic
procedures are documented. Other system maintenance (OS updates, disk
cleanup) belongs to the operator's host-level workflow, not this service.

## Escalation and Communications

1. Primary on-call: The operator running `ddx-server`.
2. Secondary escalation: HELIX maintainers via the repo issue tracker for
   reproducible bugs in `ddx-server` itself.
3. Incident coordinator or manager: N/A — single-operator service.
4. External dependency or vendor support: Model provider support
   (OpenRouter / Anthropic / etc.) for provider-side outages or
   credential issues.

## References

- Deployment checklist: [`deployment-checklist.md`](/artifacts/deployment-checklist/)
- Monitoring setup: [`monitoring-setup.md`](/artifacts/monitoring-setup/)
- Architecture: [`../02-design/architecture.md`](/artifacts/architecture/)
- Security architecture: [`../02-design/security-architecture.md`](/artifacts/security-architecture/)
- DDx/HELIX boundary contract: [`../02-design/contracts/CONTRACT-001-ddx-helix-boundary.md`](/artifacts/contracts/contract-001-ddx-helix-boundary/)
