# Validation Checklist Generation Prompt
Create the checklist that decides whether Frame is ready to move forward.

## Reference Anchors

Use this local resource summary as grounding:

- `docs/resources/ibm-requirements-management.md` grounds traceability,
  validation, verification, and change management expectations.

## Focus
- Check only material prerequisites for the next scoped outcome: clear intent,
  testable behavior, consequential constraints, and unresolved decisions.
- Lifecycle labels, review stamps, and missing edges alone are not blockers.
  Read relevant content rather than requiring a complete linkage inventory.
- Keep the pass/fail criteria concrete.
- Avoid duplicating the content already covered by source artifacts.
- Cite evidence or the missing artifact for every conditional or failed gate.

## Role Boundary

Validation Checklist is not a replacement for PRD review, risk review, or
stakeholder review. It is the final Frame activity gate: it records whether the
required artifacts are coherent enough for Design and what conditions remain.

## Completion Criteria
- The checklist is short and actionable.
- Blocking gaps are easy to spot.
- A missing reference is reported only when unavailable intent affects the work.
- Result is Pass, Conditional Pass, or Fail with named conditions.
