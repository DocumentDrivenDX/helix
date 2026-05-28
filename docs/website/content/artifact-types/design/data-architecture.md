---
title: "Data Architecture"
linkTitle: "Data Architecture"
slug: data-architecture
activity: "Design"
artifactRole: "supporting"
weight: 90
generated: true
---

## Purpose

Data Architecture is the **highest-authority structural artifact for data pipeline
design** in the Design activity. Its unique job is to describe the durable pipeline
shape: ingestion patterns, medallion layer topology, streaming vs. batch semantics,
transformation patterns, governance boundaries, quality gates, and critical
performance or cost tradeoffs.

Data Architecture is not a data model (captured in Data Design), implementation plan,
or ADR. It is the bridge between Data PRD (requirements) and implementation: "given
these requirements, here is how the pipeline is structured."

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: example.data-architecture.customer-360
  depends_on:
    - example.data-prd.customer-360
---

# Data Architecture: Customer-360 Analytics

## Scope

This architecture covers the Customer-360 medallion pipeline: daily batch ingestion
of Salesforce accounts, opportunities, and Stripe customers, subscriptions, invoices,
and charges into a Databricks Lakehouse. It includes Bronze raw-layer storage,
Silver reconciliation and deduplication, and Gold fact/dimension tables for
analytics queries. Historical loads of 12 months are supported; incremental daily
loads begin in week 2. Streaming ingestion, ML training stores, and external data
warehouse federation are outside v1 scope.

## Level 1: System Context

| Element | Type | Purpose | Protocol |
|---------|------|---------|----------|
| Salesforce | External source | Customer accounts, opportunities, ownership | HTTPS REST API; daily full export |
| Stripe | External source | Customers, subscriptions, invoices, charges | HTTPS REST API; daily full export (webhook in v2) |
| Databricks Lakehouse | Data Platform | Medallion storage and compute for ingestion and queries | Databricks SQL; PySpark jobs |
| BI Tool (Tableau/Sigma) | Consumer | Sales and finance dashboards querying Gold tables | Databricks SQL via ODBC |
| Data Engineer | Role | Orchestrates jobs, monitors SLAs, maintains schemas | Databricks workflows, notebooks |

```mermaid
graph TB
    SF[Salesforce<br/>Accounts + Opps] -->|HTTPS API<br/>Daily export| DBX[Databricks Lakehouse<br/>Bronze + Silver + Gold]
    Stripe[Stripe<br/>Customers + Subscriptions<br/>+ Invoices + Charges] -->|HTTPS API<br/>Daily export| DBX
    DBX -->|Databricks SQL| BI[BI Tool<br/>Sales Dashboards]
    DBX -->|Databricks SQL| DE[Data Engineer<br/>Monitoring]
```

## Level 2: Medallion Architecture

### Bronze Layer (Raw)

Immutable copies of source system exports, organized by system and entity.

| Table | Source | Partitioning | Retention | Notes |
|-------|--------|--------------|-----------|-------|
| bronze.salesforce_accounts | Salesforce API | date_loaded | 90 days | Full daily export; preserves all fields |
| bronze.salesforce_opportunities | Salesforce API | date_loaded | 90 days | Full daily export; includes closed_date |
| bronze.stripe_customers | Stripe API | date_loaded | 90 days | Full daily export; includes metadata tags |
| bronze.stripe_subscriptions | Stripe API | date_loaded | 90 days | Full daily export; includes status changes |
| bronze.stripe_invoices | Stripe API | date_loaded | 90 days | Full daily export; raw line items |
| bronze.stripe_charges | Stripe API | date_loaded | 90 days | Full daily export; includes payment outcomes |

**Quality**: No transformation; SLA violations block Silver load until Bronze is complete.

### Silver Layer (Deduplicated & Reconciled)

Cleaned, deduplicated, and reconciled data with lineage and quality flags.

