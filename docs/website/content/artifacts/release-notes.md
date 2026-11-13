---
title: "Release Notes — HELIX v0.25.0"
slug: release-notes
weight: 690
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

# Release Notes — HELIX v0.25.0

## Release Scope

- Release identifier: `v0.25.0`
- Release date: 2026-11-12
- Previous release: `v0.24.0`
- Scope: technology assessments can cover engineering practices.
- Release owner: HELIX maintainer, publishing through the release PR workflow.

## Audience and Channels

| Audience | Impact | Channel |
|----------|--------|---------|
| Technology atlas authors | Can document a practice in a technology assessment | HELIX plugin and skill bundles |

## Highlights

- Use `scope: practice` on a technology assessment to describe how a practice works, when to apply it, and what sources support the findings.
- Practice assessments require Scope, Findings, and Sources. Product comparison sections are optional for this scope.
- The catalog includes a practice assessment of continuous integration for web applications.

## Required Actions Summary

- Use the new scope when assessing a practice on its own. Existing assessments require no migration.

## Changes and Fixes

| Area | What changed | Who is affected |
|------|--------------|-----------------|
| Technology assessment | Added a practice scope with its own validation rules, authoring guidance, and example | Technology atlas authors |

## Breaking Changes and Required Actions

The existing technology comparison scope keeps its validation rules.

## Migration or Rollback Guidance

Pin `v0.24.0` to return to the previous assessment catalog.

## Known Issues and Support

Open a GitHub issue in the HELIX repository for support.

## References

- Deployment checklist: [deployment-checklist.md](/artifacts/deployment-checklist/)
- Pull request: #132
- Release changes: https://github.com/DocumentDrivenDX/helix/compare/v0.24.0...v0.25.0
- Bundle publication: `.github/workflows/release-genie-bundle.yml`
