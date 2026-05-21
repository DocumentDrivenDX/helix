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

Data Quality Expectations is the **contract layer between Data PRD (what quality
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
    - example.data-prd.customer-360
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
<tr><th>Activity</th><td><a href="/reference/glossary/activities/"><strong>Test</strong></a> — Define how we know it works. Plans, suites, and procedures that bind specs to implementation.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/03-test/data-quality-expectations.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="/artifact-types/test/test-plan/">Test Plan</a><br><a href="/artifact-types/test/story-test-plan/">Story Test Plan</a><br><a href="/artifact-types/build/implementation-plan/">Implementation Plan</a></td></tr>
<tr><th>Referenced by</th><td><a href="/artifact-types/build/implementation-plan/">Implementation Plan</a><br><a href="/artifact-types/deploy/runbook/">Runbook</a><br><a href="/artifact-types/deploy/monitoring-setup/">Monitoring Setup</a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Data Quality Expectations Generation Prompt

Define the quality contracts that the data pipeline must satisfy, written as
testable predicates on data shape, completeness, accuracy, and freshness.

## Purpose

Data Quality Expectations is the **contract layer between Data PRD (what quality
is needed) and implementation** (how to verify it). Its unique job is to define
measurable quality assertions as executable tests: data should not be released
to consumers until these contracts are satisfied.

Unlike Test Plan (which is the overall test strategy) or Test Suites (which is
test code organization), Data Quality Expectations are the *quality commitments*
written in a machine-readable form before code is written.

## Reference Anchors

Use these local resource summaries as grounding:

- `docs/resources/databricks-sdp-expect.md` grounds Databricks Semantic Data
  Platform `EXPECT ... ON VIOLATION ...` syntax for inline quality assertions
  and contract-driven pipeline composition.
- `docs/resources/dbt-tests.md` grounds dbt&#x27;s assertion language (tests,
  contracts, and constraints) for data quality as code.
- `docs/resources/great-expectations.md` grounds Great Expectations vocabulary,
  expectations, suites, and checkpoints for flexible, reusable quality checks.

## Focus

- For each requirement in the Data PRD, write at least one testable expectation.
- Group expectations by layer (Bronze, Silver, Gold) and validate at the
  appropriate layer.
- Use SDP `EXPECT` syntax for Databricks Streaming Tables, dbt tests for
  transformed tables, and Great Expectations for custom or complex checks.
- Name what happens when expectations fail: quarantine the data, alert,
  rollback, or skip dependent pipelines.
- Document freshness SLAs and how they are monitored (timestamp columns,
  row-count trends, lag detection).

## Role Boundary

Data Quality Expectations are not implementation code, not test infrastructure,
and not the data model. They are the *contract* that implementation must satisfy.

**Databricks Platform Substitution:** If you are adopting this on another data
platform, substitute as follows:

| Databricks Concept | Snowflake Equivalent | BigQuery Equivalent | On-Prem / Other |
|---|---|---|---|
| SDP `EXPECT ... ON VIOLATION ...` | Data Quality Checks + Task error handling | BigQuery Data Quality API + assertions | dbt tests, Great Expectations, SQL assertions |
| Streaming Tables with built-in `EXPECT` | Stream-triggered materialized views + constraints | Dataflow with Beam assertions | Flink-based pipelines with custom state |
| SDP Genie for test generation | dbt auto-generate tests from table samples | BigQuery Data Catalog insights | dbt, custom metadata scanning |
| Databricks Lakeview dashboards for monitoring | Snowflake Dashboards | Looker, Data Studio | Grafana, custom dashboards |

## Completion Criteria

- Every P0 requirement from Data PRD has at least one corresponding expectation.
- Expectations are grouped by layer (Bronze input validation, Silver
  transformation contracts, Gold business rule verification).
- Expectations are written in the platform&#x27;s native syntax (SDP `EXPECT`,
  dbt test, Great Expectations).
- Each expectation names the failure mode: what happens if the check fails
  (quarantine, alert, skip downstream, rollback).
- Freshness SLAs are explicit: expected refresh interval and how lag is
  detected.
