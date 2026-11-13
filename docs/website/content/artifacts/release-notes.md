---
title: "Release Notes — HELIX v0.24.0"
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

# Release Notes — HELIX v0.24.0

## Release Scope

- Release identifier: `v0.24.0`
- Release date: 2026-11-12
- Previous release: `v0.23.0`
- Scope: shared document editing, bidirectional draft sync, and the installable draftsync tool.
- Release owner: HELIX maintainer, publishing through the release PR workflow.

## Audience and Channels

| Audience | Impact | Channel |
|----------|--------|---------|
| Teams reviewing governed documents in Claude Docs | Open a shared draft, review changes, and land edits through a pull request | HELIX plugin and Claude Docs adapter |
| Teams keeping drafts open after merge | Sync edits in both directions using a recorded binding | HELIX plugin and draftsync |
| Maintainers | Claude, Codex, marketplace, documentor, and draftsync versions advance together | GitHub release |

## Highlights

- The shared-edit mode lets authors review a governed document in Claude Docs while keeping the repository as the record. Draftsync applies body edits as a patch and leaves front matter in Git.
- A persistent binding records the draft address, revision, and Git base. Draftsync can prepare changes in either direction and resolves text conflicts toward the document's declared authoring home.
- Draftsync ships as a standalone uv tool and can be installed directly from the HELIX tag.

## Required Actions Summary

- To use shared editing, update HELIX and install draftsync from the same tag. Existing projects can continue with their current editing workflow.

## Changes and Fixes

| Area | What changed | Who is affected |
|------|--------------|-----------------|
| Shared editing | Added the workflow, Claude Docs adapter, and patch validation | Document authors and reviewers |
| Persistent bindings | Added status, draft-to-Git and Git-to-draft operations, and an optional Claude Code edit hook | Teams maintaining shared drafts |
| Packaging | Added a tagged uv install target and version checks for draftsync | Operators and maintainers |

## Breaking Changes and Required Actions

Existing projects require no migration. Shared editing requires a runtime with a supported editing surface and the draftsync tool.

## Migration or Rollback Guidance

Install the tool for this release:

```sh
uv tool install 'git+https://github.com/DocumentDrivenDX/helix@v0.24.0#subdirectory=tools/draftsync'
draftsync --help
```

To return to the prior workflow, pin HELIX to `v0.23.0` and remove the optional draftsync hook if you registered it.

## Known Issues and Support

The shipped editing adapter supports Claude Docs. Sync reports formatting changes, new lists and tables, and deleted blocks for manual review when preparing Git-to-draft changes.

Open a GitHub issue in the HELIX repository for support.

## References

- Deployment checklist: [deployment-checklist.md](/artifacts/deployment-checklist/)
- Pull requests: #128, #129, #130
- Release changes: https://github.com/DocumentDrivenDX/helix/compare/v0.23.0...v0.24.0
- Bundle publication: `.github/workflows/release-genie-bundle.yml`
- Version guard: `.github/workflows/release-version-guard.yml`
