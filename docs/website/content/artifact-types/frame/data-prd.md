---
title: "Data Product Requirements Document"
linkTitle: "Data Prd"
slug: data-prd
activity: "Frame"
artifactRole: "supporting"
weight: 90
generated: true
---

## Purpose

The Data PRD is the **data-product-scope authority for what data to build and why**.
Its unique job is to translate business intent into data-centric requirements:
data sources, consumer personas, quality contracts, technical constraints (catalog,
schema, medallion layer), and measurable success metrics. It sits between the
general Product Vision and Data Architecture. Every data pipeline design choice
and quality expectation should trace back to a Data PRD requirement.

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: example.data-prd.customer-360
---

# Data Product Requirements Document: Customer-360 Analytics

## Summary

Customer-360 is a unified analytics dataset that reconciles Salesforce customer
accounts with Stripe payment history and customer lifecycle events. It powers
sales forecasting, churn analysis, and account health scoring. The first release
ingests 12 months of historical data and supports daily incremental updates for
ongoing revenue and subscription trends. Success means sales analysts can query a
single Gold table to answer "total ARR per customer," "months since last payment,"
and "invoice aging" without joining across multiple systems.

## Problem and Goals

### Problem

Sales and finance teams use Salesforce for CRM and Stripe for payment processing,
but data is siloed. Analysts manually pull exports, reconcile customer IDs across
systems, and build fragile spreadsheets to answer cash-flow and churn questions.
Each reconciliation takes 3-4 hours and risks stale data by the time insights are
shared.

### Goals

1. Unify Salesforce accounts and Stripe customers under a single customer identity.
2. Preserve payment lineage: which invoice, subscription, or charge event drove
   each revenue transaction.
3. Deliver Gold tables that require no post-query transformation for common
   business questions.

### Success Metrics

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| Query response time | Under 5 seconds for customer-year aggregations | Databricks query execution time |
| Data freshness | Daily updates complete before 7am UTC | Pipeline job logs and SLA monitoring |
| Customer ID reconciliation accuracy | 98% of Salesforce accounts matched to Stripe customers | Manual audit sample of matched pairs |
| Analyst adoption | 10+ scheduled reports consuming Gold tables | Databricks workspace audit logs |

### Non-Goals

- Streaming ingestion (batch-daily is sufficient for v1).
- Custom churn-scoring algorithms (featurized data enables external ML).
- Integration with Marketo, HubSpot, or third-party data warehouses.
- Supporting sub-account hierarchies within Stripe.

## Data Consumers

| Role | Team | Key Questions | Tables |
|------|------|---------------|--------|
| Sales Analyst | Revenue | ARR by account, churn risk score, invoice aging | dim_customer, fct_monthly_revenue |
| Finance Manager | Revenue Operations | Subscription changes, failed payment count, billing exceptions | fct_subscription_event, fct_payment_transaction |
| Data Engineer | Analytics | Lineage validation, late-arriving facts, reconciliation record counts | all layer tables, metadata.processing_log |

## Data Sources

| Source System | Entity | Volume (12-month history) | Frequency | SLA |
|---------------|--------|---------------------------|-----------|-----|
| Salesforce | Account records (customer name, owner, industry) | 5,000 accounts | Daily export (API) | 6-hour lag acceptable |
| Salesforce | Opportunity records (pipeline, closed deals) | 50,000 opps | Daily export (API) | 6-hour lag acceptable |
| Stripe | Customer objects (email, metadata tags) | 4,500 customers | Real-time webhook (v1 batch daily) | 24-hour batch acceptable for v1 |
| Stripe | Subscription objects (plan, status, start/end dates) | 6,200 subscriptions | Real-time webhook (v1 batch daily) | 24-hour batch acceptable for v1 |
| Stripe | Invoice records (amount, status, line items) | 45,000 invoices | Real-time webhook (v1 batch daily) | 24-hour batch acceptable for v1 |
| Stripe | Charge records (card, amount, outcome) | 180,000 charges | Real-time webhook (v1 batch daily) | 24-hour batch acceptable for v1 |

## Data Quality Requirements

### Coverage

| Expectation | Threshold | Owner | Severity |
|-------------|-----------|-------|----------|
| Salesforce account export completeness | ≥ 95% of prior day's account count | Data Eng | P0 (block load) |
| Stripe customer export completeness | ≥ 95% of prior day's distinct customers | Data Eng | P0 (block load) |
| Customer ID reconciliation rate | ≥ 98% of matched Salesforce-Stripe pairs | Data Eng | P1 (alert, allow backfill) |
| Invoice line-item accuracy | 100% of invoices ≥ $0; amount matches sum of line items | Data Eng | P0 (block load) |

