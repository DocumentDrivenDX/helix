# RC-03 — mid-migration marker (both `methodologies:` AND `flows:`) is rejected

**Category:** rename-compat (standalone) — codex review feedback
**Phase:** P12 (terminology rename: methodology → flow)
**Tier:** must_pass_core
**Flow classification:** marker-key rename compatibility. This row rejects a
mixed spelling during the rename; it is not artifact-link or scope-instance
coverage.

## What this asserts

A `.helix.yml` that carries BOTH the legacy `methodologies:` key AND the v2
`flows:` key is a mid-migration artifact. The author renamed one entry and
left another behind. The validator MUST reject this with a marker-class
hard error (`exit=4`, code `M040`) and the diagnostic MUST name BOTH keys so
the author sees what to fix.

There is no quiet "pick the first one" or alphabetical winner — the rename
contract requires a single authoritative list.

## Contract

Run `helix_check.py marker marker.yml`.

- exit code: `4` (M-class marker violation)
- required codes: `M040`
- required diagnostic phrases: ``methodologies:``, ``flows:``
- forbidden codes: `M001` (the generic schema error this used to collapse into)

## Validator extension

`M040` is added as a NEW code distinct from `M001`. Previously this case fired
`M001` (generic "schema bad"); RC-03 promotes it to its own code so a
mid-migration regression is independently observable.

## Why standalone

T01–T38 never hit this case (none of them carry both keys). Without RC-03 a
regression that silently picked one list and ignored the other would go
undetected.

## Files

- `marker.yml` — the both-keys marker under test
- `expected-validator-output.txt` — golden validator output
- `expected.yml` — runner-consumed contract (`kind: validator-row`)
- `docs/helix/`, `pipelines/` — placeholder scope roots (unreached;
  validation fails at M040 before scope resolution)
