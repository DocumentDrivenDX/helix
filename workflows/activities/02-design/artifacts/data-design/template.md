---
ddx:
  id: data-design
  authoring:
    home: repo
---

# Data Design

Entity-level data model for the feature or subsystem: logical entities,
stores, relationships, access patterns, integrity/security constraints, and
migration strategy. Platform-level concerns (medallion topology, processing
framework, governance model, pipeline-level quality contracts) live in
[[data-architecture]].

## Data Summary

- Scope: [What feature, subsystem, or workflow this data design supports]
- Storage systems: [Database, queue, cache, object store — names only; the
  platform-level rationale lives in [[data-architecture]]]
- Main concerns: [Consistency, scale, retention, privacy, migration]

## Entities and Stores

| Entity or Store | Purpose | Key Fields | Volume / Growth | Notes |
|-----------------|---------|------------|-----------------|-------|
| [Name] | [What it represents] | [Important fields] | [Expected scale] | [Business rules or constraints] |

## Relationships

| From | To | Type | Cardinality | On Delete |
|------|----|------|-------------|-----------|
| [Entity1] | [Entity2] | [1:N, N:M] | [Required/Optional] | [CASCADE/RESTRICT/SET NULL] |

## Access Patterns and Constraints

| Access Pattern | Frequency | Performance Need | Supporting Index or Cache |
|----------------|-----------|------------------|---------------------------|
| [Read or write path] | [Rate] | [Latency or throughput target] | [Index, partition, cache] |

## Validation and Security

Field-level rules. Pipeline-level masking and access policy live in
[[data-architecture]] (Governance and Access Control).

| Field or Data Type | Rules / Classification | Protection or Error Handling |
|--------------------|------------------------|------------------------------|
| [Field] | [Constraints or classification] | [Masking, encryption, validation, retention] |

## Migration Strategy

- Tooling: [Migration framework]
- Approach: [Schema rollout and rollback strategy]
- Backfill or cleanup: [If needed]

## Cross-References

- [[data-architecture]] — platform/pipeline shape, medallion topology,
  processing framework, governance model, and pipeline-level quality
  contracts.
- [[data-quality-expectations]] — executable field-level and freshness
  contracts that this model must satisfy.

## Schema Basis (when applicable)

Follow `workflows/references/umf-schemas.md`. Name the inspected UMF core,
extensions/domain packs and versions; what is reused/composed/extended; or the
specific gap justifying an alternative. Reference the authoritative Contract
and source through `ddx.schemas`; explain unsupported semantics and tests.
Omit this section for work with no schema, structured interface, or domain model.

## Machine-readable relational tables (when applicable)

For relational designs, keep one upstream UMF TableSpec YAML per table under
`docs/helix/02-design/umf/tables/` (or name the project's chosen specs directory).
Use the upstream UMF project's TableSpec 1.0 format: `version: "1.0"`,
`table_name`, `columns`, primary/unique keys, and
`relationships.foreign_keys` (`column`, `references_table`, `references_column`).
The YAML owns exact columns, types, keys and foreign keys; this document owns
rationale, access patterns, transactions and migration decisions. Summaries link
the specs; change them in the same revision rather than maintaining a second
independent schema. Shared interfaces still follow the Contract ownership rule.

Declare local sources through `ddx.schemas` with `schemaFormat: tablespec`
(see `workflows/references/umf-schemas.md`), or select documentor's
`umf-tablespec` trait for automatic table discovery. Install the pinned
`@documentdrivendx/umf-schema-browser` version required by documentor in the
site's locked dependencies, then run `documentor build --root .` to generate
the table reference and publish the schema browser. The upstream UMF browser
is the tool named here; tablespec guidebook remains for tablespec pipelines.
Validate the YAML with the upstream validator supported by the project's pinned
UMF version, and check FK targets plus prose/spec agreement. Rendering a browser
is publication evidence, not schema validity or a database migration. Record the
exact validation and browser build commands and observed results in the design.
Skip this section with a reason when no relational model is in scope; a planned
relational application needs specs even before application code exists.
