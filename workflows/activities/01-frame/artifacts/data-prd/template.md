---
ddx:
  id: data-prd
---

# Data Product Requirements Document

## Executive Summary

[This section works as a standalone 1-pager. Include: what data product we are building, who uses it, what business problem it solves, the data solution approach, and the top 2-3 success metrics. Write this last — it should be a distillation of the full PRD, not an introduction. Someone reading only this section should understand the data product well enough to decide whether to read the rest.]

## Problem and Goals

### Problem Statement

[What is broken or missing in the current data landscape? Who is affected? Be specific: not "users struggle with reporting" but "sales analysts spend 4 hours per week reconciling pipeline outputs with source systems because current freshness is 24 hours and source data changes hourly."]

### Business Goals

1. [Primary goal — what changes for the organization or data consumers]
2. [Secondary goal — secondary business impact or risk reduction]

### Goals and Objectives

| Goal | Objective | Success Criteria |
|------|-----------|------------------|
| [Goal] | [How we achieve it via data] | [Measurable outcome] |

### Non-Goals

[What we are explicitly not trying to achieve. Each non-goal should exclude something a reasonable person might assume is in scope.]

## Data Consumers

### Primary Consumer: [Name/Role]

**Team**: [Data Engineering, Analytics, Product, Finance, etc.]
**Use Case**: [What do they do with this data? How does it change their workflow?]
**Frequency**: [Real-time, daily, weekly, ad-hoc?]
**Key Tables/Feeds**: [Which outputs matter most to this consumer?]

### Secondary Consumer: [Name/Role]

[Repeat above structure for each secondary consumer.]

### Data Consumer Requirements Table

| Consumer | Use Case | Freshness SLA | Latency Tolerance | Key Dimensions | Access Level |
|----------|----------|---------------|-------------------|----------------|--------------|
| [Team] | [What they do] | [e.g., hourly] | [max delay] | [customer_id, product_id, ...] | [Row-level, Column-level, or Full] |

## Data Sources

### Source System Inventory

| Source System | Schema / Table | Owner | Update Frequency | Quality Baseline | Notes |
|---------------|----------------|-------|------------------|------------------|-------|
| [e.g., Salesforce] | [e.g., Accounts, Opportunities] | [Team] | [hourly, daily, on-demand] | [% completeness, freshness] | [Data model version, API limits, retry policy] |

## Requirements Overview

### P0 (Must Have)

[Critical requirements blocking data product delivery or violating SLA.]

- Requirement: [e.g., "Ingest Salesforce data within 1 hour of transaction close"]
- Requirement: [e.g., "Support daily rollup of customer spend by product category"]

### P1 (Should Have)

[Important for end-user value or operational stability.]

- Requirement: [e.g., "Detect and alert on data quality anomalies within 15 minutes"]
- Requirement: [e.g., "Enable drill-down to daily granularity without latency penalty"]

### P2 (Nice to Have)

[Nice-to-have enhancements deferred if time-constrained.]

- Requirement: [e.g., "Publish historical snapshots for year-over-year comparison"]

## Data Quality Requirements

### Quality Dimensions and Thresholds

| Dimension | P0 Threshold | P1 Threshold | Measurement Method | Enforcement |
|-----------|--------------|--------------|-------------------|-------------|
| Completeness | [e.g., ≥99%] | [e.g., ≥95%] | [Count NULLs / total rows] | [Alert if falls below P0] |
| Timeliness | [e.g., ≤1 hour lag] | [e.g., ≤4 hour lag] | [MAX(ingestion_time) - MAX(source_time)] | [Reject data if exceeds P0] |
| Accuracy | [e.g., ≥98% match to source] | [e.g., ≥95% match] | [Row-count reconciliation + sample audit] | [Manual review + auto-reject if P0 fails] |
| Uniqueness | [e.g., PK has no duplicates] | [as P0] | [COUNT(*) = COUNT(DISTINCT PK)] | [Fail ingestion] |

### Data Quality Expectations

[Reference the [[data-quality-expectations]] document for detailed EXPECT clauses per medallion layer. This section summarizes which quality dimensions are critical.]

