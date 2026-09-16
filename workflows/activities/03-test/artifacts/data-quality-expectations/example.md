---
ddx:
  id: example.data-quality-expectations.customer-360
  authoring:
    home: repo
  depends_on:
    # Previous: example.data-prd.customer-360 — dropped when data-prd
    # collapsed into prd as kind: data variant (ADR-008).
    - example.data-architecture.customer-360
---

# Data Quality Expectations: Customer-360 Analytics

## Overview and Scope

Quality expectations are written as testable predicates that the pipeline must
satisfy before Gold tables are released for analytics queries. They are organized
by layer (Bronze → Silver → Gold) and severity (P0 blocking, P1 alerting, P2
observational). Expectations are executed as part of the orchestrated job, using
Databricks SQL EXPECT clauses and dbt-style tests.

**In scope**: the Customer-360 Bronze, Silver, and Gold tables defined in
[[data-architecture]] (six Bronze source tables, five Silver tables, three
Gold tables) and the cross-layer contracts between them. **Out of scope**:
source-system data quality inside Salesforce and Stripe, BI-tool caching, and
the v2 streaming path.

### Quality Dimensions

| Dimension | Definition | P0 Threshold | P1 Threshold | Enforcement |
|-----------|-----------|--------------|--------------|-------------|
| Completeness | Non-null rate on required columns; daily row count vs prior day | 100% required columns; ≥ 95% of prior-day rows | ≥ 99% required columns | Block next layer if P0 fails |
| Timeliness | Gold tables refreshed and released | By 07:00 UTC daily | By 09:00 UTC | Alert; hold BI release |
| Accuracy | Salesforce-to-Stripe reconciliation rate; value domains | ≥ 98% matched; 100% valid status values | Median confidence ≥ 0.95 | Block Gold; manual review |
| Uniqueness | No duplicate keys in Silver facts and dimensions | 0 duplicates | n/a | Block Gold |
| Consistency | Cross-layer counts and revenue sums reconcile | ±0.01% | ±0.1% | Block BI release |

### Test Framework and Tooling

- **Framework**: Databricks SQL assertions returning `expectation_passed`,
  plus SDP `EXPECT ... ON VIOLATION` clauses on the Silver streaming tables
  where the assertion is row-level.
- **Execution**: Databricks Workflows tasks after each layer's load; results
  written to `gold.data_quality_log`.
- **Alerting**: `#data-platform-incidents` for P0; summary email to the
  analytics team for P1.
- **Remediation**: quarantine the failing batch, fix forward, rerun the layer.

### Testing Philosophy

All expectations run exhaustively on every load; Customer-360 volumes (tens of
thousands of rows per day) do not justify sampling. If Stripe charge volume
grows past ten million rows per day, GE-101 and SE-102 may move to a 10%
sample with a documented 95% confidence interval.

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

## Cross-Layer Contracts

Contracts that span layers catch transformations that pass every per-layer
check yet lose or duplicate data between layers. All cross-layer contracts are
P0 and run after the Gold aggregation task, before release to BI.

### Layer-to-Layer Validation

| Contract | Assertion | If Violated | Severity |
|----------|-----------|-------------|----------|
| CL-001 Bronze → Silver customer cardinality | Distinct `customer_id` in `silver.dim_customer` = distinct Salesforce account ids in today's Bronze load (unmatched accounts still get a flagged dim row) | Block Gold; investigate SE-001 matching | P0 |
| CL-002 Silver → Gold customer cardinality | Row count of `gold.dim_customer_account` = row count of `silver.dim_customer` | Reject Gold; re-aggregate | P0 |
| CL-003 Silver → Gold revenue reconciliation | Monthly `SUM(monthly_revenue_amount)` in Gold = monthly `SUM(amount)` of paid transactions in Silver, within 0.01% | Reject Gold; Finance and on-call audit | P0 |
| CL-004 Gold → Silver lineage | Every `subscription_id` in `gold.fct_subscription_health` exists in `silver.fct_subscription_event` | Quarantine Gold rows; alert | P0 |

### Cross-Table Contracts

