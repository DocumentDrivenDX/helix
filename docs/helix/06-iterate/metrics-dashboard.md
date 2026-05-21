---
ddx:
  id: metrics-dashboard
  review:
    self_hash: 0934ca6e0913a5da11bb822adb4b4a5e343aaefdf6444af11690eab218a52c6c
    deps: {}
    reviewed_at: "2026-05-15T04:11:24Z"
---
# Metrics Dashboard: HELIX 2026-Q2 (post-`v0.3.3`)

> Illustrative example using representative measurements taken from
> the live HELIX repo around the `v0.3.3` release window. Exact values
> reflect a single sampling period and will drift; the dashboard's
> structure and decision logic are the canonical part.

**Review Window**: 2026-04-01 → 2026-04-30
**Baseline**: `v0.3.2` release window (2026-03-01 → 2026-03-31)
**Status**: Complete

## Decision

The 2026-Q2 changes (CI stability fix, `--review-threshold` knob, plugin
manifest cleanup) **improved overall execution stability** with no
regression in cycle time or escalation frequency. The wrapper-CLI test
suite is now reliably green; bead close rate and agent attempt success
both moved in the right direction. No metric crossed a degradation
threshold.

## Summary

`v0.3.3` is a stability release: the CI green rate moved from intermittent
to reliable, and operator review-cadence noise dropped after the
`--review-threshold` knob landed. Bead close rate is up modestly; cycle
time is essentially flat (within noise). No alerting or backlog growth
signals indicate degradation.

## Metrics Table

| Metric | Baseline | Current | Direction | Result | Source |
|--------|----------|---------|-----------|--------|--------|
| Bead close rate (closed/week) | ~22 | ~26 | higher is better | pass | `ddx bead list --status closed --json` filtered by `updated_at` |
| Agent attempt success rate (closed without retry) | ~78% | ~82% | higher is better | pass | `events[]` array on closed beads |
| Median cycle time (claim → close) | ~38m | ~36m | lower is better | noise (within ±10%) | `events[]` timestamps; sampled across the 2026-Q2 window |
| Escalation frequency (`NEXT_ACTION: WAIT` per `ddx work`) | ~0.18 | ~0.15 | lower is better | pass |  snapshot history |
| Review-cycle noise (review passes per closed bead) | ~1.4 | ~1.1 | lower is better | pass (driven by `--review-threshold`) | `ddx bead show <id>` review events on closed beads |
| Wrapper-CLI test green rate (CI) | ~85% | ~99% | higher is better | pass | GitHub Actions runs of `tests/the HELIX skill.sh` |

## Trend Notes

- The wrapper-CLI green-rate jump is directly attributable to the DDx
  update-notice filter landed in `92293fd` and shipped in `v0.3.3`.
- Review-cycle noise dropped because `--review-threshold` lets operators
  raise the periodic-alignment trigger when the queue is short.
- Cycle time is flat — the release did not target latency, and no
  regression appeared.
- Close rate moved up but is partially explained by the iterate cycle
  consuming a batch of artifact-restoration beads in parallel; this is
  expected to normalize once the AR-2026-05-01 follow-ups are exhausted.

## Follow-Up

- Continue draining the AR-2026-05-01 artifact-restoration backlog
  (tracked in `improvement-backlog.md`).
- Re-measure cycle time after the FEAT-006 context-digest propagation
  beads close — those are expected to reduce mean cycle time.
- File a tracker bead to add a deterministic close-rate metric script
  under `scripts/` so this dashboard can be regenerated mechanically next
  iteration instead of sampled by hand.

## Review Checklist

- [x] Baseline is explicit (`v0.3.2` release window)
- [x] Each metric cites a source (the actual command or events array)
- [x] The summary states the decision implication (`v0.3.3` improved
      stability; no regression)
