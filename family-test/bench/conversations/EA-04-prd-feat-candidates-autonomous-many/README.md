# EA-04 — Expanded candidate set; autonomous; robustness against memorisation

**Category:** edge-asymmetry (plan §1.5b)
**Phase:** P4 (Edge Authority Asymmetry)
**Tier:** must_pass_core
**Invariant under test:** §0.5 Invariant 1 (design doc §2.7)

## What this asserts

Same shape as EA-03 (autonomous, vision approved, graph declares
`prd informs feature-specification` required:false) but the workspace
contains FOUR pre-existing feature-specifications instead of two:
FEAT-001..FEAT-004. All four are concrete graph candidates the skill
must enumerate before populating `ddx.links`.

## Why a 4-FEAT variant exists

Two failure modes the 2-FEAT rows (EA-01..EA-03) do not catch:

1. **Phrase-memorisation overfit.** A prompt-tuner reading EA-01..EA-03
   could pattern-match "EA rows expect FEAT-001 and FEAT-002 in prose"
   and add a template line. That template fails EA-04, where FEAT-003
   and FEAT-004 also need surfacing. EA-04 is the corruption-resistance
   row analogous to CD-04 in the cascade-discrimination category.
2. **Mechanical fill at scale.** A skill that mechanically populates
   `ddx.links` faces a slightly larger temptation at 4 candidates
   ("graph permits all; populate all"). EA-04 raises the cost of that
   failure mode and discriminates it from a 2-candidate auto-populate
   that might be hand-waved as "obvious from prompt context".

## Discriminator floor: `min_distinct_captures: 2`

The matcher requires the deliberation-prose pattern to capture at
least TWO distinct FEAT ids before the first mutation. The SKILL.md
§10 contract calls for ENUMERATION of candidates; naming one of four
is under-enumeration and treats one candidate as authoritative without
basis. The floor of 2 (50% of candidates) is the minimum that detects
under-enumeration without demanding exhaustive listing — which may be
inappropriate in some skills' summarisation style.

## Negative control

Same as EA-03: `plugins_remove: [methodology-product]`. The
discrimination is sharper here than at 2 candidates: skill-driven
enumeration scales with the number of workspace candidates; an agent
guessing from prompt text alone is unlikely to name multiple specific
FEAT ids it cannot see in any graph. Verdict flips present → absent
robustly.

## Halt condition

P4 halts on any EA-NN failure. EA-04 is the robustness floor — if
EA-01..EA-03 pass and EA-04 fails, the conclusion is that the skill
has a phrase-memorised win on the smaller cases that does not
generalise; the asymmetry contract is being satisfied by accident, not
by mechanism.
