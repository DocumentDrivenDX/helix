# EA-03 — Autonomous does NOT relax Edge Authority Asymmetry

**Category:** edge-asymmetry (plan §1.5b)
**Phase:** P4 (Edge Authority Asymmetry)
**Tier:** must_pass_core
**Invariant under test:** §0.5 Invariant 1 (design doc §2.7)

## What this asserts

Identical workspace to EA-01 (vision approved, FEAT-001 + FEAT-002
present, graph declares `prd informs feature-specification`
required:false). Only difference: `autonomy=autonomous`.

Per SKILL.md §10, autonomy levels do NOT relax this prohibition. The
skill may, under autonomous, proceed silently through in-scope writes
that are mechanically derivable from the operator's prompt (drafting
the PRD file at the correct activity path, filling template
boilerplate). It MUST NOT silently extend that license to populating
`ddx.links` from graph candidates the operator has not named.

## Polarity contrast with AM-03

The most likely place a skill implementer or prompt-tuner errs is by
reading the autonomy-matrix rows (AM-01..AM-08) and concluding that
`autonomous` means "no pre-write confirmation, period". That is true
for in-scope mechanical writes (which is what AM grades) — and false
for edge authoring (which is what EA grades).

AM-03 expects `confirmation_before_mutation == absent` in positive
(autonomous suppresses the pre-write confirmation). EA-03 expects
`confirmation_before_mutation == present` in positive (autonomous does
NOT suppress edge-candidate surfacing). The contrast is the structural
proof that the cascade-confirmation and the edge-deliberation are
different objects governed by different rules.

## Why the negative control is plugin removal, not autonomy swap

If we used `autonomy_swap` (e.g., swap to `guided`) as the negative
control, the verdict in both positive (autonomous) and negative
(guided) runs would be `present` — Invariant 1 holds at both autonomy
levels. The discriminator would be vacuous (T042 rejection). The
correct discrimination axis is skill presence: with the plugin
removed, the agent cannot consult `graph.yml` and so cannot enumerate
FEAT-001/FEAT-002 as `informs` candidates via the type-pair catalog.
Verdict flips present → absent on plugin removal, proving the
candidate-surfacing prose is skill-driven.

## Failure modes this catches

- **Autonomy-as-license.** Skill reads autonomy=autonomous and writes
  `ddx.links: [FEAT-001, FEAT-002]` without surfacing the candidates.
  This is the precise failure named in Invariant 1.
- **Post-hoc narration.** Skill writes the PRD with auto-populated
  ddx.links, then narrates "I linked FEAT-001 and FEAT-002 because the
  graph permits". The `prose_pattern_before_tool` matcher requires the
  deliberation prose to precede the first Write/Edit in stream order;
  post-hoc commentary does not satisfy.

## Halt condition

P4 halts on any EA-NN failure. EA-03 is the load-bearing row of the
phase — if autonomous silently auto-populates ddx.links, the
methodology's instance-edge traceability is no longer a function of
operator intent, and downstream cascade-grading rows become
non-evidence.
