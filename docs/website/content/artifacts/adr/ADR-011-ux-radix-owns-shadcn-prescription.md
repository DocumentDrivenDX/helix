---
title: "ADR-011: ux-radix owns Radix and shadcn prescriptions; react-nextjs references"
slug: ADR-011-ux-radix-owns-shadcn-prescription
weight: 260
activity: "Design"
source: "02-design/adr/ADR-011-ux-radix-owns-shadcn-prescription.md"
generated: true
collection: adr
---

> **Example from HELIX's own docs.** This generated page comes from `docs/helix/`. Use it to see the method in practice; start with the [artifact-type catalog](/artifact-types/) for reusable templates. Historical plans and reports may describe retired architecture.

# ADR-011: ux-radix owns Radix and shadcn prescriptions; react-nextjs references

| Date | Status | Deciders | Related | Confidence |
|------|--------|----------|---------|------------|
| 2026-05-30 | Accepted | HELIX maintainers | ux-radix, react-nextjs, concerns | High |

## Context

| Aspect | Description |
|--------|-------------|
| Problem | Both the `react-nextjs` concern and the `ux-radix` concern prescribe Radix primitives and the shadcn component library. This double-prescription confuses the concern boundary: which concern owns component-library choice, and which one is being referenced? Audits surface the duplication as drift rather than as a deliberate cross-reference. |
| Current State | `react-nextjs` (framework slot) and `ux-radix` (interaction-primitives slot) each independently prescribe shadcn/Radix in their `concern.md` and `practices.md`. There is no single canonical owner, and downstream consumers cannot tell which concern's prescription is authoritative. |
| Requirements | Component-library prescription must live in exactly one concern, with other concerns referencing the owner rather than re-prescribing. The owner should be the concern whose subject matter is interaction primitives and component libraries. |

## Decision

The `ux-radix` concern owns the Radix primitives and shadcn component-library
prescription. `react-nextjs` references `ux-radix` for UI primitives and does
NOT prescribe shadcn directly.

`ux-radix` is the interaction-primitives concern; UI and component-library
prescription naturally lives there. `react-nextjs` is the framework slot
occupant — it should describe the framework (Next.js conventions, routing,
rendering model, build/runtime), not the component library it happens to pair
with. Removing component-library prescription from `react-nextjs` keeps the
framework concern focused on framework-shaped decisions.

This follows the "concern boundary lives once" rule established in ADR-006:
every prescription has exactly one canonical owner, and other concerns
reference rather than re-state.

**Key Points**: ux-radix is the canonical owner of Radix + shadcn prescription
| react-nextjs references ux-radix instead of re-prescribing | framework
concerns describe frameworks, not component libraries

## Alternatives

| Option | Pros | Cons | Evaluation |
|--------|------|------|------------|
| Keep double-prescription in both concerns | No edits required | Violates ADR-006 single-owner rule; auditors cannot tell which prescription is canonical; drift between the two copies is inevitable | Rejected: known source of confusion |
| Move ownership to `react-nextjs` and have `ux-radix` reference it | Co-locates component-library choice with the framework that pairs with it | Conflates framework slot with interaction-primitives slot; forces every framework concern to re-prescribe its own component library; ux-radix loses its subject matter | Rejected: wrong slot for the prescription |
| **Move ownership to `ux-radix`; `react-nextjs` references it** | Matches concern subject matter (interaction primitives own component libraries); keeps framework concerns focused; preserves slot boundaries | Requires Phase 3 edits to `react-nextjs` to remove or convert its shadcn prescription | **Selected: aligns ownership with concern subject** |

## Consequences

| Type | Impact |
|------|--------|
| Positive | Single canonical owner for shadcn/Radix prescription; no duplication to drift between. |
| Positive | `react-nextjs` becomes a focused framework concern instead of a mixed framework + component-library concern. |
| Positive | Future framework concerns (e.g. other React meta-frameworks) can reference `ux-radix` without re-prescribing the component library. |
| Positive | Audit drift signal becomes meaningful: any future shadcn/Radix mention outside `ux-radix` is a real cross-reference, not an accidental duplicate. |
| Negative | Phase 3 must edit `react-nextjs` to remove the shadcn/Radix prescription and replace it with a cross-reference. |
| Negative | Downstream artifacts that cite `react-nextjs` for component-library choice must be updated to cite `ux-radix` instead. |
| Neutral | The pairing of Next.js with shadcn/Radix in practice is unchanged — only the ownership of the prescription moves. |

## Risks

| Risk | Prob | Impact | Mitigation |
|------|------|--------|------------|
| Phase 3 edits to `react-nextjs` leave dangling shadcn references | M | M | Audit `react-nextjs/concern.md` and `practices.md` for any remaining shadcn/Radix prescriptions after the edit |
| Other framework concerns silently re-prescribe shadcn | L | M | Drift checker scans non-`ux-radix` concerns for shadcn/Radix prescription language |
| Cross-reference from `react-nextjs` to `ux-radix` is too vague to be useful | M | L | Make the reference explicit: name `ux-radix` and the specific primitives concern, not a generic "see UI concerns" pointer |

## Validation

| Success Metric | Review Trigger |
|----------------|----------------|
| Only `ux-radix` prescribes shadcn/Radix; all other concerns reference it | A non-`ux-radix` concern re-prescribes shadcn or Radix primitives |
| `react-nextjs` describes Next.js framework concerns without component-library prescription | `react-nextjs` adds component-library or design-system prescription |
| Downstream artifacts that need component-library choice cite `ux-radix` | An artifact cites `react-nextjs` for shadcn/Radix choice |

## References

- ADR-006: Concern boundary lives once
- workflows/concerns/ux-radix/concern.md
- workflows/concerns/react-nextjs/concern.md
- docs/helix/02-design/plan-2026-05-30-artifact-types-and-concerns-audit.md
