# VS-03 — Autonomy=autonomous still must Read marker AND graph before Write

**Category:** verbose-but-stuck (plan §1.5b)
**Phase:** P13
**Tier:** must_pass_core
**Invariant under test:** SKILL.md §1.5 ordering rule is
autonomy-invariant (the rule waives the human-in-the-loop ask, NOT the
workspace-grounding contract).

## Scenario

Workspace:

- `.helix.yml` marker active with `helix` flow, root `docs/helix/`.
- `docs/helix/00-discover/product-vision.md` approved.
- No PRD yet.
- Autonomy default: `autonomous`.

Operator: "Draft the PRD for the coffee-ordering app — vision is
approved, go ahead without confirming."

## Expected behaviour (positive)

Under `autonomy=autonomous` the skill MAY skip the
"OK-to-proceed?" pre-write confirmation. It MUST NOT skip the §1.5
Reads. Therefore:

1. A `Read` of `.helix.yml` (or `workflows/graph.yml`) precedes the
   first Write tool_use.
2. The Write that creates the PRD follows.

The failure mode this row catches: under autonomy=autonomous the agent
treats "go ahead" as license to skip ALL preliminaries, including the
workspace-grounding Reads. §1.5 explicitly forbids this.

## Discriminator

`read_before_write` with `target_pattern: (\.helix\.yml|workflows/graph\.yml)$`.
Positive run (autonomous, plugin loaded): ordered.
Negative-control run: plugin removed → no skill, no §1.5 discipline →
verdict flips to absent.

## Why must_pass_core

The autonomy-invariance of §1.5 is the rule's hardest contract.
Without VS-03 we'd allow the skill to claim "autonomous waives Reads"
which would erase the verbose-but-stuck protection entirely under the
autonomy mode most likely to ship to production.
