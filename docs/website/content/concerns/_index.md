---
title: Concerns
weight: 4
generated: true
aliases:
  - /docs/glossary/concerns
  - /reference/glossary/concerns
---

**Cross-cutting concerns** are HELIX's mechanism for declaring shared standards once and propagating them everywhere agents work.

A concern bundles a description, components, constraints, and drift signals with per-activity practices. When an agent claims a bead, HELIX synthesizes a *context digest* that includes the active concerns — so the agent makes consistent technology choices, follows the project's conventions, and respects quality requirements without having to re-derive them from the codebase.

Concerns are how HELIX answers "every project needs this kind of consistency" without forcing any specific tech stack on the framework itself.

## Tech Stack

{{< cards >}}
  {{< card link="auth-local-sessions" title="Local Sessions (auth-provider)" subtitle="api, data" >}}
  {{< card link="go-std" title="Go + Standard Toolchain" subtitle="all" >}}
  {{< card link="python-uv" title="Python + uv" subtitle="all" >}}
  {{< card link="react-nextjs" title="React + Next.js" subtitle="web, ui" >}}
  {{< card link="rust-cargo" title="Rust + Cargo" subtitle="all" >}}
  {{< card link="scala-sbt" title="Scala + sbt" subtitle="all" >}}
  {{< card link="typescript-bun" title="TypeScript + Bun" subtitle="all" >}}
{{< /cards >}}

## Quality Attributes

{{< cards >}}
  {{< card link="a11y-wcag-aa" title="Accessibility (WCAG 2.1 AA)" subtitle="ui, frontend" >}}
  {{< card link="admin-console" title="Admin Console (operator backend)" subtitle="ui, api" >}}
  {{< card link="auth" title="Authentication & Accounts" subtitle="api, data, ui" >}}
  {{< card link="e2e-kind" title="E2E Testing with Kind Clusters" subtitle="api, infra" >}}
  {{< card link="e2e-playwright" title="E2E Visual Testing (Playwright)" subtitle="ui, site" >}}
  {{< card link="i18n-icu" title="Internationalization (ICU MessageFormat)" subtitle="ui, frontend" >}}
  {{< card link="o11y-otel" title="Observability (OpenTelemetry)" subtitle="api, backend, infra" >}}
  {{< card link="sample-data" title="Sample Data" subtitle="data" >}}
  {{< card link="testing" title="Testing" subtitle="all" >}}
  {{< card link="ux-radix" title="UX Interaction Patterns (Radix)" subtitle="ui, frontend" >}}
  {{< card link="verification" title="Verification" subtitle="all" >}}
{{< /cards >}}

## Security & Compliance

{{< cards >}}
  {{< card link="authorization-model" title="Authorization Model" subtitle="api" >}}
  {{< card link="multi-tenancy" title="Multi-Tenancy" subtitle="data, api" >}}
  {{< card link="security-owasp" title="Security (OWASP)" subtitle="all" >}}
{{< /cards >}}

## Infrastructure

{{< cards >}}
  {{< card link="k8s-kind" title="Kubernetes + kind" subtitle="infra" >}}
  {{< card link="twelve-factor" title="Twelve-Factor App" subtitle="infra" >}}
{{< /cards >}}

## Documentation & Demos

{{< cards >}}
  {{< card link="demo-asciinema" title="Demo Reels (Asciinema)" subtitle="all" >}}
  {{< card link="demo-playwright" title="Demo Reels (Playwright)" subtitle="ui, frontend" >}}
  {{< card link="hugo-hextra" title="Microsite (Hugo + Hextra)" subtitle="all" >}}
  {{< card link="product-microsite-ia" title="Product Microsite IA" subtitle="site, docs, frontend" >}}
{{< /cards >}}

## App Runtime

{{< cards >}}
  {{< card link="databricks-apps" title="Databricks Apps (data/AI app runtime)" subtitle="ui, api, infra" >}}
{{< /cards >}}

## Architecture

{{< cards >}}
  {{< card link="api-style" title="API Style" subtitle="api" >}}
  {{< card link="caching-strategy" title="Caching Strategy" subtitle="data, api" >}}
  {{< card link="classic-layered" title="Classic Layered Architecture" subtitle="all" >}}
  {{< card link="clean-architecture" title="Clean Architecture" subtitle="all" >}}
  {{< card link="concurrency-model" title="Concurrency Model" subtitle="backend, api" >}}
  {{< card link="cqrs" title="CQRS (Command Query Responsibility Segregation)" subtitle="data, api" >}}
  {{< card link="deployment-topology" title="Deployment Topology" subtitle="infra, api" >}}
  {{< card link="design-patterns-gof" title="Design Patterns (Gang of Four)" subtitle="api, data" >}}
  {{< card link="domain-driven-design" title="Domain-Driven Design" subtitle="data, api" >}}
  {{< card link="enterprise-application-patterns" title="Enterprise Application Patterns (PoEAA)" subtitle="api, data" >}}
  {{< card link="enterprise-integration-patterns" title="Enterprise Integration Patterns" subtitle="api, infra" >}}
  {{< card link="event-sourcing" title="Event Sourcing" subtitle="data" >}}
  {{< card link="frontend-architecture" title="Frontend Architecture" subtitle="ui, frontend" >}}
  {{< card link="hexagonal-architecture" title="Hexagonal Architecture (Ports & Adapters)" subtitle="all" >}}
  {{< card link="mcp-server" title="MCP Server" subtitle="api" >}}
  {{< card link="onion-architecture" title="Onion Architecture" subtitle="all" >}}
  {{< card link="relational-data-modeling" title="Relational Data Modeling" subtitle="data" >}}
  {{< card link="resilience" title="Resilience" subtitle="api, infra" >}}
{{< /cards >}}

## Data Governance

{{< cards >}}
  {{< card link="unity-catalog" title="Unity Catalog (Databricks data governance)" subtitle="data, api, infra" >}}
{{< /cards >}}

## Data Pipeline

{{< cards >}}
  {{< card link="databricks-declarative-pipelines" title="Databricks Declarative Pipelines (Lakeflow / DLT)" subtitle="data, infra" >}}
{{< /cards >}}

## Revenue Integrity

{{< cards >}}
  {{< card link="usage-metering" title="Usage Metering (usage-based billing)" subtitle="api, backend, data" >}}
{{< /cards >}}
