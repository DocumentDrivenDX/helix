# C016 — "Plan the rollout"; ambiguous, both flows active (guided, exploratory)

**Category:** conversation library (plan §1.5 row C016)
**Phase:** P5b
**Tier:** exploratory
**Flow classification:** legacy sibling-flow research row. Retained as an
expected-failing disambiguation probe for the retired public `helix-infra`
skill design; not current HELIX user guidance.

## Scenario

Workspace state:
- `.helix.yml` lists both helix AND helix-infra.
- No cwd disambiguator (operator is at workspace root).
- No `defaults.methodology` key in the marker.

Operator says: "Plan the rollout."

## Expected behaviour

Per plan §1.5 row C016: "rollout" is genuinely ambiguous between
helix (product rollout / release planning) and helix-infra
(infrastructure rollout / change plan). Under autonomy=guided and
with no cwd or defaults disambiguator, the skill MUST emit the
disambiguation banner asking which flow the operator means.

The banner names BOTH candidate flows so the operator can choose.

## Why exploratory

The disambiguation banner is a UX surface — the canonical wording
will drift as the SKILL.md prompt evolves. The matcher uses a
regex_pattern that captures the structural shape (mention both flow
names + interrogative) rather than a strict literal. Marked
exploratory per plan §5 row C016.

## Negative control

`marker_edit` swap to drop helix-infra. With only helix in the
marker, "Plan the rollout" is no longer ambiguous; the skill should
route to helix without asking. The banner matcher must flip from
present to absent.
