# Build Plan Generation Prompt

Create the canonical build plan for the Build activity. Keep it short, but preserve the sequencing, issue boundaries, and verification rules needed to execute implementation against the test plan and technical designs.

## Purpose

The Implementation Plan is the **build sequencing and execution-readiness
artifact**. Its unique job is to translate approved story, technical design, and
test-plan context into bounded implementation slices with dependencies,
validation gates, and closeout evidence.

It is not the tracker. The runtime owns issue state and execution. This artifact
defines the intended build shape so the runtime's work items can execute
without inventing scope, ordering, or validation rules.

## Reference Anchors

Use this local resource summary as grounding:

- `docs/resources/google-small-cls.md` grounds small, reviewable,
  rollback-friendly implementation slices with related tests.

## Active Concerns

For each concern selected in `docs/helix/01-frame/concerns.md`, apply its declared
`## Artifact Impact` (from `workflows/concerns/<name>/concern.md`) to THIS build plan — realize the
IMPLEMENTATION_PLAN-level obligations it names (relational-data-modeling -> migration steps; resilience -> guard wiring; usage-metering -> metering wired on the real path). A selected concern whose Artifact Impact names IMPLEMENTATION_PLAN
but leaves no trace here is drift (reconcile-alignment Concern->Artifact Realization check).

## Storage Location

`docs/helix/04-build/implementation-plan.md`

## Required Inputs

- `docs/helix/03-test/test-plan.md` and `docs/helix/03-test/test-plans/TP-*.md`
- `docs/helix/02-design/technical-designs/TD-*.md`
- project-level design constraints

## Include

- scope and governing artifacts
- build order and dependencies
- issue decomposition rules
- quality gates and closeout criteria
- risks that should refine upstream artifacts

## Boundary Test

| If you are writing... | Put it in... |
|---|---|
| Product or feature behavior changes | PRD / Feature Specification / User Story |
| Design or interface decisions | Solution Design / Technical Design / Contract / ADR |
| Exact story tests and fixtures | Story Test Plan |
| Build slice order, dependencies, and validation gates | Implementation Plan |
| Assignee, live status, claim, execution logs | runtime work item or issue |

## Template

`workflows/activities/04-build/artifacts/implementation-plan/template.md`
For tracker conventions see the runtime's install guide (DDx:
`docs/install/ddx.md`).
