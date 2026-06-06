# RC-04 — strict v2 marker rejects legacy `methodologies:` key

**Category:** rename-compat (standalone) — codex review feedback
**Phase:** P12 (terminology rename: methodology → flow)
**Tier:** must_pass_core

## What this asserts

When a `.helix.yml` declares `helix_version: 2`, the author has explicitly
opted into the v2 schema. Continuing to use the legacy `methodologies:` key
is a self-contradiction (v2 + v1 spelling) and MUST escalate from M020
(deprecation warn at v1) to a hard error (M041, exit 4). The diagnostic
MUST instruct the author to rename the key.

## Contract

Run `helix_check.py marker marker.yml`.

- exit code: `4` (M-class marker violation)
- required codes: `M041`
- required diagnostic phrases: ``helix_version: 2``, ``rename``, ``flows:``

## Validator extension

`M041` is added as a new code distinct from `M020`. Strictness is **implicit**
in the marker — `helix_version: 2` IS the opt-in; no separate `--strict-v2`
CLI flag is needed. The contract is: "you declared v2; we hold you to it".

## Why standalone

T01–T38 never exercise this case (none of them combine v2 declaration with
the legacy key). RC-04 makes the v2-strictness contract explicit so it
cannot quietly regress to "M020 warn" — which would silently undermine the
v2 schema gate.

## Files

- `marker.yml` — the strict-v2-with-legacy-key marker under test
- `expected-validator-output.txt` — golden validator output
- `expected.yml` — runner-consumed contract (`kind: validator-row`)
- `docs/helix/` — placeholder scope root
