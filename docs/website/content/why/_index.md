---
title: Why HELIX
weight: 1
aliases:
  - /docs
  - /docs/background
---

HELIX is the **methodology layer** for AI-assisted software development.
It defines seven activities, the artifacts that populate each, the
authority order that resolves their conflicts, and the cross-cutting
concerns that travel with the work. It is runtime-neutral: the same
methodology can be applied through DDx today, Databricks Genie, Claude
Code, or another execution surface tomorrow.

The deliverable is intentionally small: a methodology, an artifact catalog,
and one alignment-and-planning skill that helps teams keep the artifact
graph coherent. Runtime execution, issue queues, CLI wrappers, and agent
loops belong to the platform you choose, not to the core HELIX product.

The premise is narrow but load-bearing: AI agents will do real software
work in the coming decade, and the work needs structure that survives
turnover, model upgrades, and the temptation to skip the parts that
don't feel like coding. HELIX is the structure.

This section makes the case in four pages.

{{< cards >}}
  {{< card link="the-problem" title="The Problem" subtitle="Why waterfall, agile, and vibe coding each fail in the era of AI-assisted development — and why a compromise of all three doesn't fix the failure." icon="exclamation-circle" >}}
  {{< card link="the-thesis" title="The Thesis" subtitle="HELIX as a runtime-neutral methodology — seven activities, an artifact graph, and concerns that propagate across them." icon="academic-cap" >}}
  {{< card link="principles" title="Principles" subtitle="Eight load-bearing ideas behind the framework — the design choices that explain why HELIX is shaped the way it is." icon="light-bulb" >}}
  {{< card link="who-its-for" title="Who it's for" subtitle="The kinds of projects HELIX rewards, the kinds it overburdens, and the costs you pay to adopt it." icon="user-group" >}}
{{< /cards >}}

## Primary journeys

If you skip the prose and just want to orient yourself, the site is organized
around the journeys HELIX actually supports:

- **Learn the methodology** — start with [Methodology](/use/workflow/methodology/)
  to understand the double helix, the seven activities, the authority order,
  and how planning and execution stay connected without assuming one runtime.
- **Inspect worked artifacts** — browse [Artifacts](/artifacts/) to see
  concrete HELIX documents applied to this project.
- **Browse artifact types** — use [Artifact Types](/artifact-types/) as the
  canonical catalog for the shape, purpose, prompts, templates, and
  relationships behind each artifact.
- **Discover the alignment skill** — use HELIX's planning and alignment
  skill to reconcile a project's artifacts, identify drift, and decide the
  next safe planning move.
- **Choose a platform** — compare platform guides when you are ready to run
  HELIX through DDx, Databricks Genie, Claude Code, or another runtime.
- **Apply HELIX** — follow the adoption guides to introduce the artifact
  graph, connect it to your existing tracker and execution surface, and keep
  runtime-specific machinery in its own layer.
- **Inspect the research** — read the research pages for the assumptions,
  evidence, and design trade-offs behind the methodology.

## What's actually in the framework

The core framework consists of:

- **[Artifact types](/artifact-types/)** across seven activities — vision,
  PRDs, feature specs, ADRs, technical designs, test plans, runbooks,
  alignment reviews. Each type defines its purpose, relationships,
  generation prompt, template, and, where available, a worked example.
- **[Eighteen cross-cutting concerns](/concerns/)** — tech stacks
  (TypeScript+Bun, Go, Rust, etc.), quality attributes (accessibility,
  observability, testing, i18n), security postures, infrastructure
  conventions. Each with components, constraints, and per-activity
  practices.
- **[Seven activities](/reference/glossary/activities/)** — Discover,
  Frame, Design, Test, Build, Deploy, Iterate — with the artifacts they
  produce and the gates between them.
- **One alignment-and-planning skill** — the portable skill that reads the
  artifact graph, reports inconsistencies, and recommends the next planning
  action. Runtime commands and CLI wrappers are compatibility surfaces, not
  the spine of the methodology.

Once the *why* lands, [Use HELIX](/use/) shows you how to install the
framework, define your project's first artifacts, choose a platform, and
apply HELIX without confusing the methodology with any one runtime.
