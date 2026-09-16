---
ddx:
  id: metrics-dashboard
  authoring:
    home: repo
  review:
    self_hash: aecf7fa7f07f3ee5b8b69bf58e4a78d0491e3d4d3e769448e623a94e1fe9184c
    deps: {}
    reviewed_at: "2026-09-16T01:53:39Z"
---
# Metrics Dashboard: HELIX 2026-Q3 (human-outputs branch)

**Review Window**: 2026-09-10 → 2026-09-15 (`feat/helix-human-outputs`)
**Baseline**: none. This is the first sample against the PRD's success
metrics (`docs/helix/01-frame/prd.md` Success Metrics). The previous
dashboard measured the execution loop (bead close rate, cycle time,
wrapper-CLI green rate); those metrics belong to the runtime and are
retired here.
**Status**: Complete

## Decision

The branch made three PRD metrics measurable for the first time and
measured a fourth surface, present mode, through its own gate. The eval
run passes every deterministic check (32/32) and scores 48/54 on the
rubric; the skill body carries zero runtime-specific commands; the one
deck produced so far passes the deliverable gate with 0 blocking findings.
The alignment-quality target (fewer than three findings per `align` run on
a healthy artifact set) is not yet measurable: the only sample is a fixture
seeded with drift. No metric crossed a degradation threshold because there
is no prior reading to degrade from.

## Summary

`evals/results/20260911-0955/summary.md` is the current sample for the
skill metrics (commit `0756e5fa`, eight briefs, about $23 per run); the
present-mode sample is the DEL-001 gate record
(`docs/helix/06-iterate/deliverables/DEL-001-helix-evaluation-deck.md`
Render section). Authoring quality reads well on the proxy available
(template-authored PRDs pass `validate-instance.py` on the first attempt);
the PRD's comparative study against free-form PRDs has not been run.

## Metrics Table

| Metric | Baseline | Current | Direction | Result | Source |
|--------|----------|---------|-----------|--------|--------|
| Alignment findings per `align` run (healthy set) | none | 28 on the seeded `recipe-app/baseline` fixture; no healthy-set sample | lower is better (target < 3) | not measurable yet | `evals/results/20260911-0955/align-baseline.json`; `evals/briefs.yml` `align-baseline` |
| Eval deterministic checks | none | 32/32 across 8 briefs | higher is better | pass | `evals/results/20260911-0955/summary.md` |
| Eval rubric total | none | 48/54 (present brief 6/8, align brief 6/8) | higher is better | trend signal only | `evals/results/20260911-0955/summary.md` Rubric notes |
| Authoring quality: template-authored PRD passes first review | none | 2/2 PRD-producing briefs pass `validate-instance.py` with 0 blocking findings (`frame-prd-from-vision` 5/5, `validate-prd` 4/4); no free-form comparison | higher is better | pass (proxy) | `evals/results/20260911-0955/frame-prd-from-vision.json`, `validate-prd.json` |
| Skill portability: runtime-specific commands in the skill body | 0 | 0 | lower is better | pass | `tests/validate-skills.sh` runtime-neutrality gate; eval `output_not_contains` tracker vocabulary 8/8 clean |
| Present mode: deliverable gate on DEL-001 | none | `check-deliverable.py` 0 blocking, 0 warnings; `deck-qa.py` 15 slides, 0 blocking, 3 warnings; `validate-instance.py` 0 findings; Vale 0 errors | lower is better | pass | DEL-001 Render section; `python3 skills/helix/scripts/check-deliverable.py docs/helix/06-iterate/deliverables/DEL-001-helix-evaluation-deck.md` |
| Present mode: eval brief | none | `present-investor-deck` checks 4/4, rubric 6/8 (render checks excluded on a headless host) | higher is better | pass; voice points lost | `evals/results/20260911-0955/present-investor-deck.json` |

## Interpretation Rules

- Deterministic checks are pass or fail; a lost check on any brief is a
  regression and blocks the change that caused it.
- Rubric scores are a trend signal between runs, not a pass mark; a change
  is kept when checks stay green and the rubric total moves up on the
  briefs it targets (`evals/README.md` Reading a result).
- The alignment target reads only on a healthy artifact set. A finding
  count on a seeded fixture records the mode's recall, not the metric.
- A present-mode gate warning is tolerated when the Render section names
  it and the reason; a blocking finding is not.
- A row marked "not measurable yet" creates a follow-up; a "proxy" row
  creates a follow-up to replace the proxy with the PRD's measurement.

## Trend Notes

- First reading; no trend. The eval was run at `0756e5fa`, before the
  headline-rule port, the slide-shape checks, and the deck rebuild landed;
  the next run is the first comparison.
- The two rubric points lost on `present-investor-deck` were voice
  (source references an investor would not use; intake fields not named),
  the same gap the human-facing Sloptimizer adapter in the improvement
  backlog targets.
- The two points lost on `align-baseline` were report length (the YAML
  block repeats the table) and a truncated handoff block, both report
  shape rather than finding quality.

## Follow-Up

- Add a healthy-set `align` brief (a fixture with no seeded drift, or
  `docs/helix/` itself) so the < 3 findings target has a reading;
  `improvement-backlog.md` carries the item.
- Run the eval at the branch head and commit the summary as the second
  sample.
- Replace the first-review proxy with the PRD's comparative study
  (template-authored vs free-form PRDs through the same review).

## Review Checklist

- [x] Baseline is explicit (none; first sample, prior execution metrics retired)
- [x] Each metric cites a source (an eval result file, a test lane, or the
      DEL-001 gate record)
- [x] The summary states the decision implication (checks and portability
      pass; alignment target not yet measurable)
