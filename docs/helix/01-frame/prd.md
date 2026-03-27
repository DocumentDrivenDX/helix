---
dun:
  id: helix.prd
---
# Product Requirements Document

## Summary

HELIX is a development control system for AI-assisted software delivery. It
combines collaborative planning with a supervisory autopilot that keeps work
moving across requirements, specifications, designs, tests, implementation,
review, and metrics until human judgment is actually needed.

The primary product experience is not a bag of commands. It is a loop in which
the user can work interactively at any layer, while `helix-run` autonomously
detects downstream implications, selects the least-powerful sufficient next
action, and advances the workflow without requiring repeated manual
orchestration.

## Problem and Goals

### Problem

AI-assisted development tools are good at producing local output, but weak at
maintaining coherent progress across a full software delivery stack. Users must
still tell the system what phase to enter next, remember when requirements
changes imply design updates, decide when stale issues need refinement, and
manually reconnect implementation work to governing artifacts.

That creates three failures:

1. Too much operator effort goes into orchestration instead of judgment.
2. Requirements, designs, tests, issues, and code drift out of alignment after
   iterative changes.
3. The agent behaves too literally unless the user remembers the HELIX method
   and explicitly restates it.

### Goals

1. Make `helix-run` the default supervisory autopilot for HELIX-managed work.
2. Ensure HELIX automatically advances the highest-leverage ready layer that
   does not require human input.
3. Make direct commands and skills available as intervention points inside the
   same loop, not as disconnected parallel interfaces.
4. Preserve bounded execution, authority order, and tracker-first discipline
   while making the system feel fluid in interactive use.

### Success Metrics

| Metric | Target | Measurement Method | Timeline |
|--------|--------|-------------------|----------|
| Autopilot progression | `helix-run` can advance from existing vision/requirements through downstream refinement and bounded execution without explicit phase instructions | End-to-end scenario tests and workflow walkthroughs | Year 1 |
| Reduced orchestration burden | Users rarely need to tell HELIX which phase to enter next when authority is sufficient | Qualitative operator evaluation and session review | Year 1 |
| Trigger correctness | Requirement changes, spec changes, and ready implementation work route to the expected HELIX actions | Deterministic tests and spec-driven examples | Year 1 |
| Safe escalation | HELIX asks for input mainly at real judgment boundaries, not because the control contract is underspecified | Review of intervention points in representative sessions | Year 2 |

### Non-Goals

- Create an unbounded autonomous coding agent.
- Replace product, design, or prioritization judgment with guessed decisions.
- Require autopilot mode for all users or all tasks.
- Flatten all HELIX phases into one generic prompt.

Deferred items tracked in `docs/helix/parking-lot.md`.

## Users and Scope

### Primary Persona: HELIX Operator
**Role**: Developer, tech lead, or staff engineer using AI as a day-to-day development partner  
**Goals**: Express product intent clearly, intervene where judgment matters, and let the system carry forward the rest of the workflow  
**Pain Points**: Too much manual orchestration, repeated re-explaining of workflow expectations, artifact drift after changes, and inconsistent issue quality

### Secondary Persona: HELIX Maintainer
**Role**: Maintainer evolving the HELIX workflow, CLI, skills, and tracker  
**Goals**: Keep the workflow contract coherent across docs, skills, and implementation  
**Pain Points**: The product intent is easy to dilute when surface docs or skill descriptions become too command-literal

## Requirements

### Must Have (P0)

1. `helix-run` acts as HELIX's supervisory autopilot rather than a narrow
   command wrapper.
2. `helix-run` continuously selects the highest-leverage next bounded action
   that can be taken safely without user input.
3. HELIX applies the principle of least power when choosing the next action.
   It should refine or reconcile existing artifacts before escalating to larger
   changes.
4. HELIX detects downstream implications of user-driven changes.
   - A functionality change request triggers specification and design work when
     needed.
   - A specification or design change triggers issue refinement when open work
     already exists.
   - Ready execution work triggers bounded implementation.
