---
status: deferred
---

# T8 — library + helix + helix-web [DEFERRED]

## Status

**Deferred legacy fixture.** `helix-web` was a proposed sibling methodology
plugin in the research fork. Current HELIX exposes one public `helix` skill
with internal flows; this file remains only as historical numbering ballast.

This fixture slot is reserved so that:

1. When `helix-web` lands as a third methodology, the numbering does
   not shift (T9–T13 stay where they are).
2. The intended precedence question (three methodologies co-active,
   web-shaped repo with `package.json`/`index.html`) is documented
   here as a TODO.

## Intended scenario (when helix-web exists)

- **Installed:** `helix-library`, `helix`, `helix-web`.
- **Workspace:** product-shaped repo PLUS `package.json` and `src/`.
- **Question:** does helix-web win for web-shaped product repos? Or
  does helix-the-product-methodology stay the spine and helix-web
  surface as an overlay?

## Why deferred

Per the FINAL plan §0, v1 family ships with only `helix-library +
helix + helix-infra`. A third methodology is out of scope until at
least one user requests it. Encoding precedence for an unbuilt
plugin would be speculative.

## What lives here

Only this README with `status: deferred` frontmatter. No
`workspace/`, no `prompts/`, no `expected/`, no
`plugins-installed.txt`.

**Runner rule (pinned):** the runner SKIPS a fixture iff its
`README.md` has top-level frontmatter `status: deferred`. Absence
of `plugins-installed.txt` is NOT a skip signal — it would be a
fixture-authoring error elsewhere. One rule, not "or alternatively."
