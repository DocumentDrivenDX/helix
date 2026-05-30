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
or ADR. It is the bridge between PRD (kind: data) (requirements) and implementation: "given
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

**Non-Databricks platforms:** see
`docs/resources/databricks-platform-substitution.md` for the equivalent
terms on Snowflake, BigQuery, and on-prem stacks. The artifact shape and
prompt stay the same.

## Completion Criteria

- Medallion layer diagram or description is clear (what lands where, why).
- Each layer's transformation responsibilities are explicit.
- Ingestion patterns name actual technologies and explain why each is used.
- Quality gates are named (where validation happens, what contracts are
  enforced).
- Performance/cost tradeoffs are visible (partitioning, clustering, retention,
  refresh strategy).
- Deployment topology is concrete (number of clusters, auto-scaling, failover).
- Major decisions link to PRD (kind: data) requirements or include inline rationale.
