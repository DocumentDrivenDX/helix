# T4 — library + helix-infra (happy path)

**Flow classification:** legacy sibling-flow fixture. Retained as a frozen
compatibility probe for the retired public `helix-infra` skill design.

## Scenario

`helix-library` and `helix-infra` are installed (no `helix`). The
workspace is a Terraform repo (`main.tf`, `terraform/modules/...`).

## Why it matters

The mirror of T3 for the infrastructure methodology. helix-infra
must resolve `library:adr` against the same library tree and write
ADRs into its canonical location (`docs/adr/`).

## What passes

A `Write` `tool_use` against `docs/adr/<NNNN>-<slug>.md` whose body
includes `library_type: library:adr` in the frontmatter.

## What fails

- Setup-gap fires (library resolver bug).
- ADR written to `docs/helix/02-design/` (precedence confusion — but
  this scenario does not have helix installed, so any helix-shaped
  path is a strong wrong signal).

## Risk

Low. Baseline regression for the infra side.
