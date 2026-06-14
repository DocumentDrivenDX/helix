# T5a — marker absent, product-shaped repo, heuristic fallback fires [MEDIUM RISK]

**Flow classification:** legacy heuristic fallback fixture. Retained to protect
pre-marker workspaces while documenting that marker-based flows are current
guidance.

## Scenario

Same install set as T5 (helix-library + helix + helix-infra) but NO
`.helix.yml`. Repo is product-shaped: `docs/helix/01-frame/prd.md`
exists, no IaC files.

## Why it matters

This is the FROZEN heuristic fallback path (design §1.3). The
fallback fires the one-time banner ("No .helix.yml found. Activating
helix by heuristic ...") then activates the product methodology
because the repo shape dominates. The behavior must remain
unchanged from the prior design's §7.5 rules 1, 2, 5.

This fixture is the regression guard against breaking existing
installs that have not yet adopted the marker.

## What passes

- One-time fallback banner mentioning `.helix.yml` and the heuristic
  routing (allow_match_any).
- `Write` `tool_use` against `docs/helix/02-design/<NNNN>-<slug>.md`.
- NO `Write` against `docs/adr/`.

## What fails

- Silent activation without the banner (silent heuristic is the
  failure mode the marker exists to eliminate; the banner is the
  contract).
- ADR written to `docs/adr/`.
- Setup-gap (library resolution failed).

## Risk

MEDIUM. Heuristic fallback is FROZEN — no growth — so this fixture's
job is purely regression protection.