5. HELIX escalates to the user when safe progress depends on missing authority,
   unresolved ambiguity, tradeoffs, prioritization, or approval.
6. Users can directly invoke any layer of the workflow interactively without
   breaking the overall control model.
7. Tracker state remains the durable execution layer for refinement, ordering,
   ownership, and completion of work.

### Should Have (P1)

1. HELIX documents explicit trigger rules between `run`, `align`, `plan`,
   `polish`, `implement`, `review`, `check`, and `backfill`.
2. Skills describe not only what each command does, but when it should
   activate based on user intent and repo state.
3. The workflow contract makes it obvious where human attention is expected and
   where autopilot should proceed silently.
4. Deterministic tests cover the most important state transitions in the
   supervisory loop.

### Nice to Have (P2)

1. Operator-facing examples show common transitions such as requirements change
   -> align/plan -> polish -> implement -> review.
2. The tracker can evolve to support richer metadata updates needed by issue
   refinement workflows.

## Functional Requirements

### Supervisory Run Loop

1. `helix-run` must own autonomous forward progress for HELIX-managed work.
2. `helix-run` must treat the companion HELIX actions as triggered subroutines
   inside the loop, while still allowing them to be invoked directly.
3. `helix-run` must stop when human input is required rather than continuing
   through uncertainty.

### Trigger Rules

1. When the user asks for a functionality change, HELIX must evaluate whether
   existing requirements, feature specs, or designs need reconciliation or
   expansion before implementation work continues.
2. When requirements or design artifacts change and open issues already exist,
   HELIX must refine the issue queue before implementation resumes.
3. When issues are ready and adequately governed by upstream artifacts, HELIX
   must prefer bounded implementation over further speculative planning.
4. After implementation, HELIX must review the recent work before proceeding to
   additional execution.
5. When canonical artifacts are missing or too incomplete for safe progress,
   HELIX must stop for guidance or run a bounded reconstruction path rather
   than guessing.

### Interactive Operation

1. Users must be able to work directly in vision, PRD, specs, designs, issues,
   tests, implementation, review, or metrics.
2. Direct invocation of a single HELIX command or skill must not break the
   broader model that `helix-run` uses to resume supervision later.

## Constraints, Assumptions, Dependencies

### Constraints

- **Technical**: HELIX must preserve bounded actions, authority-ordered
  decision-making, and tracker-first execution.
- **Product**: The interface must stay comprehensible; new supervisory behavior
  cannot devolve into hidden magical state changes.
- **Testing**: The control loop should be explainable and testable through
  deterministic scenarios, not only anecdotal chat transcripts.

### Assumptions

- Repositories using HELIX have or will produce a usable authority stack:
  vision, requirements, specs, designs, tests, and issues.
- Users want the ability to intervene anywhere in the workflow even when
  autopilot exists.
- The least-power heuristic can be documented tightly enough to avoid arbitrary
  agent behavior.

### Dependencies

- Workflow contract documents under `workflows/`
- HELIX tracker contract in `workflows/TRACKER.md` and `scripts/tracker.sh`
- Skill surfaces under `skills/`
- CLI execution surface in `scripts/helix`

## Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Autopilot remains too vague and agents continue behaving literally | High | High | Define trigger rules and escalation boundaries explicitly in the PRD and workflow contract |
| The system overreaches and makes product decisions without authority | Medium | High | Preserve bounded actions, least-power rules, and escalation-on-ambiguity requirements |
| Interactive commands and autopilot drift into separate mental models | Medium | High | Define companion commands as intervention points inside one shared control system |
| Existing docs and skills lag behind the product contract | High | Medium | Follow the PRD with explicit workflow and skill-spec updates plus tracker issues |

## Success Criteria

- `helix-run` is defined as HELIX's supervisory autopilot in the product docs.
- The PRD makes clear when HELIX should continue autonomously and when it must
  stop for user input.
- The PRD defines the required transitions among requirement changes, design
  reconciliation, issue refinement, bounded implementation, and review.
- The PRD makes direct commands and skills subordinate to one coherent control
  model rather than describing them as isolated wrappers.
