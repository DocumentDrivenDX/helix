---
ddx:
  id: helix.prd
  depends_on:
    - helix.removed-feature-001
  status: draft
classification: STALE_PLAN
---

# Product Requirements Document

## Summary

HELIX is a software development methodology and artifact catalog for AI-assisted teams.

## Problem and Goals

### Problem

AI-assisted software development is the default practice, but the practice itself is unpracticed.

### Goals

1. **Catalog.** Define a minimal, complete catalog of artifact types.
2. **Alignment skill.** Provide a single skill that any AI agent can run.
3. **Methodology spec.** Specify the artifact authority hierarchy and alignment skill contract.

### Success Metrics

| Metric | Target | Measurement Method |
|---|---|---|
| Runtime breadth | 3 documented runtime deployments | Release audit |
| Adoption | 50+ repos using HELIX templates | GitHub search |

### Non-Goals

- HELIX will not provide a CLI, tracker, queue, or execution engine.
- HELIX will not impose technology choices.
