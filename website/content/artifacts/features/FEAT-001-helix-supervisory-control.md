---
title: "Feature Specification: FEAT-001 - HELIX Supervisory Control"
slug: FEAT-001-helix-supervisory-control
weight: 30
activity: "Frame"
source: "01-frame/features/FEAT-001-helix-supervisory-control.md"
generated: true
collection: features
---

> **Source identity** (from `01-frame/features/FEAT-001-helix-supervisory-control.md`):

```yaml
ddx:
  id: FEAT-001
  depends_on:
    - helix.prd
  status: superseded
  superseded_by: helix.prd
  review:
    self_hash: df7d279639d071dc9404f0b779f3e7fcc4bfc6a263dff28fd1ded3a01039a8cd
    deps:
      helix.prd: 703d5ebaa378d037fd5ff6cbdf43e015ee014ca6a29b5df0b4c67ba9b117a510
    reviewed_at: "2026-05-15T04:11:24Z"
```

> **SUPERSEDED** — This feature defined `helix-run` as HELIX's supervisory
> autopilot and treated tracker-first execution as a core product capability.
> The current PRD (`helix.prd`) reverses that scope: HELIX is a portable
> methodology and artifact catalog; CLI, execution loop, and runtime
> orchestration are out of scope and belong to the adopting runtime (DDx,
> Genie, etc.). This document is retained for historical context only and
> must not govern new HELIX work.

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
- Ready governed work must trigger bounded build work.
- Users must be able to enter any layer of the loop interactively without
  breaking autonomous continuation later.
- Interactive refinement performed while `helix-run` is active must be
  reflected at the next safe execution boundary.
- HELIX must stop and ask for guidance when authority, approval, or product
  judgment is missing.
- The supervisory loop must keep doing useful work by staying focused on an
  active epic, retrying difficult work with bounded exponential backoff, and
  absorbing small adjacent changes when they are clearly part of the current
  slice.
- The supervisory loop must produce a blocker report and expose enough
  structured state for `helix status` to explain what the run controller is
  doing and why it stopped.

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
**So that** I do not have to manually decide every activity transition

**Acceptance Criteria:**
- [ ] Given a repository with vision and PRD, when HELIX can safely continue,
  then `helix-run` advances the next bounded layer without asking for a activity
  name.
- [ ] Given a user-requested functionality change, when it affects downstream
  artifacts, then HELIX routes to alignment, evolve, or design before build
  resumes.

### US-002: Intervene directly anywhere [FEAT-001]
**As a** HELIX operator
**I want** to invoke align, evolve, design, polish, build, review, status, or
backfill
directly
**So that** I can focus on the highest-impact area that needs my judgment

**Acceptance Criteria:**
- [ ] Given a user invoking a specific layer directly, when they do so, then
  HELIX performs that action without breaking the supervisory model.

## Edge Cases and Error Handling

- Missing or conflicting authority artifacts must stop autopilot instead of
  guessing.
- Open issues with changed specs must be polished before build resumes.
- A selected execution issue that changes materially before claim or close must
  be revalidated instead of being processed from stale state.
- If the tracker or workflow contract is unhealthy, `helix-run` must stop and
  surface guidance.
- If an epic is in focus and one child becomes intractable after bounded
  retries, HELIX must block the epic explicitly and report the blocker rather
  than silently drifting to unrelated work.

## Success Metrics

- `helix-run` can continue autonomous progress across multiple activities without
  explicit activity instructions.
- Users spend less time manually orchestrating activity transitions.
- Trigger correctness is observable in deterministic tests and workflow docs.

## Constraints and Assumptions

- HELIX remains bounded and tracker-first.
- The tracker is the steering wheel for day-to-day execution control, and the
  workflow contract plus skill descriptions must preserve that model.
- Cross-model verification is preferred when review or critique automation is
  configured.

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

- Which tracker metadata mutations and supersession relationships need to
  become first-class CLI operations for issue refinement workflows?
