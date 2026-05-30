# Test Suites Generation Prompt

Scope: suite layout under `tests/` — boundaries (contract/integration/unit/E2E), behaviors each suite owns, shared fixtures, and execution commands.

Related:
- [Test Plan](../test-plan/prompt.md) — project verification strategy these suites realize
- [Story Test Plan](../story-test-plan/prompt.md) — per-story tests that land in these suites
- [Test Procedures](../test-procedures/prompt.md) — writing, running, and maintaining the tests in these suites

## Reference Anchors

Use these local resource summaries as grounding:

- `docs/resources/fowler-practical-test-pyramid.md` grounds suite balance across
  unit, integration, and end-to-end coverage.
- `docs/resources/google-test-sizes.md` grounds runtime and dependency
  expectations for suite grouping.
- `docs/resources/openapi-specification.md` grounds API contract suites where
  interface contracts exist.

## Storage Location

`tests/` at the project root

## Include

- contract, integration, unit, and E2E boundaries
- the behaviors each suite owns
- required fixtures, factories, or mocks
- any coverage target that matters for this stack
- suite ownership, execution commands, and evidence outputs

## Keep Out

- generic TDD teaching text
- oversized code examples
- repeated explanations of why tests come first

Use template at `workflows/activities/03-test/artifacts/test-suites/template.md`.
