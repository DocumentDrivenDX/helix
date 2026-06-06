# C011 — "What methodologies are active here?" (literal marker answer)

**Category:** conversation-library (happy paths) (plan §1.5b)
**Phase:** P5
**Tier:** must_pass_core

## What this asserts

Marker activates `helix` AND `helix-infra`. Operator asks
"What methodologies are active here?". The skill MUST engage and answer
LITERALLY from the marker — naming both flow ids (`helix` and
`helix-infra`) — rather than guessing from training or omitting one.

Surface-naming is a non-vacuous discriminator (per §1.4b
`literal_or_banner_text`): the matcher requires BOTH ids to appear,
and the banned-matcher list rejects flow-name-only attribution (`helix`
alone) at ≥20 chars. The compound regex captures both names with the
"active" verb anchor.

## Negative control

`marker_swap` to a marker with ONLY `helix` active. The pattern
requiring `helix-infra` in the answer can no longer match (the agent
truthfully should not name a flow that's not in the marker). Verdict
flips present → absent, proving the answer was marker-driven, not
prompt-prefix-driven.
