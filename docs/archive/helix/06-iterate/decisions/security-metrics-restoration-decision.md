# Security Metrics — Restoration Decision

> Historical decision; superseded by the worked example at `docs/helix/06-iterate/security-metrics.md`.

`security-metrics` is restored as the canonical iterate-activity security posture
report artifact.

## Decision

This artifact is restored rather than retired. HELIX still needs a distinct
security learnings report because incident response, vulnerability management,
application security, and compliance are not fully represented by the general
metrics dashboard.

## Why It Exists

- `metrics-dashboard` summarizes overall iteration health.
- `security-metrics` captures security-specific posture, trends, and
  recommendations.
- The report feeds tracker-backed follow-up work and the improvement backlog.

## Canonical Inputs

- security monitoring and incident data for the iteration period
- vulnerability scan results
- compliance audit findings, when applicable
- previous security metrics report or baseline
- `docs/helix/06-iterate/metrics-dashboard.md` for shared iteration window context

## Minimum Prompt Bar

- cover incident response, vulnerability management, application security, and compliance
- compare current values to prior period or baseline
- require actionable recommendations that can become tracker issues
- include root-cause notes for critical or high-severity incidents

## Minimum Template Bar

- review window
- incident response metrics
- vulnerability management metrics
- application security metrics
- compliance status
- overall posture trend
- actionable recommendations

## Canonical Replacement Status

`security-metrics` is not replaced by `metrics-dashboard` or tracker issues. It
remains the canonical security-specific iterate report that informs follow-up
work.
