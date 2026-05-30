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
