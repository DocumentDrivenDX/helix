---
title: Why HELIX
weight: 1
aliases:
  - /docs
  - /docs/background
---

The argument behind HELIX. The four pages below make the case for a
methodology layer that holds across runtimes, agents, and model
upgrades.

{{< cards >}}
  {{< card link="the-problem" title="The Problem" subtitle="Why waterfall, agile, and vibe coding each fail in the era of AI-assisted development, and why a compromise of all three doesn't fix the failure." icon="exclamation-circle" >}}
  {{< card link="the-thesis" title="The Thesis" subtitle="HELIX as a runtime-neutral methodology: seven activities, an artifact graph, and concerns that propagate across them." icon="academic-cap" >}}
<!-- vale Helix.PassiveVoice = NO -->
  {{< card link="principles" title="Principles" subtitle="Eight load-bearing ideas behind the framework: the design choices that explain why HELIX is shaped the way it is." icon="light-bulb" >}}
<!-- vale Helix.PassiveVoice = YES -->
  {{< card link="who-its-for" title="Who it's for" subtitle="The kinds of projects HELIX rewards, the kinds it overburdens, and the costs you pay to adopt it." icon="user-group" >}}
{{< /cards >}}

## Primary journeys

<!-- vale Helix.PassiveVoice = NO -->
If you skip the prose and want to orient yourself, the site is organized
<!-- vale Helix.PassiveVoice = YES -->
around the HELIX reader journeys:

- **Learn the workflow**: start with [Workflow](/use/workflow/)
  to understand the double helix, the seven activities, the artifact
  authority hierarchy,
  and how planning and execution stay connected without assuming one runtime.
- **Inspect dogfood artifacts**: browse [Artifacts](/artifacts/) to see
  generated HELIX self-docs as example evidence.
- **Browse artifact types**: use [Artifact Types](/artifact-types/) as the
  canonical catalog for the shape, purpose, prompts, templates, and
  relationships behind each artifact.
- **Discover the `helix` skill**: use the routing skill to reconcile a
  project's artifacts, identify drift, and decide the next safe planning move.
- **Choose a platform**: compare platform guides when you are ready to run
  HELIX through DDx, Databricks Genie, Claude Code, or another runtime.
- **Apply HELIX**: follow the adoption guides to introduce the artifact graph,
  connect it to your runtime's tracker or execution surface, and keep
  runtime-specific machinery in its own layer.
- **Inspect the research**: read the research pages for the assumptions,
  evidence, and design trade-offs behind the methodology.

## What's in the framework

The core framework consists of:

- **[Artifact types](/artifact-types/)** across seven activities: vision,
  PRDs, feature specs, ADRs, technical designs, test plans, runbooks,
  alignment reviews. Each type defines its purpose, relationships,
  generation prompt, template, and, where available, a worked example.
- **[Forty-nine cross-cutting concerns](/concerns/)**: tech stacks
  (TypeScript+Bun, Go, Rust, etc.), quality attributes (accessibility,
  observability, testing, i18n), security postures, infrastructure
  conventions. Each with components, constraints, per-activity
  practices, and an artifact-impact contract that names which artifacts
<!-- vale Helix.PassiveVoice = NO -->
  must change when the concern is selected.
<!-- vale Helix.PassiveVoice = YES -->
- **[Seven activities](/reference/glossary/activities/)**: Discover,
  Frame, Design, Test, Build, Deploy, Iterate, with the artifacts they
  produce and the gates between them.
- **One `helix` routing skill**: the portable skill that reads the artifact
  graph, chooses a workflow mode, reports inconsistencies, and recommends the
  next planning action. Runtime commands and CLI wrappers are compatibility
  surfaces, not the spine of the methodology.
- **Multiple flow scopes**: one repository can declare more than one governed
  artifact root in `.helix.yml`, such as a product scope and a microsite-docs
  scope. Domain lanes such as product, web, data, and infra shape context inside
  the `helix` skill; they are not separate public skills.

Once the *why* lands, [Use HELIX](/use/) shows you how to install the
framework, define your project's first artifacts, choose a platform, and
apply HELIX without confusing the methodology with any one runtime.
