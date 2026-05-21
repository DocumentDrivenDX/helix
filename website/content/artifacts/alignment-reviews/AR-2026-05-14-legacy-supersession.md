---
title: "Alignment Review: Legacy CLI/Autopilot Artifact Supersession"
slug: AR-2026-05-14-legacy-supersession
weight: 630
activity: "Iterate"
source: "06-iterate/alignment-reviews/AR-2026-05-14-legacy-supersession.md"
generated: true
collection: alignment-reviews
---

> **Source identity** (from `06-iterate/alignment-reviews/AR-2026-05-14-legacy-supersession.md`):

```yaml
ddx:
  id: AR-2026-05-14-legacy-supersession
  depends_on:
    - helix.prd
    - AR-2026-05-12-legacy-cli-autopilot-classification
  review:
    self_hash: c853e5ce054eefb81ee515ccaf1af6e0be61a7378cddc265b3bdaf2fb62b6f58
    deps:
      AR-2026-05-12-legacy-cli-autopilot-classification: d0886e00ae0798ff297a1eb6ccb4b0dc1fd6056a71d92c1cc07448735d8d55a7
      helix.prd: 703d5ebaa378d037fd5ff6cbdf43e015ee014ca6a29b5df0b4c67ba9b117a510
    reviewed_at: "2026-05-15T04:11:24Z"
```

# Alignment Review: Legacy CLI/Autopilot Artifact Supersession

**Date**: 2026-05-14
**Bead**: helix-7ccd819f
**Scope**: Execute the supersession actions recommended by
AR-2026-05-12-legacy-cli-autopilot-classification. Add `superseded_by`
frontmatter and top-of-body banners to every legacy CLI/autopilot artifact
identified in that review.

## Classification and Actions

| Artifact | Classification | Action |
|---|---|---|
| `docs/helix/01-frame/features/FEAT-001-helix-supervisory-control.md` | superseded-by-prd | Added `status: superseded`, `superseded_by: helix.prd`, and SUPERSEDED banner. |
| `docs/helix/01-frame/features/FEAT-002-helix-cli.md` | partially-superseded | Added `status: partially-superseded`, `superseded_by: helix.prd`, and PARTIALLY SUPERSEDED banner noting CLI survives as DDx adapter only. |
| `docs/helix/01-frame/features/FEAT-004-plugin-packaging.md` | partially-superseded | Added `status: partially-superseded`, `superseded_by: helix.prd`, and PARTIALLY SUPERSEDED banner. CLI/autopilot distribution aspects superseded; runtime packaging concept (PRD R-7) survives. |
| `docs/helix/01-frame/features/FEAT-005-execution-backed-output.md` | superseded-by-prd | Added `status: superseded`, `superseded_by: helix.prd`, and SUPERSEDED banner. Execution capture is a runtime concern. |
| `docs/helix/01-frame/features/FEAT-011-slider-autonomy.md` | superseded-by-prd | Added `status: superseded`, `superseded_by: helix.prd`, and SUPERSEDED banner. Autonomy UX belongs to the runtime. |
| `docs/helix/02-design/adr/ADR-001-supervisory-control-model.md` | superseded-by-prd | Added `status: superseded`, `superseded_by: helix.prd`, and SUPERSEDED banner. PRD reverses the architectural boundary this ADR established. |
| `docs/helix/02-design/solution-designs/SD-001-helix-supervisory-control.md` | superseded-by-prd | Added `status: superseded`, `superseded_by: helix.prd`, and SUPERSEDED banner. |
| `docs/helix/02-design/technical-designs/TD-002-helix-cli.md` | partially-superseded | Added `status: partially-superseded`, `superseded_by: helix.prd`, and PARTIALLY SUPERSEDED banner. Survives as DDx adapter documentation. |
| `docs/helix/02-design/technical-designs/TD-011-slider-autonomy-implementation.md` | superseded-by-prd | Added `status: superseded`, `superseded_by: helix.prd`, and SUPERSEDED banner. |
| `docs/helix/03-test/test-plans/STP-002-helix-cli.md` | partially-superseded | Added `status: partially-superseded`, `superseded_by: helix.prd`, and PARTIALLY SUPERSEDED banner. Survives as DDx adapter/transition compatibility test coverage. |
| `docs/helix/02-design/architecture.md` | needs-rework | Added `status: needs-rework` frontmatter and NEEDS REWORK banner. Rewrite required; follow-up bead filed (see below). |
| `docs/helix/02-design/plan-2026-03-27-supervisory-concurrency.md` | superseded-by-prd | Added frontmatter with `status: superseded`, `superseded_by: helix.prd`, and SUPERSEDED banner. |
| `docs/helix/04-build/implementation-plan.md` | superseded-by-prd | Added `status: superseded`, `superseded_by: helix.prd`, and SUPERSEDED banner. Scoped to FEAT-011 slider autonomy, which is superseded. |

Artifacts left untouched (classified as still-active in AR-2026-05-12):

| Artifact | Classification |
|---|---|
| `FEAT-003-principles.md` | still-active |
| `FEAT-006-concerns-practices-context-digest.md` | still-active |
| `FEAT-007-microsite-and-demos.md` | still-active (not mentioned in PRD open questions) |
| `FEAT-008-artifact-template-quality.md` | still-active |
| `FEAT-009-team-onboarding.md` | still-active |
| `FEAT-010-testing-strategy-templates.md` | still-active |
| `FEAT-012-public-microsite-ia.md` | still-active |
| `ADR-002-tracker-write-safety-model.md` | still-active (DDx tracker concern, not CLI/autopilot) |
| `docs/helix/02-design/contracts/CONTRACT-001-ddx-helix-boundary.md` | still-active |
| `docs/helix/02-design/contracts/CONTRACT-002-helix-execution-doc-conventions.md` | still-active |

## Banner Template Used

```
> **SUPERSEDED** — [One sentence explaining what this artifact defined and
> why it is superseded.] The current PRD (`helix.prd`) [explains the scope
> change]. This document is retained for historical context only and must
> not govern new HELIX work.
```

For partially-superseded artifacts the banner notes which portions survive
and in what context (DDx adapter, runtime distribution, etc.).

## Follow-Up Bead Filed

A follow-up bead was filed for `docs/helix/02-design/architecture.md`:
**helix-b6a1b801** — "Rewrite architecture.md as runtime-neutral HELIX
architecture". Rewrite should center catalog, artifact schema, skill
contract, packaging, and documentation projection as the primary
architectural concerns, with DDx appearing only as a reference runtime
integration.

## What Was NOT Done

- No artifacts were deleted. Supersession is additive per constraints.
- `workflows/`, `skills/`, and other non-`docs/helix/` files were not
  touched per constraints.
- `.ddx/beads.jsonl` was not modified directly.
- No commit was made.
- The implementation-plan-2026-04-11-snapshot.md in `04-build/` was not
  touched (it is a dated snapshot, not a governing artifact; disposition
  deferred to maintainer).
- CONTRACT-001-audit.md was not touched (it is an audit artifact, not a
  governing feature or design doc).
