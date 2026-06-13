---
title: "Security Architecture — DDx Agent Execution Surface"
slug: security-architecture
weight: 770
activity: "Design"
source: "02-design/security-architecture.md"
generated: true
---

> **Example from HELIX's own docs.** This generated page comes from `docs/helix/`. Use it to see the method in practice; start with the [artifact-type catalog](/artifact-types/) for reusable templates. Historical plans and reports may describe retired architecture.

> **Source identity** (from `02-design/security-architecture.md`):

```yaml
ddx:
  id: security-architecture
  depends_on:
    - helix.architecture
  review:
    self_hash: c27ab556fb2dbebb8ab0b5050a060080599304a31d45596132f8f4d717aa2258
    deps:
      helix.architecture: 49f65c706c77f174496e63379eb42676296da9527a504c90a81c204746968b0c
    reviewed_at: "2026-05-15T04:11:24Z"
```

# Security Architecture — DDx Agent Execution Surface

**Scope**: `ddx-server` and the agent-execution surface that HELIX delegates
to (`ddx agent execute-bead`, `ddx agent ddx work`, `ddx server workers`).
**Status**: Complete

## Decision

The agent-execution surface is a **local-first developer service** with no
inbound network exposure by default. Trust originates with the operator's
local user account. Secrets (model-provider API keys) are loaded from the
operator's environment, never persisted by the service, and never echoed
into bead bodies, execution evidence, or git-tracked logs. Authority is
governed by the operator's filesystem permissions and the
`CONTRACT-001`-defined boundary between HELIX (supervisory prompts) and DDx
(managed execution + tracker writes).

The primary controls are:

1. Bind `ddx-server` to loopback (`127.0.0.1:7743`) by default; remote access
   requires explicit operator opt-in via the Tailscale (`tsnet`) sidecar with
   ACL-gated identity.
2. Route every model-provider call through DDx so API keys live in one
   process boundary; HELIX never reads them directly.
3. Treat `.ddx/beads.jsonl`, `.ddx/exec-runs.jsonl`, and execution evidence
   as **public-by-default** (checked into the repo) and forbid secret-bearing
   content there by contract.
4. Make every agent invocation produce a durable execution record
   (`.ddx/exec-runs.d/<run-id>/`) so privilege use is auditable.

## Trust Boundaries

| Boundary | Assets | Trust Change | Control |
|----------|--------|--------------|---------|
| Operator shell → `ddx work` | Repo working tree, env vars | Operator authority enters the supervisory loop | Filesystem permissions; HELIX never elevates beyond operator UID |
| `ddx work` → `ddx agent execute-bead` | Selected bead, governing artifacts, prompt | Supervisor prompt crosses into DDx-managed execution | Bead claim is single-writer; DDx validates the bead is `ready` and `execution-eligible` before dispatch |
| `ddx-server` ↔ model provider (OpenRouter, Anthropic, etc.) | Prompt body, model output, API key | Plaintext prompt leaves the host; key authenticates | TLS-only client; key in environment (`OPENROUTER_API_KEY`, `ANTHROPIC_API_KEY`); never logged |
| Loopback HTTP (`127.0.0.1:7743`) | Server control plane (worker status, queue) | Local UNIX-domain trust | Bind to loopback only; remote access is opt-in via Tailscale sidecar |
| Tailscale (`tsnet`) → `ddx-server` (opt-in) | Same control plane, over WireGuard | Identity-bound mesh access | Tailscale ACLs restrict to operator's tailnet; service still trusts only the authenticated identity |
| Repo working tree → git remote | Bead bodies, execution evidence, logs | Repo content becomes public (or org-visible) on push | Contract: no secrets in beads, evidence, or logs; pre-commit hooks scan for known secret patterns |

## Control Mapping

| Threat / Risk | Control | Implementation Surface | Verification |
|---------------|---------|-------------------------|--------------|
| Remote code execution via exposed HTTP | Loopback bind by default | `ddx-server` startup config | `ss -lntp` confirms only `127.0.0.1:7743`; integration test asserts non-loopback bind requires explicit flag |
| API-key exfiltration via committed logs | Keys live in env, never written to disk by the service | DDx executor; agent harness | grep audit on `.ddx/agent-logs/`, `.ddx/exec-runs.d/`; pre-commit secret-scan |
| Prompt injection writes secrets into bead body | Bead bodies are operator-curated; agent output is captured in execution evidence with size/shape checks | `ddx agent execute-bead` write path | Review-stage `/helix review` reads recent execution evidence; pre-commit hook flags suspicious patterns |
| Stale claim leaves work locked indefinitely | Orphan-recovery sweep with dead-PID + age threshold (`HELIX_ORPHAN_THRESHOLD`, default 7200s) | `ddx bead` claim subsystem | STP-002 test cases cover orphan recovery |
| Concurrent writers tear `.ddx/beads.jsonl` | `ddx bead` is the single sanctioned writer; per-record file locking | `ddx bead` CLI | Tracker-mutation tests in STP-002; ADR-002 governs the write-safety model |
| Operator runs untrusted bead body | Beads are repo-scoped artifacts under the operator's review; supervisor stops on ambiguity | `ddx work` supervisor; `/helix review` | Stop-for-guidance tests; bounded-action contract |
| Cross-model verification bypass | Runtime-level `--review-agent` flag routes review to a second model when configured | `ddx work` review pass | STP-002 cross-model review test |
| Tailscale identity drift | Tailscale ACLs are the only authorization for non-loopback access | `tsnet` sidecar config | Operator-owned tailnet ACL; verified by tailnet admin, not by the service |

