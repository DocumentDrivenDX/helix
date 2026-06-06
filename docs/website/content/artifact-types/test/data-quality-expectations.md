---
title: "Data Quality Expectations"
linkTitle: "Data Quality Expectations"
slug: data-quality-expectations
activity: "Test"
artifactRole: "supporting"
weight: 90
generated: true
---

## Purpose

Data Quality Expectations is the **contract layer between PRD (kind: data) (what quality
is needed) and implementation** (how to verify it). Its unique job is to define
measurable quality assertions as executable tests: data should not be released
to consumers until these contracts are satisfied.

Unlike Test Plan (which is the overall test strategy) or Test Suites (which is
test code organization), Data Quality Expectations are the *quality commitments*
written in a machine-readable form before code is written.

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: example.data-quality-expectations.customer-360
  depends_on:
    # Previous: example.data-prd.customer-360 — dropped when data-prd
    # collapsed into prd as kind: data variant (ADR-008).
    - example.data-architecture.customer-360
---

# Data Quality Expectations: Customer-360 Analytics

## Overview

Quality expectations are written as testable predicates that the pipeline must
satisfy before Gold tables are released for analytics queries. They are organized
by layer (Bronze → Silver → Gold) and severity (P0 blocking, P1 alerting, P2
observational). Expectations are executed as part of the orchestrated job, using
Databricks SQL EXPECT clauses and dbt-style tests.

## Bronze Layer Expectations

### P0 Expectations (Block Load)

These expectations must pass before proceeding to Silver. Failure blocks the entire
load and triggers incident escalation.

#### BE-001: Salesforce Accounts Completeness

**Expectation**: Bronze Salesforce accounts row count ≥ 95% of prior day's count

**Rationale**: Detects incomplete exports or API failures before reconciliation

**Test**:
```sql
WITH today AS (
  SELECT COUNT(*) as record_count 
  FROM bronze.salesforce_accounts 
  WHERE date_loaded = CURRENT_DATE()
),
yesterday AS (
  SELECT COUNT(*) as record_count 
  FROM bronze.salesforce_accounts 
  WHERE date_loaded = CURRENT_DATE() - 1
)
SELECT 
  CASE 
    WHEN yesterday.record_count = 0 THEN true  -- first load, no baseline
    WHEN today.record_count / yesterday.record_count >= 0.95 THEN true
    ELSE false
  END as expectation_passed
FROM today, yesterday;
```

**Severity**: P0 (block Silver load)
**Owner**: Data Engineering

#### BE-002: Stripe Invoices Amount Non-negative

**Expectation**: 100% of Stripe invoice records have amount ≥ 0

**Rationale**: Prevents negative revenue transactions from propagating downstream

**Test**:
```sql
SELECT COUNT(*) = 0 as expectation_passed
FROM bronze.stripe_invoices
WHERE amount < 0
  AND date_loaded = CURRENT_DATE();
```

**Severity**: P0 (block Silver load)
**Owner**: Data Engineering

#### BE-003: Stripe Customers Email Required

**Expectation**: 100% of Stripe customer records have non-null email

**Rationale**: Email is the match key for Salesforce-Stripe reconciliation

**Test**:
```sql
SELECT COUNT(*) = 0 as expectation_passed
FROM bronze.stripe_customers
WHERE email IS NULL
  AND date_loaded = CURRENT_DATE();
```

**Severity**: P0 (block Silver load)
**Owner**: Data Engineering

### P1 Expectations (Alert, Allow Backfill)

These expectations trigger alerts but allow the load to continue. Failures require
manual reconciliation before Gold release.

#### BE-101: Salesforce Opportunity Expected Columns

**Expectation**: ≥ 99% of opportunity records have non-null required columns

**Rationale**: Detects API schema changes that could break downstream joins

**Test**:
```sql
SELECT 
  COUNT(CASE WHEN account_id IS NOT NULL AND amount IS NOT NULL 
             AND close_date IS NOT NULL THEN 1 END) / COUNT(*) >= 0.99 as expectation_passed
FROM bronze.salesforce_opportunities
WHERE date_loaded = CURRENT_DATE();
```

**Severity**: P1 (alert, hold Gold release until manual review)
**Owner**: Data Engineering

#### BE-102: Stripe Subscription Status Valid

**Expectation**: 100% of Stripe subscription status values ∈ {active, past_due, canceled, unpaid}

**Rationale**: Prevents invalid enum values in analytics queries

**Test**:
```sql
SELECT COUNT(*) = 0 as expectation_passed
FROM bronze.stripe_subscriptions
WHERE status NOT IN ('active', 'past_due', 'canceled', 'unpaid')
  AND date_loaded = CURRENT_DATE();
```

**Severity**: P1 (alert on invalid status, log for review)
**Owner**: Data Engineering

## Silver Layer Expectations

### P0 Expectations (Block Gold Load)

