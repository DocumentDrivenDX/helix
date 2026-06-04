# T18b — local override extends a non-existent library type

- **Installed:** `helix-library`, `helix`
- **Risk:** medium (parallel to T11 for the override surface)

## Scenario

`local:orphan-adr extends: library:not-a-real-base`. The base type
does not exist.

## Why it matters

Parallel to T11. T11 tests `binds: library:unknown` in `graph.yml`;
this fixture tests `extends: library:unknown` in an override spec.
Same risk class, different surface. Without it, the validator could
catch unknown types in graphs but silently accept them in overrides.

## Pass signature

Exit non-zero AND stderr matches one of the unknown-type messages
AND names the missing base type (`not-a-real-base`).
