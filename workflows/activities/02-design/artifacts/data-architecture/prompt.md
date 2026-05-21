# Data Architecture Generation Prompt

Document the data pipeline architecture that the team needs to build, review,
operate, and evolve the data product.

## Purpose

Data Architecture is the **highest-authority structural artifact for data pipeline
design** in the Design activity. Its unique job is to describe the durable pipeline
shape: ingestion patterns, medallion layer topology, streaming vs. batch semantics,
transformation patterns, governance boundaries, quality gates, and critical
performance or cost tradeoffs.

Data Architecture is not a data model (captured in Data Design), implementation plan,
or ADR. It is the bridge between Data PRD (requirements) and implementation: "given
these requirements, here is how the pipeline is structured."

## Reference Anchors

Use these local resource summaries as grounding:

- `docs/resources/databricks-lakehouse-medallion-architecture.md` grounds
  medallion topology (Bronze/Silver/Gold layer responsibilities, transformations,
  and quality gates).
- `docs/resources/databricks-auto-loader.md` grounds cloud-native ingestion
  patterns for incremental, scalable, schema-aware source connectors.
- `docs/resources/databricks-streaming-tables.md` grounds declarative streaming
  and materialized views for real-time transformations and quality enforcement.
- `docs/resources/databricks-sdp.md` grounds SDP lineage, governance, and
  quality-first design through `EXPECT ... ON VIOLATION ...` clauses and
  contract-driven pipeline composition.

## Focus

- Sketch the medallion layer flow: what lands in Bronze, what transformations
  happen in Silver, what business tables live in Gold.
- Name ingestion patterns (Auto Loader, Streaming Tables, batched SQL, CDC) and
  why each is used for its source.
- Document transformation semantics: idempotence, exactly-once vs. at-least-once,
  stateful operations, and how schema evolution is handled.
- Specify governance and quality checkpoints: where data is validated, which
  layers enforce which contracts, and how SLA compliance is monitored.
- Call out critical performance or cost tradeoffs: partitioning strategy,
  clustering, retention policy, incremental refresh vs. full rebuild.

## Role Boundary

Data Architecture describes pipeline topology and data flow, not the detailed
data model (Data Design), not implementation sequences (Implementation Plan),
and not individual quality checks (Data Quality Expectations).

**Databricks Platform Substitution:** If you are adopting this on another data
platform, substitute as follows:

| Databricks Concept | Snowflake Equivalent | BigQuery Equivalent | On-Prem / Other |
|---|---|---|---|
| Medallion layers (Bronze/Silver/Gold) | Same pattern applies universally | Same pattern applies universally | Same pattern applies universally |
| Auto Loader | Snowpipe or native connectors | Dataflow, BigQuery Connector Hub | Apache NiFi, Kafka connectors |
| Streaming Tables with `EXPECT` clauses | Stream-triggered materialized views + native checks | Dataflow with Beam assertions | Apache Flink with custom state management |
| Databricks Jobs for orchestration | Snowflake Tasks | Cloud Composer (Airflow) or Cloud Workflows | Apache Airflow, Dagster, dbt Cloud |
| SDP `EXPECT ... ON VIOLATION ...` | Data Quality checks + Task error handling | BigQuery Data Quality API + Cloud Workflows | dbt tests, Great Expectations, custom assertions |
| Delta Lake format | Iceberg or proprietary formats | Native BigQuery tables | Apache Parquet, Iceberg, Hudi |

## Completion Criteria

- Medallion layer diagram or description is clear (what lands where, why).
- Each layer's transformation responsibilities are explicit.
- Ingestion patterns name actual technologies and explain why each is used.
- Quality gates are named (where validation happens, what contracts are
  enforced).
- Performance/cost tradeoffs are visible (partitioning, clustering, retention,
  refresh strategy).
- Deployment topology is concrete (number of clusters, auto-scaling, failover).
- Major decisions link to Data PRD requirements or include inline rationale.