Silver expectations validate deduplication, reconciliation, and PII handling. Block
Gold aggregation if violated.

#### SE-001: Customer ID Reconciliation Rate

**Expectation**: ≥ 98% of Salesforce accounts matched to Stripe customers via email

**Rationale**: Ensures data quality for downstream joins; < 98% indicates matching logic regression

**Test**:
```sql
WITH matched AS (
  SELECT COUNT(DISTINCT customer_id) as matched_count
  FROM silver.dim_customer
  WHERE reconciliation_confidence >= 0.95
),
total AS (
  SELECT COUNT(DISTINCT customer_id) as total_count
  FROM silver.dim_customer
)
SELECT (matched.matched_count / total.total_count) >= 0.98 as expectation_passed
FROM matched, total;
```

**Severity**: P0 (block Gold; investigate matching logic)
**Owner**: Data Engineering

#### SE-002: Subscription Event Deduplication

**Expectation**: No duplicate (subscription_id, event_date) pairs in Silver fact table

**Rationale**: Prevents double-counting subscription state changes

**Test**:
```sql
SELECT COUNT(*) = 0 as expectation_passed
FROM (
  SELECT subscription_id, event_date, COUNT(*) as cnt
  FROM silver.fct_subscription_event
  GROUP BY subscription_id, event_date
  HAVING cnt > 1
);
```

**Severity**: P0 (block Gold; investigate duplicate source records)
**Owner**: Data Engineering

#### SE-003: Payment Transaction Lineage

**Expectation**: 100% of payment transactions link to a valid subscription and invoice

**Rationale**: Ensures traceability for revenue attribution

**Test**:
```sql
SELECT COUNT(*) = 0 as expectation_passed
FROM silver.fct_payment_transaction t
WHERE t.subscription_id NOT IN (SELECT subscription_id FROM silver.fct_subscription_event)
   OR t.invoice_id IS NULL;
```

**Severity**: P0 (block Gold; orphaned transactions require investigation)
**Owner**: Data Engineering

#### SE-004: PII Hashing Verification

**Expectation**: No raw email addresses or phone numbers in Silver tables (except dim_customer.email_hash)

**Rationale**: PCI/GDPR compliance; prevents accidental PII exposure

**Test**:
```sql
-- Scan dim_customer columns; verify email is hashed, not raw
SELECT COUNT(*) = 0 as expectation_passed
FROM silver.dim_customer
WHERE email NOT LIKE '%@%' OR LENGTH(email) < 64;
-- (hash will be SHA256 hex, ≥ 64 chars; raw emails are shorter)
```

**Severity**: P0 (block Gold; halt pipeline for compliance review)
**Owner**: Data Engineering, Security

### P1 Expectations (Alert, Manual Review)

#### SE-101: Late-Arriving Fact Flag Audit

**Expectation**: ≤ 5% of payment transactions marked late_arrival_flag = true on any day

**Rationale**: Detects Stripe API delays or webhook backpressure

**Test**:
```sql
SELECT 
  (SUM(CASE WHEN late_arrival_flag THEN 1 ELSE 0 END) / COUNT(*)) <= 0.05 as expectation_passed
FROM silver.fct_payment_transaction
WHERE load_date = CURRENT_DATE();
```

**Severity**: P1 (alert; if > 5%, delay Gold refresh and investigate Stripe export)
**Owner**: Data Engineering

#### SE-102: Reconciliation Confidence Score Distribution

**Expectation**: Median reconciliation_confidence ≥ 0.95 for matched customers

**Rationale**: Ensures high-quality Salesforce-Stripe pairings

**Test**:
```sql
SELECT PERCENTILE(reconciliation_confidence, 0.5) >= 0.95 as expectation_passed
FROM silver.dim_customer
WHERE reconciliation_confidence IS NOT NULL;
```

**Severity**: P1 (alert on median < 0.95; review fuzzy-match tuning)
**Owner**: Data Engineering

## Gold Layer Expectations

### P0 Expectations (Block Release to BI)

Gold expectations validate aggregations and business rule compliance.

#### GE-001: Monthly Revenue Fact Completeness

**Expectation**: Every customer with a subscription appears in fct_monthly_revenue for their active months

**Rationale**: Ensures no customers silently disappear from revenue metrics

**Test**:
```sql
WITH expected AS (
  SELECT DISTINCT customer_id, DATE_TRUNC('month', subscription_start_date) as month
  FROM silver.fct_subscription_event
  WHERE subscription_start_date <= CURRENT_DATE()
),
actual AS (
  SELECT DISTINCT customer_id, year_month
  FROM gold.fct_monthly_revenue
)
SELECT COUNT(*) = 0 as expectation_passed
FROM expected e
WHERE NOT EXISTS (
  SELECT 1 FROM actual a 
  WHERE a.customer_id = e.customer_id 
    AND a.year_month = e.month
);
```

