---
title: "Release Notes — HELIX v0.17.0"
slug: release-notes
weight: 550
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

# Release Notes — HELIX v0.17.0

## Release Scope

- Release identifier: `v0.17.0`
- Release date: 2026-10-13
- Previous release: `v0.16.0`
- Scope: requirement-linked verification, bounded experiments, factual
  authoring, progressive planning questions and behavioral regression scenarios.
- Release owner: HELIX maintainer; published through the release PR workflow.

## Audience and Channels

| Audience | Impact | Channel |
|----------|--------|---------|
| HELIX users | Less evidence ceremony and clearer planning boundaries | Plugin and generated bundles |
| Experiment operators | Cumulative limits and honest stopping claims | Experiment guidance |
| Adapter authors | Experiment outcomes without a HELIX wire protocol | Workflow catalog |

## Highlights

- Link requirements and exercising tests to observed results; no shared evidence
  diary, replacement index or additional per-change file is mandatory.
- Scope verification to the promised capability and failure risk while
  preserving applicable guards, security checks and required regression gates.
- Bound experiment runs, retries, parallel work, time, paid usage and temporary
  storage cumulatively; resuming does not reset the allowance.
- Templates and examples supply structure, not project facts. Planning asks the
  smallest unresolved decision; operator-only blockers require a question at
  every autonomy level.

## Required Actions Summary

- Update the plugin or bundle to `v0.17.0`.
- Reconcile local evidence-file rules through `align` and authorized `evolve`
  work. Preserve historical evidence, links and independent audit obligations.
- Adapters using the former experiment output trailer or XML result block must
  own their serialization; these formats are removed from the HELIX action.

## Changes and Fixes

| Area | Change | Effect |
|------|--------|--------|
| Verification (#80–#82) | Reuse observed reports and existing acceptance mappings; scope proof to claims | Reduce duplicate records without weakening completion proof |
| Experiments (#83) | Cumulative resource bounds, conditional enforcement and manual stopping; remove runtime protocol | Work independently of execution adapters; disclose work still running |
| Authoring (#84) | Preserve factual and semantic authority | Prevent example values becoming invented requirements |
| Planning (#85) | Progressive questions and all-autonomy operator-only stops | Avoid repeated questions and unresolved guesses |
| Evaluation (#86) | Five sanitized live regression scenarios and stronger checker/fixture validation | Measure behavior separately from structural checks |

## Breaking Changes and Required Actions

The experiment action no longer defines its runtime integration appendix, XML
result payload or `EXPERIMENT_STATUS` trailer. Adapt consumers of those removed
formats before upgrading. Resource exhaustion remains a semantic HELIX outcome.

A shared evidence file is no longer mandatory. Projects must retain
appropriate requirement → exercising test → observed-result proof and reviewed
exceptions. No installation mechanism changes are introduced.

## Migration or Rollback Guidance

1. Update to `v0.17.0` and review applicable guidance on the next scoped change.
2. Reconcile local verification policy without mechanically migrating history.
3. Update any experiment adapter's serialization and stopping behavior.

To roll back, pin `v0.16.0`; preserve project-owned artifacts and historical
proof. HELIX requires no DDx installation or compatibility gate.

## Known Issues and Support

- Live baseline and combined-candidate scenarios each passed 13/13 deterministic
  checks. Astra's semantic review recorded partial recommendation/rationale and
  desired-state scope items; no fully passing rubric or comparative uplift is
  claimed. See the committed session regression results.
- Optional rendering and signing tools have explicit availability limits;
  unavailable tooling is not proof of successful verification.

Support: open an issue in the HELIX repository.

## References

- Deployment checklist: [deployment-checklist.md](/artifacts/deployment-checklist/)
- Release changes: https://github.com/DocumentDrivenDX/helix/compare/v0.16.0...v0.17.0
- Live validation: `evals/results/20261013-session-regressions/summary.md`
- Bundle publication: `.github/workflows/release-genie-bundle.yml`
- Version guard: `.github/workflows/release-version-guard.yml`
