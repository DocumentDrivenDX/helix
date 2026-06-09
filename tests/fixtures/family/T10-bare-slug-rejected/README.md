# T10 — bare slug rejected

## Scenario

`helix-library` and `helix` installed. The workspace has a malformed
`graph.yml` whose node `binds: adr` (a bare slug, missing the
`library:` or `local:` namespace).

## Why it matters

Per design §7.3 + §10, bare slugs are **rejected** by the validator.
The two-namespace scheme exists exactly so that "did the author mean
library:adr or local:adr?" is never ambiguous. A bare slug is always
an error.

## What passes

`python3 library/scripts/helix_graph_check.py` (or equivalent
validator entry point) exits non-zero and stderr names the offending
node and the rule (`bare slug` / `must be namespaced`).

## What fails

Validator accepts the bare slug (rule not enforced) — silent
ambiguity in the family.

## Risk

Medium. Pure validator contract; not a runtime methodology bug.