## Identity and Access

- **Authentication**: No service-level password or OAuth surface. Local
  access is loopback-only and authenticated by UNIX user identity. Remote
  access (opt-in) is authenticated by Tailscale node identity through the
  `tsnet` sidecar; the service trusts the tailnet's ACL.
- **Authorization**: The artifact authority hierarchy is the effective
  authorization boundary inside HELIX (vision > requirements > design >
  code per the authority hierarchy). At the service layer, write
  operations are gated by
  filesystem permissions on `.ddx/`. The supervisor stops for guidance when
  required authority is missing rather than escalating privilege.
- **Session or token handling**: Model-provider API keys are session-scoped
  to the running `ddx-server` process. Keys are read from environment at
  startup and held in process memory only. No persistent token store; no
  refresh flow; no on-disk credential cache.

## Data Protection

- **Data at rest**:
  - `.ddx/beads.jsonl` and `.ddx/exec-runs.jsonl` are plain JSONL under git.
    They are public-by-default and must not contain secrets.
  - `.ddx/exec-runs.d/<run-id>/` contains prompt, result, and embedded
    transcripts. Same public-by-default rule applies.
  - `.ddx/agent-logs/` holds raw harness output. Listed in `.gitignore` for
    runtime state; pre-commit hooks block accidental commits.
- **Data in transit**:
  - Model-provider calls use TLS (provider-enforced).
  - Loopback HTTP is plaintext but constrained to `127.0.0.1`.
  - Tailscale traffic is WireGuard-encrypted end-to-end.
- **Secrets and key handling**:
  - `OPENROUTER_API_KEY`, `ANTHROPIC_API_KEY`, and similar provider keys are
    sourced from the operator environment (typically a shell rc file or
    `direnv`), never from a repo-tracked config.
  - The service does not echo keys into stdout, stderr, or any file under
    `.ddx/`.
  - Operator rotation is out-of-band: revoke at the provider, update env,
    restart `ddx-server`.

## Logging and Monitoring

- **Security events**: Worker process start/stop, claim acquisitions, claim
  releases, orphan-recovery sweeps, model-call failures (with provider name
  but never request bodies), and any non-loopback bind attempts.
- **Alerting**: This is a developer-local service; alerting is operator-
  driven through  and `ddx server workers list`. There is no
  paging surface — the operator is the on-call.
- **Audit trail**: `.ddx/exec-runs.jsonl` is the canonical execution audit
  log. Each run has a stable `run-id`, governing-artifact references, and a
  durable evidence directory. The `events[]` array on each bead provides a
  per-bead audit trail of state transitions.

## Residual Risk

- **Operator-introduced secrets in bead bodies**: The contract is "no
  secrets in beads," but enforcement is contract + pre-commit, not service-
  level. A determined operator can still leak. Mitigation is education and
  pre-commit secret scanning; the service does not (and cannot, given the
  free-form `description` field) prevent it.
- **Supply-chain risk on model providers**: Prompt and (potentially)
  governing-artifact text leaves the host. Mitigation is operator choice of
  provider and provider-side data-handling agreements; not solved at the
  HELIX layer.
- **Tailnet ACL misconfiguration**: When the operator opts into the `tsnet`
  sidecar, exposure is governed by tailnet ACLs that HELIX does not own.
  Mitigation is the loopback-default posture: opting in is an explicit
  operator action.

## Security Test Hooks

- STP-002 covers tracker write-safety: claim atomicity, orphan recovery,
  unclaim semantics, and supersession.
- STP-002 covers stop-for-guidance: the supervisor must stop rather than
  escalate when authority is missing.
- `tests/validate-skills.sh` validates plugin-layout integrity (skills do
  not import from outside the package boundary).
- Pre-commit hooks run secret-pattern scans (`detect-secrets`-style) and
  the workflow-paths check that forbids bare `workflows/` references in
  documents.
- The `ddx-server` integration tests assert that the default bind is
  `127.0.0.1:7743` and that any non-loopback bind requires an explicit flag.
