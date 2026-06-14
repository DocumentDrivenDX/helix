# T6a — marker absent, *.tf-only repo, heuristic fallback fires [MEDIUM RISK]

**Flow classification:** legacy heuristic fallback fixture. Retained to protect
pre-marker workspaces while documenting that marker-based flows are current
guidance.

## Scenario

Same install set as T6 but NO `.helix.yml`. Workspace contains
`main.tf` and nothing else relevant.

## Why it matters

Frozen heuristic fallback (design §1.3) — file pattern (`*.tf`)
dominates when repo shape is absent. helix-infra wins. The one-time
banner must surface.

This fixture is the regression guard for the infra branch of the
fallback path.

## What passes

- Fallback banner mentioning `.helix.yml` and the heuristic routing.
- `Write` against `docs/adr/<NNNN>-<slug>.md`.
- NO `Write` against `docs/helix/`.

## What fails

- Silent activation without banner.
- ADR written to `docs/helix/02-design/`.
- Setup-gap.

## Risk

MEDIUM. Regression guard for the FROZEN infra heuristic path.
