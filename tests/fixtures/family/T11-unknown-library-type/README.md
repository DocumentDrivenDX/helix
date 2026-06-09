# T11 — nonexistent library type rejected

## Scenario

`helix-library` and `helix` installed. The workspace has a malformed
`graph.yml` whose node `binds: library:not-a-real-type` (correctly
namespaced, but no such type exists in the library).

## Why it matters

The validator must catch typos and stale references. A node bound to
a missing library type would silently produce broken activity walks
at runtime.

## What passes

Validator exits non-zero; stderr names the missing type and the rule
(`unknown library type` / `not found in library`).

## What fails

Validator passes silently — methodology routes to a missing type at
runtime.

## Risk

Medium. Validator contract; catches typos early.