- Quality dashboards or monitoring strategy is sketched (where operators watch,
  what metrics matter, alert thresholds).
- Expectations are prioritized (which checks must pass for release, which are
  advisory).</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---
ddx:
  id: data-quality-expectations
---

# Data Quality Expectations

## Overview and Scope

[Define the data product being tested, the medallion layers covered (Bronze, Silver, Gold), and the quality dimensions in scope (completeness, timeliness, accuracy, consistency, uniqueness). Reference the [[data-prd]] for quality requirements and [[data-architecture]] for the layer definitions. This document translates those requirements into executable EXPECT clauses.]

### Quality Dimensions

| Dimension | Definition | P0 Threshold | P1 Threshold | Enforcement |
|-----------|-----------|--------------|--------------|------------|
| Completeness | % of non-null values in key columns | ≥99% | ≥95% | Reject if P0 fails |
| Timeliness | Max age of data (now - max timestamp) | ≤1 hour | ≤4 hours | Alert if P0, skip if P1 |
| Accuracy | % of values matching source or business rules | ≥98% | ≥95% | Manual audit + alert |
| Uniqueness | No duplicate rows on primary key | 0 duplicates | ≤0.1% | Reject if P0 fails |
| Consistency | Cross-layer contracts (sums reconcile, cardinality stable) | ±0.01% | ±0.1% | Reject if P0 fails |

### Test Framework and Tooling

- **Framework**: [SDP EXPECT clauses / dbt tests / Great Expectations / SQL constraints]
- **Execution**: [Databricks Workflows, dbt Cloud, scheduled notebooks]
- **Alerting**: [Slack + email to data-eng on-call]
- **Remediation**: [Manual data fix, pipeline rollback, quarantine until reviewed]

### Testing Philosophy

[Exhaustive testing on all rows (default) or sampling? Document the rationale. Sampling is OK for high-volume tables and computationally expensive checks, but must include a confidence interval and margin of error.]

---

## Bronze Layer Expectations

### Raw Data Validation

Bronze tables land source data without transformation. Expectations here catch ingestion failures and schema drift early.

### Schema and Structure

```sql
-- Customers Bronze: all source columns present, no truncation
EXPECT TABLE raw_customers (
  customer_id NOT NULL,
  email NOT NULL,
  phone,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL,
  _source_system STRING NOT NULL,
  _ingest_timestamp TIMESTAMP NOT NULL
);

-- Data types match source
EXPECT TABLE raw_customers (
  CHECK (customer_id IS INT),
  CHECK (email IS STRING),
  CHECK (created_at IS TIMESTAMP)
);
```

**Severity**: Blocking — fail ingestion if schema mismatch.
**Action on Failure**: Stop ingest pipeline; alert data-eng; manual review before retry.

### Completeness (Null Check)

```sql
-- Critical columns must never be null
EXPECT TABLE raw_customers
  CHECK (customer_id IS NOT NULL)
  CHECK (email IS NOT NULL);

-- If any of these are null, it&#x27;s a quality failure (not a schema error)
EXPECT TABLE raw_customers (
  completeness_check AS (
    SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) 
      / COUNT(*) &lt; 0.01  -- P0: &lt;1% nulls on customer_id
  )
);
```

**Severity**: Blocking (P0) — reject records with null customer_id.
**Threshold**: &lt;1% nulls on critical columns.
**Action on Failure**: Quarantine batch; alert; wait for manual approval.

### Freshness (Timeliness)

```sql
-- Ingestion must complete within 15 minutes of source commit
EXPECT TABLE raw_customers (
  freshness_check AS (
    MAX(_ingest_timestamp) &gt;= CURRENT_TIMESTAMP() - INTERVAL 15 MINUTES
  )
);
```

**Severity**: Warning (P1) — alert if &gt;15 min old; move to Silver anyway but flag.
**Action on Failure**: Alert to on-call; do not advance to Silver if &gt;30 min.

### No Truncation

```sql
-- Source columns must be preserved at full width (no truncation to shorter types)
EXPECT TABLE raw_customers (
  CHECK (LENGTH(email) &lt;= 255),  -- assume source is VARCHAR(255)
  CHECK (LENGTH(phone) &lt;= 20)
);
```

