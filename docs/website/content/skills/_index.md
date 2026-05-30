---
title: Skills
weight: 4
---

HELIX skills are the portable agent-facing surface of the methodology. They
package the artifact catalog, artifact authority hierarchy, and alignment
workflow so an AI
runtime can inspect a repository's Markdown artifacts and propose the next
safe plan. For the methodology behind the skill, see
[the thesis](/why/the-thesis/); for invocation reference, see
[/reference/skills/](/reference/skills/).

## The core skill

{{< cards >}}
  {{< card link="#alignment-and-planning" title="Alignment and Planning" subtitle="Find drift, gaps, and contradictions across governing artifacts, then propose an authority-ranked update plan." icon="sparkles" >}}
{{< /cards >}}

### Alignment and Planning

The core HELIX skill reads an artifact set, compares artifacts via the
authority hierarchy, and returns a plan for restoring coherence. It is not an execution
engine. It answers questions such as:

- Which upstream artifact governs this change?
- Which PRDs, feature specs, designs, tests, or deployment artifacts are now
  stale?
- Which new artifacts should the team write before code changes begin?
- Which contradictions should a human resolve before implementation proceeds?

The skill is portable because its minimum runtime contract is simple: read
Markdown, search files, write Markdown when approved, and present a plan for
review.

The full inputs, outputs, authority-hierarchy rule, open-question
behavior, and runtime expectations live on the
[invocation reference](/reference/skills/); the
[authority hierarchy](/use/workflow/#authority-hierarchy) itself is
canonical in the workflow page.

## What the skill operates on

{{< cards >}}
  {{< card link="../artifact-types" title="Artifact-Type Catalog" subtitle="The reusable templates, prompts, metadata, and quality criteria that define HELIX document shapes." icon="collection" >}}
  {{< card link="../artifacts" title="HELIX's Own Artifacts" subtitle="The worked example: HELIX applies its catalog to itself under docs/helix/." icon="document-text" >}}
  {{< card link="../why/principles/#3-the-artifact-authority-hierarchy-governs-reconciliation" title="Authority Hierarchy" subtitle="The rule that higher-level intent governs lower-level designs, tests, and implementation plans." icon="scale" >}}
{{< /cards >}}

Artifact types define the reusable shapes. Concrete artifacts are the documents
inside a project. HELIX's own artifacts are public so maintainers and adopters
can inspect how HELIX applies the methodology to itself.

## Runtime packages are not forks

<!-- vale Helix.PassiveVoice = NO -->
HELIX can be packaged for different runtimes, but the methodology should not
<!-- vale Helix.PassiveVoice = YES -->
fork by platform. A DDx package, a Claude Code skill, or a Databricks
integration should wrap the same source content and skill contract.

{{< cards >}}
  {{< card link="../platforms" title="Platform Integrations" subtitle="Compare DDx, Claude Code, Codex, Databricks, and manual operation as runtimes around the same HELIX content." icon="server" >}}
{{< /cards >}}

## Legacy wrappers

HELIX ships exactly one skill: the umbrella router at `skills/helix/SKILL.md`.
Operators invoke modes by intent (e.g., "use HELIX to frame this") or with
the slash form `/helix <mode>`. Earlier shapes of the project shipped
multiple `helix-*` skills; the umbrella router now subsumes those.

The durable public concepts are:

- Artifact-type catalog
- Concrete governing artifacts
- Authority-hierarchy reconciliation
- One alignment-and-planning skill
- Runtime integrations that execute or package the method
