---
ddx:
  id: TP-XXX
  authoring:
    home: repo
---

# Test Plan

## Testing Strategy

**Goals**: [Primary objective] | [Quality gates]
**Out of Scope**: [Excluded areas]
**Traceability Source**: [PRD / FEAT / US artifacts that drive the plan]

### Test Levels

| Level | Coverage Target | Priority |
|-------|-----------------|----------|
| Contract | [Target and scope] | P0/P1 |
| Integration | [Target and scope] | P0/P1 |
| Unit | [Target and scope] | P0/P1 |
| E2E | [Target and scope] | P0/P1 |

### Frameworks

| Type | Framework | Reason |
|------|-----------|--------|
| Contract | [Framework] | [Why] |
| Integration | [Framework] | [Why] |
| Unit | [Framework] | [Why] |
| E2E | [Framework] | [Why] |

## Test Data

| Type | Strategy |
|------|----------|
| Fixtures | [Static data approach] |
| Factories | [Dynamic generation] |
| Mocks | [External service mocking] |

## Coverage Requirements

| Metric | Target | Minimum | Enforcement |
|--------|--------|---------|-------------|
| Line | 80% | 70% | CI blocks |
| Critical | 100% | 100% | Required |

### Critical Paths (P0)

1. [Auth flow]
2. [Core transaction]
3. [Data persistence]
4. [Error handling]

### Secondary Paths (P1-P2)

- P1: [Secondary features] | P2: [Edge cases, rare scenarios]

## Acceptance Criteria Layer Allocation

This project test plan **aggregates** strategy across stories. It does **not**
restate the per-criterion AC↔test matrix — that lives in each story test plan
(STP), keyed by stable `US-<n>-AC<m>` IDs (FEAT-008 FR-6). Here, allocate
criterion *classes* to test layers and confirm every P0 criterion is allocated:

| AC class / source | Story Test Plan(s) | Primary Layer | Why this layer |
|-------------------|--------------------|---------------|----------------|
| [e.g. upload/validation criteria] | [[STP-XXX]] | Integration | [boundary + persistence] |
| [e.g. visible reviewer flow] | [[STP-XXX]] | E2E | [user-observable outcome] |

**Allocation rule**: no P0 acceptance criterion is left unallocated — every
`US-<n>-AC<m>` from an in-scope story maps to exactly one primary layer here and
to concrete tests in its STP. The STP owns the per-AC rows; this plan owns the
layer allocation.

## Implementation Order
1. [What must be written first and why]
2. [What follows]
3. [What can wait]

## Infrastructure

| Requirement | Specification |
|-------------|---------------|
| CI Tool | [Tool, version] |
| Test DB | [Type, seeding, cleanup] |
| Services | [Required services] |

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Flaky tests | High | Retry logic, isolation |
| Slow execution | Med | Parallelize |

**Known Gaps**: [Limitations and accepted risks]

## Build Handoff

**Commands**: `[test command]` | `[coverage command]`
**Priority**: [Recommended order]

**Blocking Gate**: [What must pass before implementation is considered done]
