---
ddx:
  id: MON-001
  type: monitoring-setup
  status: in-progress
  links:
    - DP-001
---

# Monitoring Setup — customer-events pipeline

## Dashboard

A Grafana dashboard at `https://customer-events.metrics.example.com`
visualizes ingest lag, event-rate, and DLQ depth for the
customer-events pipeline.

## Outstanding work

The dashboard URL needs DNS. The hostname
`customer-events.metrics.example.com` is not yet routable; until the
DNS record is created the on-call team cannot reach the dashboard
during an incident.

## Alerts

- ingest-lag > 5 min for 10 consecutive minutes
- DLQ depth growth > 0 for 30 consecutive minutes
