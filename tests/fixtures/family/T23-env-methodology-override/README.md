# T23 — HELIX_METHODOLOGY env override exercised

- **Installed:** `helix-library`, `helix`, `helix-infra`
- **Env:** `HELIX_METHODOLOGY=helix-infra` (see `env.txt`)
- **Risk:** medium (contract-surface verification)

## Scenario

Workspace identical to T5 (product-shaped, no `*.tf`). The repo
shape says "helix wins." But `HELIX_METHODOLOGY=helix-infra` is set
in the runner environment. The env MUST win.

## Why it matters

T7's expected/ lists `HELIX_METHODOLOGY` as an acceptable
disambiguation hint in prose, but no fixture actually USES the
env var. The env override is a contract surface — if it's not
tested, an impl can fail to honor it and still pass T1-T22. Either
the env variable is part of the contract (this fixture) or it
should be removed from the design.

## Runner mechanics

The runner reads `env.txt` (if present) and exports each `KEY=VALUE`
line into the subprocess environment before invoking Claude Code.

## Pass signature

Exactly one Write at `docs/adr/NNNN-*.md` (helix-infra location),
and NO Write at `docs/helix/02-design/` (which is where repo-shape
alone would have routed).

## Failure signatures

- Write at docs/helix/02-design/ → env override ignored, repo shape
  won.
- Disambiguation banner with no write → env override was treated as
  a hint, not an override.
