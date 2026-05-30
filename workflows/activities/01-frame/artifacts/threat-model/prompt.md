# Threat Modeling Prompt
Enumerate threats by STRIDE category and assign mitigation owners.

## Traceability chain

This artifact's place in the security triangle: **threats -> STRIDE +
mitigation owners**.
- See `security-requirements` for the testable controls that mitigate each
  threat.
- See `compliance-requirements` for the regulations those mitigations satisfy.

## Reference Anchors

Use these local resource summaries as grounding:

- `docs/resources/owasp-threat-modeling-cheat-sheet.md` grounds assets, data
  flows, trust boundaries, STRIDE, assumptions, and mitigation mapping.
- `docs/resources/owasp-asvs.md` grounds mapping threat mitigations into
  verifiable security controls.

## Focus
- Define boundaries, assets, and trust changes first.
- Analyze threats with STRIDE and assign each one a mitigation owner.
- Cross-reference the control(s) in `security-requirements` that mitigate the
  threat rather than restating control text.
- Keep risk scoring and mitigation ownership explicit.
- Treat missing boundaries, unclear assets, or unstated assumptions as findings.
- Do not author control acceptance criteria. Cross-reference
  `security-requirements`.
- Do not analyze regulatory applicability. Cross-reference
  `compliance-requirements`.

## Completion Criteria
- The threat surface is clear and threats are categorized by STRIDE.
- Each high-risk threat has a named mitigation owner and a cross-reference to
  the mitigating control in `security-requirements`.
- Important threats are prioritized.