## Databricks-Specific Technical Context

### Catalog and Schema Strategy

- **Target Catalog**: [e.g., `prod`, `analytics`, or domain-specific catalog]
- **Target Schema**: [e.g., `customer_360`, `payment_events`]
- **Medallion Layers**: Bronze (raw), Silver (validated), Gold (business)
- **Access Control Model**: [UC policies, Row-level security, column masking]

### Medallion Layer Strategy

- **Bronze**: [Raw data ingestion point; what is ingested, what constraints apply, how often]
- **Silver**: [Validated and deduplicated; transformation rules, quality gates]
- **Gold**: [Business-ready tables; aggregations, dimensions, fact tables for consumers]

### Databricks Features and Compute Strategy

| Feature | Decision | Rationale |
|---------|----------|-----------|
| Ingestion Pattern | [Auto Loader, Streaming Tables, batch] | [Why this choice?] |
| Processing Model | [Streaming, Batch, Incremental] | [Freshness SLA and cost tradeoff] |
| Compute Tier | [All-purpose, Jobs, Serverless] | [Workload characteristics, cost model] |
| Storage Format | [Delta, Parquet, CSV] | [Durability, query performance needs] |
| DBU Budget (Monthly) | [Estimated spend] | [Based on row volume, freshness, complexity] |

### Governance and Compliance

- **Data Classification**: [Public, Internal, Sensitive, PII]
- **Retention Policy**: [e.g., Bronze: 7 days, Silver: 90 days, Gold: 2 years]
- **Audit Trail**: [Who accessed what, when, why]
- **Lineage Tracking**: [Table-to-table dependencies for impact analysis]

## Success Metrics

| Metric | Target | Baseline | Measurement Method | Cadence |
|--------|--------|----------|-------------------|---------|
| [Throughput] | [e.g., 1M rows/day] | [Current: 100K rows/day] | [COUNT(*) from production table] | Daily |
| [Latency] | [e.g., ≤1 hour end-to-end] | [Current: 4 hours] | [MAX(ingestion_timestamp) - MAX(source_timestamp)] | Hourly |
| [Quality Score] | [e.g., ≥98%] | [Current: 85%] | [Automated quality checks pass rate] | Daily |
| [Cost per GB] | [e.g., $0.05/GB/month] | [Current: $0.12/GB/month] | [DBU spend / data volume] | Monthly |

## Risks and Mitigation

| Risk | Likelihood | Impact | Mitigation Strategy |
|------|------------|--------|-------------------|
| [e.g., Source API rate limits] | [High] | [Data ingestion delays] | [Implement backoff + queue; alert on throttling] |
| [e.g., Schema drift in source] | [Medium] | [Pipeline failure or silent corruption] | [Schema registry; alerts on new columns; manual review] |
| [e.g., Cost overrun from compute] | [Medium] | [Budget overrun] | [Set DBU limits; implement cost monitoring] |

---

## Review Checklist

Use this checklist during review to validate that the data PRD is complete and ready for design:

- [ ] **Executive Summary** is self-contained and clearly states the data product purpose
- [ ] **Problem Statement** is specific: includes failure mode, frequency, and affected stakeholders (not generic)
- [ ] **Data Consumers table** names actual teams/roles with concrete use cases (not abstract personas)
- [ ] **Data Sources** table is complete: every source system has an entry with owner and update frequency
- [ ] **Requirements** are prioritized (P0/P1/P2) and traceable to data consumer use cases
- [ ] **Quality Dimensions** have numeric thresholds (not vague targets like "high quality")
- [ ] **Databricks Context** specifies catalog, schema, medallion layer strategy, and compute approach
- [ ] **Success Metrics** are quantified: throughput (rows/day), latency (max age), quality score (%), cost ($/GB)
- [ ] **Risks** are specific with likelihood/impact assessment and mitigation tactics
- [ ] No `[TBD]`, `[TODO]`, or `[NEEDS CLARIFICATION]` markers remain
- [ ] Naming and terminology align with Databricks Unity Catalog and SDP conventions
- [ ] Every P0 requirement has at least one data quality expectation (link to [[data-quality-expectations]])
