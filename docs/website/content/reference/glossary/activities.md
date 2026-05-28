---
title: Activities
weight: 1
prev: /reference/glossary
next: /artifact-types
aliases:
  - /docs/glossary/activities
  - /reference/glossary/activities
---

HELIX names seven **activities** in software development: Discover, Frame,
Design, Test, Build, Deploy, Iterate. Each owns a defined set of [artifact
types](/artifact-types/). Work moves between them — a vision change propagates
downstream, a failing test reveals a design gap, a production metric revises
the PRD. The activity names describe a kind of work, not a position in a
sequence.

```
       ╭──── Discover ────╮
       │                  ↓
   Iterate ←─── Frame ───→ Design
       ↑                  ↓
       ╰── Deploy ←── Build ←── Test
```

Each activity produces a defined set of [artifact types](/artifact-types/).
Authority flows from higher-level activities (Discover, Frame) toward
lower-level ones (Build, Deploy), but **feedback flows freely in all
directions** — implementation reveals missing requirements; a deploy-time
gap surfaces an ADR question; an iterate-activity metric revises the vision.

## Discover

Validate the opportunity before committing to building anything.

| | |
|---|---|
| **Purpose** | Research the market, users, and technical feasibility |
| **Location** | `docs/helix/00-discover/` |
| **Key artifact types** | [Product Vision](/artifact-types/product-vision/), [Business Case](/artifact-types/business-case/), [Competitive Analysis](/artifact-types/competitive-analysis/), [Opportunity Canvas](/artifact-types/opportunity-canvas/) |
| **Output** | A validated opportunity worth pursuing |

## Frame

Turn the opportunity into actionable requirements.

| | |
|---|---|
| **Purpose** | Define the problem, establish requirements, and scope the work |
| **Location** | `docs/helix/01-frame/` |
| **Key artifact types** | [PRD](/artifact-types/prd/), [Feature Specifications](/artifact-types/feature-specification/), [User Stories](/artifact-types/user-stories/), [Principles](/artifact-types/principles/), [Stakeholder Map](/artifact-types/stakeholder-map/), [Risk Register](/artifact-types/risk-register/) |
| **Output** | Requirements clear enough to design against |

Frame also selects the project's active [cross-cutting
concerns](/concerns/) and establishes [design
principles](/artifact-types/principles/) that govern downstream judgment.

## Design

Architect the solution approach.

| | |
|---|---|
| **Purpose** | Make technology and architecture decisions before writing code |
| **Location** | `docs/helix/02-design/` |
| **Key artifact types** | [Architecture](/artifact-types/architecture/), [ADR](/artifact-types/adr/), [Solution Design](/artifact-types/solution-design/), [Technical Design](/artifact-types/technical-design/), [Contract](/artifact-types/contract/), [Data Design](/artifact-types/data-design/), [Tech Spike](/artifact-types/tech-spike/) |
| **Output** | Design contracts that tests can verify |

Solution designs are feature-level. Technical designs are story-level slices
that inherit from a solution design.

## Test

Encode requirements and designs as executable specifications — failing tests
that define what "done" means.

| | |
|---|---|
| **Purpose** | Turn requirements and designs into executable specifications |
| **Location** | `docs/helix/03-test/`, `tests/` |
| **Key artifact types** | [Test Plan](/artifact-types/test-plan/), [Story Test Plan](/artifact-types/story-test-plan/), [Test Procedures](/artifact-types/test-procedures/), [Test Suites](/artifact-types/test-suites/), [Security Tests](/artifact-types/security-tests/) |
| **Output** | Failing tests that define behavior |

Tests are the contract between design and implementation. Code must satisfy
tests, not the other way around.

## Build

Implement code to make the failing tests pass.

| | |
|---|---|
| **Purpose** | Write the minimum code needed to satisfy the tests |
| **Location** | `docs/helix/04-build/`, source code |
| **Key artifact types** | [Implementation Plan](/artifact-types/implementation-plan/) |
| **Output** | Passing tests, committed code |

Implementation is complete when the tests pass.

## Deploy

Release the work to production with observability and operator guidance.

| | |
|---|---|
| **Purpose** | Safely deliver the built software to users |
| **Location** | `docs/helix/05-deploy/` |
| **Key artifact types** | [Deployment Checklist](/artifact-types/deployment-checklist/), [Monitoring Setup](/artifact-types/monitoring-setup/), [Runbook](/artifact-types/runbook/), [Release Notes](/artifact-types/release-notes/) |
| **Output** | A production rollout with observability and operator guidance |

## Iterate

Learn from real signal and feed it back into the loop.

| | |
|---|---|
| **Purpose** | Review what was built, capture learnings, inform the next cycle |
| **Location** | `docs/helix/06-iterate/` |
| **Key artifact types** | [Improvement Backlog](/artifact-types/improvement-backlog/), [Metric Definition](/artifact-types/metric-definition/), [Metrics Dashboard](/artifact-types/metrics-dashboard/), [Security Metrics](/artifact-types/security-metrics/) |
| **Output** | Findings, metrics, and follow-up work that feed the next iteration |

Iterate closes the loop — alignment reviews, experiments, and metric
analyses produce inputs to the next pass through Discover or Frame.
