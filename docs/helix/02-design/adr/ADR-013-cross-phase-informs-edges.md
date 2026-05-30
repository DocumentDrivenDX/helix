---
ddx:
  id: ADR-013
  depends_on:
    - helix.prd
---
# ADR-013: Cross-phase informs edges are valid when declared on the downstream artifact

| Date | Status | Deciders | Related | Confidence |
|------|--------|----------|---------|------------|
| 2026-05-30 | Accepted | HELIX maintainers | artifact dependencies, schema validator | High |

## Context

| Aspect | Description |
|--------|-------------|
| Problem | The audit flagged the Deploy artifact `monitoring-setup` declaring `informs: metrics-dashboard`, an Iterate artifact in a later phase. It is unclear whether HELIX permits an artifact to declare an `informs` edge that crosses a phase boundary into a downstream phase, and whether the back-edge must also be declared on the consumer. |
| Current State | `workflows/activities/05-deploy/artifacts/monitoring-setup/meta.yml` declares `informs: metrics-dashboard`. `workflows/activities/06-iterate/artifacts/metrics-dashboard/meta.yml` declares both `informed_by` and `informs` lists but does not currently encode every back-edge for every upstream `informs`. The schema validator does not enforce edge symmetry across artifacts. |
| Requirements | The methodology must not forbid real evidence-flow edges that cross phases (production telemetry feeding dashboards is a real flow). At the same time, cross-phase edges must be explicit on both ends so that walking from either side reveals the relationship. |

## Decision

An artifact may declare `informs` an artifact in a later phase. The cross-phase
edge is valid when:

1. The source artifact's purpose produces evidence the target consumes (the
   edge encodes a real evidence flow, not a speculative association), and
2. The edge is declared on both sides — `informs` on the source artifact and
   `informed_by` on the target artifact — or in a single canonical place
   chosen by the consumer when only one direction can be authoritative.

The `monitoring-setup` → `metrics-dashboard` edge is the canonical example:
production telemetry configured in Deploy feeds the dashboards consumed in
Iterate. The methodology accepts this as a valid cross-phase informs edge.

**Key Points**: cross-phase informs allowed | edge must be real evidence flow |
declared on both ends (or canonical single place) | symmetry check is a
follow-up validator concern, not required by this ADR

## Alternatives

| Option | Pros | Cons | Evaluation |
|--------|------|------|------------|
| Forbid cross-phase informs edges entirely; restrict `informs` to same-phase artifacts | Simpler validator; clear phase boundary | Erases real evidence flows (Deploy telemetry → Iterate dashboards); forces artifacts to invent intermediate hops or drop the edge | Rejected: phase boundary is not a methodology firewall against evidence flow |
| Allow cross-phase informs but only when declared on the upstream side | Single source of truth | Walking from the consumer no longer reveals the upstream; reviewers must scan all earlier phases to find inbound edges | Rejected: breaks bidirectional discoverability |
| **Allow cross-phase informs; require declaration on both ends (or a canonical single place); leave symmetry enforcement as a follow-up validator concern** | Preserves real evidence flows; keeps edges discoverable from both ends; does not block this ADR on validator work | Phase 3 walk must check both sides; some artifacts will need back-edges added | **Selected: accepts the real flow without overcommitting the validator** |

## Consequences

| Type | Impact |
|------|--------|
| Positive | Real cross-phase evidence flows (e.g., Deploy telemetry → Iterate dashboards) are recognized as first-class edges. |
| Positive | Both-end declaration keeps the dependency graph walkable from either direction. |
| Positive | Phase 3 has a clear rule: walk all artifacts for `informs` edges and ensure the back-edge is declared. |
| Negative | Phase 3 must check edge symmetry across the full artifact set and add missing back-edges where the upstream declares `informs` but the downstream does not declare `informed_by`. |
| Neutral | The schema validator is unchanged in this ADR. Symmetry enforcement is a follow-up Phase 1B validator concern. |

## Risks

| Risk | Prob | Impact | Mitigation |
|------|------|--------|------------|
| Authors declare speculative cross-phase edges that are not real evidence flows | M | M | Phase 3 walk and reviewers reject edges that do not match the source artifact's stated purpose |
| Back-edges drift out of sync as artifacts evolve | M | M | Follow-up Phase 1B validator extension checks edge symmetry; until then, the Phase 3 walk establishes the baseline |
| Confusion about whether to declare on one end or both | L | L | This ADR states the rule: both ends, or a single canonical place chosen by the consumer when only one direction can be authoritative |

## Validation

| Success Metric | Review Trigger |
|----------------|----------------|
| Every `informs` edge declared on an upstream artifact has a matching `informed_by` entry on the downstream artifact (or a documented canonical-single-place choice) | A Phase 3 walk finds an upstream `informs` with no corresponding downstream `informed_by` |
| `monitoring-setup` → `metrics-dashboard` is preserved as a valid cross-phase informs edge | A review flags the edge as invalid because it crosses a phase boundary |
| Schema validator extension for edge symmetry is filed as a follow-up Phase 1B concern | Edge symmetry drift recurs and is not surfaced mechanically |

## References

- [PRD](../../01-frame/prd.md)
- [Plan: 2026-05-30 Artifact Types and Concerns Audit](../plan-2026-05-30-artifact-types-and-concerns-audit.md)
- ADR-004: Dependencies Encoding
