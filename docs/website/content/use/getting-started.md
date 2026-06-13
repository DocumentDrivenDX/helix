---
title: Getting Started
weight: 1
prev: /
next: /why
aliases:
  - /docs/getting-started
---

Start with documents, not tooling. HELIX gives you reusable document patterns,
such as PRDs, feature specs, test plans, and runbooks, plus one HELIX skill that
helps agents read those documents and propose the next update. Any AI tool that
can read and write Markdown in your repository can use it.

You do not need a HELIX server, a HELIX tracker, or a HELIX-owned execution
loop to start. A runtime, meaning the tool doing the work, can supply those
pieces later. DDx is the reference runtime integration, not the definition of
HELIX.

## The Core Flow

1. **Adopt the document shape.** Use the [artifact-type
   catalog](/artifact-types/) to choose the HELIX document pattern you need:
   vision, PRD, feature spec, design decision, test plan, runbook, metric, or
   report.
2. **Create or collect your governing documents.** Put the highest-authority
   artifacts first: product vision, PRD, feature specs, and the design artifacts
   that explain current decisions. Existing Markdown docs are valid inputs.
3. **Invoke the HELIX skill.** Ask your agent to reconcile the artifact stack,
   meaning the set of HELIX documents for the project, identify drift, choose a
   workflow mode, and propose the next bounded planning or implementation step.
4. **Let your runtime execute the work.** The runtime can be DDx, Claude Code,
   Codex, Databricks Genie, a CI workflow, or a local agent harness. HELIX
   supplies the document method; the runtime supplies queueing, execution,
   review, and evidence capture.

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

HELIX resolves conflicts through the artifact authority hierarchy: higher-level
documents govern lower-level documents.

```text
Product Vision          "What is this and why?"
  -> PRD                "What must it do?"
     -> Feature Spec    "What exactly does this feature do?"
        -> Design       "How will it work?"
           -> Work Item "What is the next bounded change?"
```

If a feature spec contradicts the PRD, the PRD governs. If a design contradicts
a feature spec, the feature spec governs. The HELIX skill exists to find those
conflicts before a runtime spreads them through the codebase.

## What Your Runtime Must Provide

HELIX is intentionally small. A compatible runtime needs only these
capabilities:

- Read and write Markdown artifacts in the repository.
- Preserve links between requirements, designs, work items, and evidence.
- Run an agent against a bounded scope.
- Record what changed and what remains unresolved.

Everything else is integration detail. Some teams use a tracker, some use pull
requests, some use notebooks or workspace tasks. HELIX should make those systems
more coherent without becoming one of them.

## Using DDx

DDx is the reference runtime integration for HELIX. It ships a document library,
a dependency-aware tracker, an agent harness, and execution evidence.
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
- Learn [multiple flows and microsites](../multiple-flows/) when one repository
  has a product scope and a documentation-site scope.
- Review [HELIX's own example docs](/artifacts/) to see how this repository
  applies the method to itself.
- Read [Why HELIX](/why/) for the principles behind the document method.
- Continue to [The Workflow](../workflow/) for the lifecycle activities and where
  alignment fits.
