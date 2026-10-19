---
ddx:
  id: feature-registry
  authoring:
    home: repo
---

# Feature Registry

**Last Updated**: [Date]

## Active Features

| ID | Name | Description | Priority | Owner | Source | Updated |
|----|------|-------------|----------|-------|--------|---------|
| FEAT-001 | [Name] | [Brief description] | P0 | [Owner] | [PRD/spec/story] | [Date] |

## Product Lifecycle

Record release, product deprecation, or cancellation information only when it
changes a product decision. Implementation progress belongs in the relevant
plan, selected work item, or factual report. Do not track document stages here.

## Dependencies

| Feature | Depends On | Type | Notes |
|---------|------------|------|-------|
| FEAT-002 | FEAT-001 | Required | [Why] |

## Relevant References

Link governing artifacts and evidence when useful for the scoped work. Do not
seed empty traceability matrices or report missing links as separate work.

## Feature Categories

### [Category Name]
- FEAT-XXX: [Feature Name]

## ID Rules

1. Sequential numbering: FEAT-XXX (zero-padded 3 digits)
2. Never reuse IDs, even for cancelled features
3. Do not encode category or priority into the ID
4. Keep full behavior in Feature Specifications, not in this registry

## Deprecated/Cancelled

| ID | Name | Status | Reason | Date |
|----|------|--------|--------|------|
| FEAT-XXX | [Name] | [Cancelled/Deprecated] | [Why] | [Date] |
