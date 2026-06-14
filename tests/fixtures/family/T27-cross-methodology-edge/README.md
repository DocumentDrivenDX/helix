# T27 — cross-methodology informs edge resolves [HIGH RISK]

**Flow classification:** legacy sibling-flow fixture. Retained as compatibility
evidence for the old cross-methodology design; it is not current user guidance
for the single public `helix` skill and flow marker model.

## Scenario

Marker declares helix + helix-infra. helix `graph.yml`
`external_edges:` authorizes `prd informs helix-infra:change-intent`.
PRD-001 declares `{ kind: informs, to: "helix-infra:CI-001",
cross_methodology: true }`. helix-infra's instance corpus contains
CI-001.

## Why it matters

Positive cross-methodology path. The validator must:
1. Detect cross_methodology: true on the link.
2. Look up the edge in helix.external_edges (not edges).
3. Resolve "helix-infra:CI-001" against helix-infra's instance_index
   (not helix's).
4. Exit clean.

Pairs with the I120/I121 warning fixtures (deferred to v1.1 small).

## What passes

- Exit 0.
- No I120, I121, or G140 records.

## What fails

- Exit nonzero.
- Treating the cross-methodology id as a local id (would resolve as
  unresolved → I101).

## Risk

HIGH. Without this, cross-methodology informs is theory not contract.
