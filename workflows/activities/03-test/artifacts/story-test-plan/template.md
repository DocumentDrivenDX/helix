---
ddx:
  id: STP-XXX
---

# Story Test Plan: STP-XXX-[story-name]

## Story Reference

**User Story**: [[US-XXX-[story-name]]]
**Technical Design**: [[TD-XXX-[story-name]]]
**Related Solution Design**: [[SD-XXX-[feature-name]]] or N/A
**Project Test Plan**: [[test-plan]]

## Scope and Objective

**Goal**: [What this story must prove before build starts]
**Blocking Gate**: [Command or suite that must pass for this story]

**In Scope**
- [Bounded behavior this TP governs]

**Out of Scope**
- [Adjacent behavior intentionally left to another TP, feature, or future slice]

## Acceptance Criteria Test Mapping

This matrix is the **story-level** AC↔test traceability surface. Key each row on
the story's **stable AC ID** (`US-<n>-AC<m>`) so a specific criterion maps to a
specific failing test. This story test plan owns this matrix; the project-level
test plan aggregates strategy and allocates layers — it does **not** duplicate
these rows (FEAT-008 FR-6).

Each row must name the **behavior the test asserts** — the specific observable
outcome it checks — not merely a test name. A row that lists a test name with no
named assertion does not prove the criterion is *exercised*; reconcile-alignment
classifies such a criterion `UNTESTED` (or `ASSERTED_UNBACKED` if the named test
does not exist), not covered.

Each row must also name the **covering test AND record that the test cites the
AC ID** in the canonical, parseable syntax `@covers US-<n>-AC<m>` (the structured
tag in the test body, name, or doc comment). The citation makes AC→test
traceability machine-checkable. A test that exercises and passes but does **not**
cite the AC ID is classified `UNCITED_COVERAGE` (not covered for traceability;
the fix is to add the citation, not a new test) — distinct from `UNTESTED`. The
citation is an *additional* gate on top of exercise+pass+satisfy, never a
replacement. The canonical, parseable citation syntax is `@covers US-<n>-AC<m>`
with numeric stable IDs (e.g. `@covers US-001-AC1`); `US-XXX` below is a
placeholder for the numeric story id — replace `XXX` with the real number.

| AC ID | Acceptance Criterion (Given/When/Then) | Failing Test(s) to Create or Run | Asserted Behavior (what the test verifies) | AC-ID Citation (`@covers`) | Test Level | File or Command | Setup / Data | Notes |
|-------|----------------------------------------|----------------------------------|--------------------------------------------|----------------------------|------------|-----------------|--------------|-------|
| US-001-AC1 | [Given/When/Then criterion] | `[test_name]` | [the concrete outcome the test asserts — e.g. "response is 200 with body {id}"] | `@covers US-001-AC1` | Unit / Integration / Contract / E2E | `tests/...` or `bash ...` | [Fixture, seed, mock] | [Edge case or sequencing note] |

## Executable Proof

### Primary Commands

```bash
[command that proves this TP]
```

### Planned Test Files

- `tests/...`
- `tests/...`

### Coverage Focus

- P0: [Must-pass behavior]
- P1: [Important secondary behavior]

## Data and Setup

| Need | Required For | Source / Strategy |
|------|--------------|-------------------|
| [Fixture / seed / mock / env var] | [Tests] | [Where it comes from] |

## Edge Cases and Failure Modes

- [Boundary value or empty-state handling]
- [Validation failure or invalid input]
- [Dependency failure, timeout, or permission edge]

## Build Handoff

**Implementation Order**
1. [What should be implemented first to turn the first red test green]
2. [What follows once the core path passes]

**Constraints**
- [Constraint inherited from requirements, design, concern, or contract]

**Done When**
- [ ] Every in-scope acceptance criterion has passing evidence
- [ ] Named commands or test files exist and run
- [ ] Out-of-scope coverage remains explicitly deferred rather than silently skipped
- [ ] The story can fail red before implementation and pass green after implementation

## Review Checklist

- [ ] References the governing story and technical design
- [ ] Every active acceptance criterion maps to concrete failing tests, keyed by its stable `US-<n>-AC<m>` ID
- [ ] Every AC row names the behavior/assertion the test makes, not just a test name
- [ ] Every AC row names the covering test AND records its `@covers US-<n>-AC<m>` citation (canonical AC-ID syntax)
- [ ] File paths, commands, or test identifiers are specific enough to execute
- [ ] Setup, fixtures, mocks, and seed data are explicit
- [ ] Edge cases cover real story risks rather than generic boilerplate
- [ ] Scope remains bounded to one story slice
- [ ] Build handoff gives implementation a usable sequence
