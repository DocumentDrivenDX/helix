---
title: "Google SRE: Monitoring Distributed Systems"
slug: google-sre-monitoring-distributed-systems
generated: true
---
> **Source identity**:

```yaml
ddx:
  id: resource.google-sre-monitoring-distributed-systems
```

# Google SRE: Monitoring Distributed Systems

## Source

- URL: https://sre.google/sre-book/monitoring-distributed-systems/
- Accessed: 2026-05-12

## Summary

Google's Site Reliability Engineering book describes monitoring as collecting,
processing, aggregating, and displaying quantitative system data. It explains
why monitoring supports long-term analysis, comparison, alerting, dashboards,
and debugging, and introduces the four golden signals: latency, traffic,
errors, and saturation.

## Relevant Findings

- Useful metrics should answer operational or product questions, not merely
  exist because data is available.
- Service metrics need clear definitions so dashboards and alerts remain
  consistent over time.
- Latency, traffic, errors, and saturation are durable starting points for
  user-facing systems.
- Monitoring should stay simple enough to maintain and interpret.

## HELIX Usage

This resource informs Metric Definition, Metrics Dashboard, and Monitoring
Setup artifacts. HELIX uses it to keep metric contracts precise about what is
measured, how it is measured, how to interpret directionality, and how
dashboards, alerts, and ratchets should use the value.

## Authority Boundary

This resource supports monitoring discipline. It does not replace HELIX metric
dashboards, improvement backlogs, or project-specific success definitions.
