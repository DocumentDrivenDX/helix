---
ddx:
  id: DQE-001
  type: data-quality-expectations
  methodology: helix-data
  library_type_version: 1.0.0
  links:
    - {kind: informs, to: DQT-001}
    - {kind: informs, to: MS-001}
---

# Data Quality Expectations: Customer Events

Expectations are layered Bronze → Silver → Gold. Each layer's failure has a
documented escalation path in `runbook.md` (RB-001).

## Bronze Expectations (raw schema integrity)

| ID | Expectation | Fixture |
|---|---|---|
| B-01 | `event_id` present and non-empty | — |
| B-02 | `event_id` unique within a 7-day window (idempotency check) | **F1** |
| B-03 | `created` parses to a valid UTC instant | — |
| B-04 | `created` within `now() - 90d ≤ created ≤ now() + 5min` (late + future bound) | **F2** |
| B-05 | `type` matches `^[a-z]+\\.[a-z_.]+$` shape | — |
| B-06 | `api_version` is one of the 4 known values; new value triggers W-01 warn | **F3** |
| B-07 | Stripe signature verifies | — |

**Bronze failure → DLQ** (per F10 dead-letter handling). Operator runbook
RB-001 §"DLQ replay" covers recovery once root cause is fixed.

## Silver Expectations (transformed semantics)

| ID | Expectation | Fixture |
|---|---|---|
| S-01 | `customer_token` is a 64-char hex string (sha256 output) | **F4** |
| S-02 | No row in silver contains `@` (email-leak canary) | **F4** |
| S-03 | `payload_silver` matches the typed projection for its `event_type` | **F3** |
| S-04 | `lineage_ref` resolves to a known bronze `event_id` | **F7** |
| S-05 | Hourly partition row counts within 3σ of 28-day rolling baseline | **F9** |
| S-06 | Hot-key check: no single `customer_token` accounts for > 5% of an hourly partition | **F9** |
| S-07 | DLQ size at silver < 0.1% of inflow (rolling 1h) | **F10** |

**Silver failure → reject row to DLQ + alert.** S-02 (email canary) is a
**hard-block**: pipeline halts silver→gold promotion until the canary
clears.

## Gold Expectations (consumer-facing invariants)

| ID | Expectation | Fixture |
|---|---|---|
| G-01 | Hourly `count(distinct event_id)` Redshift = Stripe API count within 0.01% | **F6** |
| G-02 | Customer-deletion propagation: any `customer_token` in `customer.deleted` event has 0 rows in gold within 24h | **F5** |
| G-03 | All gold rows have a non-null `lineage_ref` traceable to a bronze row | **F7** |
| G-04 | Ops alert latency p99 ≤ 5min | — |
| G-05 | Analytics freshness p99 ≤ 1h | — |
| G-06 | Schema fingerprint matches the contract's published version | **F11** |

**Gold failure → consumer-visible.** Analytics dashboards display a "stale"
banner when G-04/G-05 breach.

## Escalation When Failed

| Severity | Trigger | Owner | SLA |
|---|---|---|---|
| Sev1 | S-02 email canary OR G-02 deletion-propagation OR G-04 ops latency | on-call data eng | 15min ack |
| Sev2 | G-01 reconciliation drift OR B-04 future-event flood OR S-07 DLQ explosion | data eng | 1h ack |
| Sev3 | B-06 new api_version OR S-05 row-count drift OR F8 cost overrun | data eng | next business day |

## Override Policy
- Bronze/Silver expectations can be temporarily relaxed via a documented
  override in the runbook (RB-001 §"expectation overrides"). Override has
  a mandatory expiry; an open-ended override is a defect.
- Gold expectations cannot be overridden — failures are escalated, not
  silenced. This is the F6 / F11 firewall: silencing G-01 or G-06 would
  hide the failure modes the contract exists to prevent.
