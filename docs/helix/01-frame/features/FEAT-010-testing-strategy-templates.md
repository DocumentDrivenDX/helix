---
ddx:
  id: FEAT-010
  depends_on:
    - helix.prd
    - FEAT-006
    - FEAT-008
  review:
    self_hash: a2c80390aabe1e7c8e7f2145b712e3dadf3d17b8cdc1b733c9b59ead7be4869d
    deps:
      FEAT-006: 1711c08bf5e041cd041c762594f278d35744351d4a25b8251566de2dd778abd3
      FEAT-008: 898b8004c60c52c73185f68b907445f057b797bcc03706bab227b181cc07281f
      helix.prd: 2b22383538b33c6ecee57f43d85128dfef7d56254766b757aa36439e35f2bfc9
    reviewed_at: "2026-05-25T21:21:27Z"
---
# Feature Specification: FEAT-010 — Testing Strategy Templates

**Feature ID**: FEAT-010
**Status**: Draft
**Priority**: P1
**Owner**: HELIX maintainers

## Overview

"How do I know my software works?" is the central challenge of agentic
development. HELIX should provide structured guidance on testing approaches
— not test frameworks, but structured prompts and patterns that help agents
write better tests and help humans define what "works" means.

## Problem Statement

- **Current situation**: HELIX has a Plan activity that converts acceptance
  criteria into tests, but no structured templates for different testing
  strategies. Agents default to unit tests and miss integration patterns,
  property-based testing, performance benchmarking, and flow testing.
- **Pain points**:
  1. Acceptance criteria are often too vague to generate meaningful tests.
  2. Agents write narrow unit tests that pass but miss integration failures.
  3. No standard way to define performance targets and verify them.
  4. Property-based testing (invariants that hold across all inputs) is
     rarely used because agents aren't prompted for it.
  5. Resilience testing (what happens when things fail?) is never considered
     unless explicitly requested.

## Functional Requirements

### FR-1: Acceptance Test Generation

Templates and prompts for generating test scaffolding directly from
acceptance criteria. Given a feature spec with acceptance criteria, the
template guides agents to produce:

- One test per acceptance criterion.
- Setup/teardown that matches the criterion's preconditions.
- Assertions that map directly to the criterion's expected outcomes.

### FR-2: Property-Based Testing Patterns

Templates for defining invariants — properties that should hold across all
inputs. Includes:

- How to identify good properties for a given domain.
- How to express properties as test assertions.
- When property-based testing adds value vs. example-based testing.
- Integration with common property-testing libraries (e.g., fast-check,
  proptest, hypothesis).

### FR-3: Integration and Flow Testing

Templates for testing multi-step workflows where individual units pass but
the composition fails:

- API contract testing between components.
- End-to-end flow testing for user-facing workflows.
- State machine testing for stateful protocols.

### FR-4: Performance Benchmarking

Templates for defining and measuring performance targets:

- How to define measurable performance criteria (latency percentiles,
  throughput, cost budgets).
- How to write reproducible benchmarks.
- How to integrate performance checks into the build loop.
- How to set ratchet floors for performance metrics.

### FR-5: Concern-Specific Testing

Testing templates that activate based on project concerns:

- `a11y`: accessibility audit patterns, screen reader testing.
- `o11y`: observability verification (are metrics emitted? are traces
  connected?).
- `i18n`: locale testing, string extraction verification.
- `security`: input validation, authentication boundary testing.

### FR-6: AC→Test Coverage Floor

Every acceptance criterion must trace to **≥1 test that exercises it** — drives
the criterion's action and asserts its observable outcome. The story test plan's
per-AC matrix names the asserting behavior (not just a test name) so coverage is
mechanically checkable. A criterion with no exercising test is a **blocking
coverage gap** (reconcile-alignment Acceptance Criteria Validation), with one
escape hatch: a recorded reviewed exception ("manual verification accepted" /
"non-automatable AC") with evidence. A weak or irrelevant test does not count as
coverage — it is classified `UNTESTED` / `ASSERTED_UNBACKED`. This is a floor on
minimum rigor; tests beyond one-per-AC are always welcome.

### FR-7: E2E Core-Flow Coverage

A UI web app fills the `e2e-framework` slot (FEAT-006; default `e2e-playwright`).
**Selecting the tool is not coverage**: at least one core user-flow must have a
**browser e2e test that runs green against the running app** — a config plus an
unexecuted `.spec` file does not satisfy it. The run-core-flow gate lives in the
`e2e-playwright` practices; reconcile-alignment treats a core flow whose e2e was
never run against the app as `UNTESTED`.

## Non-Functional Requirements

### NFR-1: Framework Agnostic

Templates must describe *what* to test and *how to think about* testing, not
mandate specific test frameworks. Framework-specific details belong in
concern practices (FEAT-006), not here.

### NFR-2: Composable

Templates can be combined — a feature may need acceptance tests, property
tests, and performance benchmarks simultaneously.

## Acceptance Criteria

1. Acceptance test generation template exists and can produce test
   scaffolding from a feature spec's acceptance criteria.
2. Property-based testing template exists with at least three domain-specific
   examples.
3. Integration/flow testing template exists with multi-step workflow
   coverage.
4. Performance benchmarking template exists with ratchet floor integration.
5. At least two concern-specific testing templates exist (e.g., a11y, o11y).
6. Templates are referenced from `/helix frame` and `/helix plan` prompts
   so agents use them when generating test strategies.
7. Every acceptance criterion traces to ≥1 exercising test; an untested AC is a
   blocking coverage gap unless a reviewed manual/non-automatable exception is
   recorded with evidence (FR-6).
8. A UI web app fills `e2e-framework` (default `e2e-playwright`) and has ≥1 core
   user-flow covered by a browser e2e that runs green against the running app —
   tool selection alone does not satisfy this (FR-7).

## Constraints

- Must work with the existing concern system (FEAT-006).
- Must integrate with HELIX's Plan activity workflow.
- Templates are advisory — they guide agents but don't enforce specific
  tools.

## Out of Scope

- Implementing actual test framework integrations (that's concern-level).
- Chaos/fault injection testing (defer until resilience concerns exist).
- Mutation testing (interesting but not essential for initial release).
