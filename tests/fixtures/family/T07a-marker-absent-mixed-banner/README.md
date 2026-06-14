# T7a — marker absent, mixed repo, disambiguation banner [HIGH RISK]

**Flow classification:** legacy heuristic fallback fixture. Retained to protect
pre-marker workspaces while documenting that marker-based flows are current
guidance.

## Scenario

Same install set as T7 but NO `.helix.yml`. Workspace contains BOTH
`docs/helix/01-frame/prd.md` AND `main.tf`. Both heuristic signals
fire.

## Why it matters

This is the OLD T07 case: with no marker AND both signals present,
the heuristic fallback's tie-break is FROZEN at "informative, not
silent" — the skill MUST surface a disambiguation banner naming BOTH
methodologies and ask the user to disambiguate (or set
`HELIX_METHODOLOGY`, or create `.helix.yml`).

A `Write` before disambiguation is a silent pick — fixture fails.

## What passes

- Disambiguation banner naming BOTH `helix` (bare) and `helix-infra`.
- NO `Write` `tool_use` fires before disambiguation.
- The assistant prompts the user to pick, set
  `HELIX_METHODOLOGY`, or run `init-marker`.

## What fails

- A `Write` fires anywhere on turn 1 (silent pick).
- Banner names only one methodology.
- Banner does not mention the marker as the fix.

## Risk

HIGH. Mirrors the old T07 high-risk contract; the marker-absent path
is the regression backstop that ensures dual-signal ambiguity stays
loud.
