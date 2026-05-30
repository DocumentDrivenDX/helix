---
title: "Data Design"
linkTitle: "Data Design"
slug: data-design
activity: "Design"
artifactRole: "supporting"
weight: 15
generated: true
---

## Purpose

Design-level data architecture covering entities, stores, access patterns,
constraints, and migration strategy.

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: example.data-design.depositmatch
  depends_on:
    - example.solution-design.depositmatch.csv-import
    - example.security-requirements.depositmatch
    - example.threat-model.depositmatch
  review:
    self_hash: dc25da87b6288f686dfb11eae276dd334aca0dce4d6cd562c8da70b7f169a7c5
    deps:
      example.security-requirements.depositmatch: 2a1f7efe6e55c1edaa67b76e5a11a49be55e4420d9adc456be5482d417312a43
      example.solution-design.depositmatch.csv-import: 4d5a2bf5c6b05affdcf7ecc35497aae9f7bb64007e45b62f2a87b42a6914aa00
      example.threat-model.depositmatch: 28c760cff8d40eab543a794535603b0a70e333e9cd808c45c23b885e621e7602
    reviewed_at: "2026-05-15T04:11:24Z"
---

# Data Design

## Data Summary

- Scope: DepositMatch CSV import, match review, exception ownership, and review
  log export for the CSV-first pilot.
- Storage systems: PostgreSQL for normalized records and audit data; object
  storage for temporary source CSV files.
- Main concerns: firm/client isolation, import validation, audit integrity,
  retention, restricted telemetry, and reversible schema migration.

## Entities and Stores

| Entity or Store | Purpose | Key Fields | Volume / Growth | Notes |
|-----------------|---------|------------|-----------------|-------|
| Firm | Tenant boundary for staff, clients, imports, and records | id, name, status | Low; one per pilot firm | All customer data scopes through firm_id |
| Client | Customer business managed by a firm | id, firm_id, name, status | 5-25 per pilot firm | Required for exception grouping |
| Import Batch | One uploaded CSV set for a client and period | id, firm_id, client_id, type, status, uploaded_by, source_file_ref | Weekly per client | Stores processing state, not raw CSV content |
| Deposit Record | Normalized bank deposit row | id, firm_id, client_id, batch_id, amount, date, payer_ref, normalized_hash | Hundreds per client/week | Restricted financial data |
| Invoice Record | Normalized invoice export row | id, firm_id, client_id, batch_id, invoice_ref, amount_due, due_date, payer_ref | Hundreds per client/week | Restricted business/customer data |
| Match Suggestion | Candidate link between deposit and invoice records | id, firm_id, client_id, deposit_id, invoice_id, confidence, evidence_json, status | Derived per import | Must be reviewable before acceptance |
| Review Decision | Reviewer action on a suggestion or exception | id, firm_id, client_id, actor_id, action, source_refs, created_at | Grows with review activity | Audit record; immutable after write |
| Exception Item | Unresolved deposit needing ownership and next action | id, firm_id, client_id, deposit_id, owner_id, next_action, status, due_at | Small subset of deposits | Drives follow-up queue |
| Source File Object | Temporary original CSV file | object_key, firm_id, client_id, batch_id, retention_until | Short-lived | Delete according to retention policy |

## Relationships

| From | To | Type | Cardinality | On Delete |
|------|----|------|-------------|-----------|
| Firm | Client | 1:N | Required | RESTRICT |
| Client | Import Batch | 1:N | Required | RESTRICT |
| Import Batch | Deposit Record | 1:N | Optional by batch type | RESTRICT |
| Import Batch | Invoice Record | 1:N | Optional by batch type | RESTRICT |
| Deposit Record | Match Suggestion | 1:N | Optional | RESTRICT |
| Invoice Record | Match Suggestion | 1:N | Optional | RESTRICT |
| Match Suggestion | Review Decision | 1:N | Optional | RESTRICT |
| Deposit Record | Exception Item | 1:0..1 | Optional | RESTRICT |

## Access Patterns and Constraints

| Access Pattern | Frequency | Performance Need | Supporting Index or Cache |
|----------------|-----------|------------------|---------------------------|
| List imports by firm/client/status | Daily per reviewer | <500 ms for pilot scale | `(firm_id, client_id, status, created_at)` |
| Load review queue for a client | Weekly per client | <1 s for hundreds of suggestions | `(firm_id, client_id, status, confidence)` |
| Accept or reject a match | Many per review session | Transactional write with audit record | Transaction on suggestion + review_decision |
| List open exceptions by owner/client | Daily | <500 ms | `(firm_id, owner_id, status, due_at)` |
| Export review log by client/date range | Weekly/monthly | Async if large | `(firm_id, client_id, created_at)` on review decisions |
| Delete expired source files | Daily job | Complete within maintenance window | object metadata: retention_until |

## Validation and Security

| Field or Data Type | Rules / Classification | Protection or Error Handling |
|--------------------|------------------------|------------------------------|
| firm_id/client_id | Tenant and client boundary | Required in every restricted table and authorization query |
| source CSV object | Restricted financial data | Encrypt, short retention, delete after retention_until |
| amount/date/payer_ref | Restricted financial/customer data | Validate type and bounds; avoid telemetry/logging raw values |
| evidence_json | Audit-supporting evidence | Store source row references and normalized evidence, not unnecessary raw file content |
| Review Decision | Audit record | Append-only; corrections create new decisions |
| normalized_hash | Deduplication support | Use for duplicate detection; do not expose to users |

