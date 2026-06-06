# Customer Events v1 Deprecation Notice

## artifact_being_deprecated
`redshift.gold.customer_events_v1`, including columns `customer_email`, legacy `billing_reason`, and hourly materialized view `ops_customer_events_v1_mv`.

## successor
Use `redshift.gold.customer_events_v2` and `redshift.gold.ops_customer_events_live`. The successor contains `customer_email_sha256`, Stripe 2025-01 enum values, and OpenLineage coverage from the lineage spec.

## consumers_affected
- Finance reconciliation: reads daily revenue fields; owner `fin-data-recon`.
- Marketing attribution: reads event attributes and email identity; owner `mktg-data`.
- Ops dashboard: reads hourly live view; owner `ops-analytics`.
- F11 confirms marketing parser mismatch until enum migration lands.

## timeline
- Announcement: 2026-06-03 in data catalog and `#data-customer-events`.
- Migration support: 2026-06-10 through 2026-06-24.
- Read-only freeze for v1 changes: 2026-06-25.
- Final validation of zero v1 queries: 2026-07-08.

## final_decommission_date
2026-07-15.