**Severity**: P0 (block BI refresh; indicates aggregation logic error)
**Owner**: Data Engineering

#### GE-002: Revenue Amount Non-negative

**Expectation**: 100% of Gold revenue facts have non-negative monthly_revenue_amount

**Rationale**: Prevents negative revenue from reaching dashboards

**Test**:
```sql
SELECT COUNT(*) = 0 as expectation_passed
FROM gold.fct_monthly_revenue
WHERE monthly_revenue_amount < 0;
```

**Severity**: P0 (block BI refresh)
**Owner**: Data Engineering

#### GE-003: Subscription Health State Validity

**Expectation**: 100% of subscription health records have status ∈ {active, past_due, canceled, paused}

**Rationale**: Prevents invalid churn-risk categories from reaching dashboards

**Test**:
```sql
SELECT COUNT(*) = 0 as expectation_passed
FROM gold.fct_subscription_health
WHERE subscription_status NOT IN ('active', 'past_due', 'canceled', 'paused');
```

**Severity**: P0 (block BI refresh)
**Owner**: Data Engineering

### P1 Expectations (Alert, Review Before Publish)

#### GE-101: Revenue Year-over-Year Change Threshold

**Expectation**: Monthly revenue variance ≤ 25% month-over-month (unless new subscription)

**Rationale**: Detects anomalous aggregation or missing data

**Test**:
```sql
WITH month_over_month AS (
  SELECT 
    customer_id,
    year_month,
    monthly_revenue_amount,
    LAG(monthly_revenue_amount) OVER (PARTITION BY customer_id ORDER BY year_month) as prior_month_amount,
    ABS((monthly_revenue_amount - LAG(monthly_revenue_amount) OVER (PARTITION BY customer_id ORDER BY year_month)) 
      / LAG(monthly_revenue_amount) OVER (PARTITION BY customer_id ORDER BY year_month)) as pct_change
  FROM gold.fct_monthly_revenue
  WHERE is_new_subscription = false  -- exclude new subscriptions
)
SELECT (COUNT(CASE WHEN pct_change <= 0.25 THEN 1 END) / COUNT(*)) > 0.95 as expectation_passed
FROM month_over_month
WHERE prior_month_amount > 0;
```

**Severity**: P1 (alert; review changes in Silver aggregation before publishing Gold)
**Owner**: Data Engineering, Sales Analytics

#### GE-102: Unpaid Invoice Aging

**Expectation**: All unpaid invoices in fct_subscription_health ≤ 90 days old

**Rationale**: Flags invoices that may be stuck in Stripe (data quality issue) or genuinely past-due (business issue)

**Test**:
```sql
SELECT COUNT(*) = 0 as expectation_passed
FROM gold.fct_subscription_health
WHERE unpaid_invoice_count > 0 
  AND days_since_last_unpaid_invoice > 90;
```

**Severity**: P1 (alert; prioritize collection or investigate stuck Stripe records)
**Owner**: Data Engineering, Finance

## Test Execution

### Orchestration Integration

Expectations run as part of the daily load workflow:

```
Bronze Load → [Validate BE-001 to BE-102]
  ↓ (if all P0 pass; P1s logged)
Silver Transform → [Validate SE-001 to SE-102]
  ↓ (if all P0 pass; P1s logged)
Gold Aggregation → [Validate GE-001 to GE-102]
  ↓ (if all P0 pass; P1s logged)
Release to BI (if GE-001, GE-002, GE-003 pass)
```

### Reporting

- **Blocking failures (P0)**: Halt pipeline; send incident alert to `#data-platform-incidents`
- **Warnings (P1)**: Log to `gold.data_quality_log`; send summary email to analytics team
- **Dashboard**: Daily expectation summary in `gold.data_quality_dashboard` showing pass/fail counts per layer

## Maintenance and Tuning

| Expectation | Review Cadence | Trigger for Tuning |
|-------------|----------------|--------------------|
| BE-001, SE-001, GE-001 | Monthly | Failure rate > 5% in past 30 days |
| SE-101, GE-102 | Quarterly | Threshold consistently exceeded but no incidents |
| SE-102 | As needed | Reconciliation logic changes |
| GE-101 | Quarterly | New customer segment added to pricing model |

---

