# T13 — plugin.json with no skills field [HIGH RISK]

## Scenario

A `plugin.json` for `helix-library` that deliberately omits the
`skills:` field. The fixture attempts to install the plugin via the
Claude Code marketplace machinery and observes the result.

## Why it matters

This is **risk #2 in the FINAL plan** made into a test: does Claude
Code accept a data-only plugin (no skills)?

- If install succeeds → the architecture stands as designed; the
  library is a pure data tree mounted under `~/.claude/plugins/`.
- If install fails with "missing skills field" → the architecture
  must fall back to the documented workaround: ship a
  `skills/_data/SKILL.md` whose frontmatter declares a negative
  trigger so it never routes but still mounts the tree. Tradeoff:
  noise in `skills list`.

This fixture is the **load-bearing test for the architecture**.
A red T13 forces the workaround across the family.

## What passes

`claude plugin install <fixture-marketplace>` (or the harness
equivalent) exits 0; the library tree is mounted at the expected
path. The captured stderr is empty or informational.

## What fails

Install exits non-zero with a stderr message matching `missing
skills` / `required field skills` / `invalid plugin.json`. On
failure the README must be updated to record the actual Claude Code
behaviour, and the FINAL plan's workaround becomes the active path.

## Risk

HIGH. This is one of the two architectural questions that cannot be
answered from the docs alone (the other is plugin loader mount path
predictability, risk #1).
