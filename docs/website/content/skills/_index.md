---
title: Skills
weight: 4
---

The HELIX skill is the agent instruction that reads project documents, finds
missing or stale context, and proposes the next document update. This page
assumes you know what an AI coding tool is; it explains what the HELIX skill
does before that tool edits files. For the method behind the skill, see
[the thesis](/why/the-thesis/); for invocation reference, see
[/reference/skills/](/reference/skills/).

## The core skill

{{< cards >}}
  {{< card link="#the-helix-skill" title="The HELIX Skill" subtitle="Read project documents, find gaps or drift, and propose the next document update." icon="sparkles" >}}
{{< /cards >}}

### The HELIX Skill

The core HELIX skill is `helix`. It reads an artifact set, meaning the HELIX
documents for a project or scope, compares those documents through the authority
hierarchy, and returns a plan for restoring coherence. It is not an execution
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
  {{< card link="../artifact-types" title="Artifact-Type Catalog" subtitle="Reusable HELIX document patterns: templates, prompts, metadata, and quality criteria." icon="collection" >}}
  {{< card link="../artifacts" title="HELIX Example Docs" subtitle="Generated pages from this repository's own HELIX documents under docs/helix/." icon="document-text" >}}
  {{< card link="../why/principles/#3-the-artifact-authority-hierarchy-governs-reconciliation" title="Authority Hierarchy" subtitle="The rule that higher-level intent governs lower-level designs, tests, and implementation plans." icon="scale" >}}
{{< /cards >}}

Artifact types define reusable HELIX document patterns. Concrete artifacts are
the documents inside a project. HELIX's own documents are public so maintainers
and users can inspect how HELIX applies the method to itself.

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

HELIX ships exactly one skill: `skills/helix/SKILL.md`.
Operators invoke modes by intent (e.g., "use HELIX to frame this") or with
the slash form `/helix <mode>`. Earlier shapes of the project shipped
multiple `helix-*` skills; the umbrella router now subsumes those.

The durable public concepts are:

- Artifact-type catalog
- Concrete governing artifacts
- Authority-hierarchy reconciliation
- One HELIX skill
- Runtime integrations that execute or package the method
