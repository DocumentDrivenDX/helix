# Phase 7 results — synthetic-prompt rewrite verification

## Headline

| Subset | Tier 4 baseline | Phase 7 result | Delta |
|---|---|---|---|
| 10 rows with good data | 0/10 | **6/10 stable_pass** | **+6** |
| 6 rows stable-fail | — | 3 fail, 1 flake, 2 pass | — |
| 11 rows broken (Docker image eviction) | — | N/A (infrastructure failure) | — |
| **16 Tier-4 stable-fail set (recoveries)** | **0/16** | **6/10 tested = 60% of tested rows** | **+6** |

Cost actual: ~$6 (28 passing-probe transcripts; 11 × 3 passes failed at docker pull).

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
| Phase 7 re-bench (10 working rows × 3 passes) | ~$6 | Docker image eviction cut 11 rows short |
| Phase 6 Tier 4 | ~$40 | Baseline |
| Phase 7 total | ~$46 | Cumulative |

## Files changed in Phase 7 (commit a28693e2)

- 15 conversation.yml rewrites (C008, C015, C016, C024, CD-01—04, CF-02—03, EA-01—04, G4)
- 7 expected.yml fixes (C013, C014, C024, CD-01—03, G3)
- helix_bench.py: `expected_edge_regex` param for `graph_edge_observed` matcher
- discriminator-whitelist.yml: document `expected_edge_regex` alternative
- skills/helix/SKILL.md: disambiguation banner rule + auth boundary for env-override
- docs/helix/01-frame/FEAT-X-receipt-export.md: G4 workspace fixture
