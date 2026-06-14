---
title: Multiple Flows and Microsites
weight: 2
prev: /use/getting-started
next: /use/ddx-runtime
---

HELIX can govern more than one set of project documents in the same repository.
Use this when one repository contains distinct durable surfaces, such as a
product and the microsite that explains it. After reading this page, you can
decide whether those surfaces need separate flow scopes.

The public surface is still one HELIX skill. A flow scope is one governed
artifact root, such as `docs/helix` for product documents or `docs/website` for
website documents. Multiple flows tell the skill which root owns the current
question. They are not separate domain-specific skills.

## Terms

| Term | Meaning |
| --- | --- |
| Methodology | The HELIX document method: activities, artifact types, authority hierarchy, concerns, and workflow modes. |
| Flow scope | One governed artifact root declared in `.helix.yml`. |
| Domain lane | Product, web, data, infra, or another subject lens that shapes context and stop rules inside the `helix` skill. |
| Workflow mode | A HELIX action such as `frame`, `design`, `polish`, `check`, or `review`. |
| Runtime | The tool that reads files, writes files, queues work, executes agents, records evidence, or runs validation. |

## Product plus microsite

A product flow owns product intent: vision, PRD, feature specs, architecture,
tests, and implementation handoff. A microsite flow owns public information
architecture, page content, demos, screenshots, publishing rules, and content
quality checks.

They should have separate roots because they answer different questions:

- Product flow: "What should the product be?"
- Microsite flow: "How should this site explain and publish the product?"

The microsite can read product artifacts as source material, but product
positioning changes should go back through the product flow before they become
public guidance.

## Marker shape

Declare each scope in `.helix.yml`:

```yaml
helix_version: 2
defaults:
  flow: product
flows:
  - id: product
    kind: helix
    root: docs/helix
    lanes: [product]
  - id: docs-site
    kind: helix
    root: docs/website
    lanes: [web]
    template: microsite-docs
```

The `kind: helix` value says both entries use the same public HELIX skill.
Use `id` to select the scope. Use `lanes` to tell the skill which domain
vocabulary to prefer after it has resolved the owner scope.

When a request could apply to more than one scope, HELIX resolves the owner in
this order:

1. The current working directory is inside one declared `root`.
2. `defaults.flow` names one declared flow.
3. Only one declared flow exists.
4. Otherwise, the skill asks which scope should own the turn.

## Cross-flow handoff

Cross-flow work starts with the owner scope. If the microsite says the product
positioning is unclear, the microsite flow should identify the product artifact
that blocks it and hand that update to the product flow. If the product PRD
changes, the product flow can hand a public-copy update to the microsite flow.

Good handoffs name:

- the owner flow;
- the prerequisite flow, if any;
- the artifact that carries authority;
- the runtime or work item that should execute the change.

## Microsite-docs Template

Use a `microsite-docs` template when a project wants to publish HELIX-governed
Markdown as a static documentation site.

Template parameters:

| Parameter | Purpose |
| --- | --- |
| `source` | Artifact root to publish, such as `docs/helix` or `docs/website`. |
| `destination` | Site route, such as `/examples/helix-docs/` or `/artifacts/`. |
| `nav` | `hidden`, `reference`, or `main`. Default to `hidden` for internal examples. Use `main` only for pages intended as adoption guidance. |
| `audience` | Who the rendered pages serve: adopter, maintainer, contributor, or internal operator. |
| `collection_label` | Visible label such as "HELIX example docs", "Examples", or "Project docs". |
| `include` / `exclude` | Path rules that keep stale, internal, or historical material out of adopter guidance. |
| `frontmatter` | Generated fields for source path, collection label, publication status, and historical warnings. |

HELIX's own `/artifacts/` section is one instance of this template. It publishes
the project's own documents as examples. It is not the main adoption path. Some
pages may describe historical decisions that are useful context, not current
user guidance.
