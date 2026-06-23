# Story Test Plan Generation Prompt

Scope: one story's acceptance-criteria-to-test traceability — concrete failing tests, fixtures, commands, and setup for a single bounded slice.

Related:
- [Test Plan](../test-plan/prompt.md) — project-wide strategy this STP inherits
- [Test Suites](../test-suites/prompt.md) — where these story tests live under `tests/`
- [Test Procedures](../test-procedures/prompt.md) — how tests get written and run

## Reference Anchors

Use these local resource summaries as grounding:

- `docs/resources/cucumber-executable-specifications.md` grounds acceptance
  criteria as observable executable examples.
- `docs/resources/google-test-sizes.md` grounds story test levels by scope,
  dependency, and execution cost.

## Storage Location

`docs/helix/03-test/test-plans/STP-{id}-{name}.md`

## What to Include

- the governing `[[US-XXX-*]]` and `[[TD-XXX-*]]` references
- a tight scope statement plus explicit out-of-scope boundaries
- a matrix mapping each active acceptance criterion to concrete failing tests,
  keyed by the story's **stable `US-<n>-AC<m>` ID** (this story-level matrix is
  the AC↔test traceability surface; the project test plan aggregates strategy
  and allocates layers but does not duplicate these rows — FEAT-008 FR-6). Each
  row names the **behavior/assertion the test makes** (the observable outcome it
  checks), not just a test name — a named test with no named assertion does not
  show the criterion is *exercised*. Each row also names the **covering test AND
  records that the test cites the AC ID** in the canonical, parseable syntax
  `@covers US-<n>-AC<m>` — a test that exercises and passes but does not cite the
  AC ID is `UNCITED_COVERAGE` (not covered for traceability; fix = add the
  citation, not a new test), distinct from `UNTESTED`. Citation is an additional
  gate on top of exercise+pass+satisfy, never a replacement
- executable proof details: test file paths, commands, or named test cases
- setup, fixtures, seed data, mocks, and environment assumptions
- edge cases and error scenarios that the story must prove before build begins
- build handoff notes that help implementation sequence the work

## Minimum Quality Bar

- Stay story-scoped. Do not drift into feature-wide strategy or generic testing doctrine.
- Name runnable evidence, not just test categories.
- Prefer one compact mapping table over repeated prose.
- If an acceptance criterion is not being covered now, say why explicitly.

## Boundary Test

| If you are writing... | Put it in... |
|---|---|
| Project-wide test levels, coverage, and CI gates | Test Plan |
| One story's concrete tests, fixtures, commands, and setup | Story Test Plan |
| Product behavior or acceptance criteria | User Story / Feature Specification |
| Implementation file changes | Technical Design / Implementation Plan |

Use template at `workflows/activities/03-test/artifacts/story-test-plan/template.md`.
