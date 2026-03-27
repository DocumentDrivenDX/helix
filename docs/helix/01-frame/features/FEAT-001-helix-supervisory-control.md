---
dun:
  id: FEAT-001
  depends_on:
    - helix.prd
---
# Feature Specification: FEAT-001 - HELIX Supervisory Control

**Feature ID**: FEAT-001
**Status**: Specified
**Priority**: P0
**Owner**: HELIX maintainers

## Overview

HELIX supervisory control is the capability that lets `helix-run` act as an
autopilot controller for repository work. It keeps the workflow moving across
requirements, designs, tests, implementation, review, and metrics until human
judgment is actually needed.

## Problem Statement

- **Current situation**: HELIX can execute bounded commands, but the control
  model is still easy to read literally unless the user restates the workflow
  contract.
- **Pain points**: Users must manually decide when requirements changes imply
  alignment, when specs should trigger polish, and when ready work should move
  into implementation.
- **Desired outcome**: `helix-run` advances the weakest ready layer
  autonomously, escalates only when human input is needed, and keeps the
  workflow coherent across interactive and autopilot use.

## Requirements

### Functional Requirements
- `helix-run` must act as HELIX's supervisory autopilot.
- `helix-run` must choose the least-power next bounded action that restores
  progress.
- Requirement or specification changes must trigger alignment, planning, or
  polish when downstream work is affected.
- Ready governed work must trigger bounded implementation.
- Users must be able to enter any layer of the loop interactively without
  breaking autonomous continuation later.
- HELIX must stop and ask for guidance when authority, approval, or product
  judgment is missing.

### Non-Functional Requirements
- **Performance**: Control-loop decisions should be quick enough to feel
  continuous in an interactive session.
- **Security**: Supervisor actions must remain bounded and authority-ordered.
- **Scalability**: The control model should work for small repos and larger
  tracker-backed queues.
- **Reliability**: Autopilot decisions must be deterministic enough to test
  with the wrapper harness and workflow docs.

## User Stories

### US-001: Steer HELIX autopilot [FEAT-001]
**As a** HELIX operator
**I want** `helix-run` to keep advancing work until human input is required
**So that** I do not have to manually decide every phase transition

**Acceptance Criteria:**
- [ ] Given a repository with vision and PRD, when HELIX can safely continue,
  then `helix-run` advances the next bounded layer without asking for a phase
  name.
- [ ] Given a user-requested functionality change, when it affects downstream
  artifacts, then HELIX routes to alignment or planning before implementation
  resumes.

### US-002: Intervene directly anywhere [FEAT-001]
**As a** HELIX operator
**I want** to invoke align, plan, polish, implement, review, or backfill
directly
**So that** I can focus on the highest-impact area that needs my judgment

**Acceptance Criteria:**
- [ ] Given a user invoking a specific layer directly, when they do so, then
  HELIX performs that action without breaking the supervisory model.

## Edge Cases and Error Handling

- Missing or conflicting authority artifacts must stop autopilot instead of
  guessing.
- Open issues with changed specs must be polished before implementation.
- If the tracker or workflow contract is unhealthy, `helix-run` must stop and
  surface guidance.

## Success Metrics

- `helix-run` can continue autonomous progress across multiple phases without
  explicit phase instructions.
- Users spend less time manually orchestrating phase transitions.
- Trigger correctness is observable in deterministic tests and workflow docs.

## Constraints and Assumptions

- HELIX remains bounded and tracker-first.
- The workflow contract and skill descriptions will be updated to reflect the
  supervisory model.

## Dependencies

- `helix.prd`
- `ADR-001`
- Workflow contract docs
- Skill descriptions and CLI wrapper behavior

## Out of Scope

- Generic autonomous coding beyond the HELIX workflow contract
- Replacing product judgment with guessed decisions
- Parallel issue tracking systems

## Open Questions

- Which tracker metadata mutations need to become first-class CLI operations
  for issue refinement workflows?

