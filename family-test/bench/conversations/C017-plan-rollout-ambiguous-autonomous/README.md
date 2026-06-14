# C017 — "Plan the rollout"; ambiguous, autonomous (defaults.methodology)

**Category:** conversation library (plan §1.5 row C017)
**Phase:** P5b
**Tier:** exploratory
**Flow classification:** legacy sibling-flow research row. Retained as an
expected-failing default-selection probe for the retired public `helix-infra`
skill design; not current HELIX user guidance.

## Scenario

Identical workspace to C016 (both helix and helix-infra in marker, no
cwd) EXCEPT:
- `.helix.yml` declares `defaults.methodology: helix`.
- `autonomy.default: autonomous`.

Operator says: "Plan the rollout."

## Expected behaviour

Per plan §1.5 row C017 and §1.5 resolution chain: under autonomous
autonomy, the skill MUST honour `defaults.methodology: helix` and
route to helix without emitting the disambiguation banner. The
operator's stated preference (encoded in the marker's defaults)
overrides the verb-ambiguity ask.

Routing signal: prose_attribution — the agent names helix in the
route announcement.

## Why exploratory

`defaults.methodology` resolution under autonomy=autonomous is a
brand-new surface that doesn't have a verified canonical pattern
yet. The expected route is helix (per defaults) but the matcher's
"helix BUT NOT helix-infra" disambiguation is fragile under
paraphrase. Marked exploratory per plan §5 row C017.

## Negative control

`marker_edit` — drop `defaults.methodology` from the marker. Without
the defaults, autonomous mode has to fall back to disambiguation
(banner) OR a heuristic guess; the strict route_decision to
`helix` no longer cleanly fires. Verdict flips from present to
absent.
