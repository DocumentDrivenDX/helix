# T12b — section_aliases removed (negative companion to T12)

- **Installed:** `helix-library`, `helix`
- **Risk:** medium (validator-honesty)

## Scenario

Identical ADR document to T12 (uses the alias `## Outcome` instead of
the canonical `## Decision`), but `methodology.yml` declares NO
`section_aliases`. The validator must reject the doc with a
"missing Decision" diagnostic.

## Why it matters

T12 alone is necessary but not sufficient. A broken validator that
SKIPS all `required_sections` checks for `library:adr` passes T12 for
the wrong reason. T12b proves the alias is the load-bearing input: if
the alias is removed, the same doc must fail. Positive + negative pair
pins the contract.

## Pass signature

`python3 library/scripts/helix_graph_check.py --methodology
workspace/methodology.yml workspace/docs/adr/0001-pick-postgres.md`
exits non-zero AND stderr matches `(?i)missing.*decision`.

## Failure signatures

- Exit 0 → validator is not enforcing required_sections at all.
- Exit non-zero but stderr does not mention "Decision" → diagnostic is
  not actionable.
