---
title: "Alignment Review: Legacy CLI and Autopilot Artifact Classification"
slug: AR-2026-05-12-legacy-cli-autopilot-classification
weight: 620
activity: "Iterate"
source: "06-iterate/alignment-reviews/AR-2026-05-12-legacy-cli-autopilot-classification.md"
generated: true
collection: alignment-reviews
---

> **Source identity** (from `06-iterate/alignment-reviews/AR-2026-05-12-legacy-cli-autopilot-classification.md`):

```yaml
ddx:
  id: AR-2026-05-12-legacy-cli-autopilot-classification
  depends_on:
    - helix.prd
  review:
    self_hash: d0886e00ae0798ff297a1eb6ccb4b0dc1fd6056a71d92c1cc07448735d8d55a7
    deps:
      helix.prd: 703d5ebaa378d037fd5ff6cbdf43e015ee014ca6a29b5df0b4c67ba9b117a510
    reviewed_at: "2026-05-15T04:11:24Z"
  status: superseded
  superseded_at: 2026-05-21
  superseded_reason: |
    HELIX collapsed to content-only methodology; CLI surface (scripts/helix, bin/helix, execute-loop, HELIX_SELECTED_ISSUE) was removed in commit 823aa1ac. Historical reference only — do not act on CLI commands in this document.
```

# Alignment Review: Legacy CLI and Autopilot Artifact Classification

**Date**: 2026-05-12
**Bead**: helix-7ccd819f
**Scope**: Legacy CLI, supervisory-control, slider-autonomy, architecture, and
implementation-planning artifacts that still present HELIX as a runtime,
tracker, CLI, or autopilot system.

## Governing Direction

The current product vision and PRD define HELIX as a portable methodology:

- methodology documentation
- authority-ordered artifact catalog
- artifact templates, prompts, metadata, and examples
- one portable alignment/planning skill

The PRD explicitly states that HELIX does not provide a CLI, tracker, queue,
execution loop, or runtime infrastructure. DDx remains important as the
reference runtime integration, but DDx integration docs cannot define HELIX's
product identity.

This review classifies legacy governing artifacts against that direction. It
does not modify the artifacts themselves.

## Classification Values

| Value | Meaning |
|---|---|
| runtime-neutral core | Survives as part of HELIX's portable methodology with little or no runtime-specific framing. |
| DDx integration only | May survive only after being moved or rewritten as DDx adapter/reference-runtime documentation. |
| historical/superseded | Records past direction but must stop governing current product behavior. |
| retire | Should be removed from active governing docs after any necessary historical note or replacement is created. |
| needs decision | Requires maintainer decision before rewrite, move, or retirement. |

## Classification Table

| Artifact | Classification | Reason | Recommended disposition |
|---|---|---|---|
| `docs/helix/01-frame/features/FEAT-001-helix-supervisory-control.md` | historical/superseded | Defines `helix-run` as HELIX's supervisory autopilot and treats tracker-first execution as a HELIX product capability. That conflicts with the PRD boundary that execution belongs to runtimes. | Mark superseded by the current PRD. Extract any still-useful loop-control concepts into DDx reference-runtime docs only if DDx needs them. Do not keep this as a core HELIX feature. |
| `docs/helix/01-frame/features/FEAT-002-helix-cli.md` | DDx integration only | Specifies a HELIX CLI surface and wrapper behavior. A CLI can exist as a DDx compatibility or development adapter, but it is not part of HELIX's portable product definition. | Move or rewrite as a DDx adapter feature if still needed. Replace core references to this feature with the runtime-neutral alignment skill contract. |
| `docs/helix/01-frame/features/FEAT-011-slider-autonomy.md` | retire | Defines operator-facing autonomy controls for `helix run`. This is execution-loop UX, not methodology or portable artifact-catalog behavior. | Retire from active HELIX governing artifacts. If DDx wants an autonomy slider, recreate it in DDx-owned integration docs with no implication that HELIX owns the runtime loop. |
| `docs/helix/02-design/adr/ADR-001-supervisory-control-model.md` | historical/superseded | Records an architectural decision to make HELIX supervisory control explicit through `helix-run`. The current PRD reverses that boundary by making runtime orchestration out of scope. | Supersede with a new ADR that codifies HELIX as runtime-neutral content plus one alignment/planning skill, with DDx as a reference runtime. |
| `docs/helix/02-design/solution-designs/SD-001-helix-supervisory-control.md` | historical/superseded | Designs HELIX as a supervisory control system. Its core premise is incompatible with the current product direction. | Mark superseded. Preserve only concepts that describe artifact authority, alignment triggers, or stop conditions, and move those into runtime-neutral methodology docs or DDx integration docs as appropriate. |
| `docs/helix/02-design/technical-designs/TD-002-helix-cli.md` | DDx integration only | Describes technical implementation of a CLI wrapper and associated command behavior. This may remain useful for transition or DDx packaging, but it is not a core HELIX technical design. | Move or rewrite under a DDx integration section. Any retained design must state that the CLI is adapter/runtime glue, not HELIX's primary product surface. |
| `docs/helix/02-design/technical-designs/TD-011-slider-autonomy-implementation.md` | retire | Implements the retired slider-autonomy concept for `helix run`. It deepens runtime-loop ownership and therefore should not govern HELIX. | Retire after confirming no open DDx adapter work still depends on it. If needed, recreate the concept in DDx-owned docs rather than preserving this HELIX technical design. |
| `docs/helix/03-test/test-plans/STP-002-helix-cli.md` | DDx integration only | Test plan validates wrapper CLI behavior, tracker operations, and run-loop mechanics. These are useful for the DDx adapter or transitional compatibility surface, not for HELIX core. | Move or relabel as DDx adapter test coverage. Core HELIX validation should instead test catalog completeness, artifact schema, and portable alignment skill behavior. |
| `docs/helix/02-design/architecture.md` | needs decision | Currently presents HELIX as a methodology layer running on DDx with `scripts/helix`, one skill per CLI verb, and DDx-owned execution services as core architecture. The repo still needs an architecture artifact, but this one is not aligned. | Rewrite as the runtime-neutral HELIX architecture. Move DDx-specific deployment, tracker, and CLI sections into a separate DDx reference-runtime architecture note. |
| `docs/helix/04-build/implementation-plan.md` | retire | Build plan is scoped to slider autonomy and `helix run --autonomy`, which is no longer a product direction for HELIX core. | Retire from active build planning. Replace with implementation plans for artifact schema completion, template metadata, portable alignment skill, and public documentation projection. |

