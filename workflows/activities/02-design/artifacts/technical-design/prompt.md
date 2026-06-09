# Technical Design for User Story Prompt

Create a concise technical design for one user story.

## Purpose

Technical Design is the **story-level implementation design artifact**. Its
unique job is to make one user story buildable by naming the concrete component
changes, files, interfaces, data model changes, security implications, tests,
rollback path, and implementation sequence.

Technical Design applies shared interface contracts; it does not define them.
When exact API, CLI, event, schema, config, telemetry, or adapter surface is
needed, reference the governing Contract ID. If the story uncovers a missing or
changed shared surface, create or update the Contract first, then reference it
from the TD.

It inherits Architecture and Solution Design. For what belongs at this level
versus those higher levels, see the zoom-stack matrix in
`workflows/activities/02-design/README.md`; if the story forces a change at a
higher level, update that governing artifact first.

## Reference Anchors

Use these local resource summaries as grounding:

- `docs/resources/google-small-cls.md` grounds bounded implementation slices
  with related tests and rollback.
- `docs/resources/cucumber-executable-specifications.md` grounds mapping
  acceptance criteria to observable tests.

## Active Concerns

For each concern selected in `docs/helix/01-frame/concerns.md`, apply its declared
`## Artifact Impact` (from `workflows/concerns/<name>/concern.md`) to THIS technical design — realize the
TD-level obligations it names (domain-driven-design -> aggregates/value-objects/repositories; architecture-style -> layering + dependency direction; cqrs -> command/query split). A selected concern whose Artifact Impact names TD
but leaves no trace here is drift (reconcile-alignment Concern->Artifact Realization check).

## Focus
- Create a story-level artifact named `docs/helix/02-design/technical-designs/TD-XXX-[name].md`.
- Realize each governing-story AC-ID (US-{n}-AC{m}) through component changes, interfaces, data, security, and tests; reference AC-IDs, do not restate AC text (ADR-009 — AC ownership lives in user-stories).
- Stay on the vertical slice for the story, within the story scope defined in
  the zoom-stack matrix (`workflows/activities/02-design/README.md`).
- Reference Contract IDs for exact commands, endpoints, payloads, error
  semantics, config keys, telemetry fields, event schemas, and adapter
  signatures instead of defining those normative surfaces inline.
- Keep implementation sequence and rollout or migration notes only when they affect execution.

## Boundary Test

See the zoom-stack matrix in `workflows/activities/02-design/README.md` for
which decisions belong at the system, feature, and story levels.

## Completion Criteria
- The story is implementable.
- Key interfaces, changes, and test coverage are explicit.
- Shared interface changes are captured in Contract artifacts before this TD
  references them.
- The design stays compact.
- The output is clearly story-level and disambiguated from a solution design.
- The implementation sequence can be turned into one or more small,
  reviewable changes without losing test coverage.
