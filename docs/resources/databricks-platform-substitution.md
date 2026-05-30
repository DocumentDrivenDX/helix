# Databricks Platform Substitution Reference

If you are adopting HELIX data artifacts (`data-prd`, `data-architecture`,
`data-quality-expectations`) on a platform other than Databricks, substitute
the platform-specific terms below. The artifact templates and prompts stay
the same; only the named platform features change.

## Catalog / Governance

| Databricks Concept | Snowflake Equivalent | BigQuery Equivalent | On-Prem / Other |
|---|---|---|---|
| Unity Catalog (UC) hierarchy (metastore → catalog → schema → volume/table) | Database + Schema + Table | Project + Dataset + Table | Database + Schema |
| UC fine-grained access (row filters, column masks) | Row-access policies + masking policies | Authorized views + column-level security | Database views, RLS extensions |
| UC lineage | Object dependencies + Account Usage | Data lineage in Dataplex | Manual lineage in dbt/Marquez |

## Ingestion / Streaming

| Databricks Concept | Snowflake Equivalent | BigQuery Equivalent | On-Prem / Other |
|---|---|---|---|
| Auto Loader (incremental cloud-file ingestion) | Snowpipe or native connectors | Dataflow, BigQuery Connector Hub, Streaming Inserts | Apache NiFi, Kafka connectors |
| Streaming Tables (declarative streaming with EXPECT) | Stream-triggered materialized views + native checks | Dataflow with Beam assertions | Apache Flink with custom state management |
| Spark Structured Streaming | Snowflake streams + tasks | Dataflow | Apache Spark / Flink |

## Orchestration / Pipelines

| Databricks Concept | Snowflake Equivalent | BigQuery Equivalent | On-Prem / Other |
|---|---|---|---|
| Databricks Workflows / Jobs | Snowflake Tasks | Cloud Composer (Airflow) or Cloud Workflows | Apache Airflow, Dagster, dbt Cloud |
| Delta Live Tables / SDP pipeline orchestration | Dynamic Tables | Dataform | dbt, Dagster assets |

## Quality / Contracts

| Databricks Concept | Snowflake Equivalent | BigQuery Equivalent | On-Prem / Other |
|---|---|---|---|
| SDP `EXPECT ... ON VIOLATION ...` | Data Quality checks + Task error handling | BigQuery Data Quality API + Cloud Workflows | dbt tests, Great Expectations, custom assertions |
| SDP Genie test generation | dbt auto-generate tests from table samples | BigQuery Data Catalog insights | dbt, custom metadata scanning |
| Lakeview dashboards (quality monitoring) | Snowflake Dashboards | Looker, Data Studio | Grafana, custom dashboards |

## Storage / Formats

| Databricks Concept | Snowflake Equivalent | BigQuery Equivalent | On-Prem / Other |
|---|---|---|---|
| Delta Lake format | Iceberg or proprietary formats | Native BigQuery tables | Apache Parquet, Iceberg, Hudi |
| Medallion layers (Bronze / Silver / Gold) | Same pattern applies universally | Same pattern applies universally | Same pattern applies universally |

## Compute / Cost

| Databricks Concept | Snowflake Equivalent | BigQuery Equivalent | On-Prem / Other |
|---|---|---|---|
| DBU budget estimation | Credit consumption | On-demand or flat-rate pricing | Compute resource allocation |
| All-purpose / Jobs / Serverless SQL compute tiers | Warehouses (XS through 6XL) | On-demand vs reservation slots | Cluster sizing |
