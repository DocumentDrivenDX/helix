---
ddx:
  id: metrics-dashboard
  type: metrics-dashboard
  authoring:
    home: repo
---

# Metrics Dashboard: pilot week 4

**Review Window**: 2026-10-19 - 2026-10-25
**Baseline**: pilot week 3

## Decision

The renamed-column warning improved import completion.

## Summary

Completion rose from 81% to 90% after the warning shipped.

## Metrics Table

| Metric | Baseline | Current | Direction | Result | Source |
|--------|----------|---------|-----------|--------|--------|
| Import completion | 81% | 90% | higher | pass | `import-completion` metric definition |

## Interpretation Rules

- A change under 3 points is noise.

## Trend Notes

- Completion rose in every pilot firm.

## Journey Funnels

| Journey | Completion | Biggest Drop-off | Diagnosis | Source |
|---------|------------|------------------|-----------|--------|
| import weekly files | 90% (was 81%) | validation results | Reviewers stop when every row is rejected; backlog item to explain why | Analytics export 2026-10-26, kept in the analytics workspace |

## Follow-Up

- Improvement backlog: explain an all-rows-rejected result.
