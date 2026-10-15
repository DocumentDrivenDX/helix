---
title: "Release Notes — HELIX v0.16.0"
slug: release-notes
weight: 580
activity: "Deploy"
source: "05-deploy/release-notes.md"
generated: true
---

> **Example from HELIX's own docs.** This generated page comes from `docs/helix/`. Use it to see the method in practice; start with the [artifact-type catalog](/artifact-types/) for reusable templates. Historical plans and reports may describe retired architecture.

> **Source identity** (from `05-deploy/release-notes.md`):

```yaml
ddx:
  id: release-notes
  authoring:
    home: repo
  depends_on:
    - deployment-checklist
  review:
    self_hash: fb47a9c6a156682c88a3f34e22cdb968b09f586f711e82b16ab068d2cb85f553
    deps:
      deployment-checklist: 00556985f9bfc7cabe6c1288473bb2935f3fe4a83fb5fcd53918e95bf29e5d21
    reviewed_at: "2026-10-04T03:52:23Z"
```

# Release Notes — HELIX v0.16.0

## Release Scope

- Release identifier: `v0.16.0`
- Release date: 2026-10-11
- Previous release: `v0.15.4`
- Scope: intent-driven templates, concern library reconciliation, token-based
  estimates and spending bounds, model gateways, and UX governance.
- Release owner: HELIX maintainer; the release PR triggers annotated tagging
  and generated plugin/Genie bundle publication.

## Audience and Channels

| Audience | Impact | Channel |
|----------|--------|---------|
| HELIX users | Clearer templates and concern guidance | Plugin and concern catalog |
| Runtime integrators | Token-based estimates and bounded spending | Planning and execution guidance |
| Website readers | Updated artifact and concern references | Public reference website |

## Highlights

- Templates carry intent rather than repetitive record-keeping. ADRs record
  deviations rather than routine concern selections.
- Agent estimates use token evidence and process spending bounds.
- Model-gateway guidance includes a Databricks AI Gateway realization.
- UX patterns and packaged design systems receive explicit governance.
- The concern library removes stale references, contradictions and ceremony.

## Required Actions Summary

- Update the plugin or generated bundle to `v0.16.0`.
- Apply revised templates and concern guidance when authoring or revisiting
  affected artifacts; preserve historical decisions and evidence.

## Changes and Fixes

| PR | Change | Effect |
|----|--------|--------|
| #73 | Ground agent estimates in token usage and bound process spending | Evidence-based estimates and bounded process budgets |
| #74 | Templates carry intent, not record-keeping | Reduce redundant artifact ceremony |
| #75 | Add model-gateway concern and Databricks AI Gateway realization | Govern model access through gateway guidance |
| #76 | Reconcile the concern library | Repair stale references and conflicting guidance |
| #77 | ADRs record deviations, not concern selections | Reserve decision records for meaningful deviations |
| #78 | Govern UX patterns and packaged design systems | Explicit UX coverage and concern composition |

## Breaking Changes and Required Actions

This release changes authoring guidance and template expectations. Review
applicable templates when refreshing project artifacts. No installation
mechanism changes are introduced by these six PRs.

## Migration or Rollback Guidance

1. Update to `v0.16.0`.
2. Review affected templates, estimates, ADRs and selected concerns on the next
   scoped artifact update.
3. Select model-gateway or UX guidance where applicable to the project.

To roll back the plugin, pin `v0.15.4`. Preserve project-owned artifacts and
historical evidence.

## Known Issues and Support

- Methodology guidance still requires project-specific review and evidence.
- Optional rendering and signing lanes require external tools; unavailable
  tools are reported as skips rather than verification successes.

Support: open an issue in the HELIX repository.

## References

- Deployment checklist: [deployment-checklist.md](/artifacts/deployment-checklist/)
- Release changes: https://github.com/DocumentDrivenDX/helix/compare/v0.15.4...v0.16.0
- Bundle publication: `.github/workflows/release-genie-bundle.yml`
- Version guard: `.github/workflows/release-version-guard.yml`
