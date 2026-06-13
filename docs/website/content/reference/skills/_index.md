---
title: Skills
weight: 4
prev: /reference
next: /reference/glossary
aliases:
  - /docs/skills
---

Technical reference for invoking the `helix` skill. For orientation and the
artifact-coverage list, see [/skills/](/skills/).

## Core skill contract

### Purpose

The `helix` skill reconciles a project's governing artifacts. It starts from an
explicit scope or operator question, reads the relevant Markdown artifact set,
compares artifacts via the artifact authority hierarchy, chooses a workflow
mode, and returns an actionable plan for restoring coherence.

Use it to answer questions such as:

- Which upstream artifact authorizes or blocks a proposed change?
- Which PRDs, feature specs, designs, tests, or deployment notes are stale?
- Which contradictions need a human decision before implementation?
<!-- vale Helix.PassiveVoice = NO -->
- Which artifacts should be created, amended, or retired next?
<!-- vale Helix.PassiveVoice = YES -->
- Which work items are safe for a runtime to execute after planning completes?

### Inputs

The skill expects access to:

- A scope, question, repository path, artifact path, or work-item reference.
- The HELIX artifact-type catalog from `workflows/activities/*/artifacts/`.
- The project's concrete governing artifacts, commonly under `docs/helix/`.
- Any project tracker metadata that links work items to specs, parents, or
  runtime work context, when a runtime has one.
<!-- vale Helix.PassiveVoice = NO -->
- Runtime constraints, such as whether file writes are allowed or whether the
<!-- vale Helix.PassiveVoice = YES -->
  operator only wants a read-only plan.

### Outputs

The skill produces:

- A concise alignment finding for the requested scope.
- The authority chain used to evaluate the scope.
- Drift, gaps, stale artifacts, and contradictions, grouped by impact.
<!-- vale Helix.Hedges = NO -->
- Open questions that require human authority rather than model inference.
<!-- vale Helix.Hedges = YES -->
- A plan for artifact edits, new work items, or runtime execution handoff.
- Optional Markdown edits when the operator explicitly authorizes writes.

### Authority hierarchy

The skill follows the project's authority hierarchy: higher-level intent
governs lower-level documents and implementation plans, and lower-level
disagreement is drift to reconcile.
[Workflow: Authority Hierarchy](/use/workflow/#authority-hierarchy) defines
the canonical eight-level hierarchy. If
the repository defines a more specific hierarchy, the skill should use
that project-local rule and report that it did so.

### Open-question behavior

The skill must not invent product decisions to close gaps. When authority is
missing, ambiguous, or contradictory, it should stop at a planning boundary and
surface the question explicitly.

Good open questions name:

- The conflicting or missing artifacts.
- The decision only a human or upstream artifact can make.
- The downstream work that should wait for the answer.
- The smallest artifact update that would unblock execution.

### Runtime expectations

A runtime embedding the skill needs only a small capability set:

- Read Markdown and repository files.
- Search for artifact references and linked work items.
- Present findings and plans to an operator.
- Write Markdown only after approval or according to the runtime's governance
  rules.
- Hand execution-ready work to the runtime's own queue, tracker, or agent loop.

The runtime remains responsible for claims, locks, background workers, commits,
pull requests, CI, measurement, and deployment. HELIX supplies the planning
contract those actions should respect.

Workflow modes such as `frame`, `review`, `polish`, and `check` are modes of
the `helix` skill. Runtime integrations may expose convenience commands around
those modes, but those wrappers are packaging details. New public documentation
and integrations should lead with `helix`, then describe any runtime-specific
entrypoints as local invocation syntax.

## Packaging shape

Current repository packages still use `skills/<name>/SKILL.md` files with YAML
front matter:

```yaml
---
name: helix
description: 'Route HELIX document and workflow requests to the right mode.'
argument-hint: "[scope]"
---
```

That file format is a packaging mechanism, not the methodology itself. A
Claude Code skill, Codex skill, DDx plugin, Databricks integration, or manual
operator guide should all wrap the same `helix` routing contract.
