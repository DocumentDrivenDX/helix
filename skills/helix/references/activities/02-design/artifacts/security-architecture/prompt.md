# Security Architecture Generation Prompt
Document the security architecture patterns, trust boundaries, controls, and
design-level security decisions that shape implementation and testing.

## Reference Anchors

Use these local resource summaries as grounding:

- `docs/resources/owasp-asvs.md` grounds verifiable application security
  controls.
- `docs/resources/owasp-threat-modeling-cheat-sheet.md` grounds trust
  boundaries, data flows, threats, assumptions, and mitigations.
- `docs/resources/nist-privacy-framework.md` grounds privacy-risk controls and
  data-processing constraints.

## Focus
- Start from security requirements and the threat model.
- Define trust boundaries, control points, identity, data protection, logging,
  monitoring, and residual risk.
- Map threats to controls and controls to tests.
- Keep the artifact at the design level; do not drift into code or deployment
  instructions.

## Completion Criteria
- Threats and controls are linked.
- Identity and access decisions are explicit.
- Data protection and monitoring decisions are explicit.
- The document is specific enough to guide implementation and testing.
- Residual risks are named instead of hidden.
