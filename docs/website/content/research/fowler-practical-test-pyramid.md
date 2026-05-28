---
title: "The Practical Test Pyramid"
slug: fowler-practical-test-pyramid
generated: true
---
> **Source identity**:

```yaml
ddx:
  id: resource.fowler-practical-test-pyramid
```

# The Practical Test Pyramid

## Source

- URL: https://martinfowler.com/articles/practical-test-pyramid.html
- Accessed: 2026-05-12

## Summary

The Practical Test Pyramid explains how automated test suites balance many
fast, focused tests with fewer broad, slower tests. It frames unit,
integration, and end-to-end tests as complementary layers with different costs
and confidence tradeoffs.

## Relevant Findings

- A healthy test strategy balances feedback speed, confidence, and maintenance
  cost.
- End-to-end tests should cover critical user paths without becoming the only
  source of confidence.
- Integration tests are important where components meet, especially around
  databases, APIs, and external dependencies.
- Test strategy should be grounded in actual product risk, not a generic
  percentage target alone.

## HELIX Usage

This resource informs the Test Plan artifact. HELIX uses it to keep coverage
targets risk-based and to prevent project-level plans from overloading slow
end-to-end tests.

## Authority Boundary

This resource offers a test portfolio model. HELIX still requires traceability
from requirements and stories to concrete project test obligations.
