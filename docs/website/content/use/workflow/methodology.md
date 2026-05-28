---
title: Methodology
weight: 1
aliases:
  - /docs/workflow/methodology
---

HELIX is an opinionated, runtime-neutral methodology for AI-assisted
software development. Named after the double helix of DNA, it encodes the
idea that **planning and execution are two complementary strands** that feed
back into each other. The methodology defines the artifact graph, authority
order, lifecycle activities, and alignment practice; your chosen platform owns
the runtime mechanics.

## Why HELIX Exists

Three approaches to software development each make a different mistake:

- **Waterfall** assumes you can plan completely, then execute.
- **Agile** (in many implementations) assumes you can execute without planning.
- **Vibe coding / ad-hoc agentic development** assumes agents can infer intent
  from code alone.

HELIX says: **plan and execute simultaneously, at multiple levels of
abstraction, with documentation as the shared context layer.**

## The Double Helix

HELIX operates as two interleaved cycles:

- **Planning helix**: review, plan, validate — creates and refines the
  artifacts that describe what should be true.
- **Execution helix**: apply, measure, report — uses those artifacts to
  guide implementation, review outcomes, and feed new evidence back into
  planning.

These cycles can run concurrently. A human can refine specs while an agent
builds features. New requirements flow through the planning helix while
implementation advances through the execution helix. The shared state is the
artifact graph plus whatever tracker, queue, or runtime your platform uses.

## Progressive Abstraction Layers

Each layer is a lens at a different zoom level. Changes can enter at any layer
and propagate up, down, or sideways.

| Layer | Artifact | Purpose |
|-------|----------|---------|
| **Discovery** | Research, competitive analysis | Understand the problem space |
| **Vision** | Product Vision | What is the thing? Why does it exist? |
| **Requirements** | PRD | High-level features and constraints |
| **Specification** | Feature Specs + Acceptance Criteria | What each feature does, how we know it works |
| **Design** | Technical Designs, Solution Designs, ADRs | How to build it, what trade-offs we make |
| **Test** | Test suites (from acceptance criteria) | Executable assertions proving requirements are met |
| **Code** | Implementation | The software itself |

Higher layers govern lower layers. Source code reflects what exists, not what
should exist. When layers disagree, HELIX resolves by escalating to the
governing source — not by guessing from code alone.

## Seven Activities

Work moves through seven activities. These are not a sequential pipeline — teams
regularly loop back as they learn — but each activity has a distinct job in the
artifact graph.

| Activity | Description | Key Activities |
|-------|-------------|----------------|
| **Discover** | Explore the problem space | Market analysis, competitive review, stakeholder research |
| **Frame** | Decompose the problem into structured artifacts | Vision, PRD, Feature Specs, Acceptance Criteria |
| **Design** | Decide how the system should change | Technical designs, solution designs, ADRs, interface contracts |
| **Test** | Encode requirements as testable assertions | Test plans, acceptance tests, verification strategy |
| **Build** | Implement against the governing artifacts | Code changes, reviews, integration, concern compliance |
| **Deploy** | Release and operate the result | Runbooks, rollout plans, operational evidence |
| **Iterate** | Improve from measured outcomes | Retrospectives, research updates, optimization, follow-on planning |

## Multi-Directional Workflow

HELIX is **not top-down**. Changes can enter at any layer:

- **Top-down**: Update the vision, and HELIX propagates through specs, designs,
  and implementation.
- **Bottom-up**: See the output of a build, provide feedback, and HELIX routes
  corrections to the right layer.
- **Middle-out**: Refine a feature spec because implementation revealed a
  missing requirement.
- **From running systems**: Interact with the working software, provide
  unstructured feedback ("I don't like how this looks"), and HELIX determines
  which abstraction layer the feedback applies to.

All of these flows use the same authority order. The alignment-and-planning
skill helps reconcile drift and recommend the next safe planning action.
Runtime commands, queue operations, and CLI wrappers may automate parts of
the flow on a specific platform, but they are not the methodology itself.

## Artifact Graph

HELIX artifacts form a directed graph of relationships:

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

This graph enables:

- **Impact analysis** — when an artifact changes, identify which others are
  affected
- **Reconciliation** — verify that dependent artifacts remain consistent
- **Context synthesis** — a runtime can pull in the governance chain needed
  for a specific change

## Cross-Cutting Concerns

Cross-cutting concerns are first-class artifacts in HELIX. They capture
technology choices, quality attributes, and conventions that apply across
multiple features:

- **Technology stacks**: language, runtime, package manager, test framework
- **Quality attributes**: accessibility, observability, internationalization
- **Conventions**: linting, formatting, naming, error handling

Concerns are declared in the project and folded into the work context through
context digests or an equivalent platform mechanism, so agents respect them
without being reminded in every prompt.

## Review and Alignment

HELIX encourages independent review and alignment as core practices:

- After an agent completes work, a different agent (or different AI model)
  examines it against the artifact hierarchy
- Reviews check: Does the implementation match the spec? Does the spec still
  align with the PRD? Are cross-cutting concerns respected?
- Review findings become artifact amendments, tracker work, or platform
  tasks, feeding back into the planning helix

The portable alignment skill is the main HELIX surface here. It is where the
methodology inspects artifact consistency, identifies drift, and helps humans
choose whether to refine the plan, update artifacts, select a platform task,
or continue implementation.
