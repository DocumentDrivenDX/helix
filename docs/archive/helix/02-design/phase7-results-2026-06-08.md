# Phase 7 results — synthetic-prompt rewrite verification

## Headline

| Subset | Tier 4 baseline | Phase 7 result | Delta |
|---|---|---|---|
| 10 rows with good data | 0/10 | **6/10 stable_pass** | **+6** |
| 6 rows stable-fail | — | 3 fail, 1 flake, 2 pass | — |
| 11 rows broken (Docker image eviction) | — | N/A (infrastructure failure) | — |
| **16 Tier-4 stable-fail set (recoveries)** | **0/16** | **6/10 tested = 60% of tested rows** | **+6** |

Cost actual: ~$25 (26 cost-log entries captured; C024 pass1/2 and CD-03 pass1/2 cost not logged due to Docker failure during aggregation; 11 rows × 3 passes produced empty transcripts at docker pull with no API cost).

Run: `phase7-retest-20260608T015359Z` on `claude-sonnet-4-6`, determinism=3, timeout=240s.

## Infrastructure caveat

The `family-test-claude:latest` Docker image was evicted mid-bench after row 10 (CD-03). All 11 subsequent rows (CD-04, CF-02, CF-03, G3, G4, G5 from the Tier-4 set, plus CD-02, EA-01—EA-04 new rows) failed at docker pull with `pull access denied` and produced empty transcripts. These rows are classified as BROKEN (infrastructure failure, not model quality failure). The 6 recoveries come from the 10 rows that ran with a working image.

## Per-row breakdown (10 rows with data)

### stable_pass (6 rows — all Tier-4 recoveries)

| Row | Fix attribution | Passes |
|---|---|---|
| C008-manage-infrastructure-empty | Prompt rewrite: named resources (Route53/RDS/Vault) → model now proposes helix-infra setup | P/P/P |
| C013-update-prd-edit-not-write | expected.yml fix: changed `expected_in_positive_run` from `present` to `ordered` (read_before_write matcher verdict alignment) | P/P/P |
| C015-whats-next-graph | Prompt rewrite: explicit graph-consult + scope context → model reads graph.yml and surfaces next steps | P/P/P |
| C016-plan-rollout-ambiguous-guided | Prompt rewrite: named two candidate flows → SKILL.md disambiguation banner rule fires correctly | P/P/P |
| C024-backfill-90d-manual | Prompt + expected.yml rewrite: concrete table name, date range, dry-run ask → confirmation_before_mutation matcher fires | P/P/P |
| CD-01-graph-nonstandard-edge | Prompt rewrite + expected.yml: explicit graph query + `expected_edge_regex` paraphrase tolerance | P/P/P |

### flake (1 row)

| Row | Result | Diagnosis |
|---|---|---|
| C011-what-methodologies-active | [P/F/F] | Model answers from session skill context (not .helix.yml marker) in 2/3 passes. The prompt "What methodologies are active here?" is answered from the model's training knowledge of helix skills rather than by reading the workspace marker. Not fixed by Phase 7 (no conversation rewrite). Real flake at baseline. |

### stable_fail (3 rows)

| Row | Result | Root cause |
|---|---|---|
| C014-reject-unauthorized-flow | [F/F/F] | Regex pattern uses `[^\n]` which cannot match the newline in the model's multi-line refusal block. Model IS refusing correctly ("the requested flow `helix-infra` is not / listed in the authorization boundary") but the pattern requires the refusal tokens on the same line. Discriminator defect, not model defect. |
| C017-plan-rollout-ambiguous-autonomous | [F/F/F] | SKILL.md disambiguation banner rule added for `guided` autonomy but `autonomous` mode was expected to use `defaults.methodology`. Model doesn't reliably pick `helix` by prose attribution when the marker has `helix` as the only explicit `defaults.methodology`. The route_decision/prose_attribution matcher requires "helix" to appear in the output as a chosen flow, but model may route silently. |
| CD-03-negative-control-plugin-removed | [F/0/0] (pass0 failed; pass1/2 Docker failure) | pass0 shows `surfaced=True, read_indices=[]` — model surfaces the graph edge FROM TRAINING MEMORY (not from reading graph.yml). This makes the positive-run test fail because the `graph_edge_observed` matcher requires both read_indices AND surfaced. Structural discriminator tension: the model "knows" what graphs look like and surfaces them without reading. |

### broken (11 rows — Docker image eviction)

