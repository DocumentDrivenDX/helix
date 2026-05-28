---
title: Artifact Types
linkTitle: Types
weight: 3
generated: true
---

HELIX defines a catalog of **artifact types** — categories of governing document, each with a template, an authoring prompt, metadata, and quality criteria. Every project applying HELIX produces concrete artifacts that instantiate these types. Artifact types are reusable methodology content; they are not tied to DDx or any other runtime.

There are two related public landing paths:

- [/artifact-types/](/artifact-types/) is the reusable catalog: document shapes, prompts, and quality rules.
- [/artifacts/](/artifacts/) is the worked example: HELIX's own governing artifacts, authored from the catalog under `docs/helix/`.

The [HELIX skill](/skills/) uses this catalog and the authority order to find drift between concrete artifacts and propose a plan for restoring alignment.

Browse by activity. Each activity lists the core artifacts first, then the supporting artifacts teams use when they need more detail, risk control, or operational depth.

{{< cards >}}
  {{< card link="discover" title="Discover" subtitle="Validate that an opportunity is worth pursuing before committing to a development cycle." >}}
  {{< card link="frame" title="Frame" subtitle="Define what the system should do, for whom, and how success will be measured." >}}
  {{< card link="design" title="Design" subtitle="Decide how to build it. Capture trade-offs, contracts, and architecture decisions." >}}
  {{< card link="test" title="Test" subtitle="Define how we know it works. Plans, suites, and procedures that bind specs to implementation." >}}
  {{< card link="build" title="Build" subtitle="Implement against the specs and tests. Capture the implementation plan that scopes the work." >}}
  {{< card link="deploy" title="Deploy" subtitle="Ship to users with appropriate operational support, monitoring, and rollback plans." >}}
  {{< card link="iterate" title="Iterate" subtitle="Measure, align, and improve. Close the feedback loop back into the planning strand." >}}
{{< /cards >}}
