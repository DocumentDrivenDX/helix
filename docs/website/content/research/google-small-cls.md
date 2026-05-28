---
title: "Google Engineering Practices: Small CLs"
slug: google-small-cls
generated: true
---
> **Source identity**:

```yaml
ddx:
  id: resource.google-small-cls
```

# Google Engineering Practices: Small CLs

## Source

- URL: https://google.github.io/eng-practices/review/developer/small-cls.html
- Accessed: 2026-05-12

## Summary

Google's Engineering Practices recommend small, self-contained changes because
they are easier to review, reason about, test, merge, and roll back. The
guidance emphasizes that a change should address one coherent thing, include
related tests, and leave the system working after it lands.

## Relevant Findings

- Small implementation slices reduce review burden and make defects easier to
  spot.
- A change should be self-contained and include the tests needed to understand
  and validate it.
- Splitting by files, interfaces, or layers can help large work move through
  review without losing coherence.
- Rollback is simpler when each change is bounded and conceptually focused.

## HELIX Usage

This resource informs the Technical Design artifact. HELIX uses it to keep
story-level technical designs bounded to one vertical slice with explicit file
changes, tests, rollback expectations, and implementation sequencing.

## Authority Boundary

This resource supports implementation slicing and reviewability. It does not
replace HELIX Solution Design, Test Plan, Implementation Plan, or DDx runtime
issue tracking.
