# Test Plan Generation Prompt

Scope: project-level verification strategy — test levels, coverage targets, critical paths, data strategy, infrastructure, sequencing, risks, and build handoff commands.

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

- test levels and scope
- framework choices only where they matter
- coverage targets and critical paths
- acceptance-criteria **layer allocation** — allocate each in-scope
  `US-<n>-AC<m>` criterion class to a primary test layer and confirm every P0 is
  allocated. **Aggregate** the story test plans; do **not** duplicate their
  per-AC matrix (the STP owns that, keyed by stable AC ID — FEAT-008 FR-6).
- test data strategy
- sequencing, dependencies, and infrastructure needs
- risks that can block test execution

## Keep In Mind

- tests are the executable specification
- every test should trace to a requirement or story
- coverage targets should be risk-based and enforced, not decorative
- do not add generic testing doctrine that the template already implies

## Boundary Test

| If you are writing... | Put it in... |
|---|---|
| Overall test levels, coverage targets, data strategy, CI gates | Test Plan |
| One story's concrete test cases and fixtures | Story Test Plan |
| Feature behavior or acceptance criteria | Feature Specification or User Story |
| Implementation sequencing for code changes | Implementation Plan |

Use template at `workflows/activities/03-test/artifacts/test-plan/template.md`.
