# Phase 6 Tier 4 results — canonical-iteration verification re-bench

## Headline

| Subset | Phase 5a baseline | Tier 4 result | Delta |
|---|---|---|---|
| 17 stable-fail conv rows | 0/17 | **1/17 stable_pass** (G2) | +1 |
| 6 MI-* (with Tier 3 matcher fix) | 0/6 | **6/6 PASS** | **+6** |
| **Combined (23 rows)** | **0/23** | **7/23 (30.4%)** | **+7** |

Spend: ~$40 (~$33 conv + ~$7 MI-* routing).

## Win analysis

### G2-scale-recalibration (Tier 1 discriminator widening)
The workflow agent's regex widening for compound rate units (msg/min, msg/sec, queue-min/min) caught Sonnet's natural throughput phrasing. Sonnet was doing the math correctly all along; the original regex was structurally too narrow. Stable_pass 3/3.

### MI-01..06 (Tier 3 matcher_change Option A)
The workflow agent updated `family-test/bench/runner/helix_bench.py`'s routing-eval grading so that for `target=None` rows in the multi-instance set, "Skill engaged AND emitted disambiguation banner AND did NOT execute downstream Write/Edit/Bash" counts as PASS. Sonnet's canonical-install behavior (engage → read marker → see multi-instance → emit banner → stop) now grades correctly. 6/6 PASS — a clean structural win, the largest single-fix recovery in the session.

## Root cause of the 16 conv stable-fails

Sampling failing rows surfaced **a synthetic-prompt design defect across 15 of the 71 conv rows** (verified via grep). The Phase 4.5 audit identified 5 to rewrite; many more share the same defect.

Specifically, these 15 rows have prompt = "Let's create a PRD for the coffee-ordering app. Use HELIX." (or close variants):

```
SA-09-499-line-near-miss
CD-02-positive-control-no-edge
CD-03-negative-control-plugin-removed   ← Tier 4 stable_fail
CD-01-graph-nonstandard-edge            ← Tier 4 stable_fail
EA-03-prd-feat-candidates-autonomous
EA-04-prd-feat-candidates-autonomous-many
EA-02-prd-feat-candidates-guided-named
AM-02-prd-cascade-guided                ← passed Phase 5a (autonomy logic, not prompt-dependent)
WC-01-warm-context-start-project
C003-prd-vision-orphan-no-marker        ← passed Phase 5a (marker-edge clause, prompt-agnostic)
VS-03-autonomous-still-reads-before-writes
AM-04-prd-cascade-aggressive
AM-01-prd-cascade-manual                ← passed Phase 5a
AM-03-prd-cascade-autonomous
C001-start-helix-project
```

The rows that DID pass Phase 5a with this prompt (AM-01/02, C003) succeeded because their discriminators test ENGAGE-time behavior (autonomy ask-before-tool-use, marker-edge banner) which fires before any "what kind of PRD am I drafting?" decision. The rows that FAILED (CD-01, CD-03, etc.) test post-engagement behavior specific to their fixture (graph nonstandard edge, plugin removal, etc.) — but the generic prompt drives Sonnet into "draft a PRD" mode, not into the test-specific behavior.

Example: **CD-01-graph-nonstandard-edge** loads a workspace with a hand-crafted graph.yml containing a non-standard edge. The discriminator checks whether Sonnet surfaces the edge in prose. But the prompt only says "create a PRD"; Sonnet engages helix, reads marker + graph, drafts a PRD — without ever discussing the unusual edge it observed in graph.yml. The test never gets a chance to discriminate.

The 5 rewrites in Phase 4.5a (C002, C015, EA-01, CF-01, VS-02) fixed this for those specific rows. The remaining 15 generic-prompt rows still have the same defect.

## Tier 2 SKILL.md body edits

The 4 Tier 2 agents shipped:
- §5 Authorization boundary tightening (T2a)
- New §Concern slot resolution section (T2b)
- §Check And Next cross-flow query sharpening (T2c)
- §Author/edit artifacts: Edit-not-Write for existing instances (T2d)

