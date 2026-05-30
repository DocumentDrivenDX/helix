---
title: Getting Started
weight: 1
prev: /
next: /why
aliases:
  - /docs/getting-started
---

Start with the artifacts. HELIX is a methodology, an artifact-type catalog, and
one alignment/planning skill. It can run in any agent runtime that can read and
write Markdown in your repository.

You do not need a HELIX server, a HELIX tracker, or a HELIX-owned execution
loop to start. Your runtime can supply those. DDx is the reference
runtime integration, not the definition of HELIX.

## The Core Flow

1. **Adopt the artifact shape.** Use the [artifact catalog](/artifact-types/) to
   decide which project artifacts matter for your current activity: vision, PRD,
   feature specs, design decisions, test plans, runbooks, metrics, and reports.
2. **Create or collect your governing documents.** Put the highest-authority
   artifacts first: product vision, PRD, feature specs, and the design artifacts
   that explain current decisions. Existing Markdown docs are valid inputs.
3. **Invoke the HELIX alignment/planning skill.** Ask your agent/runtime to use
   HELIX to reconcile the artifact stack, identify drift, and propose the next
   bounded planning or implementation step.
4. **Let your runtime execute the work.** The runtime can be DDx, Claude Code,
   Codex, Databricks Genie, a CI workflow, or a local agent harness. HELIX
   supplies the method and artifact discipline; the runtime supplies queueing,
   execution, review, and evidence capture.

The simplest prompt is enough:

```text
Use HELIX to review this repository top down. Start from the product vision,
check the downstream artifacts for drift, and propose the next bounded change.
```

For new work, make the planning request explicit:

```text
Use HELIX to frame "Build a REST API for managing bookmarks". Create the
governing artifacts first, then identify the smallest safe implementation step.
```

## Understand the Artifact Hierarchy

HELIX resolves conflicts via the artifact authority hierarchy.
Higher-level artifacts govern lower-level artifacts:

```text
Product Vision          "What is this and why?"
  -> PRD                "What must it do?"
     -> Feature Spec    "What exactly does this feature do?"
        -> Design       "How will it work?"
           -> Work Item "What is the next bounded change?"
```

If a feature spec contradicts the PRD, the PRD wins. If a design contradicts a
feature spec, the feature spec wins. The alignment skill exists to find those
conflicts before implementation spreads them through the codebase.

## What Your Runtime Must Provide

HELIX is intentionally small. A compatible runtime only needs to provide a few
capabilities:

- Read and write Markdown artifacts in the repository.
- Preserve links between requirements, designs, work items, and evidence.
- Run an agent against a bounded scope.
- Record what changed and what remains unresolved.

Everything else is integration detail. Some teams use a tracker, some use pull
requests, some use notebooks or workspace tasks. HELIX should make those systems
more coherent without becoming one of them.

## Using DDx

DDx is the reference runtime integration for HELIX. It provides a document
library, a dependency-aware tracker, an agent harness, and execution evidence.
Use DDx when you want a ready-made queue and review loop around HELIX artifacts.

```bash
curl -fsSL https://raw.githubusercontent.com/DocumentDrivenDX/ddx/main/install.sh | bash
ddx install helix
```

After that, DDx-owned commands such as `ddx bead` and `ddx work` can drive
HELIX-shaped work.

See [Using HELIX with DDx](../ddx-runtime/) for the DDx-specific path.

## Explore the Catalog and Examples

- Browse the [artifact-type catalog](/artifact-types/) for templates,
  generation prompts, and expected relationships.
- Review the projected [HELIX self-artifacts](/artifacts/) to see HELIX applied
  to itself.
- Read [Why HELIX](/why/) for the principles behind the methodology layer.
- Continue to [The Workflow](../workflow/) for the lifecycle activities and where
  alignment fits.
