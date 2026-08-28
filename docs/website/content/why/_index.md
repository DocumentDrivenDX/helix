---
title: Why HELIX
weight: 1
aliases:
  - /docs
  - /docs/background
---

HELIX is a document-driven framework for teams that use AI agents to plan, build, test, deploy, and improve software.

AI agents can produce and modify software quickly, but they still need reliable project context such as which document expresses the current intent, which decisions remain authoritative, which standards apply, and what else must change when a requirement, design, or constraint changes. Without that structure in place, plans can drift from implementation, decisions can get repeated, and agents can act on the nearest prompt without enough context. 

HELIX organizes this context as a connected graph of project artifacts. Each artifact has a clear purpose, defined relationships, and a place in the authority hierarchy. Cross-cutting concerns carry standards such as security, observability, accessibility, and testing across the graph. The HELIX skill reads this structure, identifies inconsistencies, and recommends the next planning action. 

HELIX remains independent of any one agent, command-line interface, or platform. The methodology defines how a project records and connects intent, decisions, constraints, evidence, and operational knowledge. DDx, Databricks Genie, Claude Code, and other runtimes provide the environment in which an agent uses that information. 

Use this section to understand the problem HELIX addresses, the model it proposes, the principles behind it, and the kinds of projects where it helps.

{{< cards >}}
  {{< card link="the-problem" title="The Problem" subtitle="Open the argument for why existing planning styles break down with AI-assisted development." icon="exclamation-circle" >}}
  {{< card link="the-thesis" title="The Thesis" subtitle="Open the HELIX model: seven document activities, an artifact graph, and concerns that carry standards across work." icon="academic-cap" >}}
<!-- vale Helix.PassiveVoice = NO -->
  {{< card link="principles" title="Principles" subtitle="Open the design principles that explain HELIX's artifact hierarchy, skill routing, and runtime boundaries." icon="light-bulb" >}}
<!-- vale Helix.PassiveVoice = YES -->
  {{< card link="who-its-for" title="Who it's for" subtitle="Open the adoption guide for projects HELIX helps, projects it slows down, and costs to expect." icon="user-group" >}}
{{< /cards >}}

## Where to start

Choose the path that matches your immediate goal: 

- **Understand the workflow**: start with [Workflow](/use/workflow/) to see how the double-helix model connects seven activities, how the artifact authority hierarchy works, and how planning stays connected to execution across different runtimes. 
- **See HELIX applied to a real repository**: browse [Artifacts](/artifacts/) to inspect the documents HELIX uses to plan and maintain its own development. 
- **Find the right document pattern**: use [Artifact Types](/artifact-types/) as the canonical catalog of artifact purposes, structures, relationships, prompts, templates, and worked examples. 
- **Understand the HELIX skill**: review the portable agent instruction that reads project documents, selects a workflow mode, detects drift, and proposes the next planning action. 
- **Choose a platform**: compare the platform guides when you are ready to run HELIX through DDx, Databricks Genie, Claude Code, or another runtime. 
- **Adopt HELIX in a project**: follow the adoption guides to introduce an artifact graph, connect it to your runtime's tracker or execution surface, and keep platform-specific machinery in the runtime layer. 
- **Review the research**: read the research pages for the assumptions, evidence, and design trade-offs behind the methodology. 

## What HELIX contains

HELIX combines the following parts:

- **[Seven activities](/reference/glossary/activities/)**: Discover, Frame,
  Design, Test, Build, Deploy, and Iterate. These activities describe how work
  moves from an initial problem to a deployed system and then back into
  learning and revision. They also define the artifacts and gates associated
  with each stage.
- **[Artifact types](/artifact-types/)**: reusable document patterns for vision
  documents, product requirements documents, feature specifications,
  architecture decision records, technical designs, test plans, runbooks, and
  alignment reviews. Each artifact type defines its purpose, expected
  relationships, generation prompt, template, and, where available, a worked
  example.
- **An artifact graph and authority hierarchy**: HELIX connects documents
  instead of treating them as isolated files. The graph records how artifacts
  depend on one another, where a piece of information originates, which
  artifact takes precedence when sources disagree, and which downstream
  artifacts may need review after a change.
- **[Cross-cutting concerns](/concerns/)**: standards and constraints that apply
  across several activities and artifacts. These include technology choices
  such as TypeScript with Bun, Go, and Rust; quality attributes such as
  accessibility, observability, testing, and internationalization; security
  postures; and infrastructure conventions. Each concern defines its
  components, constraints, per-activity practices, and an artifact-impact
  contract that identifies which documents require attention.
- **One portable HELIX skill**: the skill reads the artifact graph, selects a
  workflow mode, reports inconsistencies, and recommends the next planning
  action. Runtime commands and command-line wrappers support this process without defining the methodology.
- **Multiple flow scopes and domain lanes**: one repository can declare several
  governed artifact roots in `.helix.yml`, such as separate scopes for a
  product and its documentation site. Domain lanes such as product, web, data,
  and infrastructure narrow the context used by the `helix` skill within a
  scope. They do not become separate public skills.

## Methodology and runtime

HELIX separates the planning model from the tool that executes it.

The activities, artifact types, relationships, authority rules, concerns, and
skill behavior belong to the methodology. Trackers, commands, command-line
wrappers, and platform integrations belong to the runtime layer.

This separation allows a team to preserve the same project structure when it
changes agents or platforms. It also prevents the behavior of one tool from
becoming the definition of HELIX itself.

Once the rationale is clear, [Use HELIX](/use/) shows you how to install the
framework, define your first artifacts and flow scope, choose a runtime, and
connect the artifact graph to that runtime's tracker or execution surface.
