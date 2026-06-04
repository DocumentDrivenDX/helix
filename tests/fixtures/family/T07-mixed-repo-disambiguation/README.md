# T7 — mixed repo, both signals present [HIGH RISK]

## Scenario

`helix-library`, `helix`, and `helix-infra` are all installed. The
workspace contains BOTH `docs/helix/01-frame/prd.md` AND `main.tf`.
Both methodology signals are present.

## Why it matters

This is the **ambiguous** precedence case. Per design §7.5:

- When both signals exist, **the methodology must not silently pick**.
- The disambiguation banner must surface BOTH methodologies and ask
  the user (or rely on `HELIX_METHODOLOGY` env override).
- A `Write` before disambiguation is a silent pick — fixture fails.

## What passes

- The first turn surfaces a disambiguation banner naming both
  helix and helix-infra.
- NO `Write` `tool_use` fires before the user has disambiguated.
- The assistant prompts the user to pick or to set
  `HELIX_METHODOLOGY`.

## What fails

- A `Write` fires anywhere on turn 1 (silent pick).
- Disambiguation banner only names one methodology.

## Risk

HIGH. This is the case the design explicitly calls out as
"informative, not silent" — if it fails, users in mixed repos get
nondeterministic routing.