**Severity**: Warning — audit only.
**Action on Failure**: Log; manual spot-check.

---

## Silver Layer Expectations

### Validation and Transformation

Silver tables apply business logic: deduplication, null handling, type coercion, referential integrity. Expectations here enforce &quot;clean&quot; data for consumption.

### Uniqueness (Deduplication)

```sql
-- Each customer appears exactly once (deduplicated by latest timestamp)
EXPECT TABLE customers_validated (
  PRIMARY KEY (customer_id),
  UNIQUE (customer_id)
);

EXPECT TABLE customers_validated (
  uniqueness_check AS (
    COUNT(*) = COUNT(DISTINCT customer_id)
  )
);
```

**Severity**: Blocking — reject if duplicates.
**Threshold**: 0 duplicates on PK.
**Action on Failure**: Fail pipeline; manual dedup review; rerun.

### Completeness (Post-Transform)

```sql
-- After validation, critical columns must be NOT NULL
EXPECT TABLE customers_validated (
  CHECK (customer_id IS NOT NULL),
  CHECK (email IS NOT NULL)
);

EXPECT TABLE customers_validated (
  CHECK (
    (SUM(CASE WHEN email IS NULL THEN 1 ELSE 0 END) / COUNT(*)) &lt; 0.01
  )  -- &lt;1% nulls on email
);
```

**Severity**: Blocking (P0).
**Threshold**: 0% nulls on customer_id; &lt;1% nulls on email.
**Action on Failure**: Reject batch; alert.

### Data Quality and Normalization

```sql
-- Email addresses are normalized and valid
EXPECT TABLE customers_validated (
  CHECK (
    email LIKE &#x27;%@%.%&#x27; AND email NOT LIKE &#x27; %&#x27; AND email NOT LIKE &#x27;% &#x27;
  )
);

-- Phone numbers (if present) are valid format
EXPECT TABLE customers_validated (
  CHECK (
    phone IS NULL OR phone REGEXP &#x27;^[0-9\-\+\(\) ]+$&#x27;
  )
);

-- Created_at is before or equal to updated_at
EXPECT TABLE customers_validated (
  CHECK (created_at &lt;= updated_at)
);
```

**Severity**: Warning (P1) — log invalid records but don&#x27;t block.
**Action on Failure**: Alert + audit; filter invalid records for Gold.

### Referential Integrity

```sql
-- If this table is child of a parent, all foreign keys must exist
-- (e.g., customer_segment.customer_id must exist in customers_validated)
EXPECT TABLE customers_validated (
  referential_integrity_check AS (
    NOT EXISTS (
      SELECT 1 FROM customer_segment cs
      WHERE NOT EXISTS (
        SELECT 1 FROM customers_validated cv
        WHERE cv.customer_id = cs.customer_id
      )
    )
  )
);
```

**Severity**: Blocking (P0) for critical relationships.
**Action on Failure**: Reject segment batch; alert; manual review.

### Timeliness (Staleness)

```sql
-- Silver must be refreshed at least daily (no more than 24 hours stale)
EXPECT TABLE customers_validated (
  freshness_check AS (
    MAX(_modified_at) &gt;= CURRENT_TIMESTAMP() - INTERVAL 1 DAY
  )
);
```

**Severity**: Warning (P1).
**SLA**: Alert if &gt;24 hours old.
**Action on Failure**: Alert to on-call; check if pipeline is hung.

### Row Count Reconciliation

```sql
-- Silver row count must be close to Bronze (within dedup margin)
-- Account for legitimate filtering (e.g., test records, deleted accounts)
EXPECT TABLE customers_validated (
  reconciliation_check AS (
    (SELECT COUNT(*) FROM customers_validated)
    BETWEEN
      (SELECT COUNT(*) FROM raw_customers) * 0.90  -- allow 10% loss for dedup
      AND (SELECT COUNT(*) FROM raw_customers) * 1.01  -- allow 1% gain for corrections
  )
);
```

**Severity**: Blocking (P0).
**Tolerance**: ±10% (dedup and corrections).
**Action on Failure**: Reject; alert; manual audit.

---

