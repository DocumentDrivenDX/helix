# T29 — external_edge with required: true fails G104 [HIGH RISK]

**Flow classification:** current external-edge invariant. This fixture preserves
the `required: false` rule for cross-artifact references that leave the local
artifact graph.

## Scenario

A `graph.yml` declares an `external_edges:` entry with
`required: true`. The graph validator must hard-fail with G104 per
§2.2: cross-methodology requires is the deferred bilateral-mechanism
case; permitting required: true on external edges would silently
invalidate existing source-methodology instances when the edge ships.

## Why it matters

Without this check, methodology authors can ship an external edge
with required: true, and every existing PRD across every consumer
repo retroactively fails validation on the next library install.
That's the green→red-on-git-pull failure mode the verification-exit-
gate memory exists to prevent.

## What passes

- `helix_check.py graph` exits non-zero (G-class).
- `G104` violation citing the offending external_edges entry.

## What fails

- Exit 0.
- Diagnostic missing G104 code OR missing the bad edge's identifier.

## Risk

HIGH. This is the structural rule preventing retroactive
invalidation; without the test, the rule is a comment.
