---
title: The Thesis
weight: 3
---

HELIX is the **methodology layer** for AI-assisted software development.
It packages seven kinds of work — Discover, Frame, Design, Test, Build,
Deploy, Iterate — as a catalog of artifact types and prompts, with one
skill that keeps the resulting documents aligned. The execution
runtime — agent runtime, tracker, queue control — is somebody else's
job. DDx is the reference runtime; Databricks Genie, Claude Code, and
others can run HELIX with their own per-runtime packages. The two layers together
give you supervised autonomy: AI agents doing real work, on artifacts you
can audit, with human judgment exactly where it matters.

## Three structural commitments

### Activities and artifacts give the work its shape

A HELIX project produces artifacts across seven
[activities](/reference/glossary/activities/): **Discover, Frame, Design,
Test, Build, Deploy, Iterate**. Each owns a specific set of [artifact
types](/artifact-types/) — vision documents in Discover, PRDs and feature
specs in Frame, ADRs and designs in Design, test plans in Test,
implementation work in Build, runbooks and monitoring in Deploy,
alignment reviews and metrics in Iterate.

The activities are connected by authority. A vision change propagates
downstream; a failing test reveals a missing requirement; a production
metric revises the PRD. Forty-plus artifact types each have a defined
role, an authoring prompt, a template, and a place in the [authority
order](/why/principles/#3-authority-order-governs-reconciliation). When
an artifact is missing or stale, HELIX knows which activity produces it.
When two artifacts disagree, the higher one wins.

### Concerns inject standards across activities

[Cross-cutting concerns](/concerns/) — accessibility requirements, the
project's tech stack, observability strategy, security posture — are
declared once and propagated into every relevant bead via a *context
digest*. An agent claiming a bead inherits the active concerns
automatically. Stack drift, convention drift, and quality-attribute
amnesia stop being problems an operator has to remember to fix.

This is HELIX's answer to "every project needs consistency" without
forcing any specific tech stack on the framework itself. The standards
are project-owned. The injection mechanism is universal.

### One alignment skill closes the loop

HELIX ships a single skill that reads a project's governing artifacts,
identifies drift, gaps, and contradictions, and produces a plan to close
them. It runs against any HELIX-shaped artifact tree on any runtime
that can read and write markdown. The runtime executes the plan; HELIX
just keeps the documents honest.

When something requires human judgment the system cannot make for itself
— authority missing, ambiguity beyond automation, a product question
only the team can answer — the alignment plan surfaces it and waits.

## What this shape buys you

- **Coherence at scale.** The artifact graph grows with the project.
  Agents joining (or replacing earlier agents) inherit full context, not
  partial recollection.
- **Durable knowledge.** Documents survive sessions, model upgrades, and
  team turnover. Institutional memory lives in the repository, not in
  someone's head.
- **Runtime portability.** The same methodology + content runs on DDx,
  Databricks Genie, Claude Code, or a plain agent shell. Pick the
  runtime; keep the discipline.
- **Compounding feedback.** Every bead leaves execution evidence. Every
  review leaves findings. Every change updates downstream artifacts. The
  knowledge that produces good work next time is captured by the work
  that happened this time.

## Read more

The load-bearing ideas behind these commitments are documented in
[Principles](/why/principles/). The research basis for the claims above is
collected in [Research Foundations](/research/), including the methodology for
time-boxed investigation, the bibliography HELIX borrows from, and published
research-derived artifacts. The full type catalog is in
[Artifact Types](/artifact-types/); this project's actual instances are in
[Artifacts](/artifacts/). The cross-cutting standards layer is in
[Concerns](/concerns/). When you're ready to build, [Use HELIX](/use/)
walks through installing, defining your project's first artifacts, and
running your first alignment pass.
