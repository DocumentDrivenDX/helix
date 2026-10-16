# Session regression validation

Baseline: `3b8c76fa87266e8f31601f9a6158610effbcf77d`. Candidate: `475f54fbcc7eaeb3804ef9e2bd92aa1d5da2fe5a` (temporary combined revision of PRs #81–#86 plus review fixes).

Five sanitized scenarios ran against both versions using the same configured Codex runner. The exact model identifier was not captured. Each fresh fixture installed the evaluated skill under `.agents/skills/helix`; bare prompts were passed without route or catalog-read instructions. Tool traces confirmed the intended catalog was read. The desired-state pair used complete packages built by `scripts/build-plugin-package.sh`; the other runs resolved the installed source-checkout catalog.

| Scenario | Baseline checks | Candidate checks |
|---|---|---|
| session-tracking-is-optional | 2/2 | 2/2 |
| session-desired-state-without-code | 2/2 | 2/2 |
| session-complete-authorized-plan | 5/5 | 5/5 |
| session-concern-selection-is-not-adoption | 2/2 | 2/2 |
| session-low-autonomy-still-pauses | 2/2 | 2/2 |

Both versions passed 13/13 deterministic checks. This validates the scenarios as regression probes; it does not demonstrate improvement from the methodology changes. Expected modes are reporting metadata, not observed-route assertions. Literal checks do not replace semantic review. Final responses and diffs are retained in `results.json`; ephemeral workspace prefixes are normalized to fixture-relative paths.

Resource envelope: ten planned calls, each capped at 120 seconds. Trace inspection invalidated two desired-state calls that fell back to the global cached catalog. Only those two calls were repeated with complete packaged skills, for twelve calls total; the contaminated results are excluded. Accepted-run token usage is recorded as reported by Codex. Monetary cost is unknown, not zero.

Live observations cannot prove no attempted tracker discovery merely from file checks. No tool-trace enforcement was added to the reusable runner.


Astra reviewed final outputs and actual diffs: the title edits and concern-gap
reports satisfy their semantic requirements. Two rubric items remain partial:
the candidate low-autonomy response pauses but supplies no recommended
validation decision/rationale; both desired-state reviews include grounded TD
wording findings beyond the decision-only scope. These are recorded behavioral
limitations, not a fully passing rubric score. No automated judge score is
claimed, and this PR does not change workflow doctrine to mask them.
