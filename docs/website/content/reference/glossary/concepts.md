---
title: Concepts
weight: 5
prev: /reference/glossary/concerns
next: /reference/glossary/tracker
aliases:
  - /docs/glossary/concepts
---

# Core Concepts

The ideas that make HELIX work.

## Artifact Authority Hierarchy

When HELIX artifacts disagree, resolve the conflict using this precedence:

1. **Product Vision** (highest authority)
2. **Product Requirements** (PRD)
3. **Feature Specs / User Stories**
4. **Architecture / ADRs**
5. **Solution Designs / Technical Designs**
6. **Test Plans / Tests**
7. **Implementation Plans**
8. **Source Code / Build Artifacts** (lowest authority)

Higher-authority artifacts govern lower-authority artifacts. Tests are executable specifications: code must satisfy tests, not the other way around. Source code is evidence of current state, not the source of truth for requirements.

If a lower-level artifact contradicts a higher one, fix the lower-level artifact. Only change higher-level artifacts when the evidence is strong and the governing artifacts are stale or incomplete.

## Specification-First Development

HELIX asks teams to state intent before implementation. Tests are one way to
turn intent into executable evidence. A common cycle is:

1. **Red** (Test activity): write a failing test that defines desired behavior
2. **Green** (Build activity): write minimal code to make the test pass
3. **Refactor** (Build activity): simplify the implementation while keeping tests green

Tests connect design and implementation, but they are not the only authority.
Runtime evidence records whether a work item is complete; tests prove the
observable behavior named by the governing artifacts.

## Principles

Design and engineering values that guide judgment calls throughout the project.

- Loaded from `docs/helix/01-frame/principles.md` (project-specific)
- Falls back to `workflows/principles.md` (HELIX defaults) if no project file exists
- Applied by every action that makes technology or quality choices
- Only the HELIX skill in `frame` mode may create or modify the principles file

Examples: "design for simplicity", "tests first", "local-first UX", "prefer composition over inheritance".

## Runtime Work Context

A runtime assembles this compact summary at triage or polish time. DDx calls it
a context digest and commonly prepends it to a bead description so the DDx work
item is self-contained.

Contents:
- **Principles**: full list, compact format
- **Concerns**: area-matched concern names
- **Practices**: key conventions from matched concerns
- **ADRs**: decision statements and rationale from relevant ADRs
- **Governing spec**: the specific requirement or constraint this work item addresses

Format: XML-tagged block prepended to the work-item description:

```xml
<context-digest>
<principles>Simplicity · Tests first · Local-first UX</principles>
<concerns>rust-cargo | security-owasp</concerns>
<practices>clippy pedantic · cargo deny · parameterized queries</practices>
<adrs>ADR-003 chose Axum over Actix for async compatibility</adrs>
<governing>FEAT-002 §3.1: WAL must fsync before acknowledging writes</governing>
</context-digest>
```

Agents read the digest as a bounded context package. The `helix` skill in
`polish` mode can propose digest updates when the runtime uses them.

## Runtime-Tracked Execution

Some runtimes, including DDx, use tracked work items as the execution handoff:

- **Operators steer** by creating, prioritizing, and blocking issues
- **Agents execute** by claiming and closing issues
- **The ready queue** is the only durable hand-off mechanism between sessions
- File follow-up work as DDx beads before an action closes; prose suggestions without tracked work items disappear

Every execution issue should cite the canonical artifacts that authorize the
work via a field such as `spec-id`.

## Bounded Execution

Every HELIX action is intentionally bounded:

- `build` handles one issue and exits
- `check` reads the queue and recommends one action
- `review` examines one scope and files findings
- `design` produces one design document

A runtime supervisor such as `ddx work` can chain bounded actions based on queue
state. No HELIX action needs to run forever. This makes execution predictable,
auditable, and interruptible.

## Cross-Model Verification

HELIX permits different AI models for implementation and review:

- The build agent implements code
- A different review agent examines the work with fresh perspective
- Alternating models creates adversarial review: the reviewer has no implementation blindness

Configured by the runtime. In DDx, review routing is runtime configuration, not
a HELIX environment-variable contract.

## Epic Focus

<!-- vale Helix.Hedges = NO -->
When the supervisor encounters a large scope (epic), it decomposes rather than deferring:
<!-- vale Helix.Hedges = YES -->

1. Break the epic into subtask issues
2. Implement the first subtask
3. Review, then continue to the next
<!-- vale Helix.PassiveVoice = NO -->
4. Close the epic when all subtasks are done
<!-- vale Helix.PassiveVoice = YES -->

Decomposition IS implementation work. The right response to a hard problem is to break it into smaller pieces, not to bail.

## Continuous Useful Work

Agents should maximize forward progress:

- **Absorb small adjacent work**: if a fix requires updating a nearby test or doc, do it in the same issue
- **Stay within scope**: don't expand beyond what the issue asks for
- **Finish with blocker reports**: if you can't complete the work, explain exactly what's blocked and create follow-on issues
<!-- vale Helix.PassiveVoice = NO -->
- **Never stop silently**: a DDx bead must be closed with evidence, or left open with a precise status note
<!-- vale Helix.PassiveVoice = YES -->

## Quality Ratchets

A mechanism for keeping metric floors monotonic:

- A **floor** is a committed minimum value for a metric (e.g., 70% test coverage)
- The floor can only go up, never down
- If the metric drops below the floor, it's a regression the team must fix
- Experiments can auto-bump the floor when improvement exceeds a threshold

<!-- vale Helix.PassiveVoice = NO -->
Ratchet definitions live in `workflows/ratchets.md` and floor fixtures are committed to the repo.
<!-- vale Helix.PassiveVoice = YES -->

## Area Taxonomy

Areas scope which [concerns](/concerns/) apply to which runtime work items:

| Area | Typical scope | Example concerns |
|------|--------------|-----------------|
| `all` | Every work item | Tech stacks, security |
| `ui` | Frontend, web | a11y, i18n |
| `api` | Backend, server | o11y, rate limiting |
| `data` | Database, storage | Data modeling |
| `infra` | Deployment, CI | k8s, monitoring |
| `cli` | CLI tools | CLI conventions |

Projects define their area labels in `docs/helix/01-frame/concerns.md`. A DDx
bead with `area:ui` gets a11y practices; a database migration work item does
not.
