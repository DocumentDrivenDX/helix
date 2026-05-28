---
title: "Architecture"
linkTitle: "Architecture"
slug: architecture
activity: "Design"
artifactRole: "core"
weight: 10
generated: true
---

## Purpose

Architecture is the **highest-authority structural artifact** in the Design
activity. Its unique job is to describe the durable system shape: boundaries,
containers, externally visible integrations, deployment topology, critical data
flows, quality attributes, and structural tradeoffs.

Architecture is not a feature solution design, story technical design, ADR, or
runbook. ADRs record individual decisions. Solution and technical designs apply
the architecture to narrower scopes. Operational artifacts inherit deployment
and quality constraints from architecture.

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: example.architecture.depositmatch
  depends_on:
    - example.product-vision.depositmatch
    - example.prd.depositmatch
    - example.concerns.depositmatch
    - example.feature-specification.depositmatch.csv-import
  review:
    self_hash: 64b7297158175ff16812e401fe093f7624b5ba70b11265a7a4bdf324e50a6bff
    deps:
      example.concerns.depositmatch: 34738dd02d95489bcc3c00b5be15b630ae9fb15ab4f99f45d0ec1ecd1d3f1c6e
      example.feature-specification.depositmatch.csv-import: d85530eb091209cf9989c9cac3bc1f1063358a5b79964ca0e5e7a384fa77c44a
      example.prd.depositmatch: c9c24e1694af4548a6deaad8d92059e365da110148bd9adc44d8640dff9770a4
      example.product-vision.depositmatch: 8abbb2fcb552b536f07829f57d91ef3ae8dbf52a6066955222e83d196b59b5ae
    reviewed_at: "2026-05-15T04:11:24Z"
---

# Architecture

## Scope

This architecture covers DepositMatch v1: CSV import, match suggestion review,
exception handling, audit evidence, and reconciliation exports for small
bookkeeping firms. It is driven by the PRD goals of reducing weekly
reconciliation time, preserving reviewer trust, and keeping unresolved deposits
owned. Bank feeds, accounting platform sync, payroll, inventory, and tax
workflows are outside the v1 architecture boundary.

## Level 1: System Context

| Element | Type | Purpose | Protocol |
|---------|------|---------|----------|
| Maya, Reconciliation Lead | User | Imports exports, reviews suggestions, resolves exceptions | HTTPS browser |
| Andre, Firm Owner | User | Reviews firm-level reconciliation reports | HTTPS browser |
| DepositMatch | System | Reconciliation workspace and evidence store | HTTPS |
| Bank portal exports | External source | Provides deposit CSV files | Manual CSV export/upload |
| Accounting exports | External source | Provides invoice CSV files | Manual CSV export/upload |

```mermaid
graph TB
    Maya[Maya - Reconciliation Lead] -->|HTTPS| DM[DepositMatch]
    Andre[Andre - Firm Owner] -->|HTTPS| DM
    Bank[Bank portal exports] -->|CSV upload| DM
    Accounting[Accounting exports] -->|CSV upload| DM
```

## Level 2: Container Diagram

| Container | Technology | Responsibilities | Communication |
|-----------|------------|------------------|---------------|
| Web App | React 18, TypeScript 5 | Import workflow, mapping review, match review, exception queue, reports | HTTPS JSON to API |
| API Service | Node 20, Fastify 5, TypeScript 5 | Auth boundary, CSV upload orchestration, validation, matching commands, exception commands, exports | HTTPS JSON; SQL to PostgreSQL; S3 SDK |
| Matching Worker | Node 20, TypeScript 5 | Asynchronous match suggestion generation and confidence scoring | PostgreSQL job table; SQL |
| Database | PostgreSQL 16 on Amazon RDS | Clients, imports, source rows, invoices, deposits, matches, exceptions, audit log | TLS SQL |
| Source File Store | Amazon S3 with SSE-KMS | Encrypted uploaded CSV originals for audit and reprocessing | S3 API from API Service |
| Observability | CloudWatch Logs and Metrics | Application logs, import timing, worker failures, backup alarms | AWS agent/API |

