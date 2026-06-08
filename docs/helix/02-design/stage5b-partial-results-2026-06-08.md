# Stage 5b — partial results + bench infra defect surfaced

## Status: incomplete

The Phase 9+5b workflow (`w1qjvx3yi`) failed at the grade-agent step because
the final agent didn't call StructuredOutput within its budget. Before that
the routing leg ran and the conv leg never started. The workflow has been
killed; this doc captures what we know.

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

## Diagnosed defect: 8.1 fix is racy

Manual verification — delete the image, run `run-probe.sh` once, image is
rebuilt and probe succeeds. Stderr shows the INFO rebuild message exactly
as expected.

Under sustained bench load (`helix_bench.py routing-evals` calling
run-probe.sh ~80 times in sequence), 43 invocations failed with empty
stderr files and exit code 3. Two hypotheses:

1. **Race condition**: docker GC fires WHILE a probe is mid-build,
   leaving an inconsistent image state. The next probe's `docker image
   inspect` succeeds (because the image NAME is still pinned) but the
   actual content is gone. The `docker run` fails at content-pull time
   and the stderr gets overwritten because the run-probe.sh redirects
   `2>"$EVIDENCE_FILE.stderr"` AFTER the auth-args + plugin-args setup,
   so rebuild messages from THAT iteration aren't preserved.
2. **OrbStack-specific GC bug**: OrbStack may be evicting the image
   asynchronously even while `docker image inspect` reports it present.

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

1. **Fix run-probe.sh properly**:
   - Move the image-presence check to a SEPARATE script that runs ONCE
     before each loop (not per-probe)
   - OR add a docker-image-watcher loop script that just `docker pull/build`
     every ~5 min while a bench is running
   - OR pin the image with `--restart=unless-stopped` on a sentinel
     container that prevents GC
2. **Verify Phase 9 fixes**: re-bench the 14 rows from Phase 8's stable-fail
   set + the 6 Phase 9 edited rows = ~20 rows × 3 passes
3. **Then** Stage 5b for ratchet seeding (only after Phase 10 infra is
   bulletproof — this is the second time docker eviction has broken a
   bench run mid-flight, and pretending it's solved would just produce
   another partial result)

## Spend

Stage 5b routing: ~$30 (the 37 probes that ran). Conv: $0 (didn't start).
Workflow agent orchestration: ~$5.

Total session burn ~$280-300 across all phases.
