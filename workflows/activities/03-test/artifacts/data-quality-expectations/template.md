---
ddx:
  id: data-quality-expectations
---

# Data Quality Expectations

## Overview and Scope

[Define the data product being tested, the medallion layers covered (Bronze, Silver, Gold), and the quality dimensions in scope (completeness, timeliness, accuracy, consistency, uniqueness). Reference the [[prd]] (kind: data) for quality requirements and [[data-architecture]] for the layer definitions. This document translates those requirements into executable EXPECT clauses.]

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

-- If any of these are null, it's a quality failure (not a schema error)
EXPECT TABLE raw_customers (
  completeness_check AS (
    SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) 
      / COUNT(*) < 0.01  -- P0: <1% nulls on customer_id
  )
);
```

**Severity**: Blocking (P0) — reject records with null customer_id.
**Threshold**: <1% nulls on critical columns.
**Action on Failure**: Quarantine batch; alert; wait for manual approval.

### Freshness (Timeliness)

```sql
-- Ingestion must complete within 15 minutes of source commit
EXPECT TABLE raw_customers (
  freshness_check AS (
    MAX(_ingest_timestamp) >= CURRENT_TIMESTAMP() - INTERVAL 15 MINUTES
  )
);
```

**Severity**: Warning (P1) — alert if >15 min old; move to Silver anyway but flag.
**Action on Failure**: Alert to on-call; do not advance to Silver if >30 min.

### No Truncation

```sql
-- Source columns must be preserved at full width (no truncation to shorter types)
EXPECT TABLE raw_customers (
  CHECK (LENGTH(email) <= 255),  -- assume source is VARCHAR(255)
  CHECK (LENGTH(phone) <= 20)
);
```

**Severity**: Warning — audit only.
**Action on Failure**: Log; manual spot-check.

---

## Silver Layer Expectations

### Validation and Transformation

Silver tables apply business logic: deduplication, null handling, type coercion, referential integrity. Expectations here enforce "clean" data for consumption.

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
    (SUM(CASE WHEN email IS NULL THEN 1 ELSE 0 END) / COUNT(*)) < 0.01
  )  -- <1% nulls on email
);
```

**Severity**: Blocking (P0).
**Threshold**: 0% nulls on customer_id; <1% nulls on email.
**Action on Failure**: Reject batch; alert.

### Data Quality and Normalization

```sql
-- Email addresses are normalized and valid
EXPECT TABLE customers_validated (
  CHECK (
    email LIKE '%@%.%' AND email NOT LIKE ' %' AND email NOT LIKE '% '
  )
);

-- Phone numbers (if present) are valid format
EXPECT TABLE customers_validated (
  CHECK (
    phone IS NULL OR phone REGEXP '^[0-9\-\+\(\) ]+$'
  )
);

-- Created_at is before or equal to updated_at
EXPECT TABLE customers_validated (
  CHECK (created_at <= updated_at)
);
```

**Severity**: Warning (P1) — log invalid records but don't block.
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
    MAX(_modified_at) >= CURRENT_TIMESTAMP() - INTERVAL 1 DAY
  )
);
```

**Severity**: Warning (P1).
**SLA**: Alert if >24 hours old.
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
    MAX(_modified_at) >= CURRENT_TIMESTAMP() - INTERVAL 1 HOUR
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
**SLA**: <1 hour stale.
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
-- Query performance: p95 query latency must be <5 seconds for customer_360
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
  CHECK (amount >= 0)
);

-- Order dates should be within reasonable bounds (not in future, not before company founded)
EXPECT TABLE daily_sales_summary (
  CHECK (order_date BETWEEN '2015-01-01' AND CURRENT_DATE)
);
```

**Severity**: Blocking (P0).
**Action on Failure**: Reject; alert; audit source data.

---

## Cross-Layer Contracts

### Data Lineage and Consistency

Expectations that span multiple layers ensure data doesn't transform incorrectly as it flows Bronze → Silver → Gold.

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
| [Bronze completeness] | Blocking | <5 min | Page on-call | Pause ingest; investigate |
| [Silver uniqueness] | Blocking | <10 min | Slack + email | Stop pipeline; manual dedup review |
| [Gold freshness] | Blocking | <15 min | Page + email | Investigate scheduler; rerun |
| [Aggregate reconciliation] | Blocking | <30 min | Finance + on-call | Recompute; audit |
| [Query latency] | Warning | <1 min (logged) | Email on-call | Investigate cluster; optimize queries |

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

- **Detection**: <5 min for Bronze, <15 min for Silver/Gold
- **Mean Time to Recovery (MTTR)**: <30 min for blocking failures
- **False Positive Rate**: <1% (tune thresholds to reduce alert fatigue)

---

## Review Checklist

Use this checklist during review to validate that the data quality expectations are complete and testable:

- [ ] **Overview and Scope** clearly states which medallion layers and quality dimensions are covered
- [ ] **Bronze Layer Expectations** validate schema, completeness, freshness, and ingestion integrity
- [ ] **Silver Layer Expectations** enforce deduplication, nullability, normalization, and referential integrity
- [ ] **Gold Layer Expectations** guarantee freshness, consistency, and accuracy for consumer queries
- [ ] **Expectations are written in executable form**: SDP EXPECT, dbt test, or SQL constraint (not prose)
- [ ] **Each expectation traces back** to a quality requirement in [[prd]] (kind: data) (reference by name)
- [ ] **Failure modes are explicit**: What happens when an expectation fails (reject, alert, quarantine)?
- [ ] **SLA per layer** is documented: freshness target, detection time, recovery time
- [ ] **Sampling vs exhaustive** is clear: All rows tested, or sample with confidence interval documented?
- [ ] **Cross-layer data contracts** ensure consistency across layers (sums reconcile, cardinality stable, no orphans)
- [ ] **Alert routing and escalation policy** is defined: Who gets paged? When does on-call respond?
- [ ] **No `[TBD]`, `[TODO]`, or `[NEEDS CLARIFICATION]` markers remain**
- [ ] **At least one expectation per quality dimension** (completeness, timeliness, accuracy, consistency, uniqueness)
- [ ] **P0 requirements have multiple expectations** (layered checks: Bronze schema, Silver uniqueness, Gold freshness)
- [ ] **Terminology aligns with Databricks SDP** (EXPECT clauses, UC, medallion layers, VIOLATION rules)
