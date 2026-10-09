---
ddx:
  id: implementation-plan
  authoring:
    home: repo
---

# Build Plan

## Scope

**Governing Artifacts**:
- [docs/helix/01-frame/...]
- [docs/helix/02-design/...]
- [docs/helix/03-test/...]

## Shared Constraints

- [Constraint from requirements, design, architecture, or security]

## Implementation Slices

For handwritten source, put boundary adoption/map and checker scaffolding before
feature slices that depend on them. Name the project-local boundary command and
its local/pre-commit/CI wiring; identify allowed/forbidden import controls.

| Slice | Story / Area | Governing Artifacts | Depends On | Validation Gate | Notes |
|-------|---------------|---------------------|------------|-----------------|-------|
| [B-001] | [US-XXX or area] | [TP/TD refs] | None | [Command/evidence] | [Why first] |
| [B-002] | [US-XXX or area] | [TP/TD refs] | [Dependency] | [Command/evidence] | [Why next] |

## Issue Decomposition

Story-level work is tracked as work items in the runtime's work-item store.

**Per-issue requirements**:
- Labels: `helix`, `activity:build`, `kind:build`, `story:US-{story-id}`
- References: user story, technical design, story test plan, this build plan
- `spec-id` pointing at the nearest governing artifact
- Blockers as dependency links

| Story / Area | Goal | Dependencies |
|--------------|------|--------------|
| [US-XXX] | [Outcome] | [Deps] |

## Validation Plan

- [ ] Failing tests exist before implementation starts
- [ ] All required tests pass before closing a build issue
- [ ] Behavior changes update canonical documents
- [ ] Code review is complete before activity exit

## Risks and Rollbacks

| Risk | Impact | Response | Rollback |
|------|--------|----------|----------|
| [Risk] | [H/M/L] | [Action] | [How to reverse or disable] |

## Exit Criteria

- [ ] Build issue set is defined with sequence and dependencies
- [ ] Shared constraints are documented
- [ ] Verification expectations are explicit
- [ ] Runtime issues can be created from this plan without inventing scope

## Diagnostic Evidence Sequencing (when applicable)

For selected `o11y-otel` practices, sequence Contracts before dependent wiring,
then real receiver/conformance and failure proof before the service/CLI diagnostic
pilot. Each closeout names run/attempt, safe evidence location, verification
outcome and capture limits. A quiet console is not verification evidence.
