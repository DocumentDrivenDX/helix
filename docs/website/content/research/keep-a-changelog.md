---
title: "Keep a Changelog"
slug: keep-a-changelog
generated: true
---
> **Source identity**:

```yaml
ddx:
  id: resource.keep-a-changelog
```

# Keep a Changelog

## Source

- URL: https://keepachangelog.com/en/1.1.0/
- Accessed: 2026-05-12

## Summary

Keep a Changelog provides a structured format for communicating software
changes in a human-readable way. It recommends grouping notable changes under
clear categories such as added, changed, deprecated, removed, fixed, and
security, and emphasizes writing for people rather than only machines or commit
history.

## Relevant Findings

- Release communication should summarize notable user-impacting changes rather
  than dump raw commit history.
- Categories help readers quickly identify new features, fixes, removals,
  security items, and required attention.
- Human-readable change summaries remain valuable even when automation can
  collect underlying issues or commits.
- Version and date context help readers understand what shipped and when.

## HELIX Usage

This resource informs the Release Notes artifact. HELIX uses it to keep release
notes scoped to shipped change, user/operator impact, required actions, known
issues, and references to deeper evidence.

## Authority Boundary

This resource is a changelog format, not a deployment checklist or launch plan.
HELIX Release Notes may borrow its reader-centered categories without becoming
a repository changelog.
