# RC-01 — v1 marker (`methodologies:`) loads under post-rename validator

**Category:** rename-compat (standalone) — codex review feedback
**Phase:** P12 (terminology rename: methodology → flow)
**Tier:** must_pass_core

## What this asserts

A `.helix.yml` written against the v1 schema — legacy `methodologies:` list,
`helix_version: 1` — MUST still load cleanly under the post-rename validator.
The rename is additive: the v1 key is a one-cycle alias that emits an M020
deprecation warning but does NOT block.

## Contract

Run `helix_check.py marker marker.yml`.

- exit code: `0` (clean)
- required codes: `M020`
- required diagnostic phrase: ``legacy `methodologies:` key``
- forbidden codes: `M040` (both-keys), `M041` (strict-v2 hard error)

## Why standalone

The P12 rename contract has only EMBEDDED coverage today: T01–T38 fixtures
pass both pre- and post-rename, which is a side-effect of correctness, not
an explicit gate. Codex flagged that a regression breaking v1 acceptance
could go silent (T01–T38 might still pass by other paths). RC-01..RC-04
make the four corners of the rename contract explicit and independently
discoverable.

## Files

- `marker.yml` — the v1 marker under test
- `expected-validator-output.txt` — golden validator output (humans read this)
- `expected.yml` — runner-consumed contract (`kind: validator-row`)
- `docs/helix/` — placeholder scope root so marker validation reaches M020
  (not M006 "missing root")