### Freshness

| Dataset | Expected latency | Acceptable Delay | Monitoring |
|---------|------------------|------------------|------------|
| Bronze Salesforce (raw export) | Within 6 hours of API call | 8 hours | Query SLA dashboard |
| Bronze Stripe (raw export) | Within 24 hours of event (batch v1) | 26 hours | Query SLA dashboard |
| Silver (deduplicated, reconciled) | Within 8 hours of Bronze completion | 10 hours | Pipeline job history |
| Gold (aggregated facts) | Before 7am UTC daily | 8am UTC | Scheduled report execution |

### Metadata Requirements

- **Lineage**: Every Gold row must record the source Salesforce and Stripe record IDs,
  import batch ID, and last-modified timestamp.
- **Data Quality Flags**: Silver layer must include reconciliation match confidence,
  late-arriving fact flags, and anomaly detection scores.
- **Processing Metadata**: All tables must include `_loaded_at`, `_processed_by_job_id`,
  and `_source_system`.

## Databricks-Specific Technical Context

### Workspace and Catalog

- **Catalog**: main (Unity Catalog enabled)
- **Schema Naming**: customer_360_{bronze,silver,gold}
- **Medallion Layers**: Separate schemas for isolation and access control

### Compute

- **Orchestration**: Databricks Workflows with daily 10pm UTC trigger
- **Compute**: Job cluster, 2 workers, 8 DBU/hour estimate
- **Language**: Python with PySpark for orchestration, SQL for transformations

### Access Control

- **Bronze**: Data Engineer read/write; Analyst no access (sensitive raw PII)
- **Silver**: Data Engineer read/write; Analyst read-only (internal team only)
- **Gold**: Data Engineer read/write; Analyst read; Managers read (published via BI)

### Compliance

- **PII Handling**: Customer email and phone hashed in Silver+ layers; raw email in Bronze only
- **Retention**: Bronze/Silver retained 90 days; Gold retained 3 years
- **Masking**: Stripe card tokens never stored; card brand only in Silver

## Constraints and Assumptions

### Constraints

- **Data Volume**: 12-month history = ~250GB uncompressed; daily increments ~1GB
- **Cost**: ≤ $500 USD/month DBU spend for batch jobs + queries
- **Latency**: Daily batch only for v1; no streaming/real-time SLAs

### Assumptions

- Salesforce and Stripe customer data stabilizes within 24 hours of creation
- No single customer appears as multiple accounts in Salesforce (will validate in reconciliation)
- Email is a sufficient match key for Salesforce-Stripe reconciliation (vs. manual linking)

### Dependencies

- Salesforce API credentials and rate-limit quota
- Stripe API credentials and historical export access
- Databricks Unity Catalog workspace with ≥ 2 worker nodes available

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Email format inconsistency blocks Stripe-Salesforce joins | High | High | Implement fuzzy email matching (lowercase, domain normalization) in Silver |
| Stripe subscription deletion removes invoice lineage | Medium | High | Copy foreign keys to Bronze before join; archive deleted subscriptions in reference table |
| Gold table query cost exceeds budget | Medium | Medium | Add partition pruning by month; set query-timeout alarms; publish consumption dashboard |

## Open Questions

- [ ] Does Salesforce contain sub-accounts or partner-account hierarchies? Will this affect the 1:1 customer assumption?
- [ ] Are there known Stripe test customers in the export that should be filtered in Bronze?
- [ ] Which BI tool will query Gold tables (Tableau, Looker, Sigma)? Will it handle incremental refresh?

## Success Criteria

