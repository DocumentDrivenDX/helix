---
title: "Stage 5b — partial results + API rate limit hit"
slug: stage5b-partial-results-2026-06-08
weight: 790
activity: "Design"
source: "02-design/stage5b-partial-results-2026-06-08.md"
generated: true
---
# Stage 5b — partial results + API rate limit hit

## Status: incomplete

The Phase 9+5b workflow (`w1qjvx3yi`) failed at the grade-agent step because
the final agent didn't call StructuredOutput within its budget. The routing
leg ran 81 probes but 43 of them hit the **Claude API weekly rate limit**
mid-flight — not docker eviction as initially diagnosed.

## Correction to original diagnosis

Original draft claimed docker eviction. **That was wrong.** Forensic on
RE-POS-002's stream.jsonl shows the actual cause:

```json
{"type":"rate_limit_event","rate_limit_info":{"status":"rejected",
 "overageStatus":"rejected","overageDisabledReason":"out_of_credits"}}
{"type":"assistant","message":{"content":[{"type":"text",
 "text":"You've hit your weekly limit · resets Jun 11, 4am (UTC)"}]}}
```

The probes received a one-line synthetic "rate limit hit" response. The
runner counted these as failures (no Skill tool_use → fired_skills=[]),
duration ~2-5s (no inference happened), probe_rc=3.

The Phase 8.1 rebuild-on-demand docker fix is fine; not implicated.

## What landed before the failure (committed to main)

| Commit | What |
|---|---|
| `53ec5382` | Phase 9 fixes — C014 wording / CD-02-04 fixture defense / G4 FEAT-X / EA-04 regex / flake investigations |
| `71ba469a` | docs: HELIX documentation voice contract (separate work) |
| `825bdb5c` | chore: close helix-52801064 |

## Stage 5b routing — measured but unreliable

| Set | Runner-reported pass | Real interpretation |
|---|---|---|
| helix-positive | 1/30 | 1 graded PASS + 29 docker-eviction failures (probe_rc=3, duration < 10s, empty transcripts) |
| helix-negative | 30/30 | True PASS (the 30 negatives that DID run all engaged correctly; matches Phase-8-era data) |
| helix-ambiguous | 0/15 | 14 docker-eviction failures + 1 real failure (RE-AMB-013) |
| helix-multi-instance | 6/6 | True PASS (the Tier 3 matcher fix holds; all 6 correctly emitted disambiguation banner) |
| **Overall** | **precision 0.0333** | **Not interpretable** — 43 of 81 probes failed at docker pull |

The 30 helix-negative + 6 MI-* + 1 helix-positive RE-POS-001 = 37 probes ran cleanly. The other 44 hit docker eviction. The bench infra fix from Phase 8.1 (rebuild-on-demand inside `run-probe.sh`) tested clean in isolation but didn't survive sustained ~80-min bench load.

## Real diagnosis: API weekly quota exhausted

The OAuth token's max-2x weekly limit ran out partway through Stage 5b.
`resetsAt: 1781150400` (2026-06-11 04:00 UTC) — about 54 hours from
the time of failure. Once the quota was hit, every subsequent probe
returned the synthetic rate-limit-rejected response and the bench
counted them all as failures.

The runner SHOULD detect this and halt instead of marching through the
remaining ~40 probes producing fake-failure data. Phase 10 surface:
add a rate-limit-detect-and-halt path to `helix_bench.py` that parses
the init-line's `rate_limit_event` and aborts the loop if `status ==
"rejected"`.

## Stage 5b conv — did not run

The workflow's launch-agent set up the conv loop but `ps -ef` showed no
matching process, suggesting it was launched and exited quickly (likely
same docker eviction issue, given the cost-log shows the last conv
entry was ~6h before the routing started).

## Recommendation

**Don't seed ratchets from this run.** Pre-existing floors stand:
routing_precision 0.6667, conv stable_pass_rate 0.4722 (both measured
on partial data per Phase 5a results doc).

## Phase 9 fixes status (commit 53ec5382)

Per the in-flight workflow logs, all 6 Phase 9 parallel fix agents reported
"fixed":
- C014 wording: SKILL.md §5 tightened
- CD-02 fixture: edge name made un-guessable
- CD-04 fixture: same approach
- G4 FEAT-X: workspace fixture file added
- EA-04 regex: widened (one more iteration)
- Flake investigations: targeted edits or no-change decisions

But these were committed WITHOUT re-bench verification — the workflow died
before Stage 5b could measure them. Need a clean Phase 9 verification run
once the docker infra is bulletproof.

## Next steps (Phase 10)

1. **Add rate-limit-detect to helix_bench.py**: parse init-line's
   `rate_limit_event` from claude stream-json; if `status: rejected`,
   halt the loop immediately and emit a clear message. ~20 LOC in
   the runner. Prevents wasting time + accumulating fake failures.
2. **Wait for quota reset** (resetsAt: 2026-06-11 04:00 UTC, ~54h
   from failure).
3. **Verify Phase 9 fixes**: re-bench the 14 rows from Phase 8's stable-fail
   set + the 6 Phase 9 edited rows = ~20 rows × 3 passes (~$30).
4. **Then** Stage 5b for ratchet seeding.

## Spend

Stage 5b routing: ~$30 (the 37 probes that ran). Conv: $0 (didn't start).
Workflow agent orchestration: ~$5.

Total session burn ~$280-300 across all phases.
