# Customer Events Lineage Spec

## emitter_strategy
Use OpenLineage from Airflow DAG `stripe_customer_events_v2`. Airflow emits run events for extraction and Redshift loads; dbt emits model-level lineage for silver and gold transforms. F7 lineage gap must fail validation if `gold.customer_revenue_daily` has no upstream silver node.

## nodes_to_emit
- Source: `stripe.webhook_events`, `stripe.balance_transactions_export`.
- Bronze: `redshift.bronze.stripe_events_raw`.
- Silver: `dbt.silver.customer_events`, `dbt.silver.customer_identity_map`.
- Validation: `dq.customer_events_hourly`, `recon.customer_events_daily`.
- Gold: `dbt.gold.customer_revenue_daily`, `dbt.gold.marketing_attribution_events`, `dbt.gold.ops_customer_events_live`.

## consumer_of_lineage
Primary backend: Marquez namespace `prod-customer-events`. Secondary export to DataHub for consumer impact search by finance reconciliation, marketing attribution, and ops dashboard owners.
