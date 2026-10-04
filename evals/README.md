# HELIX skill evaluation

The PRD promises two things nobody could measure: healthy artifact sets
average fewer than three alignment findings per run, and HELIX-template PRDs
pass first review more often than free-form ones. This directory is the
first measurement path. It runs the routing skill headlessly against a
fixed corpus and scores what came back.

## What is here

- `briefs.yml`: nine briefs, one per mode that matters (frame, align,
  evolve, a contradiction, two present decks, check, an ambiguous request,
  validate). Each names its fixture, its prompt, deterministic checks, and
  a rubric.
- `results/<stamp>/`: one JSON per brief (checks, judge scores, the final
  response, the workspace diff stat) plus `summary.md`. Commit the summary
  of a run you want to compare against later; the JSON files are evidence.

The corpus is `tests/workflows/fixtures/recipe-app/baseline` (a vision, a
PRD, a feature spec, an ADR, a technical design for a recipe-sharing app)
and a `vision`-only cut of it.

## Running

```bash
python3 scripts/run-eval.py --dry-run                 # list briefs
python3 scripts/run-eval.py --briefs check-whats-next # one brief
python3 scripts/run-eval.py --judge                   # all briefs, rubric scored
python3 scripts/run-eval.py --rejudge evals/results/<stamp> --briefs align-baseline  # judge again, no host run
```

The default runner is Claude Code in print mode with this checkout as the
plugin directory, edits auto-accepted inside a throwaway workspace, and a
read-only tool allowlist. Pass `--runner` with a template that receives
`{prompt}`, `{cwd}`, `{repo}`, and `{max_turns}` to evaluate another host.
`--keep` leaves each workspace under the results directory.

## Runs

- `results/20260911-0955/`: run at commit `0756e5fa` over eight briefs
  (`present-survey-deck` was added afterwards); a baseline from before the
  present-mode changes.
- `results/20260915-2202/`: run at commit `20315d5c` over nine briefs:
  33 of 36 checks, rubric 57 of 62. The three failed checks: the investor
  deck tripped the shape rule on a bullet ending ", not a result" and used
  coverage status "gap" instead of covered or omitted; the survey deck had
  two 11-word titles against the 10-word stop; the ambiguous-request reply
  asked for direction without a question mark, which an
  `output_contains_any` check now covers.

- `results/20261003-2245/`: run at commit `023e6d14` over twelve briefs
  (three new desired-state briefs): 43 of 45 checks, rubric 70 of 80. The
  align report omitted the `aligned:` count, and the investor deck left
  "At the second meeting" unsourced. `-frame-r2` and `-frame-r3` rerun the
  frame brief (rubric 7 and 8 of 8; first run 6) to separate noise from
  regression. `-evolve-r2` and `-evolve-r3` rerun the evolve brief after its
  rubric changed to require one current ADR rather than a supersession chain:
  r2 still superseded (5 of 8); r3, after the ADR guidance changed, rewrote
  ADR-001 in place (7 of 8; a rename left a duplicate because the runner
  allows no file deletion).

## Reading a result

- **Checks** are deterministic and need no judgment: the files a mode must
  create or must not touch, `validate-instance.py` on every produced
  artifact, the `helix_report` block and its mode, tracker vocabulary that
  must not appear, and the deliverable gate for `present` (render checks
  excluded, since a headless host cannot rasterize). Validation uses delta
  semantics: the run is blamed only for blocking findings the fixture did
  not already carry, so fixture debt does not read as a regression, while
  a file the run created must be fully clean.
- **Rubric** scores come from a second headless call that sees only the
  brief, the rubric, the final response, and the diff. Treat them as a
  trend signal between runs, not as a pass mark.
- A change to the skill or a mode contract is worth keeping when checks stay
  green and the rubric total moves up on the briefs it targets. Keep what
  moved; cut what did not.

## Adding a brief

Add an entry to `briefs.yml`. Prefer checks over rubric items: a check
catches a regression in CI, a rubric item only describes one.
