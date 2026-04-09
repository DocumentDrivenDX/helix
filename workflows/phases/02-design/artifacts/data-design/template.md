# Data Design

## Data Summary

- Scope: [What feature, subsystem, or workflow this data design supports]
- Storage systems: [Database, queue, cache, object store]
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

| Field or Data Type | Rules / Classification | Protection or Error Handling |
|--------------------|------------------------|------------------------------|
| [Field] | [Constraints or classification] | [Masking, encryption, validation, retention] |

## Migration Strategy

- Tooling: [Migration framework]
- Approach: [Schema rollout and rollback strategy]
- Backfill or cleanup: [If needed]
