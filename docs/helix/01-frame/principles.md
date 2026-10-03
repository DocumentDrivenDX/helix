---
ddx:
  id: helix.principles
  authoring:
    home: repo
  depends_on:
    - helix.prd
    - helix.product-vision
  review:
    self_hash: 23db2c830aa9a8cabe8d7b6701b4da13bbe04bc979a9c0dc24900f1de2093cf2
    deps:
      helix.prd: e11b46de6300cc84460245fcfd6739210ce38406a76f90e32d26685938302eb1
      helix.product-vision: 13555b55d11d13ad2c01657a4f3b9c421867ca9f41dfb575c829ecb7c0990164
    reviewed_at: "2026-06-14T03:20:37Z"
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
3. **Scope the work.** Read the requested artifact and the authorities that can
   affect the change. Audit implementation only when explicitly requested and
   within the named scope.
4. **Decisions guide implementation.** An accepted decision sets direction; it
   does not claim that the system implements that direction.
5. **People decide; agents draft and check.** People own intent and approval.
   Agents draft, compare, and surface questions at the governed hand-offs.
6. **HELIX stays small.** HELIX defines methodology and ships one routing skill.
   Execution and tracking belong to the runtime.
7. **Prefer useful evidence to ceremony.** Keep checks that find real defects.
   Do not add gates, reports, or checklist sections only for completeness.

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