| Table | Source(s) | Partitioning | Retention | Key Transformations |
|-------|-----------|--------------|-----------|---------------------|
| silver.dim_customer | bronze.salesforce_accounts + bronze.stripe_customers | customer_id | 3 years | 1:1 Salesforce-to-Stripe match via email; hash PII; null-check on account names |
| silver.dim_date | N/A (calendar) | date_key | 5 years | Standard calendar table; fiscal month, quarter, year |
| silver.fct_subscription_event | bronze.stripe_subscriptions | subscription_id, event_date | 3 years | Deduplicate on Stripe subscription ID; flag late-arriving rows; join to dim_customer |
| silver.fct_payment_transaction | bronze.stripe_charges + bronze.stripe_invoices | charge_id, payment_date | 3 years | Flatten invoice line items; join charge to invoice and subscription; hash card brand |
| silver.reconciliation_log | N/A | load_date | 90 days | Count of matched/unmatched pairs per load; reconciliation confidence scores |

**Quality**: PII hashing, null validation, late-arriving fact flags, join lineage recorded.

### Gold Layer (Aggregated Facts)

Business-ready tables for analytics and reporting.

| Table | Business Use | Grain | Partitioning | Retention |
|-------|------------------|-------|--------------|-----------|
| gold.fct_monthly_revenue | Sales forecasting, revenue metrics | 1 row per customer per month | customer_id, year_month | 3 years |
| gold.fct_subscription_health | Churn risk scoring, subscription metrics | 1 row per subscription | subscription_id, as_of_date | 3 years |
| gold.dim_customer_account | Account overview, drill-down | 1 row per customer | customer_id | 3 years |

**Computations**:
- `fct_monthly_revenue`: Sums paid invoices grouped by customer and calendar month; includes subscription state
- `fct_subscription_health`: Latest subscription status, months active, failed payment count, aging of unpaid invoices
- `dim_customer_account`: Joins Salesforce account attributes with current Stripe subscription status

## Level 3: Data Flow

```mermaid
sequenceDiagram
    participant SF as Salesforce API
    participant Stripe as Stripe API
    participant DBX as Databricks
    participant Bronze as Bronze Tables
    participant Silver as Silver Tables
    participant Gold as Gold Tables
    participant BI as BI Tool

    SF->>DBX: Daily export (accounts, opps)
    Stripe->>DBX: Daily export (customers, subs, invoices, charges)
    DBX->>Bronze: Land raw data; validate schema and completeness
    Note over DBX: Reconciliation: match Salesforce-Stripe via email
    Bronze->>Silver: Deduplicate, hash PII, join and flag late arrivals
    Note over Silver: Check reconciliation accuracy (98% threshold)
    Silver->>Gold: Aggregate facts and dimensions
    Gold->>BI: SQL query for dashboards
    Note over BI: Sales forecast, churn alerts, AR aging
```

## Level 4: Deployment and Compute

### Orchestration

| Component | Technology | Schedule | Resource | SLA |
|-----------|----------|----------|----------|-----|
| Salesforce Export Job | Databricks Workflow + PySpark | 10pm UTC daily | 2-worker job cluster, 8 DBU | Complete by 2am UTC |
| Stripe Export Job | Databricks Workflow + PySpark | 10pm UTC daily | 2-worker job cluster, 8 DBU | Complete by 2am UTC |
| Reconciliation + Silver Load | Databricks Workflow + SQL | 3am UTC daily (after Bronze) | 2-worker job cluster, 8 DBU | Complete by 5am UTC |
| Gold Aggregation + Refresh | Databricks Workflow + SQL | 5am UTC daily (after Silver) | 2-worker job cluster, 8 DBU | Complete by 7am UTC |

### Compute Sizing

- **Job Cluster**: 2 workers, 8 DBU/hour per cluster
- **Estimated Monthly Cost**: 4 jobs × 8 DBU × 30 days = 960 DBU ≈ $480 USD
- **Query Workload**: +50 DBU/month for analyst ad-hoc queries (estimate)
- **Total Budget**: ≤ $500 USD/month

### Storage

