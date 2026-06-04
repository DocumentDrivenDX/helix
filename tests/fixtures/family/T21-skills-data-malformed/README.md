# T21 — skills/_data malformed (negative companion to T20)

- **Installed:** `helix-library` with a broken SKILL.md
- **Risk:** medium (validates the workaround is enforced)

## Scenario

`plugin.json` references `skills/_data` but the SKILL.md has
unterminated frontmatter and is missing required fields. Install
must fail with a diagnostic.

## Why it matters

T20 proves the workaround works when correct. T21 proves the
workaround is enforced — a malformed SKILL.md does not silently
mount a broken skill. Without T21 the architecture could pass T20 in
CI while production users ship broken workarounds undetected.

## Pass signature

Install exits non-zero AND stderr surfaces a diagnostic mentioning
malformation/invalid/frontmatter/yaml.

## Failure signatures

- Install exits 0 → silent mount of a broken skill.
- Install fails but stderr is unrelated → diagnostic does not
  identify the SKILL.md as the cause.