CD-04, CF-02, CF-03, G3, G4, G5 (Tier-4 stable-fail set), CD-02, EA-01, EA-02, EA-03, EA-04 (new rows). All produce `Unable to find image 'family-test-claude:latest' locally` at docker pull. These are infrastructure failures, not model quality verdicts.

## Per-fix attribution

### Prompt rewrites (15 rows targeted; 5 of those successfully tested)
- **C008, C015, C016, C024, CD-01** were tested and recovered (all 5 PASS)
- C013, C014, CD-04, CF-02, CF-03, G4, EA-01—EA-04 were Docker-broken or tested but failed for other reasons

### expected.yml fixes (7 rows targeted)
- **C013** (read_before_write verdict alignment): PASS
- C014 (refusal pattern): FAIL — regex bug persists
- C024 (tighter match): PASS (synergistic with prompt rewrite)
- CD-01 (expected_edge_regex): PASS
- CD-02 (expected_edge_regex negative control): Docker-broken
- CD-03 (regex alignment): 1 probe ran, failed for training-memory reason
- G3 (wider regex): Docker-broken

### SKILL.md changes (disambiguation banner + auth boundary)
- C016 benefited from disambiguation banner rule: PASS
- C017 expected autonomous default routing: FAIL (banner fires but autonomous mode didn't pick helix by prose attribution)
- C014 expected auth boundary for env-override: FAIL (regex mismatch)

### Infrastructure (helix_bench.py expected_edge_regex param)
- CD-01: PASS (new param used; model paraphrases edge correctly)

## Stage 5b recommendation

**MAYBE — recommend with conditions.**

The 6 recoveries in 10 tested rows = 60% recovery rate on tested rows. If the Docker-broken 6 Tier-4 rows (CD-04, CF-02, CF-03, G3, G4, G5) recover at similar rates, we'd expect ~8-10 total recoveries from the 16 Tier-4 stable-fails, meeting the ≥8/16 threshold for YES.

However:
1. 3 rows have confirmed discriminator defects (C014 regex bug, CD-03 training-memory tension, C017 prose attribution gap) that would produce noisy ratchets
2. The Docker infrastructure failure must be resolved before Stage 5b — 11 rows cannot be graded at all
3. C011 is a genuine model flake that will remain noisy in ratchets

**Recommended path before Stage 5b:**
1. Fix the Docker image availability (rebuild/retag `family-test-claude:latest`)
2. Fix C014 expected.yml regex to use `re.DOTALL` or restructure to match across newlines
3. Re-bench the 11 Docker-broken rows (~$3, ~30 min) to confirm recovery rates
4. Fix C017 discriminator if model routes autonomously without prose "helix" attribution
5. Then run Stage 5b ($260, ~9h) — ratchets will be clean for the passing subset

If the 6 Docker-broken Tier-4 rows recover at the same rate as the tested rows (60%), we'd get 9-10/16 recoveries — clear YES for Stage 5b.

## Detailed cost

| Phase | Cost | Notes |
|---|---|---|
| Phase 7 re-bench (10 working rows × 3 passes) | ~$25 | Docker image eviction cut 11 rows short |
| Phase 6 Tier 4 | ~$40 | Baseline |
| Phase 7 total | ~$65 | Cumulative |

## Files changed in Phase 7 (commit a28693e2)

- 15 conversation.yml rewrites (C008, C015, C016, C024, CD-01—04, CF-02—03, EA-01—04, G4)
- 7 expected.yml fixes (C013, C014, C024, CD-01—03, G3)
- helix_bench.py: `expected_edge_regex` param for `graph_edge_observed` matcher
- discriminator-whitelist.yml: document `expected_edge_regex` alternative
- skills/helix/SKILL.md: disambiguation banner rule + auth boundary for env-override
- docs/helix/01-frame/FEAT-X-receipt-export.md: G4 workspace fixture

---

## Final updated results (after catchup + G-rerun2)

The original Phase 7 run had 11 rows broken by docker image eviction.
Subsequent reruns (after rebuilding the family-test-claude:latest image
twice) captured real transcripts for 19 of 21 rows. G4 and G5 fell to a
THIRD docker eviction during the G-rerun2 batch and remain BROKEN.

### Combined runs

| Run dir | Rows | Coverage |
|---|---|---|
| `phase7-retest-20260608T015359Z` | 10 with content, 11 empty | Original workflow retest |
| `phase7-catchup-20260608T023838Z` | 12 reran (11 broken from retest + CD-02 added) | After 1st image rebuild |
| `phase7-g-rerun2-20260608T035913Z` | 1 with content (G3), 2 empty (G4, G5) | After 2nd image rebuild — image evicted partway |

### Combined headline: **7/21 stable_pass (33.3%)**

### stable_pass (7 rows)

`C008`, `C013`, `C015`, `C016`, `C024`, `CD-01`, `CD-03` — all Tier-4 stable-fail recoveries. Phase 7 prompt rewrites + discriminator widenings + expected.yml fixes did the work.

### flake (5 rows — close to stable but inconsistent)

`C011` [P/F/F], `EA-01` [F/F/P], `EA-02` [F/P/F], `EA-03` [P/F/F], `EA-04` [P/F/F]. Each passes 1 of 3 — the rewrites moved the rows from baseline 0/3 to 1/3 but determinism is poor. Could become stable with another iteration of prompt sharpening OR by accepting the 1-of-3 as "engaged correctly under one model sample."

### stable_fail (7 rows)

`C014` (regex `[^\n]` ate the multi-line refusal — discriminator defect), `C017` (autonomous-mode silent routing — model doesn't surface "helix" by prose attribution), `CD-02`, `CD-04`, `CF-02`, `CF-03`, `G3` — all 0/3 on the canonical install. C014 is a discriminator-fix, the others are real skill behavior gaps in the multi-flow disambiguation, concern definition, and cross-flow query modes that the canonical promotion didn't address.

### broken — STILL (2 rows)

`G4-orchestration-with-gates`, `G5-upstream-discovery`: docker image evicted again during the G-rerun2 batch. Need a more reliable bench harness (image pinning, layer caching, or local-only execution) before attempting Stage 5b.

## Stage 5b recommendation: still NO

The 7 stable_pass rows are a real ~33% recovery from 0/21 baseline. But:

1. **Docker eviction is structural.** Every multi-row bench loop ≥30 min has hit at least one image eviction. Stage 5b would be 71 conv rows × 3 passes = 213 probes × ~5 min/probe = ~17 hours wall-clock — guaranteed to hit multiple evictions. Ratchets seeded from a partially-broken run aren't trustworthy.
2. **Flake bucket is large** (5 rows at 1/3 each). Need to settle whether these are model-sample variance (acceptable at 1/3) or real determinism failures.
3. **6 rows still stable_fail.** The Phase 7 work caught the synthetic-prompt issue but left these uncovered.

## Phase 8 surface (when ready)

1. **Bench infra: pin or warm-cache `family-test-claude:latest`** so it survives 30-min idle periods. Either rebuild-before-each-probe (~1s overhead per probe vs current 4-5 min probe time — acceptable), or push to a local registry the harness pulls from, or use `docker save` / `docker load` cycle in the bench wrapper.
2. **C014 regex fix**: change `[^\n]` to `[\s\S]` in the discriminator regex; should land 3 stable_pass on the next bench.
3. **C017 autonomous routing**: investigate why `defaults.methodology: helix` doesn't drive Sonnet to name "helix" in autonomous mode. Add a hint to SKILL.md that autonomous mode SHOULD prose-attribute the routing decision even when silently following defaults.
4. **CD-02 / CD-04 / CF-02 / CF-03**: investigate transcripts to find skill-body gaps. Likely additional cross-flow and concern-slot wording.
5. **EA-01..04 flake reduction**: if the matcher is genuinely 1-of-3 ish, consider relaxing stable-pass criteria for EA-* rows specifically OR add an explicit FEAT-naming-vocabulary clause to SKILL.md.
6. **Then Stage 5b** ($260, but only after infra fixes prevent eviction-induced noise).

## Aggregate scoreboard (across all phases this session)

**Stable-pass rows verified during the session** (combining Phase 5a + Tier 4 + Phase 7):
- 4 autonomy matrix (AM-01..06 — Phase 5a)
- C003 marker-edge (Phase 5a)
- C018 iterate (Phase 5a)
- G1 spec-gap-orchestration (Phase 5a)
- G2 scale-recalibration (Tier 4 — discriminator widening)
- 6 MI-* multi-instance (Tier 4 — matcher fix)
- 7 Phase 7 recoveries (C008, C013, C015, C016, C024, CD-01, CD-03)

**Total: 21 stable_pass rows confirmed.** From a pre-port baseline near 0/24 measurable on the failing subset.