| Layer | Format | Location | Retention Policy |
|-------|--------|----------|------------------|
| Bronze | Delta | s3://main-catalog/customer_360_bronze/ | Delete after 90 days |
| Silver | Delta | s3://main-catalog/customer_360_silver/ | Delete after 3 years (Delta VACUUM) |
| Gold | Delta | s3://main-catalog/customer_360_gold/ | Delete after 3 years (Delta VACUUM) |

## Quality Attributes

| Attribute | Target | Strategy | Verification |
|-----------|--------|----------|--------------|
| Data Freshness | Gold tables available by 7am UTC daily | Orchestrated daily batch completing 5am; monitor job logs for failures | Scheduled report execution; query execution logs |
| Reconciliation Accuracy | ≥ 98% Salesforce-Stripe matched pairs | Fuzzy email matching in Silver; confidence scoring on match quality | Daily reconciliation_log audit; manual spot-check |
| Lineage Traceability | 100% of Gold rows trace to Bronze source records | Preserve source IDs and load timestamps through all layers | Audit queries joining Gold → Silver → Bronze |
| Cost Containment | ≤ $500 USD/month | Monitor job runtime and query execution time; set alarms on DBU overage | Monthly billing dashboard in Databricks |

## Key Design Decisions

| Decision | Rationale | Tradeoffs |
|----------|-----------|-----------|
| Daily batch, not streaming | Stripe webhook integration costs 2+ weeks; batch fully validates; sales SLA accepts 24-hour latency | Query latency ≤ 24 hours; no real-time churn alerts; easier to replay failed days |
| Separate Bronze/Silver/Silver schemas | Data governance: PII isolation, access control per layer, easy to backfill one layer without reprocessing others | More tables to maintain and document; requires clear naming conventions |
| Salesforce-Stripe match via email + fuzzy | Email is the most reliable cross-system identifier; fuzzy matching handles case and domain normalization | ≠ 100% accuracy; requires manual linking for edge cases; depends on email data quality |
| Flatten Stripe invoice line items in Silver | Simplifies Gold aggregations; avoids multi-row-per-invoice complexity in joins | Denormalizes at Silver (but Silver is allowed to denormalize for analytics) |
| Hash card brand (not full card) in Silver | PCI compliance: no raw card tokens or full numbers stored | Aggregate metrics cannot distinguish card issuer; acceptable for v1 |

## Future Considerations

- **Streaming Subscriptions**: Stripe webhooks in v2 for sub-minute payment latency
- **ML Feature Store**: Separate feature-engineering layer for churn-scoring models
- **Cross-System Orchestration**: Airflow/dbt Cloud for multi-workspace lineage
- **Snowflake Federation**: External tables for cost optimization if query volume scales
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="/reference/glossary/activities/"><strong>Design</strong></a> — Decide how to build it. Capture trade-offs, contracts, and architecture decisions.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/02-design/data-architecture.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="/artifact-types/test/data-quality-expectations/">Data Quality Expectations</a><br><a href="/artifact-types/design/technical-design/">Technical Design</a><br><a href="/artifact-types/design/solution-design/">Solution Design</a></td></tr>
<tr><th>Referenced by</th><td><a href="/artifact-types/test/data-quality-expectations/">Data Quality Expectations</a><br><a href="/artifact-types/build/implementation-plan/">Implementation Plan</a><br><a href="/artifact-types/deploy/runbook/">Runbook</a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Data Architecture Generation Prompt

Document the data pipeline architecture that the team needs to build, review,
operate, and evolve the data product.

## Purpose

Data Architecture is the **highest-authority structural artifact for data pipeline
design** in the Design activity. Its unique job is to describe the durable pipeline
shape: ingestion patterns, medallion layer topology, streaming vs. batch semantics,
transformation patterns, governance boundaries, quality gates, and critical
performance or cost tradeoffs.

Data Architecture is not a data model (captured in Data Design), implementation plan,
or ADR. It is the bridge between Data PRD (requirements) and implementation: &quot;given
these requirements, here is how the pipeline is structured.&quot;

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
- Each layer&#x27;s transformation responsibilities are explicit.
- Ingestion patterns name actual technologies and explain why each is used.
- Quality gates are named (where validation happens, what contracts are
  enforced).
