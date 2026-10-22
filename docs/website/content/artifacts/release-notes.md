---
title: "Release Notes — HELIX v0.19.1"
slug: release-notes
weight: 610
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

# Release Notes — HELIX v0.19.1

## Release Scope

- Release identifier: `v0.19.1`
- Release date: 2026-10-22
- Previous release: `v0.19.0`
- Scope: a patch to documentor's version report. The guide mode and documentor themselves
  arrived in `v0.19.0`; its notes are at the `v0.19.0` tag.
- Release owner: HELIX maintainer; published through the release PR workflow.

## Audience and Channels

| Audience | Impact | Channel |
|----------|--------|---------|
| documentor users | `documentor --version` names the release its catalog shipped in | documentor, installed from the tag |
| HELIX users | No change to the skill or the catalog | Plugin and bundles |

## Highlights

- `documentor --version` now prints `documentor 0.19.1 (HELIX catalog packaged 0.19.1)`.
  In `v0.19.0` it printed `packaged in-repo`, which named no release.

## Required Actions Summary

- Install documentor from this tag:
  `uv tool install --force "git+https://github.com/DocumentDrivenDX/helix@v0.19.1#subdirectory=tools/documentor"`.
- Plugin users need no action.

## Changes and Fixes

### New or Improved

| Area | What changed | Who is affected |
|------|--------------|-----------------|
| None | This release fixes one report and adds nothing. | — |

### Fixes

| Issue or symptom | Resolution | User or operator impact |
|------------------|------------|-------------------------|
| `documentor --version` printed `packaged in-repo` | It prints the package's own version, which equals the HELIX release | A reader can tell which catalog an installed documentor carries |

## Breaking Changes and Required Actions

There are no breaking changes and no migrations.

| Change | Impact | Required action | Deadline or trigger |
|--------|--------|-----------------|---------------------|
| None | — | — | — |

## Migration or Rollback Guidance

### Upgrade or Migration

1. Reinstall documentor from `v0.19.1`, or update the pin in a CI workflow copied from
   documentor's template.

### Rollback or Hold Guidance

- Pin `v0.19.0` to roll back; only the version line differs.
- Ask for help in the HELIX repository's issues.

## Known Issues and Support

| Issue | Who is affected | Workaround or next step |
|------|------------------|-------------------------|
| Writing pages needs an agent and its credentials | `documentor write` users | Run it where the agent is signed in; the CI check needs no agent |
| The evaluating model sometimes returns no verdict | `documentor write` users | Run `write` again, or evaluate with `documentor prompt --reviewer` and record it with `documentor review` |

Support: open an issue in the HELIX repository.

## References

- Deployment checklist: [deployment-checklist.md](/artifacts/deployment-checklist/)
- Release changes: https://github.com/DocumentDrivenDX/helix/compare/v0.19.0...v0.19.1
- Bundle publication: `.github/workflows/release-genie-bundle.yml`
- Version guard: `.github/workflows/release-version-guard.yml`
