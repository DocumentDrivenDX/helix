# Compliance Requirements Analysis Prompt
Map the external regulations and standards that apply to this project to the
controls and evidence that satisfy them.

## Traceability chain

This artifact's place in the security triangle: **regulations -> controls**.
- See `security-requirements` for the testable acceptance criteria that
  exercise those controls.
- See `threat-model` for the abuse paths those controls mitigate and the
  STRIDE owners.

## Reference Anchors

Use these local resource summaries as grounding:

- `docs/resources/ftc-safeguards-rule.md` grounds financial customer
  information security obligations and applicability caveats.
- `docs/resources/nist-privacy-framework.md` grounds privacy risk management,
  data processing, controls, and validation evidence.

## Focus
- Identify only the regulations and standards that actually apply to this system.
- Mark uncertain applicability explicitly and route it to counsel or compliance review.
- Map each obligation to its source, affected scope, the control(s) that satisfy
  it, owners, evidence, and timing.
- Keep the result concise and implementation-relevant.
- Do not invent legal conclusions. State assumptions and review gaps.
- Do not enumerate threats, attacker behavior, or STRIDE categories. Cross-
  reference `threat-model` for those.
- Do not author testable acceptance criteria for controls. Cross-reference
  `security-requirements` for that.

## Completion Criteria
- Applicable, not-applicable, and uncertain obligations are identified.
- Each applicable obligation names the control(s), evidence, owner, and deadline.
- No generic filler is added.