- Performance/cost tradeoffs are visible (partitioning, clustering, retention,
  refresh strategy).
- Deployment topology is concrete (number of clusters, auto-scaling, failover).
- Major decisions link to Data PRD requirements or include inline rationale.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---
ddx:
  id: data-architecture
---

# Data Architecture

## Overview

[Describe the data product being architected, the business problem it solves, and the system context. Name the key data flows and Databricks platform fit. Reference the [[data-prd]] for the business requirements and success metrics this architecture must satisfy.]

### Scope

[What data flows and systems are covered by this architecture? What is deliberately outside the boundary? Which requirements from [[data-prd]] drive the design decisions?]

### System Context

| External System | Role | Protocol | Data Volume |
|-----------------|------|----------|------------|
| [e.g., Salesforce] | [Source system for customer data] | [REST API, batch export] | [M records/day] |
| [e.g., Data Warehouse] | [Consumer of aggregated data] | [Delta API, SQL] | [K rows/hour] |

```mermaid
graph TB
    A[&quot;Salesforce&lt;br/&gt;(Source)&quot;] --&gt;|REST API&lt;br/&gt;hourly| B[&quot;Databricks&lt;br/&gt;Data Platform&quot;]
    C[&quot;Stripe&lt;br/&gt;(Source)&quot;] --&gt;|S3 batch export| B
    B --&gt;|Consumption Layer| D[&quot;BI Tool&lt;br/&gt;(Looker/Tableau)&quot;]
    B --&gt;|ML Training| E[&quot;ML Platform&quot;]
```

## Medallion Topology

### Architecture Pattern

[Describe the medallion layer strategy: Bronze (raw), Silver (validated), Gold (consumption). For each layer, explain the transformation scope, quality gates, and consumer responsibilities.]

### Bronze Layer (Raw Ingestion)

**Purpose**: Land source data in its native form without transformation.

**Source Integration**:
- Source System: [e.g., Salesforce]
- Integration Pattern: [Auto Loader, Streaming Tables, scheduled batch import]
- Schema Validation: [Applied at ingestion, reject if schema mismatch]
- Retention: [e.g., 7 days rolling window for cost efficiency]

**Responsibilities**:
- Ingest all records from source
- Preserve source schema exactly (no column renames or type coercion)
- Tag records with `_ingest_timestamp` and source system identifier
- Detect and quarantine records that fail schema validation

**Quality Gates**:
- All records have `_ingest_timestamp` and source system id
- No truncation of source columns
- Fail fast if source unavailable for &gt;4 hours

### Silver Layer (Validated and Transformed)

**Purpose**: Cleansed, deduplicated, and business-logic-ready data.

**Transformations**:
- Deduplication: [Method: e.g., &quot;keep latest by timestamp&quot;, &quot;PK uniqueness constraint&quot;]
- Data type coercion: [e.g., &quot;convert dates to ISO-8601, currency to numeric&quot;]
- Null handling: [e.g., &quot;fill defaults, or fail if critical column null&quot;]
- Referential integrity: [e.g., &quot;customer_id must exist in customer dimension&quot;]

**Join Strategy**:
| Join | Left | Right | Type | Cardinality | Latency Impact |
|------|------|-------|------|-------------|---|
| [customer enrichment] | `customer_events` | `customer_master` | [Left Outer] | [1:1] | [Add 100ms] |

**Retention**: [e.g., 90 days]

**Responsibilities**:
- Enforce UNIQUE and NOT NULL constraints per data quality expectations
- Materialize aggregations needed for Gold layer
- Document row counts and latency metrics per transformation

**Quality Gates**:
- Zero duplicates (PK uniqueness)
- ≥99% NOT NULL on critical columns
- Row count reconciliation with source ±0.1%

### Gold Layer (Consumption)

**Purpose**: Business-ready tables optimized for consumer queries.

