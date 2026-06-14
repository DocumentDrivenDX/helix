# RC-02 — v2 marker (`flows:`) loads silently, no M020

**Category:** rename-compat (standalone) — codex review feedback
**Phase:** P12 (terminology rename: methodology → flow)
**Tier:** must_pass_core
**Flow classification:** marker-key rename compatibility. This row covers the
canonical `flows:` key on the compatibility marker shape; it is not
`helix_version: 2` strict-link or strict-marker coverage.

## What this asserts

A `.helix.yml` written against the v2 schema — canonical `flows:` list — MUST
load cleanly AND MUST NOT trigger M020. The rename deprecation warn is
specific to the legacy `methodologies:` spelling; authors who migrated should
see no rename-related noise.

## Contract

Run `helix_check.py marker marker.yml`.

- exit code: `0` (clean)
- forbidden codes: `M020` (must not fire on v2 markers), `M040`, `M041`

## Why standalone

Paired with RC-01: RC-01 proves v1 still loads, RC-02 proves v2 is silent.
Together they pin both sides of the additive rename contract so neither
regression can hide in T01–T38 side-effects.

## Files

- `marker.yml` — the v2 marker under test
- `expected-validator-output.txt` — golden validator output
- `expected.yml` — runner-consumed contract (`kind: validator-row`)
- `docs/helix/` — placeholder scope root
