# Customer Events May Revenue Backfill Plan

## trigger
Finance found a Stripe-to-Redshift mismatch for May 2026 after F6 reproduced a $60.00 sink shortfall and F10 showed three dead-lettered invoice events were replayable.

## scope
- Date range: 2026-05-01 through 2026-05-03 UTC.
- Partition selector: `bronze.stripe_events.event_date in ('2026-05-01','2026-05-02','2026-05-03')`; rebuild matching silver and gold partitions only.
- Exclude customers in the F5 erasure manifest, including `cus_rtbf_7721`.

## safety_checks_pre_run
- Confirm S3 bronze checksum manifest matches Stripe export ID `se_20260504_0915`.
- Run DQT-001 through DQT-005 on shadow tables.
- Verify no finance close lock on May daily revenue partitions.

## rollback_strategy
Swap partitions only after validation. Keep pre-backfill Redshift snapshots `snap_ce_20260501_03_pre` for 7 days and restore partition pointers if DQT-003 fails.

## expected_runtime
Shadow rebuild: 38 minutes. Validation: 12 minutes. Partition swap: under 2 minutes during 2026-05-06 02:00-03:00 UTC.

## communication_to_consumers
Notify finance reconciliation, marketing attribution, and ops dashboard owners in `#data-customer-events` 24 hours before run, at start, after validation, and after swap.
