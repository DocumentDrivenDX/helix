---
ddx:
  id: IB-001
  type: improvement-backlog
  methodology: helix-data
  library_type_version: 1.0.0
  links: []
---

# Improvement Backlog: Customer Events

## Backlog

Items captured from operate/evolve cycles that feed product iteration. Each
item references the F-fixture it surfaced from (if any) so the next round of
artifacts can close the loop.

- **IB-1**: investigate revenue duplicate-tracking shortfall surfaced by F1
  patterns observed in the daily reconciliation job (RS-001).
- **IB-2**: tighten F2 late-arrival watermark policy — current 6h window is
  loose; downstream Looker (Consumer 3) requested 2h.
- **IB-3**: F3 schema-drift alert fatigue. Producers have added 4 optional
  fields in the last quarter; alert routing needs better deduplication.
- **IB-4**: F4 PII canary expansion to cover newly-onboarded `customer.email`
  webhook payloads (out-of-contract field).
- **IB-5**: F5 right-to-be-forgotten — propagation SLA is currently
  best-effort; needs a documented response window.
- **IB-6**: F6 reconciliation drift — add automated remediation for known
  Stripe-API-Lambda race conditions instead of paging ops every time.
- **IB-7**: F7 lineage gap — upstream Stripe URN emission is still manual on
  the bronze→silver boundary; automate via OpenLineage processing hooks.
- **IB-8**: F8 cost overrun — Glue partition explosion remediation is
  one-shot; need pre-flight cost estimator on contract changes.
- **IB-9**: F9 hot-key skew — current detection is post-hoc; want pre-write
  rebalance.
- **IB-10**: F10 DLQ replay tooling — replay-by-reason-code is manual; build
  a guarded CLI wrapper.
- **IB-11**: F11 consumer-side breaking-change announce chain — add a
  receipt-acknowledge step so deprecated consumers can't silently miss the
  notification.