**Consumption Tables**:
| Table | Use Case | Consumers | Freshness | Aggregation |
|-------|----------|-----------|-----------|------------|
| `customer_360` | Single customer view, 360-degree profile | Analytics, ML | Hourly | None (deduped Silver) |
| `daily_sales_summary` | Daily revenue by product | Finance, BI | Daily | SUM(amount) by product_date |

**Optimization Strategy**:
- Partitioning: [e.g., &quot;by date for date-range queries&quot;]
- Z-order: [e.g., &quot;on customer_id, product_id for filter selectivity&quot;]
- Caching: [Materialized views for slow queries]

**Retention**: [e.g., 2 years for compliance and analytics]

**Responsibilities**:
- Keep Gold current with Silver ingestion cadence
- Publish schema and SLA via UC catalog comments
- Monitor query performance; alert if p95 latency &gt; SLA

**Quality Gates**:
- Sums reconcile between Silver aggregates and Gold tables ±0.01%
- All customer IDs in Gold exist in Silver Silver
- Latency ≤SLA (e.g., ≤5 seconds for 90th percentile query)

## Data Flow

[Describe how data moves through the medallion layers. Clarify ingestion frequency, transformation latency, and refresh strategy.]

### Ingestion Flow

```mermaid
graph LR
    A[&quot;Salesforce API&quot;] --&gt;|Auto Loader&lt;br/&gt;every 15 min| B[&quot;Bronze&lt;br/&gt;raw_customers&quot;]
    B --&gt;|PySpark Job&lt;br/&gt;dedup + validate| C[&quot;Silver&lt;br/&gt;customers_validated&quot;]
    C --&gt;|SQL notebook&lt;br/&gt;daily 9am UTC| D[&quot;Gold&lt;br/&gt;customer_360&quot;]
    D --&gt;|Published to UC| E[&quot;Consumers&lt;br/&gt;BI, ML&quot;]
```

### Incremental vs Full Refresh

- **Bronze**: [Incremental via change data capture, or full reload?]
- **Silver**: [Incremental updates on specific key columns, or full recalc?]
- **Gold**: [Append-only fact tables, or snapshot updates?]

## Processing Semantics

### Streaming vs Batch Decision

| Layer | Strategy | Rationale | SLA Implication |
|-------|----------|-----------|-----------------|
| Bronze | [Streaming / Batch / Incremental Batch] | [Why this choice?] | [Freshness achieved] |
| Silver | [Streaming / Batch / Incremental Batch] | [Why this choice?] | [Freshness achieved] |
| Gold | [Streaming / Batch / Incremental Batch] | [Why this choice?] | [Freshness achieved] |

### Processing Framework

- **Framework**: [Databricks SQL, PySpark, dbt on Databricks, Streaming Tables]
- **Orchestration**: [Databricks Workflows, Airflow, dbt Cloud]
- **Failure Handling**: [Retry policy, dead-letter queue, manual intervention?]

### Latency and Throughput Targets

| Stage | Target Latency | Target Throughput | Constraint |
|-------|-----------------|-------------------|-----------|
| Salesforce → Bronze | ≤15 minutes | 1M records/day | API rate limit: 100 req/min |
| Bronze → Silver | ≤30 minutes | 1M records/day | PySpark cluster size |
| Silver → Gold | ≤2 hours | 100K aggregates/day | SQL query complexity |

## Quality Contracts

[Define expectations as testable EXPECT clauses per Databricks SDP. Each expectation binds the architecture: data violating it is rejected before reaching consumers.]

### Bronze Layer Expectations

```sql
-- Raw data must match source schema exactly
EXPECT TABLE raw_customers (
  customer_id NOT NULL,
  email NOT NULL,
  created_at TIMESTAMP NOT NULL,
  _ingest_timestamp TIMESTAMP NOT NULL GENERATED ALWAYS AS (CURRENT_TIMESTAMP())
);
```

- **Expectation**: All records ingested within 15 min of source commit
- **Violation**: Alert; do not advance to Silver
- **SLA**: Detect within 5 minutes

### Silver Layer Expectations