**Approved by**: Data Engineering Lead | **Effective Date**: 2026-05-20
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Test</strong></a> — Define how we know it works. Plans, suites, and procedures that bind specs to implementation.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/03-test/data-quality-expectations.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="../../../artifact-types/test/test-plan/">Test Plan</a><br><a href="../../../artifact-types/test/story-test-plan/">Story Test Plan</a><br><a href="../../../artifact-types/build/implementation-plan/">Implementation Plan</a></td></tr>
<tr><th>Referenced by</th><td><a href="../../../artifact-types/build/implementation-plan/">Implementation Plan</a><br><a href="../../../artifact-types/deploy/runbook/">Runbook</a><br><a href="../../../artifact-types/deploy/monitoring-setup/">Monitoring Setup</a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Data Quality Expectations Generation Prompt&#10;&#10;Define the quality contracts that the data pipeline must satisfy, written as&#10;testable predicates on data shape, completeness, accuracy, and freshness.&#10;&#10;## Purpose&#10;&#10;Data Quality Expectations is the **contract layer between PRD (kind: data) (what quality&#10;is needed) and implementation** (how to verify it). Its unique job is to define&#10;measurable quality assertions as executable tests: data should not be released&#10;to consumers until these contracts are satisfied.&#10;&#10;Unlike Test Plan (which is the overall test strategy) or Test Suites (which is&#10;test code organization), Data Quality Expectations are the *quality commitments*&#10;written in a machine-readable form before code is written.&#10;&#10;## Reference Anchors&#10;&#10;Use these local resource summaries as grounding:&#10;&#10;- `docs/resources/databricks-sdp-expect.md` grounds Databricks Semantic Data&#10;  Platform `EXPECT ... ON VIOLATION ...` syntax for inline quality assertions&#10;  and contract-driven pipeline composition.&#10;- `docs/resources/dbt-tests.md` grounds dbt&#x27;s assertion language (tests,&#10;  contracts, and constraints) for data quality as code.&#10;- `docs/resources/great-expectations.md` grounds Great Expectations vocabulary,&#10;  expectations, suites, and checkpoints for flexible, reusable quality checks.&#10;&#10;## Focus&#10;&#10;- For each requirement in the PRD (kind: data), write at least one testable expectation.&#10;- Group expectations by layer (Bronze, Silver, Gold) and validate at the&#10;  appropriate layer.&#10;- Use SDP `EXPECT` syntax for Databricks Streaming Tables, dbt tests for&#10;  transformed tables, and Great Expectations for custom or complex checks.&#10;- Name what happens when expectations fail: quarantine the data, alert,&#10;  rollback, or skip dependent pipelines.&#10;- Document freshness SLAs and how they are monitored (timestamp columns,&#10;  row-count trends, lag detection).&#10;&#10;## Role Boundary&#10;&#10;Data Quality Expectations are not implementation code, not test infrastructure,&#10;and not the data model. They are the *contract* that implementation must satisfy.&#10;&#10;**Databricks Platform Substitution:** If you are adopting this on another data&#10;platform, substitute as follows:&#10;&#10;| Databricks Concept | Snowflake Equivalent | BigQuery Equivalent | On-Prem / Other |&#10;|---|---|---|---|&#10;| SDP `EXPECT ... ON VIOLATION ...` | Data Quality Checks + Task error handling | BigQuery Data Quality API + assertions | dbt tests, Great Expectations, SQL assertions |&#10;| Streaming Tables with built-in `EXPECT` | Stream-triggered materialized views + constraints | Dataflow with Beam assertions | Flink-based pipelines with custom state |&#10;| SDP Genie for test generation | dbt auto-generate tests from table samples | BigQuery Data Catalog insights | dbt, custom metadata scanning |&#10;| Databricks Lakeview dashboards for monitoring | Snowflake Dashboards | Looker, Data Studio | Grafana, custom dashboards |&#10;&#10;## Completion Criteria&#10;&#10;- Every P0 requirement from PRD (kind: data) has at least one corresponding expectation.&#10;- Expectations are grouped by layer (Bronze input validation, Silver&#10;  transformation contracts, Gold business rule verification).&#10;- Expectations are written in the platform&#x27;s native syntax (SDP `EXPECT`,&#10;  dbt test, Great Expectations).&#10;- Each expectation names the failure mode: what happens if the check fails&#10;  (quarantine, alert, skip downstream, rollback).&#10;- Freshness SLAs are explicit: expected refresh interval and how lag is&#10;  detected.&#10;- Quality dashboards or monitoring strategy is sketched (where operators watch,&#10;  what metrics matter, alert thresholds).&#10;- Expectations are prioritized (which checks must pass for release, which are&#10;  advisory).</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: data-quality-expectations&#10;---&#10;&#10;# Data Quality Expectations&#10;&#10;## Overview and Scope&#10;&#10;[Define the data product being tested, the medallion layers covered (Bronze, Silver, Gold), and the quality dimensions in scope (completeness, timeliness, accuracy, consistency, uniqueness). Reference the [[prd]] (kind: data) for quality requirements and [[data-architecture]] for the layer definitions. This document translates those requirements into executable EXPECT clauses.]&#10;&#10;### Quality Dimensions&#10;&#10;| Dimension | Definition | P0 Threshold | P1 Threshold | Enforcement |&#10;|-----------|-----------|--------------|--------------|------------|&#10;| Completeness | % of non-null values in key columns | ≥99% | ≥95% | Reject if P0 fails |&#10;| Timeliness | Max age of data (now - max timestamp) | ≤1 hour | ≤4 hours | Alert if P0, skip if P1 |&#10;| Accuracy | % of values matching source or business rules | ≥98% | ≥95% | Manual audit + alert |&#10;| Uniqueness | No duplicate rows on primary key | 0 duplicates | ≤0.1% | Reject if P0 fails |&#10;| Consistency | Cross-layer contracts (sums reconcile, cardinality stable) | ±0.01% | ±0.1% | Reject if P0 fails |&#10;&#10;### Test Framework and Tooling&#10;&#10;- **Framework**: [SDP EXPECT clauses / dbt tests / Great Expectations / SQL constraints]&#10;- **Execution**: [Databricks Workflows, dbt Cloud, scheduled notebooks]&#10;- **Alerting**: [Slack + email to data-eng on-call]&#10;- **Remediation**: [Manual data fix, pipeline rollback, quarantine until reviewed]&#10;&#10;### Testing Philosophy&#10;&#10;[Exhaustive testing on all rows (default) or sampling? Document the rationale. Sampling is OK for high-volume tables and computationally expensive checks, but must include a confidence interval and margin of error.]&#10;&#10;---&#10;&#10;## Bronze Layer Expectations&#10;&#10;### Raw Data Validation&#10;&#10;Bronze tables land source data without transformation. Expectations here catch ingestion failures and schema drift early.&#10;&#10;### Schema and Structure&#10;&#10;```sql&#10;-- Customers Bronze: all source columns present, no truncation&#10;EXPECT TABLE raw_customers (&#10;  customer_id NOT NULL,&#10;  email NOT NULL,&#10;  phone,&#10;  created_at TIMESTAMP NOT NULL,&#10;  updated_at TIMESTAMP NOT NULL,&#10;  _source_system STRING NOT NULL,&#10;  _ingest_timestamp TIMESTAMP NOT NULL&#10;);&#10;&#10;-- Data types match source&#10;EXPECT TABLE raw_customers (&#10;  CHECK (customer_id IS INT),&#10;  CHECK (email IS STRING),&#10;  CHECK (created_at IS TIMESTAMP)&#10;);&#10;```&#10;&#10;**Severity**: Blocking — fail ingestion if schema mismatch.&#10;**Action on Failure**: Stop ingest pipeline; alert data-eng; manual review before retry.&#10;&#10;### Completeness (Null Check)&#10;&#10;```sql&#10;-- Critical columns must never be null&#10;EXPECT TABLE raw_customers&#10;  CHECK (customer_id IS NOT NULL)&#10;  CHECK (email IS NOT NULL);&#10;&#10;-- If any of these are null, it&#x27;s a quality failure (not a schema error)&#10;EXPECT TABLE raw_customers (&#10;  completeness_check AS (&#10;    SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) &#10;      / COUNT(*) &lt; 0.01  -- P0: &lt;1% nulls on customer_id&#10;  )&#10;);&#10;```&#10;&#10;**Severity**: Blocking (P0) — reject records with null customer_id.&#10;**Threshold**: &lt;1% nulls on critical columns.&#10;**Action on Failure**: Quarantine batch; alert; wait for manual approval.&#10;&#10;### Freshness (Timeliness)&#10;&#10;```sql&#10;-- Ingestion must complete within 15 minutes of source commit&#10;EXPECT TABLE raw_customers (&#10;  freshness_check AS (&#10;    MAX(_ingest_timestamp) &gt;= CURRENT_TIMESTAMP() - INTERVAL 15 MINUTES&#10;  )&#10;);&#10;```&#10;&#10;**Severity**: Warning (P1) — alert if &gt;15 min old; move to Silver anyway but flag.&#10;**Action on Failure**: Alert to on-call; do not advance to Silver if &gt;30 min.&#10;&#10;### No Truncation&#10;&#10;```sql&#10;-- Source columns must be preserved at full width (no truncation to shorter types)&#10;EXPECT TABLE raw_customers (&#10;  CHECK (LENGTH(email) &lt;= 255),  -- assume source is VARCHAR(255)&#10;  CHECK (LENGTH(phone) &lt;= 20)&#10;);&#10;```&#10;&#10;**Severity**: Warning — audit only.&#10;**Action on Failure**: Log; manual spot-check.&#10;&#10;---&#10;&#10;## Silver Layer Expectations&#10;&#10;### Validation and Transformation&#10;&#10;Silver tables apply business logic: deduplication, null handling, type coercion, referential integrity. Expectations here enforce &quot;clean&quot; data for consumption.&#10;&#10;### Uniqueness (Deduplication)&#10;&#10;```sql&#10;-- Each customer appears exactly once (deduplicated by latest timestamp)&#10;EXPECT TABLE customers_validated (&#10;  PRIMARY KEY (customer_id),&#10;  UNIQUE (customer_id)&#10;);&#10;&#10;EXPECT TABLE customers_validated (&#10;  uniqueness_check AS (&#10;    COUNT(*) = COUNT(DISTINCT customer_id)&#10;  )&#10;);&#10;```&#10;&#10;**Severity**: Blocking — reject if duplicates.&#10;**Threshold**: 0 duplicates on PK.&#10;**Action on Failure**: Fail pipeline; manual dedup review; rerun.&#10;&#10;### Completeness (Post-Transform)&#10;&#10;```sql&#10;-- After validation, critical columns must be NOT NULL&#10;EXPECT TABLE customers_validated (&#10;  CHECK (customer_id IS NOT NULL),&#10;  CHECK (email IS NOT NULL)&#10;);&#10;&#10;EXPECT TABLE customers_validated (&#10;  CHECK (&#10;    (SUM(CASE WHEN email IS NULL THEN 1 ELSE 0 END) / COUNT(*)) &lt; 0.01&#10;  )  -- &lt;1% nulls on email&#10;);&#10;```&#10;&#10;**Severity**: Blocking (P0).&#10;**Threshold**: 0% nulls on customer_id; &lt;1% nulls on email.&#10;**Action on Failure**: Reject batch; alert.&#10;&#10;### Data Quality and Normalization&#10;&#10;```sql&#10;-- Email addresses are normalized and valid&#10;EXPECT TABLE customers_validated (&#10;  CHECK (&#10;    email LIKE &#x27;%@%.%&#x27; AND email NOT LIKE &#x27; %&#x27; AND email NOT LIKE &#x27;% &#x27;&#10;  )&#10;);&#10;&#10;-- Phone numbers (if present) are valid format&#10;EXPECT TABLE customers_validated (&#10;  CHECK (&#10;    phone IS NULL OR phone REGEXP &#x27;^[0-9\-\+\(\) ]+$&#x27;&#10;  )&#10;);&#10;&#10;-- Created_at is before or equal to updated_at&#10;EXPECT TABLE customers_validated (&#10;  CHECK (created_at &lt;= updated_at)&#10;);&#10;```&#10;&#10;**Severity**: Warning (P1) — log invalid records but don&#x27;t block.&#10;**Action on Failure**: Alert + audit; filter invalid records for Gold.&#10;&#10;### Referential Integrity&#10;&#10;```sql&#10;-- If this table is child of a parent, all foreign keys must exist&#10;-- (e.g., customer_segment.customer_id must exist in customers_validated)&#10;EXPECT TABLE customers_validated (&#10;  referential_integrity_check AS (&#10;    NOT EXISTS (&#10;      SELECT 1 FROM customer_segment cs&#10;      WHERE NOT EXISTS (&#10;        SELECT 1 FROM customers_validated cv&#10;        WHERE cv.customer_id = cs.customer_id&#10;      )&#10;    )&#10;  )&#10;);&#10;```&#10;&#10;**Severity**: Blocking (P0) for critical relationships.&#10;**Action on Failure**: Reject segment batch; alert; manual review.&#10;&#10;### Timeliness (Staleness)&#10;&#10;```sql&#10;-- Silver must be refreshed at least daily (no more than 24 hours stale)&#10;EXPECT TABLE customers_validated (&#10;  freshness_check AS (&#10;    MAX(_modified_at) &gt;= CURRENT_TIMESTAMP() - INTERVAL 1 DAY&#10;  )&#10;);&#10;```&#10;&#10;**Severity**: Warning (P1).&#10;**SLA**: Alert if &gt;24 hours old.&#10;**Action on Failure**: Alert to on-call; check if pipeline is hung.&#10;&#10;### Row Count Reconciliation&#10;&#10;```sql&#10;-- Silver row count must be close to Bronze (within dedup margin)&#10;-- Account for legitimate filtering (e.g., test records, deleted accounts)&#10;EXPECT TABLE customers_validated (&#10;  reconciliation_check AS (&#10;    (SELECT COUNT(*) FROM customers_validated)&#10;    BETWEEN&#10;      (SELECT COUNT(*) FROM raw_customers) * 0.90  -- allow 10% loss for dedup&#10;      AND (SELECT COUNT(*) FROM raw_customers) * 1.01  -- allow 1% gain for corrections&#10;  )&#10;);&#10;```&#10;&#10;**Severity**: Blocking (P0).&#10;**Tolerance**: ±10% (dedup and corrections).&#10;**Action on Failure**: Reject; alert; manual audit.&#10;&#10;---&#10;&#10;## Gold Layer Expectations&#10;&#10;### Business-Ready Consumption&#10;&#10;Gold tables are optimized for consumer queries and serve as the source of truth for analytics, ML, and BI. Expectations here enforce freshness, consistency, and accuracy for downstream consumers.&#10;&#10;### Completeness and Current State&#10;&#10;```sql&#10;-- Customer 360 Gold table is current within SLA&#10;EXPECT TABLE customer_360 (&#10;  freshness_check AS (&#10;    MAX(_modified_at) &gt;= CURRENT_TIMESTAMP() - INTERVAL 1 HOUR&#10;  )&#10;);&#10;&#10;-- All customer_ids in customer_360 exist in Silver (no orphans)&#10;EXPECT TABLE customer_360 (&#10;  orphan_check AS (&#10;    NOT EXISTS (&#10;      SELECT 1 FROM customer_360 c360&#10;      WHERE NOT EXISTS (&#10;        SELECT 1 FROM customers_validated cv&#10;        WHERE cv.customer_id = c360.customer_id&#10;      )&#10;    )&#10;  )&#10;);&#10;```&#10;&#10;**Severity**: Blocking (P0).&#10;**SLA**: &lt;1 hour stale.&#10;**Action on Failure**: Reject; roll back to prior snapshot; alert on-call.&#10;&#10;### Aggregate Accuracy and Reconciliation&#10;&#10;```sql&#10;-- Daily sales summary must reconcile with Silver within $0.01 per order&#10;EXPECT TABLE daily_sales_summary (&#10;  aggregate_reconciliation AS (&#10;    SELECT SUM(amount) FROM daily_sales_summary&#10;    IS WITHIN 0.01 OF&#10;    SELECT SUM(order_amount) FROM orders_silver&#10;  )&#10;);&#10;&#10;-- Row counts match between daily and historical gold&#10;EXPECT TABLE daily_sales_summary (&#10;  cardinality_check AS (&#10;    COUNT(DISTINCT DATE(order_date)) = COUNT(DISTINCT DATE(order_date)) OVER (PARTITION BY MONTH(order_date))&#10;  )&#10;);&#10;```&#10;&#10;**Severity**: Blocking (P0) — finances depend on this.&#10;**Tolerance**: ±$0.01 per order (handle floating-point rounding).&#10;**Action on Failure**: Reject; re-aggregate; alert finance team.&#10;&#10;### Consumer Guarantees (SLA)&#10;&#10;```sql&#10;-- Query performance: p95 query latency must be &lt;5 seconds for customer_360&#10;-- (Monitored via Databricks query history, not an EXPECT clause, but documented here)&#10;&#10;-- Availability: customer_360 must be queryable during business hours (8am-8pm UTC)&#10;EXPECT TABLE customer_360 (&#10;  availability_check AS (&#10;    TABLE customer_360 IS NOT EMPTY  -- simple check; better: monitor cluster uptime&#10;  )&#10;);&#10;```&#10;&#10;**Severity**: Warning (P1) — operational SLA.&#10;**Action on Failure**: Page on-call; investigate cluster/query issues.&#10;&#10;### Consistency Across Related Gold Tables&#10;&#10;```sql&#10;-- If customer_360 and daily_sales_summary both exist:&#10;-- Sum of amounts per customer in daily_sales_summary &#10;-- should match lifetime_revenue in customer_360&#10;EXPECT (&#10;  SELECT SUM(amount) FROM daily_sales_summary WHERE customer_id = X&#10;  EQUALS&#10;  SELECT lifetime_revenue FROM customer_360 WHERE customer_id = X&#10;);&#10;```&#10;&#10;**Severity**: Blocking (P0) for critical aggregates.&#10;**Action on Failure**: Reject; investigate transformation logic; recompute.&#10;&#10;### Business Logic Validation&#10;&#10;```sql&#10;-- Revenue should never be negative&#10;EXPECT TABLE daily_sales_summary (&#10;  CHECK (amount &gt;= 0)&#10;);&#10;&#10;-- Order dates should be within reasonable bounds (not in future, not before company founded)&#10;EXPECT TABLE daily_sales_summary (&#10;  CHECK (order_date BETWEEN &#x27;2015-01-01&#x27; AND CURRENT_DATE)&#10;);&#10;```&#10;&#10;**Severity**: Blocking (P0).&#10;**Action on Failure**: Reject; alert; audit source data.&#10;&#10;---&#10;&#10;## Cross-Layer Contracts&#10;&#10;### Data Lineage and Consistency&#10;&#10;Expectations that span multiple layers ensure data doesn&#x27;t transform incorrectly as it flows Bronze → Silver → Gold.&#10;&#10;### Layer-to-Layer Validation&#10;&#10;| Contract | Assertion | If Violated | Severity |&#10;|----------|-----------|----------|----------|&#10;| Bronze → Silver row count | Silver rows ≥ 90% of Bronze rows (allow dedup) | Investigate dedup logic | Blocking |&#10;| Silver → Gold row count | Gold unique customers = Silver unique customers | Reject Gold; re-aggregate | Blocking |&#10;| Bronze → Gold data types | Gold numbers can be summed without loss of precision | Audit source → Gold transformation | Blocking |&#10;&#10;### Cross-Table Contracts (Fact-Dimension)&#10;&#10;```sql&#10;-- All orders.customer_id must exist in customer_360&#10;EXPECT TABLE orders_gold (&#10;  fk_customer_check AS (&#10;    NOT EXISTS (&#10;      SELECT 1 FROM orders_gold og&#10;      WHERE NOT EXISTS (&#10;        SELECT 1 FROM customer_360 c360&#10;        WHERE c360.customer_id = og.customer_id&#10;      )&#10;    )&#10;  )&#10;);&#10;&#10;-- Sum of order amounts per customer must match customer lifetime_revenue&#10;EXPECT (&#10;  SELECT SUM(amount) FROM orders_gold GROUP BY customer_id&#10;  EQUALS&#10;  SELECT lifetime_revenue FROM customer_360&#10;);&#10;```&#10;&#10;**Severity**: Blocking (P0).&#10;**Action on Failure**: Quarantine orders; alert; manual reconciliation.&#10;&#10;---&#10;&#10;## Failure Handling and SLA&#10;&#10;### Alert and Escalation Policy&#10;&#10;| Expectation | Severity | Detection SLA | Escalation | Action |&#10;|-----------|----------|--------------|-----------|--------|&#10;| [Bronze completeness] | Blocking | &lt;5 min | Page on-call | Pause ingest; investigate |&#10;| [Silver uniqueness] | Blocking | &lt;10 min | Slack + email | Stop pipeline; manual dedup review |&#10;| [Gold freshness] | Blocking | &lt;15 min | Page + email | Investigate scheduler; rerun |&#10;| [Aggregate reconciliation] | Blocking | &lt;30 min | Finance + on-call | Recompute; audit |&#10;| [Query latency] | Warning | &lt;1 min (logged) | Email on-call | Investigate cluster; optimize queries |&#10;&#10;### Failure Recovery&#10;&#10;**On Blocking Failure**:&#10;1. Stop the pipeline (no downstream advancement)&#10;2. Alert on-call data engineer immediately&#10;3. Log detailed failure context (which rows failed, why)&#10;4. Quarantine the batch in a `_quarantine_` location for manual review&#10;5. Do not retry automatically; require manual approval + fix before re-processing&#10;&#10;**On Warning Failure**:&#10;1. Log the failure&#10;2. Send alert to Slack (not pager)&#10;3. Continue pipeline; flag data as low-confidence&#10;4. Schedule manual audit within 24 hours&#10;&#10;### SLA Target&#10;&#10;- **Detection**: &lt;5 min for Bronze, &lt;15 min for Silver/Gold&#10;- **Mean Time to Recovery (MTTR)**: &lt;30 min for blocking failures&#10;- **False Positive Rate**: &lt;1% (tune thresholds to reduce alert fatigue)&#10;&#10;---&#10;&#10;## Review Checklist&#10;&#10;Use this checklist during review to validate that the data quality expectations are complete and testable:&#10;&#10;- [ ] **Overview and Scope** clearly states which medallion layers and quality dimensions are covered&#10;- [ ] **Bronze Layer Expectations** validate schema, completeness, freshness, and ingestion integrity&#10;- [ ] **Silver Layer Expectations** enforce deduplication, nullability, normalization, and referential integrity&#10;- [ ] **Gold Layer Expectations** guarantee freshness, consistency, and accuracy for consumer queries&#10;- [ ] **Expectations are written in executable form**: SDP EXPECT, dbt test, or SQL constraint (not prose)&#10;- [ ] **Each expectation traces back** to a quality requirement in [[prd]] (kind: data) (reference by name)&#10;- [ ] **Failure modes are explicit**: What happens when an expectation fails (reject, alert, quarantine)?&#10;- [ ] **SLA per layer** is documented: freshness target, detection time, recovery time&#10;- [ ] **Sampling vs exhaustive** is clear: All rows tested, or sample with confidence interval documented?&#10;- [ ] **Cross-layer data contracts** ensure consistency across layers (sums reconcile, cardinality stable, no orphans)&#10;- [ ] **Alert routing and escalation policy** is defined: Who gets paged? When does on-call respond?&#10;- [ ] **No `[TBD]`, `[TODO]`, or `[NEEDS CLARIFICATION]` markers remain**&#10;- [ ] **At least one expectation per quality dimension** (completeness, timeliness, accuracy, consistency, uniqueness)&#10;- [ ] **P0 requirements have multiple expectations** (layered checks: Bronze schema, Silver uniqueness, Gold freshness)&#10;- [ ] **Terminology aligns with Databricks SDP** (EXPECT clauses, UC, medallion layers, VIOLATION rules)</code></pre></details></td></tr>
</tbody>
</table>
