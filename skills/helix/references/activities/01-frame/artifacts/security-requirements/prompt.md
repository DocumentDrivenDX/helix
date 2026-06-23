# Security Requirements Generation Prompt
Specify the testable acceptance criteria for the security controls the project
must satisfy before design and build.

## Traceability chain

This artifact's place in the security triangle: **controls -> testable
acceptance criteria**.
- See `compliance-requirements` for the regulations that motivate each control.
- See `threat-model` for the STRIDE categories and mitigation owners those
  controls answer to.

## Reference Anchors

Use these local resource summaries as grounding:

- `docs/resources/owasp-asvs.md` grounds application security requirements and
  verification expectations.
- `docs/resources/ftc-safeguards-rule.md` grounds financial customer
  information safeguards and applicability caveats.
- `docs/resources/nist-privacy-framework.md` grounds privacy risk management
  and data-processing controls.

## Focus
- Cover authentication, authorization, data protection, privacy, validation, and logging.
- Express each requirement as a testable acceptance criterion (design review,
  automated test, manual test, or audit evidence).
- For each control, cross-reference the originating obligation in
  `compliance-requirements` and the STRIDE owner in `threat-model`.
- Do not restate regulatory text or applicability analysis. Cross-reference
  `compliance-requirements`.
- Do not enumerate attacker behavior, data flows, or STRIDE categories.
  Cross-reference `threat-model`.

## Completion Criteria
- Required controls are identified and each has at least one testable
  acceptance criterion.
- Each criterion traces to a compliance obligation, a threat-model STRIDE
  owner, or both.
- The result is specific enough to guide design.
