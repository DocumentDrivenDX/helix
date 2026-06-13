---
title: "ADR-010: feature-registry and parking-lot stay separate with an explicit handoff"
slug: ADR-010-feature-registry-parking-lot-handoff
weight: 250
activity: "Design"
source: "02-design/adr/ADR-010-feature-registry-parking-lot-handoff.md"
generated: true
collection: adr
---

> **Example from HELIX's own docs.** This generated page comes from `docs/helix/`. Use it to see the method in practice; start with the [artifact-type catalog](/artifact-types/) for reusable templates. Historical plans and reports may describe retired architecture.

# ADR-010: feature-registry and parking-lot stay separate with an explicit handoff

| Date | Status | Deciders | Related | Confidence |
|------|--------|----------|---------|------------|
| 2026-05-30 | Accepted | HELIX maintainers | feature-registry, parking-lot, frame-phase catalog | High |

## Context

| Aspect | Description |
|--------|-------------|
| Problem | The artifact-type audit flagged `feature-registry` and `parking-lot` as similarly-shaped registries in the frame phase, raising the question of whether they should collapse into a single registry distinguished by a status enum. |
| Current State | `feature-registry` is the source of truth for accepted features (`FEAT-XXX`, owners, priorities, status progression from `draft` through `deployed`/`deprecated`/`cancelled`). `parking-lot` is a separate registry for deferred or future work, keyed by `Source` and `Revisit Trigger` and explicitly outside current scope. They share a `type: registry` classification and live in the same activity, but encode different lifecycle states and serve different operator decisions. |
| Requirements | The catalog must either (a) merge the two into one registry with a status discriminator, or (b) keep them separate with a documented handoff so the boundary the operator triages on stays visible and tracker-relevant. |

## Decision

`feature-registry` and `parking-lot` remain separate artifacts.

`parking-lot` is the staging area for deferred or future work — items kept
visible but outside current scope until a recorded `Revisit Trigger` fires.
`feature-registry` is the source of truth for accepted features that are in
the active pipeline (`draft` → `specified` → `designed` → `in_test` →
`in_build` → `built` → `deployed`, or terminal `deprecated`/`cancelled`).

Handoff between the two is explicit: a parking-lot entry promotes to
feature-registry when its revisit criteria are met. The promotion is a
recorded transition (assign next sequential `FEAT-XXX`, set initial status,
link back to the parking-lot source), not an implicit merge or status flip
inside a single registry.

**Key Points**: deferred vs accepted is a real lifecycle boundary | promotion
is a recorded transition, not an implicit merge | the operator triages on the
boundary, so the boundary must be visible in the artifact shape

## Alternatives

| Option | Pros | Cons | Evaluation |
|--------|------|------|------------|
| Collapse into one registry with a `deferred` status value | One file, one schema, one prompt; removes "similar shape" duplication | Loses the triage boundary the operator uses; mixes accepted features (with owners, priorities, dependencies) with deferred items (with revisit triggers); forces every consumer to filter by status before reading | Rejected: collapses a real lifecycle distinction |
| Keep separate, leave handoff implicit (current state) | No new procedure to document | Promotion happens ad-hoc; no recorded link between parked source and registered feature; the audit's "same shape" concern persists | Rejected: the handoff is the thing that makes separation safe |
| **Keep separate, document an explicit promotion procedure** | Preserves the lifecycle boundary; makes the transition auditable; addresses the audit's concern without merging | Requires Phase 3 to document the promotion procedure once and cross-reference it from parking-lot | **Selected: smallest sufficient fix that keeps the boundary real** |

## Consequences

| Type | Impact |
|------|--------|
| Positive | The deferred/accepted boundary stays visible in the artifact shape, matching how operators triage. |
| Positive | Promotion becomes a recorded transition with a back-link, so traceability survives the handoff. |
| Positive | The audit's "same shape" concern is resolved by procedure, not by losing structure. |
| Negative | Phase 3 owes the promotion procedure write-up in `feature-registry`, with a cross-reference from `parking-lot`. |
| Neutral | Both artifacts keep their existing `type: registry` classification and their existing prompts/templates. |

## Risks

| Risk | Prob | Impact | Mitigation |
|------|------|--------|------------|
| Promotion procedure documented in one place but not cross-referenced from the other | M | M | Phase 3 acceptance requires both ends — feature-registry owns the procedure, parking-lot links to it |
| Operators bypass the procedure and recreate parked items in the registry without back-links | M | M | The promotion step records the parking-lot source as the first dependency/trace link on the new FEAT-XXX |
| Future audit re-raises the "same shape" question after the procedure rots | L | L | This ADR is the durable answer; future audits cite it instead of relitigating |

## Validation

| Success Metric | Review Trigger |
|----------------|----------------|
| feature-registry documents the promotion procedure exactly once | Procedure is duplicated in parking-lot rather than cross-referenced |
| parking-lot's prompt cross-references the promotion procedure | A parked item is promoted without a recorded back-link to its parking-lot source |
| Promoted features carry a recorded link back to the parking-lot entry that sourced them | Operator triage cannot distinguish "deferred" from "accepted" at a glance |

## References

- [Plan: artifact-types and concerns audit](/artifacts/plan-2026-05-30-artifact-types-and-concerns-audit/)
- `workflows/activities/01-frame/artifacts/feature-registry/`
- `workflows/activities/01-frame/artifacts/parking-lot/`