```mermaid
graph TB
    Web[React Web App] -->|HTTPS JSON| API[Fastify API Service]
    API -->|TLS SQL| DB[(PostgreSQL 16)]
    API -->|S3 SDK| S3[(S3 Source File Store)]
    Worker[Matching Worker] -->|TLS SQL| DB
    API -->|job rows| DB
    API -->|logs/metrics| CW[CloudWatch]
    Worker -->|logs/metrics| CW
```

## Level 3: Component Diagram

The API Service needs component detail because CSV import, traceability, and
matching are coupled at the boundary.

| Component | Container | Purpose | Notes |
|-----------|-----------|---------|-------|
| Upload Controller | API Service | Receives bank and invoice CSV uploads for one client import session | Rejects non-CSV files before parsing |
| Mapping Service | API Service | Saves and applies per-client column mappings | Never imports rows with unresolved required mappings |
| CSV Validation Service | API Service | Validates amounts, dates, identifiers, duplicates, and required columns | Produces row-level rejection reasons |
| Import Commit Service | API Service | Atomically records accepted source rows and traceability fields | Transaction boundary for import confirmation |
| Evidence Service | API Service | Supplies source-row evidence to match review, exceptions, and exports | Reads normalized fields and source metadata |

```mermaid
graph TB
    Upload[Upload Controller] --> Mapping[Mapping Service]
    Mapping --> Validate[CSV Validation Service]
    Validate --> Commit[Import Commit Service]
    Commit --> Evidence[Evidence Service]
    Commit --> DB[(PostgreSQL)]
    Evidence --> DB
```

## Deployment

| Component | Infrastructure | Instances | Scaling | Backup / Recovery |
|-----------|----------------|-----------|---------|-------------------|
| Web App | S3 static hosting behind CloudFront, us-east-1 | 1 distribution | CDN-managed | Versioned S3 bucket; redeploy from CI |
| API Service | ECS Fargate service behind Application Load Balancer, us-east-1 | 2 tasks minimum | CPU > 60% for 5 minutes or p95 import latency > 3 seconds | Rolling deploy; previous task definition retained |
| Matching Worker | ECS Fargate service, us-east-1 | 1 task minimum | Job backlog > 100 for 5 minutes | Restart failed task; jobs remain in PostgreSQL |
| Database | Amazon RDS PostgreSQL 16, Multi-AZ | 1 primary, 1 standby | Vertical scaling by planned maintenance | PITR enabled; 15-minute RPO; 4-hour RTO |
| Source File Store | S3 bucket with SSE-KMS and versioning | Regional service | S3-managed | Versioning and lifecycle retention |

```mermaid
graph TB
    User[Browser] --> CF[CloudFront]
    CF --> S3Web[S3 Web App]
    User --> ALB[Application Load Balancer]
    ALB --> API1[ECS API Task A]
    ALB --> API2[ECS API Task B]
    Worker[ECS Matching Worker] --> RDS[(RDS PostgreSQL 16 Multi-AZ)]
    API1 --> RDS
    API2 --> RDS
    API1 --> FileS3[(S3 Source Files)]
    API2 --> FileS3
```

## Data Flow

```mermaid
sequenceDiagram
    participant Maya
    participant Web as React Web App
    participant API as Fastify API
    participant S3 as S3 Source File Store
    participant DB as PostgreSQL
    participant Worker as Matching Worker

    Maya->>Web: Upload bank and invoice CSVs
    Web->>API: POST import session files
    API->>S3: Store encrypted originals
    API->>API: Validate mapping and rows
    API->>DB: Commit accepted rows and rejection reasons
    API-->>Web: Import summary
    Maya->>Web: Confirm import summary
    Web->>API: Confirm import
    API->>DB: Mark import confirmed and enqueue matching job
    Worker->>DB: Read accepted rows and create suggestions
    Web->>API: Load match review queue
    API->>DB: Read suggestions with source-row evidence
    API-->>Web: Suggestions and evidence
```

