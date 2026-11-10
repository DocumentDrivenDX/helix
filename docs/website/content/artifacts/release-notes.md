---
title: "Release Notes — HELIX v0.22.0"
slug: release-notes
weight: 670
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

# Release Notes — HELIX v0.22.0

## Release Scope

- Release identifier: `v0.22.0`
- Release date: 2026-11-10
- Previous release: `v0.21.0`
- Scope: structured ratings for technology assessments, structured recommendations for
  position papers, figure provenance, and keys; slimmer pull-request CI.
- Release owner: HELIX maintainer; published through the release PR workflow.

## Audience and Channels

| Audience | Impact | Channel |
|----------|--------|---------|
| Teams keeping a technology atlas | Assessment ratings and paper recommendations as checked data | Plugin and bundles |
| Existing HELIX users | None: every new field is optional | Plugin and bundles |
| HELIX maintainers | Heavy suites run on release or the `ci:full` label | Repository CI |

## Highlights

- A `technology-assessment` may keep its criteria and ratings as data in an `assessment:`
  front matter block. It holds criteria ids from a shared `criteria.yml`, subjects, and a
  finding or a stated gap for each pair. `assessment-tables.py` makes the Criteria and
  Comparison tables from it and fails when they drift.
- A `position-paper` may record stances in a `recommendations:` list. A stance is
  recommended, conditional, watch, or avoid. Each has a rationale, the pinned assessments
  it rests on, a review date, and approval given whole. Only a position paper has one.
- A figure may end with `{basis=published accessed=2026-11-06 source="..."}`.
  `validate-instance.py` requires `source` and `accessed` unless the basis is `not-published`.
- A `keys.yml` at the flow root maps short names to document ids, usable in the two blocks.
  A document records what each key resolved to, so repointing a key is a finding, not a
  silent change. `ddx.links` keep full ids and pinned revs.

## Required Actions Summary

- None. Documents without these fields validate as before.
- A repository that built its own `atlas:` ratings block can move to `assessment:` and
  `recommendations:` and drop its table generator.

## Changes and Fixes

### New or Improved

| Area | What changed | Who is affected |
|------|--------------|-----------------|
| Assessments | `assessment:` block, shared `criteria.yml`, generated tables, shape checks | Atlas authors |
| Position papers | `recommendations:` list with stance, rationale, pins, review date, approval | Atlas authors |
| Provenance | `{basis=... accessed=... source=...}` on figures, checked wherever it appears | Authors of briefs |
| Keys | `keys.yml`, recorded resolution, shadow and duplicate checks | Atlas authors |
| CI | Pull requests run a slim suite; heavy suites run on release or `ci:full`, with an evidence gate | Maintainers |

### Fixes

| Issue or symptom | Resolution | User or operator impact |
|------------------|------------|-------------------------|
| Findings on a document body reported a line one too low | The body offset now counts the closing front matter delimiter | Line numbers in `validate-instance.py` output match the file |

## Breaking Changes and Required Actions

There are no breaking changes and no migrations.

## Migration or Rollback Guidance

### Upgrade or Migration

1. Update the plugin. Add the new blocks only where you want them checked.

### Rollback or Hold Guidance

- Pin `v0.21.0` to roll back; the new blocks would then go unchecked.
- Ask for help in the HELIX repository's issues.

## Known Issues and Support

| Issue | Who is affected | Workaround or next step |
|------|------------------|-------------------------|
| No check reads other documents: a cited assessment's links and findings, or a stance repeated across papers | Authors of recommendations | Check by hand until a graph-level check exists |
| `key:` is not accepted inside `ddx.links` | Authors using keys | Keep the full id in `ddx.links`; use the key in the blocks |
| The `{...}` notation is HELIX's own, not DITA or MDITA | Anyone expecting DITA interchange | None; a DITA processor drops it |

Support: open an issue in the HELIX repository.

## References

- Deployment checklist: [deployment-checklist.md](/artifacts/deployment-checklist/)
- Pull requests: #114, #115, #116
- Release changes: https://github.com/DocumentDrivenDX/helix/compare/v0.21.0...v0.22.0
- Bundle publication: `.github/workflows/release-genie-bundle.yml`
- Version guard: `.github/workflows/release-version-guard.yml`
