# T25 — artifact-instance link violates artifact graph → G201 [HIGH RISK]

**Flow classification:** current artifact-instance link control. This fixture
does not define a scope-instance or multi-flow routing rule.

## Scenario

Same setup as T24 but PRD-001 declares `kind: requires` toward
FEAT-001. The graph only permits `informs` between prd and
feature-specification — `requires` is not declared.

## Why it matters

This is the central enforcement test for the artifact graph
(§3.1 check 2 + §4.6 example (c)). If wrong-kind edges aren't
caught, the graph is decoration and `ddx.links:` becomes
unauditable. The diagnostic must name BOTH the offending kind AND
the allowed kinds — otherwise authors can't act on the failure.

## What passes

- Non-zero exit.
- `G201` violation citing source type, kind, target type, and the
  allowed-kinds list.

## What fails

- Exit 0 (silent acceptance).
- Diagnostic missing source/kind/target identifiers.

## Risk

HIGH. Wrong-kind detection is the validator's load-bearing guarantee that
artifact links are governed by the graph, not advisory prose.