## Quality Attributes

| Attribute | Target | Strategy | Verification |
|-----------|--------|----------|--------------|
| Import performance | Validate and summarize 10,000 total rows in under 5 seconds | Stream parse uploads, validate before commit, keep import commit transactional | Import benchmark in CI with representative CSV fixtures |
| Evidence traceability | 100% of accepted rows used in suggestions expose source file, row number, identifier, amount, and date | Preserve source metadata at import commit and read it through Evidence Service | Story tests for match review evidence and reconciliation export |
| Security | No raw financial row values in analytics or application logs | Structured logging allowlist; encrypted S3 and RDS storage; role-scoped audit access | Log scan tests, infrastructure review, access-control tests |
| Availability | 99.5% monthly availability for pilot firms | Two API tasks, RDS Multi-AZ, static web CDN, worker jobs persisted in DB | CloudWatch uptime and error-rate alarms |
| Disaster Recovery | 15-minute RPO and 4-hour RTO | RDS point-in-time recovery, S3 versioning, retained task definitions | Quarterly restore drill before paid launch |

## Decisions and Tradeoffs

| Decision | Status | Rationale | Follow-up |
|----------|--------|-----------|-----------|
| Use PostgreSQL 16 as the system of record | Accepted inline | Import traceability, matching evidence, exceptions, and audit logs need transactional consistency more than separate specialized stores. | Create ADR before production if another store is introduced. |
| Store uploaded CSV originals in encrypted S3 | Accepted inline | Preserving originals supports audit and reprocessing without bloating PostgreSQL. | Define retention period with firm owners and legal reviewer. |
| Use PostgreSQL-backed worker jobs for v1 | Accepted inline | Pilot volume does not justify a separate queue yet; keeping jobs in PostgreSQL reduces operational surface. | Revisit if matching backlog exceeds 100 jobs for 5 minutes repeatedly. |
| Keep bank feeds and accounting APIs outside v1 | Accepted by PRD non-goals | CSV import is enough to validate reviewer trust and weekly reconciliation speed. | Revisit after pilot CSV success metrics are met. |
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="/reference/glossary/activities/"><strong>Design</strong></a> — Decide how to build it. Capture trade-offs, contracts, and architecture decisions.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/02-design/architecture.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="/artifact-types/design/solution-design/">Solution Design</a><br><a href="/artifact-types/design/technical-design/">Technical Design</a><br><a href="/artifact-types/design/adr/">ADR</a><br><a href="/artifact-types/design/contract/">Contract</a><br><a href="/artifact-types/design/data-design/">Data Design</a><br><a href="/artifact-types/design/security-architecture/">Security Architecture</a></td></tr>
<tr><th>Referenced by</th><td><a href="/artifact-types/design/solution-design/">Solution Design</a><br><a href="/artifact-types/design/technical-design/">Technical Design</a><br><a href="/artifact-types/deploy/deployment-checklist/">Deployment Checklist</a><br><a href="/artifact-types/deploy/runbook/">Runbook</a><br><a href="/artifact-types/deploy/monitoring-setup/">Monitoring Setup</a></td></tr>
<tr><th>HELIX documents</th><td><a href="https://github.com/DocumentDrivenDX/helix/blob/main/docs/helix/02-design/architecture.md"><code>docs/helix/02-design/architecture.md</code></a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Architecture Documentation Generation Prompt

Document the architecture views that the team actually needs to build, review,
operate, and evolve the system.

## Purpose

Architecture is the **highest-authority structural artifact** in the Design
activity. Its unique job is to describe the durable system shape: boundaries,
containers, externally visible integrations, deployment topology, critical data
flows, quality attributes, and structural tradeoffs.

