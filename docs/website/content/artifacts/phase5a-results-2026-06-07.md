---
title: "Phase 5a results — canonical promotion targeted re-bench"
slug: phase5a-results-2026-06-07
weight: 480
activity: "Design"
source: "02-design/phase5a-results-2026-06-07.md"
generated: true
---
# Phase 5a results — canonical promotion targeted re-bench

## Headline

| Subset (24 rows) | Pre-port baseline | Phase 5a result | Delta |
|---|---|---|---|
| Stable_pass (3-of-3) | 0/24 | **7/24 (29.2%)** | **+7 rows, +29.2 pp** |
| Routing failure subset (27 rows) | 3/27 | 3/27 | +0 (description-saturated) |

The 24-row subset = 19 baseline-FFF conv rows + 5 new G* gap rows.
0/24 baseline because the 19 FFF rows were all-fail and the 5 G* rows didn't exist.

## Wins (7 stable_pass)

| Row | Why it now passes |
|---|---|
| AM-01-prd-cascade-manual | Inline §"Apply The Autonomy Level" — manual asks before every tool use, including Read |
| AM-02-prd-cascade-guided | Inline autonomy — guided pauses before first state-changing tool use |
| AM-05-adr-singleton-manual | Inline autonomy applied to ADR cascade |
| AM-06-adr-singleton-guided | Inline autonomy applied to ADR cascade |
| C003-prd-vision-orphan-no-marker | §2 marker-absent-no-heuristic clause: returns `{"active": []}` instead of improvising |
| C018-iterate-current-sprint | Internal routing modes drove the iterate behavior |
| **G1-spec-gap-orchestration** | New row — `scope_write_path` matcher (forbid `^docs/helix/`, allow `.workflow-scratch/`) — skill respected the operator's "do NOT modify specs" |

## Near-misses (signal there, not stable)

| Row | Result | Note |
|---|---|---|
| C008-manage-infrastructure-empty | [True, False, False] | First pass behaved; 2 + 3 didn't |
| C011-what-methodologies-active | [True, False, False] | Same flake pattern |
| G5-upstream-discovery | [True, True, False] | 2/3 — one bad sample away from stable |

## Stable fail (14)

C013, C014, C015, C016, C017, C024, CD-01, CD-03, CD-04, CF-02, CF-03, G2, G3, G4.

Common patterns to investigate in Phase 6:
- C014 "reject-unauthorized-flow" — skill engages despite marker not authorizing the flow
- C015, C016, C017 — "what's next" / "plan the rollout" — cross-flow query mode not driving the right output shape
- CD-01..04 — concern slot resolution defects
- CF-02, CF-03 — cross-flow query / cross-instance routing
- G2 — scale recalibration math discriminator too tight (needs more permissive regex)
- G3 — artifact canonicalization 3-conjunction may need looser middle clause
- G4 — orchestration-with-gates regex may not match Sonnet's natural phrasing

## Routing

Unchanged (3/27 PASS, same 3 rows as pre-port: RE-POS-005, 008, 028).
The body changes (autonomy, internal routing modes, activation discipline) are INVISIBLE to routing-evals — routing grades whether the Skill tool_use fires, not what the skill does after.

Multi-instance (MI-*) was 0/5 — same as baseline. Bench-grading limitation: the skill engages then SHOULD emit the disambiguation banner, but the bench's `Skill tool_use observed` check fires before the banner. Investigation for Phase 6.

## Cost

~$65 total (Sonnet, 27 routing + 24 conv × 3 passes = 99 probes total, ~$0.65/probe avg).

Under the $75 budget. Stage 5b ($260 full bench) deferred until Phase 6 closes the stable-fail rows.

## Ratchets

NOT seeded from Phase 5a — the 24-row subset is not comparable to the 36-row baseline that produced routing=0.6667 / conv=0.4722. Phase 5b (full bench) is the right surface for ratchet reset.
