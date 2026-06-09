---
title: "Bench Build Results — 2026-06-05"
slug: bench-build-results-2026-06-05
weight: 310
activity: "Design"
source: "02-design/bench-build-results-2026-06-05.md"
generated: true
---
# Bench Build Results — 2026-06-05

Final verification report for the helix-family conversation-bench build plan
([`plan-2026-06-05-conversation-bench-and-autonomy.md`](/artifacts/plan-2026-06-05-conversation-bench-and-autonomy/)).

## Headline

- **Self-test:** PASS (exit 0).
- **Authored rows:** 162 (155 prior + 3 CF + 4 RC; see §Rows and §X.5).
- **Worked example:** `helix_check.py example --strict --adversarial-coverage` exits 0.
- **Regression suite:** `family-test/run-tests.sh` 27/27 PASS after a meta.yml
  fix on six new helix-data library types (see §Findings).
- **Remaining-items closure (2026-06-06):** 4 of 5 prior remaining items
  closed; full-bench live run blocked on Phase 1+ runner (see §X.5).

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
| Cross-flow scenarios | 3 | 3 | CF-01..03 standalone (added 2026-06-06; previously embedded in C021/C022/C025) |
| Rename-compat rows | 4 | 4 | RC-01..04 validator-rows standalone (added 2026-06-06; B8a/B8b/B8c remain) |
| **Total** | **162** (160 + 2 dual-role meta) | **162** | gap closed 2026-06-06 |

Row directories under `bench/conversations/` total 71 (was 64 + CF-01..03 + RC-01..04);
routing JSONL totals 81; meta-tests total 10. Grand authored total = **162**.

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

Build the Phase 1+ runner (run-all subcommand, per-row stream-json CC
invocation via `run-probe.sh`, determinism=3 stable-pass aggregation,
routing-evals grading subcommand). Once available, export
`ANTHROPIC_API_KEY` (or use the OAuth token at
`~/.cache/family-test-auth/token` already verified live) and run
`helix_bench.py run --all --determinism 3` to seed `ratchets.json`
baselines and `cost-log.jsonl`. Plan §19's $45 budget assumes the
harness exists; ~$0.022 has been burned to date on the live smoke probe.

## X.5 Remaining-items completion (2026-06-06)

Closure pass for the 5 items called out in §Remaining work. Worked in
five parallel sub-phases; verification rerun this turn confirms all
non-blocked items landed and the bench is still green.

### Per-item status

| # | Item | Status | Commit | Notes |
|---|---|---|---|---|
| 1 | 3 standalone cross-flow discriminator rows | **done** | `b253b750` | CF-01-prd-needs-infra, CF-02-pipeline-needs-dns, CF-03-whats-blocked-multi-flow; CF-01/02 use typed `route_decision` (routing_signal=explicit_skill_tool_use); CF-03 uses `skill_tool_use` pinning Skill(helix-data) with all three flows in the structural block; all tier=must_pass_core; self-test green post-add |
| 2 | 4 standalone rename-compat rows | **done** | `dba2de34` | RC-01..04 as validator-rows (marker.yml + expected-validator-output.txt) covering v1-loads, v2-loads, mixed-cycle, strict-v2-rejects-legacy. New validator codes M040 (both keys present) and M041 (helix_version:2 + legacy `methodologies:`); new `kind: validator-row` mode in runner; all 27 family-tests still PASS |
| 3 | First full-bench live run to seed ratchets + cost-log | **still-pending** | `7938f35a` (scaffold only) | Blocked: runner v0.2.0 is Phase 0a (validate-only); no `run --all` subcommand, no per-row stream-json CC invocation, no `routing-evals` subcommand. Auth IS production-ready (Docker smoke probe PASS at $0.022). Ratchets remain NULL by design; cost-log seeded with one smoke-probe entry. See `bench-build-results-2026-06-06-first-run.md` for full diagnosis |
| 4 | Pre-commit hook: `helix_check.py type --strict` on library/types/** | **done** | `fd52b62b` | Wired into existing `lefthook.yml` as `check-library-types` rule with glob `family-test/library/types/**/*`. Abort-on-broken-meta verified live: removed `version:` from monitoring-setup/meta.yml, commit aborted with T002 exit 3. Documented in `family-test/bench/README.md` |
| 5 | CC version re-validation cadence | **done** | `4d0fa194` | New procedure doc `family-test/bench/docs/cc-version-revalidation.md` (why-pinned, when-revalidate, ratchet re-baseline gate with >5% stable_pass_rate regression halt). New `check-cc-revalidation.sh` parses `re_validation_required_after` from `family-test/bench/cc-version.lock` and warns to stderr if past deadline (always exit 0; advisory). Wired into both `lefthook.yml` pre-commit AND `.github/workflows/family-bench.yml` self-test job |

### Verification rerun (this turn)

```
python3 family-test/bench/runner/helix_bench.py self-test
  → matchers 9/9, meta 10/10, property 400/400, golden 9/9,
    cost_tracker PASS, failure_dump PASS, envelope-pass 4/4
  → self-test overall: PASS

