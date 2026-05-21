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