## Gold Layer Expectations

### Business-Ready Consumption

Gold tables are optimized for consumer queries and serve as the source of truth for analytics, ML, and BI. Expectations here enforce freshness, consistency, and accuracy for downstream consumers.

### Completeness and Current State

```sql
-- Customer 360 Gold table is current within SLA
EXPECT TABLE customer_360 (
  freshness_check AS (
    MAX(_modified_at) &gt;= CURRENT_TIMESTAMP() - INTERVAL 1 HOUR
  )
);

-- All customer_ids in customer_360 exist in Silver (no orphans)
EXPECT TABLE customer_360 (
  orphan_check AS (
    NOT EXISTS (
      SELECT 1 FROM customer_360 c360
      WHERE NOT EXISTS (
        SELECT 1 FROM customers_validated cv
        WHERE cv.customer_id = c360.customer_id
      )
    )
  )
);
```

**Severity**: Blocking (P0).
**SLA**: &lt;1 hour stale.
**Action on Failure**: Reject; roll back to prior snapshot; alert on-call.

### Aggregate Accuracy and Reconciliation

```sql
-- Daily sales summary must reconcile with Silver within $0.01 per order
EXPECT TABLE daily_sales_summary (
  aggregate_reconciliation AS (
    SELECT SUM(amount) FROM daily_sales_summary
    IS WITHIN 0.01 OF
    SELECT SUM(order_amount) FROM orders_silver
  )
);

-- Row counts match between daily and historical gold
EXPECT TABLE daily_sales_summary (
  cardinality_check AS (
    COUNT(DISTINCT DATE(order_date)) = COUNT(DISTINCT DATE(order_date)) OVER (PARTITION BY MONTH(order_date))
  )
);
```

**Severity**: Blocking (P0) — finances depend on this.
**Tolerance**: ±$0.01 per order (handle floating-point rounding).
**Action on Failure**: Reject; re-aggregate; alert finance team.

### Consumer Guarantees (SLA)

```sql
-- Query performance: p95 query latency must be &lt;5 seconds for customer_360
-- (Monitored via Databricks query history, not an EXPECT clause, but documented here)

-- Availability: customer_360 must be queryable during business hours (8am-8pm UTC)
EXPECT TABLE customer_360 (
  availability_check AS (
    TABLE customer_360 IS NOT EMPTY  -- simple check; better: monitor cluster uptime
  )
);
```

**Severity**: Warning (P1) — operational SLA.
**Action on Failure**: Page on-call; investigate cluster/query issues.

### Consistency Across Related Gold Tables

```sql
-- If customer_360 and daily_sales_summary both exist:
-- Sum of amounts per customer in daily_sales_summary 
-- should match lifetime_revenue in customer_360
EXPECT (
  SELECT SUM(amount) FROM daily_sales_summary WHERE customer_id = X
  EQUALS
  SELECT lifetime_revenue FROM customer_360 WHERE customer_id = X
);
```

**Severity**: Blocking (P0) for critical aggregates.
**Action on Failure**: Reject; investigate transformation logic; recompute.

### Business Logic Validation

```sql
-- Revenue should never be negative
EXPECT TABLE daily_sales_summary (
  CHECK (amount &gt;= 0)
);

-- Order dates should be within reasonable bounds (not in future, not before company founded)
EXPECT TABLE daily_sales_summary (
  CHECK (order_date BETWEEN &#x27;2015-01-01&#x27; AND CURRENT_DATE)
);
```

**Severity**: Blocking (P0).
**Action on Failure**: Reject; alert; audit source data.

---

## Cross-Layer Contracts

### Data Lineage and Consistency

Expectations that span multiple layers ensure data doesn&#x27;t transform incorrectly as it flows Bronze → Silver → Gold.

### Layer-to-Layer Validation

| Contract | Assertion | If Violated | Severity |
|----------|-----------|----------|----------|
| Bronze → Silver row count | Silver rows ≥ 90% of Bronze rows (allow dedup) | Investigate dedup logic | Blocking |
| Silver → Gold row count | Gold unique customers = Silver unique customers | Reject Gold; re-aggregate | Blocking |
| Bronze → Gold data types | Gold numbers can be summed without loss of precision | Audit source → Gold transformation | Blocking |

