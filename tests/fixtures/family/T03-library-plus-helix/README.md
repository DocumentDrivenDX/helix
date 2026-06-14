# T3 — library + helix (happy path)

**Flow classification:** current single-skill baseline. Mentions of other
historical skill ids are negative controls only.

## Scenario

Both `helix-library` and `helix` are installed. Workspace is a normal
helix product repo (`docs/helix/01-frame/prd.md` present).

## Why it matters

The default happy-path install. The methodology resolves
`library:prd` against the library tree; editing a section uses the
library schema; no setup-gap, no precedence ambiguity.

## What passes

The agent invokes `Edit` or `Write` against the existing PRD path
to add a Risks section. Library resolution worked (no setup-gap).

## What fails

- Setup-gap fires despite library being installed (resolver bug).
- Agent writes to a non-helix path (precedence confusion despite no
  helix-infra signal).

## Risk

Low. Baseline regression check.
