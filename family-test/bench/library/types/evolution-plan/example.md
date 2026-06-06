# Customer Events Schema Evolution Plan

## breaking_changes
- Replace `customer_email` in gold outputs with `customer_email_sha256`; raw email remains only in restricted bronze.
- Rename `billing_reason` values to Stripe 2025-01 enum; F3 schema-version drift covers unexpected old values.
- Marketing attribution parser currently fails on the new enum, matching F11 consumer-side breaking mismatch.

## migration_window
Start dual-write on 2026-06-10. Consumers migrate by 2026-06-24. Freeze old-field removals during finance month close, 2026-06-28 through 2026-07-03.

## consumer_notification_plan
Notify finance reconciliation, marketing attribution, and ops dashboard in `#data-customer-events` and Jira DATA-2841. Require written acknowledgment from each owner by 2026-06-17.

## rollback_plan
Keep `customer_email` and old enum mapping in `gold.customer_events_v1` for 30 days. Repoint views to v1 and disable dbt model `gold.customer_events_v2` if DQT-004 or REC-001 fails.

## success_criteria
- 100% consumer acknowledgment by 2026-06-17.
- Seven consecutive days with DQT-001 through DQT-005 passing on v2.
- No P1/P2 reconciliation alerts and marketing attribution sample match rate at least 99.5%.