### Cross-Table Contracts (Fact-Dimension)

```sql
-- All orders.customer_id must exist in customer_360
EXPECT TABLE orders_gold (
  fk_customer_check AS (
    NOT EXISTS (
      SELECT 1 FROM orders_gold og
      WHERE NOT EXISTS (
        SELECT 1 FROM customer_360 c360
        WHERE c360.customer_id = og.customer_id
      )
    )
  )
);

-- Sum of order amounts per customer must match customer lifetime_revenue
EXPECT (
  SELECT SUM(amount) FROM orders_gold GROUP BY customer_id
  EQUALS
  SELECT lifetime_revenue FROM customer_360
);
```

**Severity**: Blocking (P0).
**Action on Failure**: Quarantine orders; alert; manual reconciliation.

---

## Failure Handling and SLA

### Alert and Escalation Policy

| Expectation | Severity | Detection SLA | Escalation | Action |
|-----------|----------|--------------|-----------|--------|
| [Bronze completeness] | Blocking | &lt;5 min | Page on-call | Pause ingest; investigate |
| [Silver uniqueness] | Blocking | &lt;10 min | Slack + email | Stop pipeline; manual dedup review |
| [Gold freshness] | Blocking | &lt;15 min | Page + email | Investigate scheduler; rerun |
| [Aggregate reconciliation] | Blocking | &lt;30 min | Finance + on-call | Recompute; audit |
| [Query latency] | Warning | &lt;1 min (logged) | Email on-call | Investigate cluster; optimize queries |

### Failure Recovery

**On Blocking Failure**:
1. Stop the pipeline (no downstream advancement)
2. Alert on-call data engineer immediately
3. Log detailed failure context (which rows failed, why)
4. Quarantine the batch in a `_quarantine_` location for manual review
5. Do not retry automatically; require manual approval + fix before re-processing

**On Warning Failure**:
1. Log the failure
2. Send alert to Slack (not pager)
3. Continue pipeline; flag data as low-confidence
4. Schedule manual audit within 24 hours

### SLA Target

- **Detection**: &lt;5 min for Bronze, &lt;15 min for Silver/Gold
- **Mean Time to Recovery (MTTR)**: &lt;30 min for blocking failures
- **False Positive Rate**: &lt;1% (tune thresholds to reduce alert fatigue)

---

## Review Checklist

Use this checklist during review to validate that the data quality expectations are complete and testable:

- [ ] **Overview and Scope** clearly states which medallion layers and quality dimensions are covered
- [ ] **Bronze Layer Expectations** validate schema, completeness, freshness, and ingestion integrity
- [ ] **Silver Layer Expectations** enforce deduplication, nullability, normalization, and referential integrity
- [ ] **Gold Layer Expectations** guarantee freshness, consistency, and accuracy for consumer queries
- [ ] **Expectations are written in executable form**: SDP EXPECT, dbt test, or SQL constraint (not prose)
- [ ] **Each expectation traces back** to a quality requirement in [[data-prd]] (reference by name)
- [ ] **Failure modes are explicit**: What happens when an expectation fails (reject, alert, quarantine)?
- [ ] **SLA per layer** is documented: freshness target, detection time, recovery time
- [ ] **Sampling vs exhaustive** is clear: All rows tested, or sample with confidence interval documented?
- [ ] **Cross-layer data contracts** ensure consistency across layers (sums reconcile, cardinality stable, no orphans)
- [ ] **Alert routing and escalation policy** is defined: Who gets paged? When does on-call respond?
- [ ] **No `[TBD]`, `[TODO]`, or `[NEEDS CLARIFICATION]` markers remain**
- [ ] **At least one expectation per quality dimension** (completeness, timeliness, accuracy, consistency, uniqueness)
- [ ] **P0 requirements have multiple expectations** (layered checks: Bronze schema, Silver uniqueness, Gold freshness)
- [ ] **Terminology aligns with Databricks SDP** (EXPECT clauses, UC, medallion layers, VIOLATION rules)</code></pre></details></td></tr>
</tbody>
</table>
