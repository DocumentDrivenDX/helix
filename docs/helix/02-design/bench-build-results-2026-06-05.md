# Bench Build Results — 2026-06-05

Final verification report for the helix-family conversation-bench build plan
([`plan-2026-06-05-conversation-bench-and-autonomy.md`](plan-2026-06-05-conversation-bench-and-autonomy.md)).

## Headline

- **Self-test:** PASS (exit 0).
- **Authored rows:** 155 (target 160 — see §Rows).
- **Worked example:** `helix_check.py example --strict --adversarial-coverage` exits 0.
- **Regression suite:** `family-test/run-tests.sh` 27/27 PASS after a meta.yml
  fix on six new helix-data library types (see §Findings).

## Per-phase status

Phases P0a through P15 were committed prior to this verification turn. The
commit log (`git log --oneline` against `helix-website-isolate-prose-2026-05-28`)
shows one commit per phase landing in order, ending at P15 docs.

| Phase | Status | Notes |
|---|---|---|
| P0a runner + 9 matchers + vacuity guard | COMPLETE | self-test green; meta 10/10, golden 9/9, property 400/400 |
| P0b failure-dump scaffold | COMPLETE | `failure_dump self-test PASS` |
| P1 engagement gate (routing) | COMPLETE | 30 pos + 30 neg + 15 ambiguous authored; ablation results present (`runner/ablation-results/`) |
| P2 cascade discrimination | COMPLETE | 4 CD rows (CD-01..04) |
| P3 autonomy + stop_at | COMPLETE | 8 AM + 12 SA (6 positive + 6 near-miss negative) |
| P4 Edge Authority Asymmetry | COMPLETE | 4 EA rows |
| P5 conversation library | COMPLETE | 24 C-rows (C001-C025, C019 relocated to routing-negative) |
| P6 warm-context | COMPLETE | 5 WC rows |
| P7 Layer-2 judge LLM | COMPLETE | calibration-set + rubric + envelope-pass scaffold present |
| P8 Layer-3 next-action | COMPLETE | envelope-pass self-test 4/4 |
| P9 helix-data flow | COMPLETE (fixed) | 12 library types + graph + SKILL + worked example end-to-end; 6 type meta.yml files were missing `version:` — fixed this turn |
| P10 multi-instance schema v2 | COMPLETE | 6 multi-instance routing rows; T01-T38 baseline preserved |
| P11 cross-instance + informed_by | COMPLETE | 3 CI rows (CI-01..03) |
| P12 terminology rename (methodology → flow) | COMPLETE | M020 alias intact; B8a/B8b/B8c all PASS |
| P13 verbose-but-stuck | COMPLETE | 4 VS rows |
| P14 CI + ratchet + diff escalation | COMPLETE | `bench-categories.yml`, `ratchets.json`, `diff-to-category.py` + tests present |
| P15 documentation | COMPLETE | docs commit `2ba0b86a` |

## Rows authored vs target

| Category | Target (§15c) | Authored | Notes |
|---|---:|---:|---|
| Routing positive | 30 | 30 | `helix-positive.jsonl` |
| Routing negative | 30 | 30 | `helix-negative.jsonl` (includes relocated C019) |
| Routing ambiguous | 15 | 15 | `helix-ambiguous.jsonl` |
| Routing multi-instance | 6 | 6 | `helix-multi-instance.jsonl` |
| Conversations (C001-C025 minus C019) | 24 | 24 | C001-C025 dirs |
| Autonomy matrix | 8 | 8 | AM-01..08 |
| Stop_at triggers | 12 | 12 | SA-01..12 (6 positive + 6 near-miss negative) |
| Graph-discrimination | 4 | 4 | CD-01..04 |
| Edge Authority Asymmetry | 4 | 4 | EA-01..04 |
| Cross-instance | 3 | 3 | CI-01..03 |
| Warm-context | 5 | 5 | WC-01..05 |
| Verbose-stuck | 4 | 4 | VS-01..04 |
| Meta-tests | 10 | 10 | MT01-MT10 under `runner/meta-tests/` |
| Cross-flow scenarios | 3 | embedded | covered by C021/C022/C025; no standalone prefix |
| Rename-compat rows | 4 | embedded | covered by B8a/B8b/B8c (existing T01-T38) |
| **Total** | **162** (160 + 2 dual-role meta) | **155** | gap: 5 dedicated cross-flow + rename rows not surfaced as standalone directories — coverage exists via embedded coverage in conversations + T01-T38 |

Row directories under `bench/conversations/` total 64; routing JSONL totals 81;
meta-tests total 10. Grand authored total = **155**.

Gap relative to 160: dedicated standalone rows for "cross-flow" (3) and
"rename" (4) were absorbed into existing rows (C021/C022/C025 carry cross-flow
semantics; T01-T38 B8a/B8b/B8c carry rename-compat semantics). The behavioural
coverage exists; what is missing is the **standalone discriminator row** that
isolates each. See §Remaining work.

