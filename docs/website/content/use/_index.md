---
title: Use HELIX
weight: 4
---

Use HELIX to write the documents an agent should read before it changes a
project. This section assumes only that you are building with an AI coding tool;
it shows how to start with HELIX document patterns, ask the HELIX skill to
review them, and choose the tool that will do the work.

## The public HELIX surfaces

HELIX has three public surfaces:

- **Artifact types** are reusable HELIX document patterns: PRDs, ADRs, test
  plans, runbooks, templates, prompts, metadata, and quality criteria.
- **Project artifacts** are concrete documents authored from those types.
  This site publishes HELIX's own project documents separately as examples.
- **The HELIX skill** tells an agent how to read those documents, find gaps or
  drift, and propose the next document update.

A runtime is the tool that performs work with those documents, such as Claude
Code, Codex, DDx, or Databricks. DDx is the reference runtime, not the product
spine.

## Start here

{{< cards >}}
  {{< card link="getting-started" title="Getting Started" subtitle="Create the first HELIX documents and ask your agent to review them." icon="play" >}}
  {{< card link="multiple-flows" title="Multiple Flows and Microsites" subtitle="Keep product documents and website documents separate while using one HELIX skill." icon="collection" >}}
  {{< card link="../skills" title="The HELIX Skill" subtitle="See how the skill reads project documents and proposes the next update." icon="sparkles" >}}
  {{< card link="../artifact-types" title="Artifact Types" subtitle="Browse HELIX document patterns: PRDs, ADRs, test plans, runbooks, prompts, and templates." icon="collection" >}}
  {{< card link="../artifacts" title="HELIX Example Docs" subtitle="See the project documents this repository generates from its own HELIX files." icon="document-text" >}}
  {{< card link="ddx-runtime" title="Using HELIX with DDx" subtitle="Use DDx as the reference runtime integration when you want a tracker, agent harness, and evidence loop." icon="terminal" >}}
  {{< card link="manual-recipe" title="Manual HELIX Recipe" subtitle="Create the first artifact stack, run alignment, and hand work to implementers without a runtime." icon="pencil" >}}
  {{< card link="claude-code-recipe" title="Claude Code Recipe" subtitle="Use HELIX in Claude Code by prompting artifact edits, alignment, and implementation handoff directly." icon="code" >}}
  {{< card link="codex-recipe" title="Codex Recipe" subtitle="Use HELIX in Codex with scoped file edits, explicit authority, and handoff prompts that stay portable across tools." icon="chip" >}}
  {{< card link="databricks-recipe" title="Databricks Recipe" subtitle="Use HELIX with Databricks Genie or agent workflows by treating HELIX artifacts as governed context." icon="database" >}}
  {{< card link="../platforms" title="Platforms" subtitle="Compare ways to use HELIX with DDx, Claude, Codex, Databricks, or a manual agent workflow." icon="server" >}}
{{< /cards >}}

## How HELIX fits your runtime

HELIX supplies the document patterns and review rules. Your runtime, meaning the
tool doing the work, supplies agent dispatch, work tracking, review, and
evidence capture.

- **Manual.** You ask an agent to create or review specific HELIX artifacts,
  then decide what to accept.
- **Runtime-assisted.** Your agent invokes the HELIX skill before creating
  work items or changing code.
- **Integrated.** A runtime such as DDx wraps HELIX artifacts with a tracker,
  queue, execution harness, and evidence model.

The same repository can mix these patterns. A critical product change may stay
manual; routine implementation can run through a runtime-managed queue.

## Non-DDx recipes

You do not need DDx to apply HELIX. The portable contract across tools is:

- Humans own the artifact stack and approve changes to it.
- Agents read the artifact stack before proposing or implementing work.
- The runtime, if any, supplies context loading, scoped execution, review, and
  evidence capture.
- Implementation handoff names the governing artifacts, the allowed write
  scope, the acceptance criteria, and the expected evidence.

Use these recipes when adopting HELIX in another toolchain:

{{< cards >}}
  {{< card link="manual-recipe" title="Manual" subtitle="Small teams or early discovery where humans edit artifacts and prompt agents directly." icon="pencil" >}}
  {{< card link="claude-code-recipe" title="Claude Code" subtitle="Claude Code sessions that need HELIX document patterns without DDx queue control." icon="code" >}}
  {{< card link="codex-recipe" title="Codex" subtitle="Codex sessions that need bounded edits, an explicit authority hierarchy, and handoff-ready work." icon="chip" >}}
  {{< card link="databricks-recipe" title="Databricks" subtitle="Databricks Genie or agent workflows that use HELIX artifacts as governed project context." icon="database" >}}
{{< /cards >}}

## Core methodology versus runtime behavior

The core HELIX method is portable across tools:

- Artifact-type catalog
- Authority hierarchy
- Seven activity loop
- One HELIX skill

Runtime behavior is platform-specific:

- Tracker and queue semantics
- Agent execution loops
- Claim, review, commit, and release workflows
- Evidence capture and reporting

Workflow modes such as `frame`, `review`, and `polish` are modes of the one
`helix` skill. Runtime-specific commands may wrap those modes, but wrappers are
packaging details, not public methodology.

## Cross-cutting concerns

When you frame a project, you select active [cross-cutting
concerns](/concerns/): tech stack, accessibility, observability,
security posture. From that point forward, downstream artifacts and work items
inherit those concerns. Agents make consistent choices because the artifact
stack tells them what the project values before they start.

{{< cards >}}
<!-- vale Helix.PassiveVoice = NO -->
  {{< card link="workflow/concerns" title="Cross-Cutting Concerns" subtitle="How concerns are declared, selected, propagated into runtime work, and used by agents during execution." icon="shield-check" >}}
<!-- vale Helix.PassiveVoice = YES -->
{{< /cards >}}
