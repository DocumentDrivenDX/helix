# Customer Events Data Quality Tests

## test_inventory
| id | name | expectation_id | run_frequency |
|---|---|---|---|
| DQT-001 | Stripe event IDs are unique in bronze | EXPECT_UNIQUE_event_id | hourly |
| DQT-002 | Silver customer_id is not null for invoice/payment events | EXPECT_NOT_NULL_customer_id | hourly |
| DQT-003 | Gold daily revenue equals reconciled Stripe amount within $25 | EXPECT_RECON_daily_revenue | daily 07:00 UTC |
| DQT-004 | Schema version is one of 2024-10, 2025-01 | EXPECT_IN_SET_schema_version | per deploy |
| DQT-005 | Deleted customers are absent from silver and gold | EXPECT_RTB_FORGOTTEN_CUSTOMER | daily |

## fixtures
- F1 duplicate webhook ID: two `evt_1QdupA` payloads in bronze must collapse to one silver row.
- F2 late event arrival: `evt_1Qlate9` arrives 2026-05-02 for 2026-04-29 partition and updates gold.
- F3 schema-version drift: unexpected `billing_reason_v3` field fails DQT-004.
- F5 right-to-be-forgotten: `cus_rtbf_7721` removed from silver and marketing attribution outputs.
- F6 source/sink reconciliation mismatch: Stripe $42,250.10 vs Redshift $42,190.10 triggers DQT-003.

## known_failures
- DQT-003 is allowed to fail for 2026-05-01 through 2026-05-03 while finance validates disputed charges; owner: data-platform; expires: 2026-05-07.