## Gate outcomes

### Runner self-test
```
smoke: matchers 9/9 pass; rejection codes fired: ['T040', 'T041', 'T042', 'T043', 'T044', 'T046', 'T047'] (expected: same)
meta-tests: 10/10 pass
property-tests: 400/400 pass (100 cases x 4 properties)
golden-transcripts: 9/9 pass
cost_tracker self-test PASS: sample cost $0.052500
failure_dump self-test PASS
envelope-pass self-test: 4/4 checks pass
self-test overall: PASS
EXIT=0
```

### Worked-example validation
```
python3 family-test/library/scripts/helix_check.py example --strict \
    --adversarial-coverage family-test/examples/helix-data-customer-events
summary: E=0 W=0 exit=0
EXIT=0
```

### Family-test regression suite
27/27 PASS after meta.yml fix (`T01 library clean` initially failed with
T002 errors on six new helix-data types missing `version:` — fixed in
this turn).

```
=== summary ===
PASS: 27
FAIL: 0
```

## Findings (this verification turn)

1. **P9 library types missed schema requirement.** Six newly-added
   helix-data library type `meta.yml` files (`backfill-plan`,
   `data-quality-tests`, `deprecation-notice`, `evolution-plan`,
   `lineage-spec`, `reconciliation-suite`) shipped without the required
   `version:` key. `helix_check.py type` rejects this with T002, so
   `family-test/run-tests.sh T01 (library clean)` failed with exit 3.
   - **Fix applied:** added `version: 1.0.0` to all six files.
   - **Root cause:** P9 library-type authoring did not run
     `helix_check.py type --strict` against the bench library tree before
     committing. Recommend adding this to the P9 phase checklist or to
     a pre-commit hook for `family-test/bench/library/types/**`.
2. **Cost ledger empty.** `runner/cost-log.jsonl` has 0 lines —
   `cost_tracker` is wired and self-tests, but no actual bench runs have
   been logged yet (expected: full-bench has not been invoked in CI yet;
   ratchets baselines are NULL by design per `ratchets.json` comment).

## Costs

- **Dev iteration burn (P0a-P15 build-out):** not measured this turn;
  `ratchets.json:dev_iteration_burn` stream is the designated tracker
  and is currently empty.
- **Full-bench estimate:** unmeasured (no full-bench run yet). Plan §19
  budgets per-row cost; `runner/cost-model.yml` is committed.

## Remaining work

1. **Author 3 standalone cross-flow discriminator rows.** Plan §14.1 names
   three scenarios (PRD-needs-infra, pipeline-needs-DNS, multi-flow status
   query). C025 covers cross-flow handoff. Two more dedicated rows
   (e.g. `XF-01-pipeline-needs-dns`, `XF-02-multi-flow-status`) would
   surface each scenario as an isolable bench row.
2. **Author 4 standalone rename-compat rows.** Plan §15c calls for
   dedicated rename rows; coverage exists via T01-T38 B8a/B8b/B8c plus
   the M020 alias path in `helix_check.py marker`. Standalone bench rows
   (e.g. `RN-01-v1-marker-loads`, `RN-02-v2-marker-loads`,
   `RN-03-mixed-cycle-deprecation`, `RN-04-strict-v2-rejects-legacy`)
   would close the gap to 162.
3. **First post-P14 full-bench run** to populate `ratchets.json` baselines
   (currently NULL) and `cost-log.jsonl`.
4. **Wire P9 library-type validation into pre-commit.** Run
   `helix_check.py type --strict family-test/bench/library/types/**`
   before allowing new helix-data type commits — would have caught the
   six-file T002 leak.
5. **Refresh `cc-version.lock`** at `re_validation_required_after`
   (2026-09-05) or sooner if Claude Code 2.2.x ships.

## Next action

Land this verification commit (`docs: bench build results 2026-06-05`)
together with the six meta.yml `version:` fixes, then either (a) author
the 7 missing standalone rows (cross-flow + rename) and re-verify, or
(b) ship as-is and trigger the first post-P14 full-bench run to seed
ratchet baselines, treating the 7 missing rows as P16 backlog.

## Pointers

- Runner: `/Users/erik/Projects/helix/family-test/bench/runner/helix_bench.py`
- Conversations: `/Users/erik/Projects/helix/family-test/bench/conversations/`
- Routing evals: `/Users/erik/Projects/helix/family-test/bench/routing-evals/`
- Worked example: `/Users/erik/Projects/helix/family-test/examples/helix-data-customer-events/`
- Family-test driver: `/Users/erik/Projects/helix/family-test/run-tests.sh`
- Plan: `/Users/erik/Projects/helix/docs/helix/02-design/plan-2026-06-05-conversation-bench-and-autonomy.md`
