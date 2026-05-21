# Data Product Requirements (Data PRD) Generation Prompt

Create a Data PRD that frames the data product problem, scope, quality requirements,
and success criteria clearly enough that downstream data architecture, quality
expectations, and implementation work can trace back to it.

## Purpose

The Data PRD is the **data-product-scope authority for what data to build and why**.
Its unique job is to translate business intent into data-centric requirements:
data sources, consumer personas, quality contracts, technical constraints (catalog,
schema, medallion layer), and measurable success metrics. It sits between the
general Product Vision and Data Architecture. Every data pipeline design choice
and quality expectation should trace back to a Data PRD requirement.

## Reference Anchors

Use these local resource summaries as grounding:

- `docs/resources/databricks-unity-catalog.md` grounds data governance through
  unified catalog hierarchies (metastore → catalog → schema → volume/table).
- `docs/resources/databricks-lakehouse-medallion-architecture.md` grounds
  medallion topology (Bronze/Silver/Gold) and layer responsibilities in a
  Lakehouse.
- `docs/resources/databricks-sdp.md` grounds Databricks Semantic Data Platform
  governance, lineage, and quality contracts through `EXPECT ... ON VIOLATION ...`
  clauses and SDP-aware pipeline patterns.

## Focus

- Name the data sources (internal and external), ingestion cadence, and expected
  volume/velocity.
- Define data consumers and their use cases: who consumes the data, what decisions
  they make, and what quality they depend on.
- List data quality requirements as testable contracts: completeness, accuracy,
  freshness, schema consistency, referential integrity.
- Specify the Databricks technical context: target catalog/schema, medallion
  layer (Bronze/Silver/Gold), pipeline type (Auto Loader, Streaming Tables, SQL
  pipeline), and estimated DBU budget.
- Frame success metrics for the data product itself: SLA compliance (freshness,
  availability), consumer satisfaction, cost per GB, defect escape rate.

## Role Boundary

Data PRD is not a general product PRD, data model, pipeline design, or quality
implementation. It specifies *what* data requirements are, not *how* to implement
them.

**Databricks Platform Substitution:** If you are adopting this on another data
platform, substitute as follows:

| Databricks Concept | Snowflake Equivalent | BigQuery Equivalent | On-Prem / Other |
|---|---|---|---|
| Unity Catalog (UC) hierarchy | Database + Schema + Table | Project + Dataset + Table | Database + Schema |
| Medallion architecture (Bronze/Silver/Gold) | Same pattern applies universally | Same pattern applies universally | Same pattern applies universally |
| Auto Loader, Streaming Tables | Snowpipe, Stream-triggered tasks | Dataflow, BigQuery Streaming Inserts | Apache Spark Structured Streaming, Airflow |
| SDP `EXPECT ... ON VIOLATION ...` | Data Quality checks in Snowflake | BigQuery Data Quality API | dbt tests, Great Expectations assertions |
| DBU budget estimation | Credit consumption | On-demand or flat-rate pricing | Compute resource allocation |

## Completion Criteria

- Data sources table names each external/internal source, ingestion pattern, and
  freshness requirement.
- Data consumers table includes consumer role, use case, and quality SLA.
- Quality requirements are specific constraints (not aspirational); each one is
  testable in Data Quality Expectations.
- Technical context names the target catalog, schema, medallion layer, and
  pipeline type.
- Success metrics have numeric targets and measurement methods (e.g., "SLA
  compliance > 95% measured by on-time delivery vs. promised refresh cadence").
- Requirements trace upward to the Product Vision or general PRD and downward
  to Data Architecture and Data Quality Expectations.
