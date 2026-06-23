# Technical Spike Generation Prompt
Use the spike to answer one technical question with evidence.

## Reference Anchors

Use these local resource summaries as grounding:

- `docs/resources/safe-spikes.md` grounds spikes as bounded experiments that
  reduce uncertainty before implementation.
- `docs/resources/agile-alliance-sizing-spikes.md` grounds spikes as visible,
  time-boxed learning work rather than hidden delivery work.

## Create this when
For an **unmatched capability, an active-concern conflict, or an operator-marked
unknown**, the capability's **top 1-3 design-defining decisions** (API shape, data
model, pricing/cost, security/permissions, operational guarantees, or
decomposition) are **assumed rather than evidenced**. "known/low-risk" requires
evidence (operator statement, governing artifact, existing implementation,
docs/API proof, or a completed spike), not model familiarity, and not because a
mechanism was picked or a provider named. Spike the assumed decision **even when a
provider is chosen and its live integration is deferred** (deferral de-risks
integration timing, not the decision). An operator-marked "spike/unknown" is
authoritative. See the anti-reframe check in
`workflows/references/concern-resolution.md` (step 3a). For a **business** unknown
a technical spike can't answer (e.g. pricing), record guidance-needed or a
blocked spike instead.

## Focus
- State the question, hypothesis, and method.
- Keep the investigation small and measurable.
- Separate spike evidence from production implementation.
- End with findings, limitations, and a recommendation that updates design,
  creates follow-up work, or stops the approach.

## Completion Criteria
- The uncertainty is reduced.
- Evidence is documented.
- The recommendation is actionable and scoped to the evidence.
- Any remaining uncertainty is named.