Architecture is not a feature solution design, story technical design, ADR, or
runbook. ADRs record individual decisions. Solution and technical designs apply
the architecture to narrower scopes. Operational artifacts inherit deployment
and quality constraints from architecture.

## Reference Anchors

Use these local resource summaries as grounding:

- `docs/resources/c4-model.md` grounds context, container, component, and
  deployment views as audience-specific structural diagrams.
- `docs/resources/sei-quality-attribute-scenarios.md` grounds measurable
  quality attributes and tradeoff reasoning.
- `docs/resources/microsoft-azure-well-architected-framework.md` grounds
  cross-cutting reliability, security, operations, performance, and cost
  tradeoffs.

## Focus
- Include only the C4 views that add information; omit empty or duplicate views.
- Keep boundaries, deployment shape, data flow, and quality attributes visible.
- Annotate major tradeoffs or constraints directly on the relevant view or summary.
- Remove generic architecture commentary.

## Boundary Test

| If you are writing... | Put it in... |
|---|---|
| Product behavior, priority, or success metrics | PRD or Feature Specification |
| One structural decision with alternatives and consequences | ADR |
| Feature-specific system design | Solution Design |
| Story-level implementation plan | Technical Design |
| Endpoint schemas or message formats | Contract |
| Deployment execution steps, rollback, or release readiness | Deployment Checklist or Runbook |

## Completion Criteria
- The views are understandable at a glance.
- Key boundaries and tradeoffs are visible.
- The document stays implementation-relevant.
- Containers name real technologies, not generic roles.
- Quality attributes have measurable targets and verification methods.
- Deployment names actual infrastructure shape, scaling, and backup approach.
- Major decisions link to ADRs or include an inline decision note.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---
ddx:
  id: architecture
---

# Architecture

## Scope

[What system this architecture covers, what is deliberately outside the
architecture boundary, and which PRD/features/user journeys drive the design.]

## Level 1: System Context

| Element | Type | Purpose | Protocol |
|---------|------|---------|----------|
| [User/System] | User/External | [Interaction] | [HTTP/API/etc] |

```mermaid
graph TB
    %% Add users, system, and external dependencies
```

## Level 2: Container Diagram

| Container | Technology | Responsibilities | Communication |
|-----------|------------|------------------|---------------|
| [Name] | [Stack] | [What it does] | [Protocol/Format] |

```mermaid
graph TB
    %% Add containers: Web, API, DB, Queue, Worker, external systems
```

## Level 3: Component Diagram

Include only when a container needs internal structure to support downstream
design and review. Omit this section when container responsibilities are enough.

| Component | Container | Purpose | Notes |
|-----------|-----------|---------|-------|
| [Name] | [Container] | [Responsibility] | [Key decisions] |

```mermaid
graph TB
    %% Optional: add components inside the container that needs detail
```

## Deployment

| Component | Infrastructure | Instances | Scaling | Backup / Recovery |
|-----------|----------------|-----------|---------|-------------------|
| [Name] | [Cloud/service/runtime] | [Count] | [Trigger or limit] | [Backup/failover path] |

```mermaid
graph TB
    %% Add actual deployment topology
```

## Data Flow

```mermaid
sequenceDiagram
    %% Add sequence for the most important user journey or operational flow
```

## Quality Attributes

| Attribute | Target | Strategy | Verification |
|-----------|--------|----------|--------------|
| Availability | [Target] | [How architecture supports it] | [How checked] |
| Performance | [Target] | [How architecture supports it] | [How checked] |
| Security | [Target] | [Controls/boundaries] | [How checked] |
| Disaster Recovery | RTO: [target] / RPO: [target] | [Backup/failover strategy] | [How checked] |

## Decisions and Tradeoffs

| Decision | Status | Rationale | Follow-up |
|----------|--------|-----------|-----------|
| [ADR-NNN or inline decision] | [Accepted/Proposed] | [Why this shape wins] | [ADR, spike, or none] |</code></pre></details></td></tr>
</tbody>
</table>
