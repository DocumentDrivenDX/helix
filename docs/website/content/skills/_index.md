---
title: Skills
weight: 4
---

HELIX skills are the portable agent-facing surface of the methodology. They
package the artifact catalog, authority order, and alignment workflow so an AI
runtime can inspect a repository's Markdown artifacts and propose the next
safe plan.

The product direction is intentionally small: HELIX is methodology content plus
one alignment-and-planning skill. Runtime mechanics such as queues, trackers,
claims, commits, and execution loops belong to platforms such as DDx, Claude
Code, Codex, or Databricks.

## The core skill

{{< cards >}}
  {{< card link="#alignment-and-planning" title="Alignment and Planning" subtitle="Find drift, gaps, and contradictions across governing artifacts, then propose an authority-ordered update plan." icon="sparkles" >}}
{{< /cards >}}

### Alignment and Planning

The core HELIX skill reads an artifact set, compares artifacts by authority
order, and returns a plan for restoring coherence. It is not an execution
engine. It answers questions such as:

- Which upstream artifact governs this change?
- Which PRDs, feature specs, designs, tests, or deployment artifacts are now
  stale?
- Which new artifacts should be authored before code changes begin?
- Which contradictions should a human resolve before implementation proceeds?

The skill is portable because its minimum runtime contract is simple: read
Markdown, search files, write Markdown when approved, and present a plan for
review.

### Contract at a glance

Inputs:

- A scope, question, artifact path, or work-item reference.
- The HELIX artifact-type catalog and the project's concrete artifacts.
- Linked tracker metadata when the runtime provides it.
- Runtime constraints, including whether the operator allows file writes.

Outputs:

- The authority chain used for the review.
- Drift, gaps, stale artifacts, and contradictions.
- Open questions that require a human or upstream artifact decision.
- A recommended plan for artifact edits, work-item creation, or execution
  handoff.
- Markdown edits only when the operator or runtime governance authorizes them.

Authority order:

1. Product vision and principles.
2. PRDs and requirements.
3. Feature specs and user stories.
4. Designs and implementation plans.
5. Tests, examples, deployment notes, and operational records.
6. Code and generated outputs.

When authority is missing or contradictory, the skill should not invent a
decision. It should name the open question, identify the affected artifacts,
and stop at the planning boundary until the operator resolves it.

Runtime expectation:

The runtime supplies file access, search, optional governed Markdown writes,
and any queue, tracker, commit, CI, or deployment mechanics. HELIX supplies the
alignment and planning contract those runtime actions should follow.

## What the skill operates on

{{< cards >}}
  {{< card link="../artifact-types" title="Artifact-Type Catalog" subtitle="The reusable templates, prompts, metadata, and quality criteria that define HELIX document shapes." icon="collection" >}}
  {{< card link="../artifacts" title="HELIX's Own Artifacts" subtitle="The worked example: HELIX applies its catalog to itself under docs/helix/." icon="document-text" >}}
  {{< card link="../why/principles/#3-authority-order-governs-reconciliation" title="Authority Order" subtitle="The rule that higher-level intent governs lower-level designs, tests, and implementation plans." icon="scale" >}}
{{< /cards >}}

Artifact types define the reusable shapes. Concrete artifacts are the documents
inside a project. HELIX's own artifacts are public so maintainers and adopters
can inspect the methodology being used on itself.

## Runtime packages are not forks

HELIX can be packaged for different runtimes, but the methodology should not
fork by platform. A DDx package, a Claude Code skill, or a Databricks
integration should wrap the same source content and skill contract.

{{< cards >}}
  {{< card link="../platforms" title="Platform Integrations" subtitle="Compare DDx, Claude Code, Codex, Databricks, and manual operation as runtimes around the same HELIX content." icon="server" >}}
{{< /cards >}}

## Legacy wrappers

HELIX ships exactly one skill: the umbrella router at `skills/helix/SKILL.md`.
Operators invoke modes by intent (e.g., "use HELIX to frame this") or with
the slash form `/helix <mode>`. Earlier shapes of the project shipped
multiple `helix-*` skills; those have been collapsed into the single
router.

The durable public concepts are:

- Artifact-type catalog
- Concrete governing artifacts
- Authority-ordered reconciliation
- One alignment-and-planning skill
- Runtime integrations that execute or package the method
