---
title: "First post-P14 full-bench run — 2026-06-06"
slug: bench-build-results-2026-06-06-first-run
weight: 320
activity: "Design"
source: "02-design/bench-build-results-2026-06-06-first-run.md"
generated: true
---

> **Example from HELIX's own docs.** This generated page comes from `docs/helix/`. Use it to see the method in practice; start with the [artifact-type catalog](/artifact-types/) for reusable templates. Historical plans and reports may describe retired architecture.

# First post-P14 full-bench run — 2026-06-06

Supplement to `bench-build-results-2026-06-05.md`. Records the outcome of
the prior workflow's Item #3 ("First full-bench run to seed ratchets +
cost-log").

## Outcome

**Scaffold confirmed; live ratchet baselines pending Phase 1+ runner.**

The plan §19 estimate ($45 / ~10 min Sonnet full-bench) assumed a runner
that drives `claude -p --output-format stream-json` per row and grades
the resulting transcripts at determinism=3. The current runner
(`family-test/bench/runner/helix_bench.py` v0.2.0) is Phase 0a per its
own header docstring: it validates row structure, runs the matcher DSL,
and executes validator-rows directly against `helix_check.py`, but
explicitly defers stream-json CC invocation for non-validator rows
(see runner line 1802 and the placeholder `run_row()` at line 1772).

So a "live full-bench run" is structurally unbuildable today. Smoke
probe through `family-test/docker/run-probe.sh` does confirm auth +
harness are live.

## What ran live

| Path | Result | Cost |
|---|---|---|
| `family-test/bench/runner/helix_bench.py self-test` | PASS (matchers 9/9, meta 10/10, property 400/400, golden 9/9, envelope 4/4) | $0 |
| `family-test/docker/smoke-test.sh` (OAuth probe) | PASS | $0.02203825 actual |
| RC-01..RC-04 validator-rows via `run --determinism 3` | 4/4 PASS | $0 |
| Layer 1 structural validate of all 71 conversation rows | 51/71 PASS, 20 REJECT T044 (AM-/SA- rows: negative_control schema) | $0 |

The 20 T044 rejections are pre-existing — they predate this run and
reflect AM-/SA- rows still in partial-build state. Not caused by this
work.

## Auth status

OAuth token at `~/.cache/family-test-auth/token` authenticates against
the Docker harness (subscription type `team`, rate-limit tier
`default_claude_max_5x`, expires 2026 per credentials file).
`ANTHROPIC_API_KEY` is not set. Live CC calls work; the runner just
doesn't drive them yet for non-validator rows.

## Ratchets

`ratchets.json` baselines remain NULL — the contract documented in the
file's `$comment` block ("first run; do not gate; subsequent runs gate")
is preserved. Added `last_attempt` block records the timestamp,
scaffold-only outcome, the partial-floor data (validator-row 4/4,
Layer 1 51/71), and the next-action gate (Phase 1+ runner).

## Cost log

Seeded the first entry: smoke probe under `phase=dev_iteration` (per the
ratchets.json `dev_iteration_burn` stream comment that tracks the
P0-P15 build-out separately from steady-state `bench` cost). Recorded
`cost_usd: 0.064603` (cost-model.yml-projected at opus pricing) with
the actual multi-model `total_cost_usd: 0.02203825` preserved in
`notes.total_cost_usd_from_event` since the smoke probe used a
haiku+opus pipeline (the live `result` event reported `0.022`).

## What the user runs next to actually seed baselines

When the Phase 1+ runner ships (per plan §1.4b roadmap), with auth
present, the full-bench invocation will look like:

```sh
# (Phase 1+; not yet implemented)
python3 family-test/bench/runner/helix_bench.py run-all \
    --determinism 3 \
    --judge-backend claude \
    --judge-model haiku
```

That run will (a) generate stream-json transcripts per row via the
Docker harness, (b) grade Layer 1 + Layer 2, (c) compute
`stable_pass_rate` per the determinism=3 stable-pass rule, (d) run the
81 routing-evals to compute `routing_precision` against the integer
confusion matrix gate (plan §15b P1), and (e) write costs per row to
`cost-log.jsonl` under `phase=bench`.

## Files touched

- `family-test/bench/ratchets.json` — added `updated_at`, `last_attempt`
- `family-test/bench/runner/cost-log.jsonl` — seeded first entry
- `docs/helix/02-design/bench-build-results-2026-06-06-first-run.md` — this file
