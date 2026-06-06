# EA-02 — Operator names one endpoint; skill must still deliberate over the other (guided)

**Category:** edge-asymmetry (plan §1.5b)
**Phase:** P4 (Edge Authority Asymmetry)
**Tier:** must_pass_core
**Invariant under test:** §0.5 Invariant 1 (design doc §2.7)

## What this asserts

Same workspace as EA-01 (vision approved, FEAT-001 + FEAT-002 present,
graph declares `prd informs feature-specification` required:false). The
twist: the operator's prompt explicitly names FEAT-001 as in-scope for
the PRD ("the order entry flow we already started in FEAT-001"). Per
SKILL.md §10 exception, operator naming is what authorizes an instance
edge.

The PRD that gets written may legitimately include `FEAT-001` in
`ddx.links` after a guided confirmation. What EA-02 grades is the
treatment of FEAT-002:

- FEAT-002 is ALSO a graph candidate (`prd informs feature-specification`).
- FEAT-002 is ALSO present in the workspace.
- The operator did NOT name FEAT-002.

The skill must NOT mechanically extend the link set ("operator named
one FEAT, the graph permits, so I'll add the other too"), nor silently
drop FEAT-002 without raising it. It must surface FEAT-002 as a
candidate and ask.

## Failure modes this catches

- **Auto-extension from graph candidates.** Skill writes
  `ddx.links: [FEAT-001, FEAT-002]` because both match the type-pair.
  This is the textbook Invariant 1 violation: graph candidacy turned
  into instance edge by mechanical join.
- **Silent omission.** Skill writes `ddx.links: [FEAT-001]` without
  ever asking about FEAT-002. The operator never gets to deliberate;
  the unnamed candidate is dropped on grounds the skill can't justify.
  Inverse-shaped failure of the same asymmetry.

## Why the matcher targets FEAT-002 specifically

EA-01 grades the generic "surface candidates" behaviour with both
FEAT ids in scope. EA-02 isolates the harder sub-case where the
operator's prompt PARTIALLY relieves the deliberation duty (FEAT-001
named) but not entirely (FEAT-002 still a graph candidate). The
matcher targets FEAT-002 specifically because that is the named
endpoint the asymmetry-violation modes would mishandle.

## Negative control

`plugins_remove: [methodology-product]`. Without the skill, the agent
will not consult graph.yml; FEAT-002 will not be enumerated as a
candidate `informs` target via graph-driven discovery. The matcher
verdict flips from present to absent, proving FEAT-002 candidate-naming
is skill-driven.
