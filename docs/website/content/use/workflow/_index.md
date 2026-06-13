---
title: Workflow
weight: 3
prev: /why
next: /reference
aliases:
  - /use/workflow/methodology/
  - /use/workflow/methodology
  - /docs/workflow
  - /docs/workflow/methodology
---

How HELIX runs in a project: the activities, the artifact authority
hierarchy, the `helix` skill, the verification gate, and the convergence
loop. For the
argument behind the procedure, see [the thesis](/why/the-thesis/) and
[principles](/why/principles/). For the activity catalog (each activity's
purpose and artifact types), see the
[activities glossary](/reference/glossary/activities/).

## The Double Helix

HELIX operates as two interleaved cycles that share the artifact graph:

- **Planning helix**: review, plan, validate. Creates and refines the
  artifacts that describe what should be true.
- **Execution helix**: apply, measure, report. Uses those artifacts to
  guide implementation, review outcomes, and feed new evidence back into
  planning.

The two cycles run concurrently. A human refines specs while an agent
builds features. The shared state is the artifact graph plus whatever
tracker, queue, or runtime your platform owns.

## Multi-Directional Workflow

Changes can enter at any activity. The same authority hierarchy
determines which artifact governs, regardless of entry point:

- **Top-down**: a vision revision propagates into PRD, features, designs,
  tests, code.
- **Bottom-up**: implementation reveals a missing requirement; the spec
  gets a refinement.
- **Middle-out**: a design exposes a conflict between two features; both
  specs update.
- **Lateral**: a deploy-time observability gap surfaces an ADR question.
- **From running systems**: unstructured feedback ("I don't like how this
  looks") routes to the layer it applies to.

The `helix` skill keeps these flows coherent. It walks the artifacts on demand,
identifies drift in any direction, chooses the matching workflow mode, and
produces a plan to close it.

<span id="authority-order" style="display:block; scroll-margin-top: 6rem;"></span>
## Authority Hierarchy

When artifacts disagree, HELIX escalates to the higher-authority artifact:

1. **Product Vision**: what the product should become.
<!-- vale Helix.PassiveVoice = NO -->
2. **Product Requirements (PRD)**: what must be built.
<!-- vale Helix.PassiveVoice = YES -->
3. **Feature Specs / User Stories**: detailed behavior.
4. **Architecture / ADRs**: structural decisions.
5. **Solution / Technical Designs**: how to build it.
6. **Test Plans / Tests**: verification criteria.
7. **Implementation Plans**: build sequencing.
8. **Source Code**: current state, not source of truth.

Higher layers govern lower layers. Source code reflects what exists, not
what should exist. If a higher layer is missing, HELIX does not infer
intent from lower layers; the `helix` skill flags the gap instead.

## Artifact Graph

The governing artifacts form a directed dependency graph:

```
Vision ──→ PRD ──→ Feature Specs ──→ Acceptance Criteria
                        │
                        ├──→ Technical Designs
                        │
                        └──→ Solution Designs
                                    │
ADRs ←── Cross-cutting Concerns ────┘
  │
  └──→ Context Digests ──→ Runtime Work Context
```

Teams use the graph for impact analysis (which artifacts a change affects),
reconciliation (verifying dependent artifacts remain consistent), and context
synthesis (a runtime pulls the governance chain for a specific change).

## The helix Skill

The portable `helix` skill operates the loop. Given the current artifacts and
(optionally) a new intent, it:

1. **Resolves** the active scope from the marker, current directory, or prompt.
2. **Walks** the governing artifacts top-down through the authority
   hierarchy.
3. **Identifies** drift, gaps, and contradictions across activities.
4. **Produces** a plan describing the artifact updates needed to restore
   coherence, ordered by authority.

The plan is the output. A runtime (DDx, Databricks Genie, Claude Code,
anything that reads markdown) executes it, creating work items,
dispatching agents, and recording evidence. HELIX itself does not
execute work.

### When alignment produces an open question

The skill stops short of a plan when:

- Authority is missing (no governing artifact for the work).
- Existing documents cannot resolve the ambiguity.
- The work needs product judgment or prioritization.
- A decision requires stakeholder approval.

In these cases the plan flags the open question and waits. Humans
<!-- vale Helix.PassiveVoice = NO -->
answer at the right altitude; the loop resumes when authority is
<!-- vale Helix.PassiveVoice = YES -->
restored.

## How a Cycle Goes

A typical iteration:

1. **Intent enters** somewhere: a feature request, a metric flag, an
   incident, a refactor itch.
2. **HELIX runs** against current artifacts and produces a plan
   describing which activities the change affects.
3. **Runtime executes** the plan, creating concrete work items in
   the runtime-owned tracker.
4. **Artifacts update** as work happens: vision revisions, new feature
   specs, fresh ADRs, additional tests, code changes.
5. **Iterate captures** what happened: metrics, alignment reviews,
   improvement backlog.
6. **Intent enters again**, feeding the next pass.

The loop does not "finish." It runs continuously, with `helix` catching drift
before it accumulates and the runtime executing work between review passes.

## Review and Alignment

After an agent completes work, an independent review (a different agent,
a different model, or a human) examines it against the artifact
hierarchy. Reviews ask three questions:

- Does the implementation match its spec?
- Does the spec still align with the PRD and vision?
- Do the [cross-cutting concerns](/use/workflow/concerns/) hold?

Review findings become artifact amendments, tracker work, or platform
tasks, and feed back into the planning helix. Nothing dead-ends at
"reviewed."

## Verification Exit Gate

Passing build, unit tests, and a happy-path end-to-end check is not
enough to exit the Build activity. The build-exit gate requires the
interface-appropriate harness to prove each acceptance criterion's
behavior:

- **Web**: Playwright or an equivalent browser harness.
- **HTTP API**: request and response checks against a running service.
- **CLI**: shell against the built binary.
- **TUI**: a terminal harness driving the real interactive tool.
- **Backend logic**: integration tests against real dependencies.

The gate guards against work that is locally green but globally
incomplete. It is the canonical exit condition for Build, not a
suggestion.

## Evolve Until Converged

Build does not stop at first-pass green. The evolve-until-converged
loop re-checks the work against its specs and concerns and iterates
until it converges:

1. Run the verification harnesses against each acceptance criterion.
2. If any criterion is not yet proven, route the gap back to the
   appropriate artifact or implementation step.
3. Re-run.

<!-- vale Helix.PassiveVoice = NO -->
The loop is bounded (a project configures a maximum number of
<!-- vale Helix.PassiveVoice = YES -->
iterations or a convergence tolerance), but the default is "go check
your work again," not "declare done as soon as the first set of tests
passes."
