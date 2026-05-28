---
title: "Google Testing Blog: Test Sizes"
slug: google-test-sizes
generated: true
---
> **Source identity**:

```yaml
ddx:
  id: resource.google-test-sizes
```

# Google Testing Blog: Test Sizes

## Source

- URL: https://testing.googleblog.com/2010/12/test-sizes.html
- Accessed: 2026-05-12

## Summary

Google's Testing Blog describes small, medium, and large tests as a practical
way to distinguish test scope. Small tests are isolated and fast, medium tests
exercise limited integration such as a database or localhost service, and large
tests exercise broader system behavior. The guidance emphasizes isolation,
parallel execution, and using test size to organize suites.

## Relevant Findings

- Test levels should be defined by scope and dependencies, not only by tool.
- Isolation and bounded dependencies make tests faster and less flaky.
- Large tests are valuable but should be fewer, slower, and focused on critical
  end-to-end paths.
- Naming test size lets teams enforce different expectations in CI.

## HELIX Usage

This resource informs the Test Plan artifact. HELIX uses it to define test
levels, infrastructure needs, sequencing, and CI gates in a way that agents can
apply consistently before implementation begins.

## Authority Boundary

This resource supports test-scope planning. It does not replace project-specific
coverage targets, acceptance criteria, or Story Test Plans.