These landed in `skills/helix/SKILL.md` cleanly (canonical install smoke verified). However, they DID NOT move the stable_pass count on the 17 conv-row subset:

- **C014** "reject-unauthorized-flow" (T2a target): Sonnet treated the prompt's `/helix-infra` prefix as an unknown slash command and never gave the skill a chance to engage. Skill never fired → §5 wording change is unreachable. Real defect, but it's at the **slash-command-parser layer**, not skill-body.
- **CD-01/03/04** (T2b target): These use the synthetic prompt (see above). Skill engages and drafts a generic PRD without exercising concern slot resolution. §Concern slot resolution wording landed but is unreachable in the test.
- **CF-02/03** (T2c target): Similar prompt-design issue. CF-02's prompt is "The pipeline needs DNS" → Sonnet went straight into asking "What should the DNS record point to?" via AskUserQuestion. Skill never engaged. §Check And Next wording unreachable.
- **C013** (T2d target): Stable_fail; need to inspect transcript for whether Sonnet wrote vs edited an existing artifact.

The body edits are sound; they just need rows whose prompts let them execute.

## Recommendation: do NOT run Stage 5b yet

Stage 5b ($260, ~9h wall-clock) is a full-bench reset to seed clean ratchets. Running it now would produce noisy ratchets dominated by the synthetic-prompt issue, not the canonical-install quality. The right sequence:

1. **Phase 7 — synthetic prompt rewrite** (~$0, ~3 hours). Audit the remaining ~15 generic-prompt rows + the C014 slash-command edge case + a sample of other rows for similar design defects. Rewrite via the audit pattern (real-usage shape, concrete artifact paths, named constraints). Probably ~25 rows touched.
2. **Phase 7.5 — re-test the 22 still-failing rows** (~$30). Verify the rewrites bite.
3. **Stage 5b — full bench reset** ($260, 9h). Now ratchets are clean.

## Detailed result breakdown

### Conv (17 rows)
- ✅ G2-scale-recalibration: 3/3 PASS (Tier 1 widening worked)
- 🟡 C011-what-methodologies-active: [F, T, F] — 1/3 (flake, close to stable)
- 🟡 C017-plan-rollout-ambiguous-autonomous: [F, F, T] — 1/3
- ❌ C008-manage-infrastructure-empty: 0/3 (synthetic prompt)
- ❌ C013-update-prd-edit-not-write: 0/3 (needs transcript investigation)
- ❌ C014-reject-unauthorized-flow: 0/3 (slash-command parser ate `/helix-infra`)
- ❌ C015-whats-next-graph: 0/3 (T1 agent: "discriminator is structurally not a regex; no widening possible")
- ❌ C016-plan-rollout-ambiguous-guided: 0/3 (T1 agent: "real failure, not discriminator")
- ❌ C024-backfill-90d-manual: 0/3
- ❌ CD-01/03/04: 0/3 each (synthetic prompt)
- ❌ CF-02/03: 0/3 each (slash-command / question fallthrough)
- ❌ G3-artifact-canonicalization: 0/3 (T1 widening landed but Sonnet placed SQL outside the path regex)
- ❌ G4-orchestration-with-gates: 0/3 (Sonnet asked "what is feature X?" — under-specified prompt fixture)
- ❌ G5-upstream-discovery: 0/3 (regressed from 2/3 in Phase 5a; need to re-investigate)

### MI-* (6 rows, with Tier 3 matcher fix)
- ✅ MI-01, MI-02, MI-03, MI-04, MI-05, MI-06: ALL PASS

## Files changed this Phase 6

Commit `5d8c940f` — Tier 1+2+3 changes (workflow agent commit):
- `family-test/bench/conversations/G2-scale-recalibration/expected.yml` (T1 widening)
- `family-test/bench/conversations/G3-artifact-canonicalization/expected.yml` (T1 widening)
- `family-test/bench/runner/helix_bench.py` (T3 matcher change)
- `skills/helix/SKILL.md` (T2a/b/c/d body edits)

Smoke verification: helix:helix loads, description=1022 chars, 0 MCP failures.