```sql
-- CL-003: revenue sums reconcile between Silver and Gold per month
WITH silver_rev AS (
  SELECT DATE_TRUNC('month', payment_date) AS year_month, SUM(amount) AS amount
  FROM silver.fct_payment_transaction
  WHERE payment_status = 'paid'
  GROUP BY 1
),
gold_rev AS (
  SELECT year_month, SUM(monthly_revenue_amount) AS amount
  FROM gold.fct_monthly_revenue
  GROUP BY 1
)
SELECT COUNT(*) = 0 AS expectation_passed
FROM silver_rev s
FULL OUTER JOIN gold_rev g USING (year_month)
WHERE s.amount IS NULL
   OR g.amount IS NULL
   OR ABS(s.amount - g.amount) / NULLIF(s.amount, 0) > 0.0001;

-- CL-004: no orphaned subscriptions in Gold
SELECT COUNT(*) = 0 AS expectation_passed
FROM gold.fct_subscription_health h
WHERE NOT EXISTS (
  SELECT 1 FROM silver.fct_subscription_event e
  WHERE e.subscription_id = h.subscription_id
);
```

**Severity**: P0 (block release to BI)
**Owner**: Data Engineering (CL-001, CL-002, CL-004); Data Engineering and Finance (CL-003)

## Failure Handling and SLA

### Orchestration Integration

Expectations run as part of the daily load workflow:

```
Bronze Load → [Validate BE-001 to BE-102]
  ↓ (if all P0 pass; P1s logged)
Silver Transform → [Validate SE-001 to SE-102]
  ↓ (if all P0 pass; P1s logged)
Gold Aggregation → [Validate GE-001 to GE-102]
  ↓ (if all P0 pass; P1s logged)
Cross-Layer Contracts → [Validate CL-001 to CL-004]
  ↓ (if all pass)
Release to BI (if GE-001, GE-002, GE-003 and CL-001 to CL-004 pass)
```

### Alert and Escalation Policy

| Expectation | Severity | Detection SLA | Escalation | Action |
|-------------|----------|---------------|------------|--------|
| BE-001 to BE-003 (Bronze completeness, domains) | Blocking | < 5 min after Bronze load | Page data-eng on-call | Hold Silver load; check source export job |
| BE-101, BE-102 | Warning | < 5 min after Bronze load | Slack summary | Continue; review before Gold release |
| SE-001 to SE-003 (reconciliation, uniqueness, lineage) | Blocking | < 10 min after Silver load | Page on-call, Slack | Stop pipeline; review matching or source duplicates |
| SE-004 (PII hashing) | Blocking | < 10 min after Silver load | Page on-call and compliance owner | Halt pipeline; compliance review before any rerun |
| SE-101, SE-102 | Warning | < 10 min after Silver load | Email analytics team | Continue; investigate Stripe export or match tuning |
| GE-001 to GE-003 (Gold completeness, domains) | Blocking | < 15 min after Gold load | Page on-call | Withhold BI release; re-aggregate |
| GE-101, GE-102 | Warning | < 15 min after Gold load | Email analytics and Finance | Release with low-confidence flag; audit within 24 h |
| CL-001 to CL-004 (cross-layer) | Blocking | < 30 min after Gold load | Page on-call; CL-003 also Finance | Withhold BI release; reconcile and rerun Gold |

### Failure Recovery

**On blocking failure**:
1. Stop the workflow; no downstream task starts.
2. Alert `#data-platform-incidents` and page the on-call data engineer.
3. Write the failing expectation id, row counts, and sample keys to
   `gold.data_quality_log`.
4. Move the failing batch (partition `date_loaded`) to
   `main.customer_360_quarantine` for review.
5. No automatic retry; rerun the layer only after a fix is approved by the
   Data Engineering Lead.

**On warning failure**:
1. Log the result to `gold.data_quality_log`.
2. Post a Slack summary (no page).
3. Continue the pipeline and flag affected Gold rows `low_confidence = true`.
4. Complete a manual audit within 24 hours.

### SLA Targets

- **Detection**: < 5 min after Bronze load, < 15 min after Silver or Gold
  load, < 30 min for cross-layer contracts.
- **Recovery**: Gold released by 09:00 UTC after a blocking failure; mean time
  to recovery ≤ 2 hours from page to rerun.
- **False positive rate**: < 1% of expectation runs; thresholds are tuned per
  the Maintenance and Tuning cadence below.
- **Reporting**: daily pass/fail summary per layer in
  `gold.data_quality_dashboard`.

## Maintenance and Tuning

| Expectation | Review Cadence | Trigger for Tuning |
|-------------|----------------|--------------------|
| BE-001, SE-001, GE-001 | Monthly | Failure rate > 5% in past 30 days |
| SE-101, GE-102 | Quarterly | Threshold consistently exceeded but no incidents |
| SE-102 | As needed | Reconciliation logic changes |
| GE-101 | Quarterly | New customer segment added to pricing model |

---

**Approved by**: Data Engineering Lead | **Effective Date**: 2026-05-20
