---
ddx:
  id: helix.principles
  authoring:
    home: repo
  depends_on:
    - helix.prd
    - helix.product-vision
  review:
    self_hash: 93cd1656916b185cc307151361be40ab1a077117ba5d1e2756ae24fecb1959bb
    deps:
      helix.prd: 48c38800e987ab54c72d79dcd9ceed6e20afbd197b87c05699c51b49f3cd1f41
      helix.product-vision: 1f1e960bc87b10da772f5a37b3947d9908a56820cc84ff786c5258c2c664173d
    reviewed_at: "2026-10-04T02:22:27Z"
---
# Project Principles

These principles guide choices about HELIX. Workflow contracts define required
steps; principles do not add steps or gates.

## Principles

1. **Authority resolves conflicts.** Follow the artifact authority hierarchy;
   implementation does not silently override an accepted specification.
2. **Specifications describe desired state.** Record requirements and
   consequential decisions in their governing artifacts. Record implementation
   status in the runtime's work tracker or a factual report.
3. **Scope the work.** Read the requested target and relevant authorities.
   A system/component alignment includes affected implementation and tests;
   document-only alignment stays within its artifacts. A comprehensive audit
   requires explicit selection. Keep each within the named scope.
4. **Work flows in every direction.** Execution feedback revises plans and
   enables simplification as responsibilities become clear. Consolidate
   overlapping mechanisms and retire unnecessary work in specifications,
   implementation and tests while preserving required behavior and evidence.
   Activity names locate the kind of work, not its position in a sequence.
5. **Decisions guide implementation.** An accepted decision sets direction; it
   does not claim that the system implements that direction.
6. **People decide; agents draft and check.** People own intent and material decisions.
   Agents draft, compare, and surface questions at the governed hand-offs.
7. **HELIX stays small.** HELIX defines methodology and ships one routing skill.
   Execution and tracking belong to the runtime.
8. **Prefer useful evidence to ceremony.** Keep checks that find real defects.
   Do not add gates, reports, or checklist sections only for completeness.
9. **Discipline over improvisation.** Agents improvise well; HELIX makes that
   improvisation reviewable.

## Living documents

Committed documents express current working intent. Expect light drift; use
higher authority to reconcile relevant gaps during authorized work. A material
gap affects user outcomes, scope, requirements, design, safety, or completion
evidence. Lifecycle labels, stale review stamps, and missing edges alone never
block work or justify housekeeping tasks. Keep progress in the relevant plan,
selected work item, or factual report. Explicit domain decisions still apply.

## Authority

The vision governs the PRD, the PRD governs features, and features govern
designs and decisions. The catalog and workflow contracts define how those
artifacts are authored and related. See `workflows/principles.md` for the
methodology statement.

## Tension Resolution

| Tension | Resolution |
|---|---|
| Methodology depth vs. simplicity | Keep detail where readers need it; remove repeated process guidance. |
| Runtime convenience vs. HELIX scope | Put execution conveniences in the runtime adapter. |
| Validation vs. machinery | Keep evidence checks that protect quality; omit ceremony without a concrete failure to prevent. |
| Desired state vs. implementation status | Keep requirements authoritative; report observed status separately. |

## Size Guidance

Keep this file short. Put workflow requirements in `workflows/` and detailed
rationale in the relevant decision record.
