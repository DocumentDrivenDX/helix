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

## Execution Contract

The user authorizes implementation separately from plan readiness. Execute the
ordered slices through their verification gates and the goal's exit criteria.
A slice is a reviewable change, not necessarily a separately scheduled issue.
Stay within Scope; stop for authority conflicts, missing authorization, or
concrete blockers requiring a decision. Ordinary debugging remains in scope.

## Continuation Evidence

On interruption, record plan revision, completed slice IDs with evidence,
remaining slices, decisions, blockers, and the next action alongside this plan.
On resume, reconcile the record with the diff and tests before continuing.
When tracking is explicitly selected, its store owns claims and live status.

## Optional Tracking

Use work items only when requested or required by the active execution contract.
Prefer one item for this goal; split for independent scheduling, ownership,
parallel execution, or deferred work. Follow the selected runtime's acceptance,
dependency, audit, and closure requirements. Do not discover tracker binaries.

## Validation Plan

- [ ] Failing tests exist before implementation starts
- [ ] All required tests pass before reporting goal completion
- [ ] Behavior changes update canonical documents
- [ ] Code review is complete before activity exit

## Risks and Rollbacks

| Risk | Impact | Response | Rollback |
|------|--------|----------|----------|
| [Risk] | [H/M/L] | [Action] | [How to reverse or disable] |

## Exit Criteria

Plan readiness requires defined scope, ordered slices, shared constraints, and
explicit verification gates. These planning checks do not establish completion.
Execution is complete only when:

- [ ] [Observable implemented goal and its acceptance evidence]
- [ ] Every required slice validation gate and the final integration gate pass.
- [ ] Acceptance evidence is recorded; no required step or material blocker remains.
- [ ] Required canonical documentation and review are complete.
- [ ] Any explicitly selected runtime's audit and closure requirements are met.

## Diagnostic Evidence Sequencing (when applicable)

For selected `o11y-otel` practices, sequence Contracts before dependent wiring,
then real receiver/conformance and failure proof before the service/CLI diagnostic
pilot. Each closeout names run/attempt, safe evidence location, verification
outcome and capture limits. A quiet console is not verification evidence.