## Cross-Cutting Findings

| Finding | Impact | Follow-on work |
|---|---|---|
| Legacy artifacts still define HELIX through `helix run`, `scripts/helix`, DDx beads, tracker-first execution, and wrapper tests. | Public and internal readers can reasonably conclude that HELIX is a DDx-backed CLI/autopilot product, contradicting the PRD. | Create a supersession pass that marks or moves each legacy artifact according to the classification above. |
| DDx integration material is mixed into core HELIX governing artifacts. | The reference runtime becomes indistinguishable from the methodology. This blocks adoption by Genie, Claude Code, Cursor, or any runtime that does not share DDx's tracker model. | Create a dedicated DDx reference-runtime documentation area and move reusable DDx-specific content there. |
| The architecture artifact is both necessary and divergent. | Removing it without replacement would leave HELIX without a design-level view, but keeping it as-is preserves the old product identity. | Author a new runtime-neutral architecture that centers catalog, schema, skill contract, packaging, and documentation projection. |
| CLI and wrapper test plans still encode valid transition coverage. | Immediate deletion may lose useful compatibility checks while DDx integration remains supported. | Reclassify wrapper tests as DDx adapter tests and add separate core tests for catalog/schema/skill portability. |
| Slider autonomy has no clear survivor in the new product shape. | Continuing to maintain it would pull HELIX back into runtime UX and execution orchestration. | Close or supersede open slider-autonomy work unless it is explicitly transferred to DDx integration ownership. |

## Recommended Follow-On Work

1. Create a supersession bead to mark FEAT-001, ADR-001, SD-001, and related supervisory-control docs as superseded by the current PRD.
2. Create a DDx integration documentation bead to move or rewrite FEAT-002, TD-002, and STP-002 as adapter/reference-runtime material.
3. Create a retirement bead for FEAT-011, TD-011, and the slider-autonomy build plan.
4. Create a runtime-neutral architecture rewrite bead for `docs/helix/02-design/architecture.md`.
5. Create a core validation bead that replaces CLI-wrapper-centric proof with checks for artifact schema completeness, template metadata, and alignment-skill portability.
6. Update the Hugo projection after the supersession/move work so generated pages do not present superseded CLI/autopilot artifacts as current HELIX doctrine.

## Decision Needed

`docs/helix/02-design/architecture.md` should not simply be retired. HELIX
still needs a core architecture artifact, but maintainers should decide whether
to rewrite it in place or add a replacement architecture artifact and mark the
current file superseded.

## Conclusion

DDx integration docs may survive, but only as reference-runtime integration
material. They cannot define HELIX's product identity. The active HELIX spine
should be:

1. artifact schema
2. artifact templates and metadata
3. portable alignment/planning skill
4. runtime-neutral methodology documentation
5. public documentation projection
6. DDx adapter as one integration, not the product core
