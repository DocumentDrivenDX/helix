# Test Plan Generation Prompt

Scope: project-level verification strategy — goal, framework choices with cost, critical paths, data strategy, known gaps, and build commands.

Related:
- [Story Test Plan](../story-test-plan/prompt.md) — per-story AC↔test traceability
- [Test Suites](../test-suites/prompt.md) — suite inventory and boundaries under `tests/`
- [Test Procedures](../test-procedures/prompt.md) — runner procedures, commands, evidence capture

## Reference Anchors

Use these local resource summaries as grounding:

- `docs/resources/google-test-sizes.md` grounds test levels by scope,
  isolation, dependencies, and CI enforcement.
- `docs/resources/fowler-practical-test-pyramid.md` grounds balanced coverage
  across fast focused tests and fewer broad end-to-end tests.

## Storage Location

`docs/helix/03-test/test-plan.md`

## What to Include

- the goal: what must be true to ship, and what is out of scope
- framework choice per layer, with why, CI time, and maintenance burden
- critical paths (P0)
- acceptance-criteria **layer allocation**: map each in-scope `US-<n>-AC<m>`
  criterion class to one primary layer and confirm every P0 is allocated (the
  STP owns the per-AC rows)
- test data strategy
- known gaps and accepted risks
- build commands and the blocking gate

Do not hand-maintain test counts or timings. If you cite a baseline, pin it to a commit.

## Keep In Mind

- tests encode governing behavior and may be consolidated as implementation improves
- every test should trace to a requirement or story
- put effort where failure costs most; reuse existing coverage and add tests for distinct gaps
- assess test maintenance cost, including setup, test code volume, runtime and assertion quality; use coverage percentages only with their measured scope and limitations
- do not add generic testing doctrine that the template already implies

## Boundary Test

| If you are writing... | Put it in... |
|---|---|
| Overall strategy, framework choices, critical paths, CI gates | Test Plan |
| One story's concrete test cases and fixtures | Story Test Plan |
| Feature behavior or acceptance criteria | Feature Specification or User Story |
| Implementation sequencing for code changes | Implementation Plan |

Use template at `workflows/activities/03-test/artifacts/test-plan/template.md`.

## Boundary Verification

For handwritten source, apply `modularity-and-encapsulation`. Name the actual
project-local dependency checker command and exercise permitted imports and a
forbidden import that must fail; cover cycles/private access where supported.
Verify invariant protection through public APIs, review public vendor-type leakage,
and test core isolation/substitution when promised by the selected style. Record
unsupported static checks as named semantic review obligations; a presence check
or green import graph does not prove encapsulation. Existing-debt baselines may
allow unchanged violations but must reject new violations.

## Diagnostic Test Strategy

When `o11y-otel` applies, allocate the template's diagnostic test layers and
project-owned budgets. Require real receiver evidence and privacy/failure proof;
put exact assertions and runnable tests in Story Test Plans. Use the pilot in
`workflows/references/agent-diagnostics.md`; distinguish planned proof from
executed measurements. Service-only expectations are conditional on actual
surfaces, not on whether an agent edits the project.
