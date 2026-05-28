---
title: Use HELIX
weight: 4
---

The how-to layer. Once you understand [why HELIX is shaped the way it
is](/why/), this section explains how to use it in practice: adopt the
artifact templates, invoke the alignment/planning skill through your agent
runtime, and choose an execution integration when you need one.

## The public HELIX surfaces

HELIX has three public surfaces:

- **Artifact types** define the reusable catalog: templates, prompts,
  metadata, and quality criteria.
- **Project artifacts** are concrete documents authored from those types. The
  HELIX repo publishes its own artifacts as a worked example.
- **Skills** give an agent the method for aligning those artifacts and planning
  safe updates.

Runtime integrations sit around those surfaces. DDx is the reference runtime,
not the product spine.

## Start here

{{< cards >}}
  {{< card link="getting-started" title="Getting Started" subtitle="Start from the artifact catalog and invoke the HELIX alignment/planning skill through your runtime." icon="play" >}}
  {{< card link="/skills" title="Skills" subtitle="Use the portable alignment-and-planning skill, and understand which wrappers are runtime-specific legacy." icon="sparkles" >}}
  {{< card link="/artifact-types" title="Artifact Types" subtitle="Browse the reusable catalog of HELIX document shapes, templates, prompts, and quality criteria." icon="collection" >}}
  {{< card link="/artifacts" title="Worked Artifacts" subtitle="Inspect HELIX's own governing artifacts as a self-applied example of the methodology." icon="document-text" >}}
  {{< card link="ddx-runtime" title="Using HELIX with DDx" subtitle="Use DDx as the reference runtime integration when you want a tracker, agent harness, and evidence loop." icon="terminal" >}}
  {{< card link="manual-recipe" title="Manual HELIX Recipe" subtitle="Create the first artifact stack, run alignment, and hand work to implementers without a runtime." icon="pencil" >}}
  {{< card link="claude-code-recipe" title="Claude Code Recipe" subtitle="Use HELIX in Claude Code by prompting artifact edits, alignment, and implementation handoff directly." icon="code" >}}
  {{< card link="codex-recipe" title="Codex Recipe" subtitle="Use HELIX in Codex with scoped file edits, explicit authority, and runtime-neutral handoff prompts." icon="chip" >}}
  {{< card link="databricks-recipe" title="Databricks Recipe" subtitle="Use HELIX with Databricks Genie or agent workflows by treating HELIX artifacts as governed context." icon="database" >}}
  {{< card link="/platforms" title="Platforms" subtitle="Compare ways to use HELIX with DDx, Claude, Codex, Databricks, or a manual agent workflow." icon="server" >}}
{{< /cards >}}

## How HELIX fits your runtime

HELIX supplies the method and artifact discipline. Your runtime supplies the
mechanics: agent dispatch, work tracking, review, and evidence capture.

- **Manual.** You ask an agent to create or review specific HELIX artifacts,
  then decide what to accept.
- **Runtime-assisted.** Your agent invokes the HELIX alignment/planning skill
  before creating work items or changing code.
- **Integrated.** A runtime such as DDx wraps HELIX artifacts with a tracker,
  queue, execution harness, and evidence model.

The same repository can mix these patterns. A critical product change may stay
manual; routine implementation can run through a runtime-managed queue.

## Non-DDx recipes

You do not need DDx to apply HELIX. The runtime-neutral contract is:

- Humans own the artifact stack and approve changes to it.
- Agents read the artifact stack before proposing or implementing work.
- The runtime, if any, supplies context loading, scoped execution, review, and
  evidence capture.
- Implementation handoff names the governing artifacts, the allowed write
  scope, the acceptance criteria, and the expected evidence.

Use these recipes when adopting HELIX in another toolchain:

{{< cards >}}
  {{< card link="manual-recipe" title="Manual" subtitle="Small teams or early discovery where humans edit artifacts and prompt agents directly." icon="pencil" >}}
  {{< card link="claude-code-recipe" title="Claude Code" subtitle="Claude Code sessions that need HELIX artifact discipline without DDx queue control." icon="code" >}}
  {{< card link="codex-recipe" title="Codex" subtitle="Codex sessions that need bounded edits, explicit authority order, and handoff-ready work." icon="chip" >}}
  {{< card link="databricks-recipe" title="Databricks" subtitle="Databricks Genie or agent workflows that use HELIX artifacts as governed project context." icon="database" >}}
{{< /cards >}}

## Core methodology versus runtime behavior

The core HELIX methodology is runtime-neutral:

- Artifact-type catalog
- Authority order
- Seven activity loop
- Alignment-and-planning skill

Runtime behavior is platform-specific:

- Tracker and queue semantics
- Agent execution loops
- Claim, review, commit, and release workflows
- Evidence capture and reporting

Legacy `helix-*` wrappers in this repository belong to the transitional runtime
surface. They may remain useful while DDx and other integrations mature, but
they are not the public product contract.

## Cross-cutting concerns

When you frame a project, you select active [cross-cutting
concerns](/concerns/) — tech stack, accessibility, observability,
security posture. From that point forward, downstream artifacts and work items
inherit those concerns. Agents make consistent choices because the artifact
stack tells them what the project values before they start.

{{< cards >}}
  {{< card link="workflow/concerns" title="Cross-Cutting Concerns" subtitle="How concerns are declared, selected, propagated into beads, and used by agents during execution." icon="shield-check" >}}
{{< /cards >}}
