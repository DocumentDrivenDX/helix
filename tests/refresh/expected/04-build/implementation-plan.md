---
ddx:
  id: implementation-plan
classification: INCOMPLETE
---

# Build Plan

## Scope

**Governing Artifacts**:
- docs/helix/01-frame/prd.md
- docs/helix/02-design/architecture.md
- docs/helix/03-test/test-plan.md

## Shared Constraints

- All work must pass integration tests before merging
- No changes to public APIs without design review
- Documentation updates required alongside code

## Implementation Slices

| Slice | Story / Area | Governing Artifacts | Depends On | Validation Gate | Notes |
|-------|---------------|---------------------|------------|-----------------|-------|
| B-001 | US-123: Validation engine | TP-XXX, TD-cache | None | pytest tests pass | Core foundation |
| B-002 | US-124: Report aggregation | TP-XXX, TD-reporting | B-001 | Integration tests | Builds on B-001 |
| B-003 | US-125: CLI interface | TP-XXX | B-002 | E2E tests | User-facing layer |

## Issue Decomposition

Story-level work is tracked via `ddx bead` in `.ddx/beads.jsonl`.

**Per-issue requirements**:
- Labels: `helix`, `activity:build`, `kind:build`, `story:US-{story-id}`
- References: user story, technical design, story test plan, this build plan
- `spec-id` pointing at the nearest governing artifact
- Blockers as dependency links

| Story / Area | Goal | Dependencies |
|--------------|------|--------------|
| US-123 | Implement validation logic for all artifact types | None |
| US-124 | Aggregate findings into unified report format | US-123 |
| US-125 | Wire CLI command handler | US-124 |

## Validation Plan

- [ ] Failing tests exist before implementation starts
- [ ] All required tests pass before closing a build issue
- [ ] Behavior changes update canonical documents
- [ ] Code review is complete before activity exit

## Risks and Rollbacks

| Risk | Impact | Response | Rollback |
|------|--------|----------|----------|
| Validation engine bugs | High | Comprehensive unit tests | Revert commits and run tests |
| Performance degradation | Med | Profile before merge | Use previous git commit |
| API breaking changes | High | Deprecation period | Maintain both old and new |

## Exit Criteria

- [ ] Build issue set is defined with sequence and dependencies
- [ ] Shared constraints are documented
- [ ] Verification expectations are explicit
- [ ] Runtime issues can be created from this plan without inventing scope

## Review Checklist

Use this checklist when reviewing an implementation plan:

- [ ] Governing artifacts are listed and exist on disk
- [ ] Shared constraints trace back to requirements, design, or architecture
- [ ] Build sequence has a justified ordering — not just arbitrary
- [ ] Dependencies between build steps are explicit
- [ ] Each story/area references its governing artifacts (TP, TD)
- [ ] Issue decomposition follows tracker conventions (labels, spec-id, deps)
- [ ] Quality gates are specific and enforceable, not aspirational
- [ ] Risks have concrete responses ("we do X"), not vague strategies
- [ ] Plan is consistent with governing test plan and technical designs
