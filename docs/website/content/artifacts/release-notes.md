---
title: "Release Notes — HELIX v0.25.1"
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

# Release Notes — HELIX v0.25.1

## Release Scope

- Release identifier: `v0.25.1`
- Release date: 2026-11-27
- Previous release: `v0.25.0`
- Scope: HELIX is published to the DocumentDrivenDX plugin marketplace, is licensed `MIT OR Apache-2.0`, and draftsync no longer inserts a landed block twice.
- Release owner: HELIX maintainer, publishing through the release PR workflow.

## Audience and Channels

| Audience | Impact | Channel |
|----------|--------|---------|
| Claude Code users | Can install `helix@documentdrivendx` | DocumentDrivenDX plugin marketplace |
| draftsync users | A write-back skips a block that git already took from the draft | draftsync uv tool |

## Highlights

- Each release now publishes the plugin to the DocumentDrivenDX marketplace. The `helix@helix` marketplace stays in service.
- HELIX is licensed `MIT OR Apache-2.0`, and the plugin package ships the license files.
- `draftsync doc-ops` no longer inserts a reviewer's added paragraph or table row a second time after it lands in git.

## Required Actions Summary

- None. Existing installs of `helix@helix` keep working.

## Changes and Fixes

| Area | What changed | Who is affected |
|------|--------------|-----------------|
| Distribution | The release workflow publishes `plugins/helix` to DocumentDrivenDX/plugins | Claude Code users |
| License | `MIT OR Apache-2.0` | Anyone who uses or redistributes HELIX |
| draftsync | The write-back pairs added git blocks with blocks the draft already holds, and reports close matches to compare by hand | draftsync users |

## Breaking Changes and Required Actions

No breaking changes.

## Migration or Rollback Guidance

Pin `v0.25.0` to return to the previous release.

## Known Issues and Support

- If git rewrites a landed block heavily, draftsync can still insert it again. If git deletes a landed block, the draft keeps it and nothing is reported.
- Open a GitHub issue in the HELIX repository for support.

## References

- Deployment checklist: [deployment-checklist.md](/artifacts/deployment-checklist/)
- Pull requests: #134, #135
- Release changes: https://github.com/DocumentDrivenDX/helix/compare/v0.25.0...v0.25.1
- Bundle publication: `.github/workflows/release-genie-bundle.yml`