```sql
-- Customers must be unique per customer_id, deduplicated by latest timestamp
EXPECT TABLE customers_validated (
  customer_id NOT NULL,
  PRIMARY KEY (customer_id),
  UNIQUE (customer_id)
);

-- Customer email addresses must be normalized and not null
EXPECT TABLE customers_validated (
  email NOT NULL LIKE &#x27;%@%.%&#x27;
);
```

- **Expectation**: ≥99% NOT NULL on `email` and `phone`
- **Expectation**: Zero duplicate customers (PK uniqueness)
- **Violation**: Quarantine; manual review before advancing to Gold

### Gold Layer Expectations

```sql
-- Customer 360 must be current within freshness SLA (1 hour)
EXPECT TABLE customer_360 (
  MAX(_modified_at) &gt;= CURRENT_TIMESTAMP() - INTERVAL 1 HOUR
);

-- Revenue aggregates must reconcile with Silver within 0.01%
EXPECT TABLE daily_sales_summary
  CHECK (
    SELECT SUM(amount) FROM daily_sales_summary 
    IS WITHIN 0.01% OF 
    SELECT SUM(amount) FROM customers_validated
  );
```

- **Expectation**: Customer 360 is no older than 1 hour
- **Expectation**: Daily sales sums reconcile with Silver ±$0.01 per order
- **Violation**: Reject; roll back to prior snapshot; alert on-call

### Cross-Layer Data Contracts

| Contract | Assertion | If Violated |
|----------|-----------|------------|
| [Bronze → Silver row count] | [Silver row count ≤ Bronze + 10% for dedup] | [Alert + manual audit] |
| [Silver → Gold cardinality] | [Gold unique customers = Silver unique customers] | [Reject until reconciled] |
| [Foreign key integrity] | [All orders.customer_id exist in customer_360] | [Quarantine order; alert] |

## Governance and Access Control

### Identity and Access Management

| Role | Catalog | Schema | Table | Permissions |
|------|---------|--------|-------|------------|
| Data Engineer | `prod` | `customer_360` | All | READ, MODIFY, EXECUTE |
| Analytics Lead | `prod` | `customer_360` | `customer_360`, `daily_sales_summary` (Gold only) | SELECT |
| Finance Team | `prod` | `customer_360` | `daily_sales_summary` | SELECT (date ≥ 2 years ago) |

### Data Classification and Retention

| Table | Classification | Sensitive Columns | Retention | Masked For |
|-------|------------------|------------------|-----------|-----------|
| `raw_customers` | Internal | `ssn`, `credit_card` | 7 days | [Not masked; only admins see] |
| `customers_validated` | Internal | `email`, `phone` | 90 days | [Non-PII audiences mask these] |
| `customer_360` | Internal | `email` | 2 years | [Mask for BI tool] |

### Fine-Grained Access Control