bash family-test/run-tests.sh
  → PASS: 27, FAIL: 0 (B8a/B8b/B8c rename gate green)

lefthook.yml
  → check-library-types rule present, glob family-test/library/types/**/*
  → check-cc-revalidation rule present, advisory (|| true)

family-test/bench/cc-version.lock           → present
family-test/bench/docs/cc-version-revalidation.md   → present
family-test/bench/runner/check-cc-revalidation.sh   → present
```

### Bench-state snapshot

- **Conversation rows:** 71 (was 64; +CF-01..03, +RC-01..04)
- **Routing JSONL rows:** 81 (unchanged)
- **Meta-tests:** 10 (unchanged)
- **Grand authored total:** **162** (target hit)
- **Ratchets seeded:** NO (Phase 1+ runner not built)
- **Cost-log seeded:** partial — 1 smoke-probe entry; full-bench actual = N/A
- **Live spend to date:** ~$0.022 (Docker smoke probe)

### Phase 1+ runner backlog (to unblock item #3)

1. `run --all` subcommand iterating `bench/conversations/`
2. Per-row stream-json CC invocation via `runner/run-probe.sh`
3. Determinism=3 stable-pass aggregation
4. `routing-evals` subcommand grading the 4 JSONL files against the
   integer confusion matrix (plan §15b P1)
5. First baseline run to populate `ratchets.json` and `cost-log.jsonl`

## X.6 Close-out 2026-06-06 PM

Final close-out across three sub-phases this turn: (1) Phase 1+ runner
build, (2) bench smoke on a representative slice, (3) attempted first
full-bench live run.

### Per-phase outcome

| Sub-phase | Status | Commit | Cost burned | Outcome summary |
|---|---|---|---:|---|
| Phase 1+ runner build | **PASS** | `3b3c2e8d` | $1.92 | `helix_bench` v0.3.0: `run <row|glob>`, `run --all`, `routing-evals`, `update-ratchets`. Stream-json persisted under `runs/<run-id>/<row-id>.pass<i>.stream.jsonl`. Matchers `skill_tool_use` + `route_decision` updated to grade live CC stream-json shapes. Determinism aggregation (stable-pass / flake / stable-fail / error), auth-failure halt, ratchet seeding + tolerance-gated regression alerts. Self-test: 9/9 matchers, 10/10 meta, 400/400 property, 9/9 golden, 4/4 envelope. 3-row smoke (CD-01, AM-02-rejected-by-T044, RE-POS-001) verified plumbing end-to-end. |
| Bench smoke (10 rows) | **PASS-with-notes** | `53c4d8d9` | $9.78 | 7/10 stable-pass (RE-POS-001/002, RE-NEG-001/002, RE-AMB-001, C001, C005); 1 real defect surfaced (CF-01 routed `helix-infra` first, skipped `helix`); 2 row-design issues (AM-02, SA-04 — `Bash` over-broadly classified as mutation). T044 validator fix: `autonomy_swap` now accepted alongside `autonomy_override` — closes the prior cost-leak path on 15 rows that previously rejected post-probe. Determinism ran at d=1 (d=3 would have blown the $5 turn budget). |
| Full-bench first run | **GATE-FAIL** | (no commit) | ~$0.55 | DID NOT COMPLETE. Only 6/30 helix-negative routing rows ran live before the stop hook fired. Positive (0/30), ambiguous (0/15), multi-instance (0/6), and all 71 conversations did not execute. Projected full-scope cost ~$347 against a stated ~$50 cap. `stable_pass_rate` baseline still NULL; no `SUMMARY.md` written; no run-end `routing-eval-results.json` produced. |

### Ratchet baselines (post-close-out)

| Ratchet | Baseline | Seeded | Last observed | Notes |
|---|---:|---|---:|---|
| `routing_precision` | **1.0** | 2026-06-06T16:01:47Z | 1.0 @ 2026-06-06T16:12:32Z | Seeded by the runner-build 1-row smoke (RE-POS-001) and held at 1.0 by the 10-row bench smoke (2 positive rows). Live floor is provisional — full positive set (30 rows) has not run. |
| `stable_pass_rate` | **null** | — | — | Full-bench d=3 run never executed. Closest signal: 7/10 (70%) stable-pass at d=1 across the bench smoke. NOT seeded into the ratchet — d=1 is not the contract. |
| `cost_per_run` | **null** | — | — | No full-bench run completed; rolling average undefined. Cost-log holds 20 per-call entries spanning the build + smoke + partial full-run windows. |
| `dev_iteration_burn` | **null** | — | — | Tracked separately; cumulative cost-log spend across all phases this turn: **$16.18**. |

### Cost actuals (this close-out)

- Phase 1+ runner build (3-row smoke + self-test): **$1.92**
- Bench smoke (10 rows, d=1): **$9.78**
- Partial full-run (6 helix-negative routing rows): **~$0.55**
- **Close-out subtotal: ~$12.25**
- **Cumulative `cost-log.jsonl` across all turns: $16.18** (20 entries)
- Aspirational $5/turn smoke budget: exceeded on the smoke pass by ~2x (median row $1.04). Stated $45-50 full-bench cap: not exercised; projected actual at d=3 across all 152 rows ~$300+.

### Verifiably proven now

1. **Runner grades real CC stream-json transcripts end-to-end.** 10 live conversation/routing rows produced parseable stream-json (`runs/<id>/<row>.pass1.stream.jsonl`), were grader-evaluated, cost-logged, and ratchet-updated without runner-side error. Matchers no longer rely on synthetic shapes.
2. **Auth path is production-ready.** OAuth token at `~/.cache/family-test-auth/token` flows through `docker/run-probe.sh` consistently across 15+ live invocations this turn; no auth-failure halts triggered against real prompts.
3. **Routing-eval ablation has a live floor.** `routing_precision = 1.0` seeded against 2 positive rows and held by the smoke. Not a full-set baseline, but a non-NULL ratchet on disk.
4. **Cost ledger is live.** `cost-log.jsonl` went from 0 → 20 entries with per-row USD, token counts, cache reads, duration, and notes; `cost_tracker` self-test still PASS.
5. **Real defects surface through the bench.** Two row-design issues (AM-02, SA-04 `Bash`-as-mutation) and one routing finding (CF-01 helix-first skip) were detected by the runner, not by hand-inspection — the harness is doing its job.
6. **Halt-on-auth-failure works.** The runner correctly distinguishes auth failures from grading failures and writes `halt_reason="auth_failure"` rather than scoring such rows as `absent`.
7. **T044 schema fix shipped.** `autonomy_swap` accepted as a valid `negative_control_modification`; the 15 AM-/SA- rows that previously cost-leaked through probe-then-reject now validate pre-probe.

### What truly remains

1. **Full-bench live run at d=3 with an explicit higher budget.** None of the integer gates (positives ≥29/30, negatives 30/30, ambiguous ≥13/15, must_pass_core 16/16) have been measured live. Projected ~$300+. Requires operator approval on budget OR a reduced-scope contract (e.g., d=1 across the full set ~$120; d=3 on a 20-row representative slice ~$60).
2. **Seed `stable_pass_rate` and `cost_per_run` baselines.** Both remain NULL. The first full-bench run at the contracted determinism is the only path.
3. **Move `validate_row` ahead of `invoke_probe` in `run_row_live`.** Smoke-detected cost-leak path: schema-invalid rows currently burn probe cost before grading rejects them. Orthogonal to Phase 1+; ~30 min fix.
4. **Tighten `mutation_tools` on autonomy/secret_read rows.** Either narrow via `mutation_target_pattern` or drop `Bash` for read-like commands (`ls`, `git status`). Affects AM-/SA- row authoring, not the runner.
5. **CF-01 routing triage.** Real signal: model routes `helix-infra` before `helix` on cross-flow PRD prompts. Either re-prompt or accept as a routing weakness in `helix-positive`/`helix-multi-instance` coverage.
6. **CC version refresh cadence.** `cc-version.lock:re_validation_required_after = 2026-09-05` (advisory check shipped in `4d0fa194`). No action this turn; revisit on schedule or on CC 2.2.x ship.
7. **Periodic re-validation.** Once baselines seed, re-run on each `main`-merge per the CI workflow; treat the first non-NULL run as the ratchet anchor and gate subsequent runs against `tolerance_pp` / `tolerance_pct`.

### Overall verdict

**mostly-shipped.** The runner (Phase 1+), auth, matchers, cost-log, and ratchet machinery are all live and proven on small live samples — the **infrastructure** the build plan asked for is complete and exercised against real CC output. The **first full-bench measurement** that the plan ultimately exists to produce did not complete this turn (budget cap vs. projected scope), so the two NULL baselines (`stable_pass_rate`, `cost_per_run`) and the integer routing gates remain unmeasured. The path from here is a single budgeted live run, not further build work.

## Pointers

- Runner: `/Users/erik/Projects/helix/family-test/bench/runner/helix_bench.py`
- Conversations: `/Users/erik/Projects/helix/family-test/bench/conversations/`
- Routing evals: `/Users/erik/Projects/helix/family-test/bench/routing-evals/`
- Worked example: `/Users/erik/Projects/helix/family-test/examples/helix-data-customer-events/`
- Family-test driver: `/Users/erik/Projects/helix/family-test/run-tests.sh`
- Plan: `/Users/erik/Projects/helix/docs/helix/02-design/plan-2026-06-05-conversation-bench-and-autonomy.md`
