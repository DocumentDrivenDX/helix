# T6 — *.tf repo, both methodologies installed [HIGH RISK]

## Scenario

`helix-library`, `helix`, and `helix-infra` are all installed. The
workspace contains `main.tf` and nothing else relevant (no
`docs/helix/`).

## Why it matters

Mirror of T5: file pattern (`*.tf`) is a strong infra signal in the
absence of helix repo shape. helix-infra must win.

## What passes

- `Write` `tool_use` against `docs/adr/<NNNN>-<slug>.md`.
- Prose MAY include a disambiguation banner.
- NO `Write` against `docs/helix/02-design/`.

## What fails

- ADR written to `docs/helix/02-design/` (helix silently won despite
  no helix repo shape).
- Setup-gap (library resolution failed).

## Risk

HIGH. Symmetric counterpart to T5; both must pass for the
"file-pattern dominates when repo-shape is absent" rule to hold.