## Migration Strategy

- Tooling: Versioned database migrations committed with application code.
- Approach: Use additive migrations for pilot tables before enabling writes.
  Avoid destructive schema changes during pilot. For breaking changes, expand
  schema first, migrate/backfill data, update code, then contract only after
  old readers/writers are gone.
- Backfill or cleanup: Import batches may require cleanup jobs for expired
  source files and failed partial imports. Backfills must be idempotent and
  firm-scoped.
- Rollback: Application rollback must remain compatible with additive schema
  changes. Destructive changes require a separate rollback plan and explicit
  approval.
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Design</strong></a> — Decide how to build it. Capture trade-offs, contracts, and architecture decisions.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/02-design/data-design.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="../../../artifact-types/design/technical-design/">Technical Design</a><br><a href="../../../artifact-types/test/test-plan/">Test Plan</a></td></tr>
<tr><th>HELIX documents</th><td><a href="https://github.com/DocumentDrivenDX/helix/blob/main/docs/helix/02-design/data-design.md"><code>docs/helix/02-design/data-design.md</code></a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Data Design Generation Prompt&#10;Document the data model and access patterns needed to support the design.&#10;&#10;## Reference Anchors&#10;&#10;Use this local resource summary as grounding:&#10;&#10;- `docs/resources/fowler-evolutionary-database-design.md` grounds schema&#10;  evolution, versioned migrations, data movement, and rollback expectations.&#10;&#10;## Focus&#10;- Name the main entities, stores, and key fields.&#10;- Make relationships, lifecycle, and integrity constraints explicit.&#10;- Capture the main access patterns and their performance or consistency needs.&#10;- Note privacy, classification, retention, and protection consequences where they&#10;  materially shape the design.&#10;- Define migration and rollback expectations for schema or storage changes.&#10;- Avoid drifting into implementation-specific query or ORM code.&#10;&#10;## Role Boundary&#10;&#10;Data Design is not the full architecture or implementation plan. It explains&#10;the data model, storage responsibilities, access patterns, integrity/security&#10;constraints, and migration consequences that technical designs must honor.&#10;&#10;## Completion Criteria&#10;- The model is understandable to another engineer without reading code.&#10;- Key data decisions and constraints are explicit.&#10;- Access patterns and migration strategy are concrete enough to guide&#10;  implementation and tests.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: data-design&#10;---&#10;&#10;# Data Design&#10;&#10;Entity-level data model for the feature or subsystem: logical entities,&#10;stores, relationships, access patterns, integrity/security constraints, and&#10;migration strategy. Platform-level concerns (medallion topology, processing&#10;framework, governance model, pipeline-level quality contracts) live in&#10;[[data-architecture]].&#10;&#10;## Data Summary&#10;&#10;- Scope: [What feature, subsystem, or workflow this data design supports]&#10;- Storage systems: [Database, queue, cache, object store — names only; the&#10;  platform-level rationale lives in [[data-architecture]]]&#10;- Main concerns: [Consistency, scale, retention, privacy, migration]&#10;&#10;## Entities and Stores&#10;&#10;| Entity or Store | Purpose | Key Fields | Volume / Growth | Notes |&#10;|-----------------|---------|------------|-----------------|-------|&#10;| [Name] | [What it represents] | [Important fields] | [Expected scale] | [Business rules or constraints] |&#10;&#10;## Relationships&#10;&#10;| From | To | Type | Cardinality | On Delete |&#10;|------|----|------|-------------|-----------|&#10;| [Entity1] | [Entity2] | [1:N, N:M] | [Required/Optional] | [CASCADE/RESTRICT/SET NULL] |&#10;&#10;## Access Patterns and Constraints&#10;&#10;| Access Pattern | Frequency | Performance Need | Supporting Index or Cache |&#10;|----------------|-----------|------------------|---------------------------|&#10;| [Read or write path] | [Rate] | [Latency or throughput target] | [Index, partition, cache] |&#10;&#10;## Validation and Security&#10;&#10;Field-level rules. Pipeline-level masking and access policy live in&#10;[[data-architecture]] (Governance and Access Control).&#10;&#10;| Field or Data Type | Rules / Classification | Protection or Error Handling |&#10;|--------------------|------------------------|------------------------------|&#10;| [Field] | [Constraints or classification] | [Masking, encryption, validation, retention] |&#10;&#10;## Migration Strategy&#10;&#10;- Tooling: [Migration framework]&#10;- Approach: [Schema rollout and rollback strategy]&#10;- Backfill or cleanup: [If needed]&#10;&#10;## Cross-References&#10;&#10;- [[data-architecture]] — platform/pipeline shape, medallion topology,&#10;  processing framework, governance model, and pipeline-level quality&#10;  contracts.&#10;- [[data-quality-expectations]] — executable field-level and freshness&#10;  contracts that this model must satisfy.</code></pre></details></td></tr>
</tbody>
</table>