Customer-360 is successful when:
1. Analysts execute fewer than 5 manual export-and-reconcile cycles per quarter.
2. Sales team's monthly revenue forecast uses only Gold table queries (no spreadsheets).
3. Churn alerting dashboard refreshes successfully every morning by 7am UTC for 30 consecutive days.
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="/reference/glossary/activities/"><strong>Frame</strong></a> — Define what the system should do, for whom, and how success will be measured.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/01-frame/data-prd.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="/artifact-types/design/data-architecture/">Data Architecture</a><br><a href="/artifact-types/frame/feature-specification/">Feature Specification</a><br><a href="/artifact-types/frame/user-stories/">User Stories</a></td></tr>
<tr><th>Referenced by</th><td><a href="/artifact-types/design/data-architecture/">Data Architecture</a><br><a href="/artifact-types/design/technical-design/">Technical Design</a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Data Product Requirements (Data PRD) Generation Prompt&#10;&#10;Create a Data PRD that frames the data product problem, scope, quality requirements,&#10;and success criteria clearly enough that downstream data architecture, quality&#10;expectations, and implementation work can trace back to it.&#10;&#10;## Purpose&#10;&#10;The Data PRD is the **data-product-scope authority for what data to build and why**.&#10;Its unique job is to translate business intent into data-centric requirements:&#10;data sources, consumer personas, quality contracts, technical constraints (catalog,&#10;schema, medallion layer), and measurable success metrics. It sits between the&#10;general Product Vision and Data Architecture. Every data pipeline design choice&#10;and quality expectation should trace back to a Data PRD requirement.&#10;&#10;## Reference Anchors&#10;&#10;Use these local resource summaries as grounding:&#10;&#10;- `docs/resources/databricks-unity-catalog.md` grounds data governance through&#10;  unified catalog hierarchies (metastore → catalog → schema → volume/table).&#10;- `docs/resources/databricks-lakehouse-medallion-architecture.md` grounds&#10;  medallion topology (Bronze/Silver/Gold) and layer responsibilities in a&#10;  Lakehouse.&#10;- `docs/resources/databricks-sdp.md` grounds Databricks Semantic Data Platform&#10;  governance, lineage, and quality contracts through `EXPECT ... ON VIOLATION ...`&#10;  clauses and SDP-aware pipeline patterns.&#10;&#10;## Focus&#10;&#10;- Name the data sources (internal and external), ingestion cadence, and expected&#10;  volume/velocity.&#10;- Define data consumers and their use cases: who consumes the data, what decisions&#10;  they make, and what quality they depend on.&#10;- List data quality requirements as testable contracts: completeness, accuracy,&#10;  freshness, schema consistency, referential integrity.&#10;- Specify the Databricks technical context: target catalog/schema, medallion&#10;  layer (Bronze/Silver/Gold), pipeline type (Auto Loader, Streaming Tables, SQL&#10;  pipeline), and estimated DBU budget.&#10;- Frame success metrics for the data product itself: SLA compliance (freshness,&#10;  availability), consumer satisfaction, cost per GB, defect escape rate.&#10;&#10;## Role Boundary&#10;&#10;Data PRD is not a general product PRD, data model, pipeline design, or quality&#10;implementation. It specifies *what* data requirements are, not *how* to implement&#10;them.&#10;&#10;**Databricks Platform Substitution:** If you are adopting this on another data&#10;platform, substitute as follows:&#10;&#10;| Databricks Concept | Snowflake Equivalent | BigQuery Equivalent | On-Prem / Other |&#10;|---|---|---|---|&#10;| Unity Catalog (UC) hierarchy | Database + Schema + Table | Project + Dataset + Table | Database + Schema |&#10;| Medallion architecture (Bronze/Silver/Gold) | Same pattern applies universally | Same pattern applies universally | Same pattern applies universally |&#10;| Auto Loader, Streaming Tables | Snowpipe, Stream-triggered tasks | Dataflow, BigQuery Streaming Inserts | Apache Spark Structured Streaming, Airflow |&#10;| SDP `EXPECT ... ON VIOLATION ...` | Data Quality checks in Snowflake | BigQuery Data Quality API | dbt tests, Great Expectations assertions |&#10;| DBU budget estimation | Credit consumption | On-demand or flat-rate pricing | Compute resource allocation |&#10;&#10;## Completion Criteria&#10;&#10;- Data sources table names each external/internal source, ingestion pattern, and&#10;  freshness requirement.&#10;- Data consumers table includes consumer role, use case, and quality SLA.&#10;- Quality requirements are specific constraints (not aspirational); each one is&#10;  testable in Data Quality Expectations.&#10;- Technical context names the target catalog, schema, medallion layer, and&#10;  pipeline type.&#10;- Success metrics have numeric targets and measurement methods (e.g., &quot;SLA&#10;  compliance &gt; 95% measured by on-time delivery vs. promised refresh cadence&quot;).&#10;- Requirements trace upward to the Product Vision or general PRD and downward&#10;  to Data Architecture and Data Quality Expectations.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: data-prd&#10;---&#10;&#10;# Data Product Requirements Document&#10;&#10;## Executive Summary&#10;&#10;[This section works as a standalone 1-pager. Include: what data product we are building, who uses it, what business problem it solves, the data solution approach, and the top 2-3 success metrics. Write this last — it should be a distillation of the full PRD, not an introduction. Someone reading only this section should understand the data product well enough to decide whether to read the rest.]&#10;&#10;## Problem and Goals&#10;&#10;### Problem Statement&#10;&#10;[What is broken or missing in the current data landscape? Who is affected? Be specific: not &quot;users struggle with reporting&quot; but &quot;sales analysts spend 4 hours per week reconciling pipeline outputs with source systems because current freshness is 24 hours and source data changes hourly.&quot;]&#10;&#10;### Business Goals&#10;&#10;1. [Primary goal — what changes for the organization or data consumers]&#10;2. [Secondary goal — secondary business impact or risk reduction]&#10;&#10;### Goals and Objectives&#10;&#10;| Goal | Objective | Success Criteria |&#10;|------|-----------|------------------|&#10;| [Goal] | [How we achieve it via data] | [Measurable outcome] |&#10;&#10;### Non-Goals&#10;&#10;[What we are explicitly not trying to achieve. Each non-goal should exclude something a reasonable person might assume is in scope.]&#10;&#10;## Data Consumers&#10;&#10;### Primary Consumer: [Name/Role]&#10;&#10;**Team**: [Data Engineering, Analytics, Product, Finance, etc.]&#10;**Use Case**: [What do they do with this data? How does it change their workflow?]&#10;**Frequency**: [Real-time, daily, weekly, ad-hoc?]&#10;**Key Tables/Feeds**: [Which outputs matter most to this consumer?]&#10;&#10;### Secondary Consumer: [Name/Role]&#10;&#10;[Repeat above structure for each secondary consumer.]&#10;&#10;### Data Consumer Requirements Table&#10;&#10;| Consumer | Use Case | Freshness SLA | Latency Tolerance | Key Dimensions | Access Level |&#10;|----------|----------|---------------|-------------------|----------------|--------------|&#10;| [Team] | [What they do] | [e.g., hourly] | [max delay] | [customer_id, product_id, ...] | [Row-level, Column-level, or Full] |&#10;&#10;## Data Sources&#10;&#10;### Source System Inventory&#10;&#10;| Source System | Schema / Table | Owner | Update Frequency | Quality Baseline | Notes |&#10;|---------------|----------------|-------|------------------|------------------|-------|&#10;| [e.g., Salesforce] | [e.g., Accounts, Opportunities] | [Team] | [hourly, daily, on-demand] | [% completeness, freshness] | [Data model version, API limits, retry policy] |&#10;&#10;## Requirements Overview&#10;&#10;### P0 (Must Have)&#10;&#10;[Critical requirements blocking data product delivery or violating SLA.]&#10;&#10;- Requirement: [e.g., &quot;Ingest Salesforce data within 1 hour of transaction close&quot;]&#10;- Requirement: [e.g., &quot;Support daily rollup of customer spend by product category&quot;]&#10;&#10;### P1 (Should Have)&#10;&#10;[Important for end-user value or operational stability.]&#10;&#10;- Requirement: [e.g., &quot;Detect and alert on data quality anomalies within 15 minutes&quot;]&#10;- Requirement: [e.g., &quot;Enable drill-down to daily granularity without latency penalty&quot;]&#10;&#10;### P2 (Nice to Have)&#10;&#10;[Nice-to-have enhancements deferred if time-constrained.]&#10;&#10;- Requirement: [e.g., &quot;Publish historical snapshots for year-over-year comparison&quot;]&#10;&#10;## Data Quality Requirements&#10;&#10;### Quality Dimensions and Thresholds&#10;&#10;| Dimension | P0 Threshold | P1 Threshold | Measurement Method | Enforcement |&#10;|-----------|--------------|--------------|-------------------|-------------|&#10;| Completeness | [e.g., ≥99%] | [e.g., ≥95%] | [Count NULLs / total rows] | [Alert if falls below P0] |&#10;| Timeliness | [e.g., ≤1 hour lag] | [e.g., ≤4 hour lag] | [MAX(ingestion_time) - MAX(source_time)] | [Reject data if exceeds P0] |&#10;| Accuracy | [e.g., ≥98% match to source] | [e.g., ≥95% match] | [Row-count reconciliation + sample audit] | [Manual review + auto-reject if P0 fails] |&#10;| Uniqueness | [e.g., PK has no duplicates] | [as P0] | [COUNT(*) = COUNT(DISTINCT PK)] | [Fail ingestion] |&#10;&#10;### Data Quality Expectations&#10;&#10;[Reference the [[data-quality-expectations]] document for detailed EXPECT clauses per medallion layer. This section summarizes which quality dimensions are critical.]&#10;&#10;## Databricks-Specific Technical Context&#10;&#10;### Catalog and Schema Strategy&#10;&#10;- **Target Catalog**: [e.g., `prod`, `analytics`, or domain-specific catalog]&#10;- **Target Schema**: [e.g., `customer_360`, `payment_events`]&#10;- **Medallion Layers**: Bronze (raw), Silver (validated), Gold (business)&#10;- **Access Control Model**: [UC policies, Row-level security, column masking]&#10;&#10;### Medallion Layer Strategy&#10;&#10;- **Bronze**: [Raw data ingestion point; what is ingested, what constraints apply, how often]&#10;- **Silver**: [Validated and deduplicated; transformation rules, quality gates]&#10;- **Gold**: [Business-ready tables; aggregations, dimensions, fact tables for consumers]&#10;&#10;### Databricks Features and Compute Strategy&#10;&#10;| Feature | Decision | Rationale |&#10;|---------|----------|-----------|&#10;| Ingestion Pattern | [Auto Loader, Streaming Tables, batch] | [Why this choice?] |&#10;| Processing Model | [Streaming, Batch, Incremental] | [Freshness SLA and cost tradeoff] |&#10;| Compute Tier | [All-purpose, Jobs, Serverless] | [Workload characteristics, cost model] |&#10;| Storage Format | [Delta, Parquet, CSV] | [Durability, query performance needs] |&#10;| DBU Budget (Monthly) | [Estimated spend] | [Based on row volume, freshness, complexity] |&#10;&#10;### Governance and Compliance&#10;&#10;- **Data Classification**: [Public, Internal, Sensitive, PII]&#10;- **Retention Policy**: [e.g., Bronze: 7 days, Silver: 90 days, Gold: 2 years]&#10;- **Audit Trail**: [Who accessed what, when, why]&#10;- **Lineage Tracking**: [Table-to-table dependencies for impact analysis]&#10;&#10;## Success Metrics&#10;&#10;| Metric | Target | Baseline | Measurement Method | Cadence |&#10;|--------|--------|----------|-------------------|---------|&#10;| [Throughput] | [e.g., 1M rows/day] | [Current: 100K rows/day] | [COUNT(*) from production table] | Daily |&#10;| [Latency] | [e.g., ≤1 hour end-to-end] | [Current: 4 hours] | [MAX(ingestion_timestamp) - MAX(source_timestamp)] | Hourly |&#10;| [Quality Score] | [e.g., ≥98%] | [Current: 85%] | [Automated quality checks pass rate] | Daily |&#10;| [Cost per GB] | [e.g., $0.05/GB/month] | [Current: $0.12/GB/month] | [DBU spend / data volume] | Monthly |&#10;&#10;## Risks and Mitigation&#10;&#10;| Risk | Likelihood | Impact | Mitigation Strategy |&#10;|------|------------|--------|-------------------|&#10;| [e.g., Source API rate limits] | [High] | [Data ingestion delays] | [Implement backoff + queue; alert on throttling] |&#10;| [e.g., Schema drift in source] | [Medium] | [Pipeline failure or silent corruption] | [Schema registry; alerts on new columns; manual review] |&#10;| [e.g., Cost overrun from compute] | [Medium] | [Budget overrun] | [Set DBU limits; implement cost monitoring] |&#10;&#10;---&#10;&#10;## Review Checklist&#10;&#10;Use this checklist during review to validate that the data PRD is complete and ready for design:&#10;&#10;- [ ] **Executive Summary** is self-contained and clearly states the data product purpose&#10;- [ ] **Problem Statement** is specific: includes failure mode, frequency, and affected stakeholders (not generic)&#10;- [ ] **Data Consumers table** names actual teams/roles with concrete use cases (not abstract personas)&#10;- [ ] **Data Sources** table is complete: every source system has an entry with owner and update frequency&#10;- [ ] **Requirements** are prioritized (P0/P1/P2) and traceable to data consumer use cases&#10;- [ ] **Quality Dimensions** have numeric thresholds (not vague targets like &quot;high quality&quot;)&#10;- [ ] **Databricks Context** specifies catalog, schema, medallion layer strategy, and compute approach&#10;- [ ] **Success Metrics** are quantified: throughput (rows/day), latency (max age), quality score (%), cost ($/GB)&#10;- [ ] **Risks** are specific with likelihood/impact assessment and mitigation tactics&#10;- [ ] No `[TBD]`, `[TODO]`, or `[NEEDS CLARIFICATION]` markers remain&#10;- [ ] Naming and terminology align with Databricks Unity Catalog and SDP conventions&#10;- [ ] Every P0 requirement has at least one data quality expectation (link to [[data-quality-expectations]])</code></pre></details></td></tr>
</tbody>
</table>
