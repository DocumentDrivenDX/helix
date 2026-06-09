---
ddx:
  id: MD-001
  type: metrics-dashboard
  methodology: helix-data
  library_type_version: 1.0.0
  links:
    - {kind: informs, to: IB-001}
---

# Metrics Dashboard: Customer Events Pipeline

Operator + stakeholder views. Each panel is sourced from CloudWatch,
Redshift, or DataHub. Each tile is tied to a runbook section AND, where
relevant, an adversarial fixture.

## Operator Overview

### Health tiles (top row)
- **Ingress rate** (events/min, last 24h) — sanity check; flat is bad.
- **Bronze landing latency p99** (last 1h vs. baseline) — F2 anchor.
- **Silver job runtime + status** (last 10 runs).
- **Gold COPY status + freshness** (per consumer).
- **DLQ inflow by reason** (stacked, last 24h) — surfaces F1, F3, F4, F10.

### Reconciliation Status Board
- **R-01 drift** (last 24h time series; tolerance band overlaid) — **F6**.
- **R-02 mass conservation** (binary status per hour, last 7d).
- **R-03 silver→gold count** (binary status per hour, last 7d).
- **R-04 round-trip sample** (daily sample success rate).
- **R-05 redaction lag** (max age of un-propagated customer.deleted
  events) — **F5**.
- **R-06 lineage completeness** (%, last 24h) — **F7**.

## Cost

- **Glue DPU-seconds (last 30d)** with the $400/mo budget overlay — **F8**.
- **Spend per event_type** — surfaces if one event_type is driving cost.
- **Spend per hour-of-day** — surfaces burst-driven autoscaling waste.
- **Partition file count** by layer (counts must stay flat per-event) —
  partition-explosion canary — **F8**.

## Schema + Contract Health

- **api_version_seen** distribution (rolling 7d) — surfaces new versions
  before they trigger F3 alerts.
- **Schema-fingerprint mismatch count** (T-G06) — **F11**.
- **Contract version active per consumer** (table from CONS-001
  contract_version column) — F11 audit surface.

## Skew

- **Top-10 customer_tokens by hourly share** (last 24h) — surfaces F9
  before T-S06 fires; tokens hashed for display.
- **Salted-join mode active?** (binary, last 7d).

## PII

- **Email-canary scan result** (daily, T-S02) — **F4**.
- **PII-quarantine inflow** (rolling 7d) — **F4** trend.
- **Redaction job daily completion** — **F5** audit.

## Lineage

- **% rows with resolvable lineage_ref** (rolling 24h, T-G03) — **F7**.
- **OL emit failure count** (rolling 1h, A-LINEAGE-EMIT) — **F7**.

## Consumer-Facing Freshness

- **Analytics dashboard freshness** (gold p99 vs. 1h SLA).
- **Ops alert latency** (gold p99 vs. 5min SLA).
- **Product Looker freshness** (gold p99 vs. 24h SLA).
- **Each panel has a banner** that turns red when the consumer's SLA
  per CONS-001 is breached.

## Cross-cutting

- Every panel exposes a "drill in" link to the underlying CloudWatch
  Logs Insights query or Redshift saved query — no panel is a dead end.
- Dashboards inherit the visual style from `helix-web:design-system`
  (cross-flow edge per §12.6); colours, spacing, and severity badges
  are not hand-rolled here.
- Stakeholder-facing variant strips the operator-overview row; product
  + ops leadership see only freshness + reconciliation summary.

## Feedback to product (helix → IB-001)

The cost, skew, and freshness panels are the upstream feeds for
`improvement-backlog.md` in the product flow. A sustained breach in
any panel auto-creates an IB-001 entry (via Slack `/backlog-add`
integration). This is the helix-data → helix `informs` cross-flow edge
in action (§12.6).
