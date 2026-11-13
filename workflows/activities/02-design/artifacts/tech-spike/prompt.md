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

## Reusable scope

For `ddx.scope: reusable`, a spike published as knowledge (a technology
atlas keeps them under `spikes/`):

- **Answer one open question of one profile.** Link the [[component-profile]]
  with kind `answers` and the question's number from its Open Questions
  table, pinned to the revision read.
- **Use public inputs only.** Anyone can rerun it from the repository. A
  spike that needs a client's systems or data, or names a project, is not
  reusable and stays in that project's graph.
- **Record the Test Setup in full,** because the result speaks only for the
  configuration measured: version, environment, settings, data, and date.
- **Report, do not advise.** Findings, the conclusion, and its limits. No
  Recommendations section; a position paper or decision brief draws advice.
- **Say which views the result changes** in the profile: Risk & Compliance,
  Finance, IT Operations, Apps Dev, or No change.
- **Make it reproducible.** Scripts in the repository, commands in order.
  The profile then cites the spike as a source of class `measured`.

## Completion Criteria
- The uncertainty is reduced.
- Evidence is documented.
- The recommendation is actionable and scoped to the evidence.
- Any remaining uncertainty is named.
