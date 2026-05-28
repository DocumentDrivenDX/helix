---
title: Workflow
weight: 3
prev: /why
next: /reference/cli
aliases:
  - /docs/workflow
---

HELIX names seven activities in software development: Discover, Frame,
Design, Test, Build, Deploy, Iterate. Each owns a set of [artifact
types](/artifact-types/) and is connected to the others through an
[authority order](/reference/glossary/activities/) that resolves conflicts
between artifacts.

```
       ╭──── Discover ────╮
       │                  ↓
   Iterate ←─── Frame ───→ Design
       ↑                  ↓
       ╰── Deploy ←── Build ←── Test
```

Work moves between activities in every direction. The activity names
describe *what kind* of work; they don't impose an order on when it happens.

### How changes flow

Changes can enter at any activity:

- **Top-down** — a vision revision propagates into PRD, features, designs, tests, code.
- **Bottom-up** — implementation reveals a missing requirement; the spec gets a refinement.
- **Middle-out** — a design exposes a conflict between two features; both specs update.
- **Lateral** — a deploy-time observability gap surfaces an ADR question.

The alignment skill keeps these flows coherent. It walks the artifacts when
invoked, identifies drift in any direction, and produces a plan to close it.

## The Seven Activities

| Activity | Purpose | Primary Artifacts |
|---|---|---|
| **Discover** | Validate the opportunity | Product vision, business case, competitive analysis |
| **Frame** | Define what to build | PRD, feature specs, user stories, principles |
| **Design** | Decide how to build it | Architecture, ADRs, solution designs, technical designs |
| **Test** | Encode the contract as failing tests | Test plans, story test plans |
| **Build** | Implement to make tests pass | Implementation plan + executed work |
| **Deploy** | Make it observable in production | Runbook, monitoring, deployment checklist |
| **Iterate** | Close the loop with real signal | Metrics, improvement backlog, alignment reviews |

Each activity owns a set of [artifact types](/artifact-types/). The actual
artifacts a project produces appear under [Artifacts](/artifacts/).

## Authority Order

When artifacts disagree, HELIX resolves conflicts **up** the order:

1. **Product Vision** — what the product should become
2. **Product Requirements** — what must be built
3. **Feature Specs / User Stories** — detailed behavior
4. **Architecture / ADRs** — structural decisions
5. **Solution / Technical Designs** — how to build it
6. **Test Plans / Tests** — verification criteria
7. **Implementation Plans** — build sequencing
8. **Source Code** — current state (not source of truth)

Higher layers govern lower layers. Source code reflects what exists, not
what should exist. If a higher layer is missing, HELIX does not infer
intent from lower layers — the alignment skill flags the gap instead.

## The Alignment Skill

HELIX ships a single skill that operates the loop. Given the current
artifacts and (optionally) a new intent, it:

1. **Walks** the governing artifacts top-down through the authority order
2. **Identifies** drift, gaps, and contradictions across activities
3. **Produces** a plan describing the artifact updates needed to restore
   coherence, ordered by authority

The plan is the output. A runtime (DDx, Databricks Genie, Claude Code,
anything that reads markdown) executes it — creating work items,
dispatching agents, recording evidence. HELIX itself does not execute work.

### When the alignment skill produces an open question

The skill stops short of plans when:

- Authority is missing (no governing artifact for the work)
- Ambiguity cannot be resolved from existing documents
- Product judgment or prioritization is needed
- A decision requires stakeholder approval

In these cases the plan flags the open question and waits. Humans answer
at the right altitude; the loop resumes when authority is restored.

## How a Cycle Goes

A typical iteration:

1. **Intent enters** somewhere — a feature request, a metric flag, an
   incident, a refactor itch
2. **Alignment runs** against current artifacts; produces a plan describing
   which activities are affected
3. **Runtime executes** the plan, creating concrete work items in
   whatever tracker the runtime provides
4. **Artifacts update** as work happens — vision revisions, new feature
   specs, fresh ADRs, additional tests, code changes
5. **Iterate captures** what happened — metrics, alignment reviews,
   improvement backlog
6. **Intent enters again** — feeding the next pass

The loop does not "finish." It runs continuously, with the alignment skill
catching drift before it accumulates and the runtime executing work
between alignment passes.
