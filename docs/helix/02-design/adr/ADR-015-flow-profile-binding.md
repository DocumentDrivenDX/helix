---
ddx:
  id: ADR-015
  authoring:
    home: repo
  status: proposed
  depends_on:
    - helix.prd
---
# ADR-015: Flows bind to a graph profile through an optional `profile:` key

| Date | Status | Deciders | Related | Confidence |
|------|--------|----------|---------|------------|
| 2026-11-06 | Proposed | HELIX maintainers | `.helix.yml`, catalog resolution, SD-003 | Medium |

## Problem

HELIX must govern a technology-intelligence graph (Atlas) beside the
software-delivery graph, in a different folder, without forcing either into the
other's artifact set or authority model. Today every flow resolves the same
catalog and the same `workflows/graph.yml`; `scripts/generate_graph.py` is
single-methodology and emits only `informs` edges.

## Decision

Keep `flows:` in `.helix.yml`. Add an optional `profile:` per entry, default
`software-delivery`. A profile is a catalog file (`workflows/profiles/<id>.yml`)
that selects artifact types, allowed edge kinds, the authority model, and
validation tiers. Artifact types stay reusable across profiles. No separate
methodology engine, no `graphs:` rename, no `helix_version` bump.

## Why we chose this

The skill already binds a graph per flow and enforces per-root scope, so a
profile only narrows and parameterizes the catalog. An absent key preserves
current behavior exactly, and the open schema lets older consumers ignore it.

## Alternatives

| Option | Evaluation |
|--------|------------|
| Rename `flows` to `graphs`, bump `helix_version: 3` | Rejected: breaks every existing marker for vocabulary only. |
| Separate Atlas catalog and tooling | Rejected: competing framework; duplicates authoring, validation, voice. |
| Infer profile from folder conventions | Rejected: implicit; violates "never silently pick". |

## Consequences

| Type | Impact |
|------|--------|
| Positive | Fully backward compatible; Atlas reuses authoring, validation, voice and present. |
| Negative | `generate_graph.py` and `validate-skills.sh` need a per-profile mode. |
| Neutral | An unknown profile id is a malformed marker: stop and report, per existing rules. |
