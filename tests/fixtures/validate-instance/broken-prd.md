---
ddx:
  id: helix.prd
  authoring:
    home: repo
---

# Product Requirements Document: Broken Fixture

## Summary

This fixture is deliberately incomplete. It exists so that
`tests/validate-instance.sh` can prove the validator reports a missing
required section, a leftover placeholder, and a failed catalog regex check.

## Problem and Goals

[TODO] describe the problem.

## Users and Scope

Reviewers of the validator.

## Requirements

- P0: the validator must exit 1 on this file.

## Functional Requirements

- FR-001: [NEEDS CLARIFICATION: which checks are blocking?]

## Acceptance Test Sketches

- Run the validator; expect `required_sections.success_criteria` and `placeholder`.

## Risks

None beyond the fixture drifting from the PRD catalog entry.
