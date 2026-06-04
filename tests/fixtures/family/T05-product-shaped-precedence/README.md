# T5 — product-shaped repo, both methodologies installed [HIGH RISK]

## Scenario

`helix-library`, `helix`, and `helix-infra` are all installed. The
workspace is a **product-shaped** repo: `docs/helix/01-frame/prd.md`
and `docs/helix/02-design/` exist; NO Terraform files; NO
`terraform/` directory.

## Why it matters

This is the precedence test for "two methodologies co-active, repo
shape unambiguous." Per design §7.5:

- Repo shape is the strongest signal.
- A repo with `docs/helix/` and no IaC files is product-shaped.
- helix wins; helix-infra stays silent (or surfaces a banner the
  user can override).

If precedence is wrong here, the family is broken — every dual-install
user gets ADRs in the wrong location.

## What passes

- `Write` `tool_use` against `docs/helix/02-design/<NNNN>-<slug>.md`.
- Prose MAY include a disambiguation banner offering helix-infra as
  an override.
- Prose MUST NOT contain a Write against `docs/adr/`.

## What fails

- ADR written to `docs/adr/` (helix-infra silently won).
- Two writes (both methodologies fired).
- Setup-gap (library resolution failed).

## Risk

HIGH. Wrong-methodology routing is the central risk of co-activation.
