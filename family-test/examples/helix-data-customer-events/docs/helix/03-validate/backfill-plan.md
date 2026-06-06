---
ddx:
  id: BP-001
  type: backfill-plan
  methodology: helix-data
  library_type_version: 1.0.0
  links:
    - {kind: informs, to: IP-001}
    - {kind: informs, to: RB-001}
---

# Backfill Plan: Customer Events

Two distinct backfill scenarios are first-class:

1. **Historical backfill**: replaying Stripe events older than the bronze
   retention horizon (e.g. cold-start a new consumer).
2. **DLQ replay** (**F10**): reprocessing rejected events after a schema or
   code fix.

## Scenario 1 — Historical Backfill

### Trigger
- New consumer onboarded; needs N days of history.
- Bronze retention shifted (rare).

### Scope
- Date range: parameterised; example "last 90 days".
- Partition selector: `event_ts_utc BETWEEN start AND end`.
- Source: Stripe's events API (`/v1/events?created[gte]=...`).
  Note: Stripe's events API has a 30-day window; older history is gone
  unless we kept bronze. This is documented to set consumer expectations.

### Safety Checks (pre-run)
1. Bronze retention covers the requested window (else escalate to ops).
2. Dedup table has capacity for the projected event count.
3. Glue concurrency capped at 1 to prevent backfill from starving live
   silver job.
4. Cost estimate within F8 envelope; over-budget runs require explicit
   ops approval.
5. Consumer notification sent 24h ahead (the backfill will produce
   delayed events that look like F2 stragglers; consumers need to know
   the spike is intentional).

### Rollback Strategy
- Backfill writes are tagged `backfill_run_id` in silver.
- Rollback = `DELETE FROM silver WHERE backfill_run_id = '<id>'` +
  equivalent `DELETE` in gold tables.
- Lineage rollback: OpenLineage emits a job-aborted event with the
  affected URNs.

### Expected Runtime
- ~2.4M events/day × 90 days = 216M events.
- At 800 events/sec sustained Glue throughput → ~75h elapsed.
- Run in 4-hour windows on off-peak hours; ~19 nights to complete.

### Communication to Consumers
- T-24h: announce in `#data-platform-changelog` with run_id, expected
  duration, expected impact.
- T-0: confirm start.
- Hourly: progress updates.
- T-end: completion confirmation + reconciliation result (per RB-001
  §"reconciliation after backfill").
- Hard consumers (Analytics, Ops) get a separate ping; soft consumers
  (Product) just see the channel announcement.

## Scenario 2 — DLQ Replay (F10)

### Trigger
- DLQ size has stabilized (no new writes for ≥1h) after a code or
  schema fix shipped.
- Operator has root-cause documented.

### Scope
- Bounded by **reason code**: replay only one DLQ subpath at a time
  (`dlq/schema_drift/`, `dlq/pii_metadata/`, etc.).
- Bounded by **time window**: usually the window from "defect introduced"
  to "fix shipped"; never unbounded.
- The bounded replay procedure is the F10 mitigation: an unbounded "replay
  the whole DLQ" command does NOT exist by design.

### Safety Checks (pre-run)
1. The fix that necessitated this replay has been merged to main AND
   deployed to production for ≥1h.
2. DLQ writes for this reason code have stopped for ≥1h (else the fix
   is incomplete).
3. Dry-run on the first 1000 rows: verify they now pass silver
   expectations. If any still fail, halt + diagnose.
4. Dedup window covers the replay range (so we don't double-count).

### Rollback Strategy
- Replay writes are tagged `replay_run_id` in silver.
- Rollback as in Scenario 1.

### Expected Runtime
- Per-incident; usually 100s-100k rows; minutes to ~1h.

### Communication to Consumers
- Soft notification in `#data-platform-changelog` at T-0 and T-end.
- No 24h advance notice (replays are corrective; the original failure
  has already been visible to consumers).

## Late-Event Replay (F2 escape valve)

Triggered when Stripe delivers events > 24h old that the bronze→silver
late-arrival check (DD-001 step 5) routed to `dlq/late_event/`.

- Same procedure as DLQ replay, restricted to the `dlq/late_event/`
  subpath.
- Acceptable cadence: weekly batch if late_event volume > 10k/week;
  otherwise on-demand.
- Lineage events for late-replayed rows get the `replay_run_id` tag so
  the lineage graph can distinguish them from primary-path arrivals.
