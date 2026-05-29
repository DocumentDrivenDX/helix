---
title: "Design"
linkTitle: "Design"
weight: 30
generated: true
---

Decide how to build it. Capture trade-offs, contracts, and architecture decisions.

## Core Artifacts

{{< cards >}}
  {{< card link="architecture/" title="Architecture" subtitle="Captures the C4 views the team needs to build and review the system — System Context, Container, Component (where helpful), Deployment, and Data Flow — plus th…" >}}
  {{< card link="adr/" title="Architecture Decision Record" subtitle="An ADR documents a significant architectural decision: the context that drove it, the alternatives considered, the chosen approach, and the consequences. Each…" >}}
  {{< card link="contract/" title="Contract" subtitle="Normative interface and schema contract that another team can implement against directly, including API, CLI, protocol, event, and data contracts. Contracts ow…" >}}
  {{< card link="solution-design/" title="Solution Design" subtitle="Feature-level solution design that explains the chosen approach for a feature or cross-component capability. It maps requirements to a concrete system shape, e…" >}}
  {{< card link="technical-design/" title="Technical Design" subtitle="Story-specific technical design that details HOW to implement a single user story within the context of the broader solution architecture. This enables vertica…" >}}
{{< /cards >}}

## Supporting Artifacts

{{< cards >}}
  {{< card link="data-design/" title="Data Design" subtitle="Design-level data architecture covering entities, stores, access patterns, constraints, and migration strategy." >}}
  {{< card link="proof-of-concept/" title="Proof of Concept" subtitle="Minimal working implementation that validates a risky technical concept end-to-end before production design or build commitment." >}}
  {{< card link="security-architecture/" title="Security Architecture" subtitle="Design-level security architecture that maps trust boundaries, controls, and security decisions to implementation and testing." >}}
  {{< card link="tech-spike/" title="Technical Spike" subtitle="Time-boxed investigation that answers one technical question with evidence before implementation." >}}
  {{< card link="data-architecture/" title="Data Architecture" subtitle="Captures the data pipeline architecture, medallion topology, streaming vs batch semantics, processing frameworks, governance model, and quality contracts. The…" >}}
  {{< card link="design-system/" title="Design System" subtitle="The per-project interface-system instance: the concrete UX/design-system decisions this app commits to. It captures the navigation model and active-state conve…" >}}
{{< /cards >}}