- **Row-Level Security**: [Do analytics users see only their region&#x27;s data? Document the policy.]
- **Column-Level Security**: [Which sensitive columns are masked for which roles?]
- **Dynamic Views**: [Use UC masking functions to redact PII per caller role?]

## Databricks Platform Design

### Catalog Organization

```
prod (Catalog)
├── customer_360 (Schema)
│   ├── raw_customers (Bronze table)
│   ├── customers_validated (Silver table)
│   ├── customer_360 (Gold table)
│   └── daily_sales_summary (Gold aggregate)
├── metadata (Schema)
│   ├── pipeline_runs (audit log)
│   └── quality_metrics (expectations results)
```

### Compute Strategy

| Workload | Compute Tier | Cluster Size | DBU Budget | Rationale |
|----------|--------------|--------------|------------|-----------|
| Bronze ingestion (streaming) | All-purpose | 4 workers (i3.xlarge) | 8 DBU/hour | Continuous streaming |
| Silver transformation (batch) | Jobs | 8 workers (i3.2xlarge) | 16 DBU/run | Scheduled nightly |
| Gold aggregation (query) | Serverless SQL | N/A | ~5 DBU/query | Ad-hoc BI queries |

**Cost Optimization**:
- Spot instances for non-critical workloads: 30% savings
- Auto-terminate idle clusters: reduce waste
- Partition pruning and z-order for faster queries: reduce scans

### Storage Strategy

| Layer | Format | Compression | Optimization |
|-------|--------|-------------|--------------|
| Bronze | Delta | Snappy | Partitioned by date (rolling 7-day window) |
| Silver | Delta | Snappy | Z-ordered by customer_id, product_id |
| Gold | Delta | Snappy | Partitioned by date; cached for BI queries |

**Storage Sizing**: ~500 GB Bronze, ~50 GB Silver, ~5 GB Gold (monthly) → ~$25/month at $0.023/GB/month

### Databricks Features in Use

| Feature | Use Case | Configuration |
|---------|----------|---------------|
| Auto Loader | Salesforce → Bronze incremental ingestion | Cloud file location: S3, Schema inference enabled |
| Streaming Tables | Bronze → Silver continuous transformation | Trigger: arrival, 30-second max latency |
| Delta Live Tables | End-to-end medallion pipeline orchestration | Refresh: hourly for Bronze/Silver, daily for Gold |
| Unity Catalog | Governance, lineage, fine-grained access | Enable open sharing across teams |

## Decisions and Tradeoffs

### Key Architecture Decisions

| Decision | Choice | Rationale | Alternative Considered | Consequence |
|----------|--------|-----------|------------------------|------------|
| [Medallion layers] | [Bronze/Silver/Gold] | [Standard Databricks pattern for quality gates] | [Flat schema, 2-layer] | [Slower queries if using Bronze directly; quality risk] |
| [Streaming vs Batch for Silver] | [Batch nightly] | [Simplicity, cost] | [Streaming] | [1-2 hour stale window; acceptable for reporting] |
| [Compute tier for Gold queries] | [Serverless SQL] | [Cost &amp; elasticity; no cluster mgmt] | [All-purpose cluster] | [Higher per-query cost; simpler ops] |

### Performance vs Cost Tradeoffs

- **Real-time ingestion** (streaming Bronze): Freshness ≤5 min, but 40% higher DBU cost
- **Materialized Gold aggregates**: Faster queries (100ms), but 20% higher storage cost
- **Spot instances for Silver jobs**: 30% cheaper, but risk of interruption (retry handles it)

### Known Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| [Salesforce API rate limit causes ingestion backlog] | [Implement exponential backoff; buffer in queue; alert if &gt;1 hour backlog] |
| [PII in Bronze accessible to all engineers] | [Mask sensitive columns in published views; audit access logs] |
| [Schema drift in source breaks ingestion] | [Schema registry; auto-detect new columns; manual approval before Silver] |

---

## Review Checklist

Use this checklist during review to validate that the data architecture is complete and ready for implementation:

- [ ] **Scope** clearly states which data flows are included and which are out of bounds
- [ ] **Medallion Topology** defines Bronze, Silver, Gold layer purposes and transformation rules
- [ ] **Data Flow diagrams** (mermaid) show how data moves through layers and to consumers
- [ ] **Processing Semantics** explicitly state streaming vs batch for each layer with latency targets
- [ ] **Quality Contracts** are written as executable EXPECT clauses (SDP, dbt, SQL constraints)
- [ ] **Failure Handling** specifies what happens when an expectation fails (alert, reject, quarantine)
- [ ] **Access Control** model covers identity, row-level, column-level, and sensitive data masking
- [ ] **Databricks Platform Design** names catalog, schema, compute tier, storage strategy, and DBU budget
- [ ] **Decisions and Tradeoffs** document key choices with rationale and alternatives considered
- [ ] **Cross-layer data contracts** are defined (sums reconcile, cardinality stable, no orphans)
- [ ] **SLA per layer** is documented (freshness, latency, availability targets)
- [ ] No `[TBD]`, `[TODO]`, or `[NEEDS CLARIFICATION]` markers remain
- [ ] Architecture aligns with requirements in [[data-prd]] and can satisfy success metrics
- [ ] References link to [[data-quality-expectations]] for detailed EXPECT clauses per layer</code></pre></details></td></tr>
</tbody>
</table>
