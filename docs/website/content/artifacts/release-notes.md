---
title: "Release Notes — HELIX v0.14.1"
slug: release-notes
weight: 490
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
    self_hash: 99574883788300395089b39ca0b1918d4a23f359269390fa4717bc0fc0c41f51
    deps:
      deployment-checklist: 78c9688645de24f33182dca537e13d0fb180abb4773ab85b48468e495a92bad1
    reviewed_at: "2026-09-17T19:23:17Z"
```

# Release Notes — HELIX v0.14.1

## Release Scope

- Release identifier or version: `v0.14.1`
- Release date: 2026-10-01 (operator-driven; tagged by CI)
- Rollout window or environment: HELIX plugin (Claude Code marketplace, Codex
  plugin, Databricks Genie bundle, Grok Build) and the public website at
  `https://documentdrivendx.github.io/helix/`
- Release owner: HELIX maintainer cutting the tag
- Previous release: `v0.14.0` (2026-09-22)

## Audience and Channels

| Audience | Why they care | Delivery channel |
|----------|---------------|------------------|
| HELIX plugin users | A refreshed Databricks Apps concern and two new concerns for a React + Vite frontend on a non-Node backend | Plugin repo tag; marketplace update |
| Website readers | The three concern pages are regenerated | GitHub Pages rebuild |
| HELIX maintainers | A hand-made release can no longer stay published with mismatched manifests | This file and `.github/workflows/release-version-guard.yml` |

## Highlights

- **The `databricks-apps` deploy-target concern is refreshed against the
  Databricks Apps documentation as of 2026-10-01.** It now covers the
  process contract (array `command`, `$DATABRICKS_APP_PORT`, a 15 s SIGTERM,
  cleartext behind the TLS proxy), `app.yaml` semantics, identity (the app
  service principal versus on-behalf-of through `x-forwarded-access-token`),
  dependency resolution (a `requirements.txt` silently switches the app to
  pip and Python 3.11), the root `package.json` build hook, horizontal
  scaling and statelessness, bundle deploys that require `bundle run`, and
  the platform's documented anti-patterns as drift signals. Questions the
  documentation leaves open are recorded as named spikes.
- **`react-vite` is a new, non-default `frontend-framework` filler.** It
  describes a client-rendered React + Vite + TypeScript app served as static
  files by the backend, with the dev proxy, the build-output hand-off, `VITE_`
  environment exposure, and toolchain defaults that yield to `typescript-bun`.
- **`databricks-appkit-ui` is a new composable concern.** It covers
  `@databricks/appkit-ui` used standalone with a non-Node backend: the `-ui`
  package only, 0.x version pinning, data mode until the standalone spike
  reports, and its relationship to `ux-radix`. `concern-resolution.md` carries
  a friction entry for python-uv with the three.
- **A mismatched release is unpublished, not just reported.** `v0.14.1` was
  first created through the Releases UI while its manifests still
  declared `0.14.0`, which is the failure the `v0.14.0` auto-tag was meant to
  prevent. The version guard now deletes the tag and its release when the
  manifests disagree, so a plugin updater never sees it.

## Required Actions Summary

- Users: none.
- Operators: none. CI creates the release tag after approval; do not create
  it through the Releases UI.
- Support: none.

## Changes and Fixes

### New or Improved

| Area | What changed | Who is affected |
|------|--------------|-----------------|
| Concerns | `databricks-apps` rewritten against current platform documentation; `react-vite` and `databricks-appkit-ui` added; the `practices.md` boundary section removed per ADR-006 | HELIX users deploying to Databricks Apps |
| Routing | `concern-resolution.md` gains a composed-concern friction entry for python-uv, databricks-apps, react-vite, and databricks-appkit-ui | HELIX users |
| CI | `release-version-guard.yml` deletes a `v*` tag and its release when the manifests do not declare the tag's version | Maintainers |

### Fixes

| Issue or symptom | Resolution | User or operator impact |
|------------------|------------|-------------------------|
| The Pages deploy failed on any stale Innsigle seal, although CI checks only warn | `pages.yml` runs `tests/validate-innsigle.sh`, the same gate as CI checks; two stale curated pages were resealed | The site publishes a release without the human signing key |
| `release-tag.yml` interpolated the release title into its shell step | The title is passed through the environment | A title with quotes or shell syntax cannot break the step |
| The first `v0.14.1` tag and release carried `0.14.0` manifests | CI deleted and recreated the release with matching manifests | The release had no downloads before it was replaced |

## Breaking Changes and Required Actions

- None. Existing artifacts, modes, and installs are unaffected.

## Migration or Rollback Guidance

- Migration: pull the tag. Nothing to regenerate for plugin consumers.
- Rollback: install the `v0.14.0` tag. The website rebuilds from `main` and
  is not pinned to a tag.

## Known Issues and Support

| Issue | Who is affected | Workaround or next step |
|------|------------------|-------------------------|
| `v0.13.2` and `v0.13.3` are skipped: the `v0.13.2` tag carries `0.13.1` manifests and `0.13.3` was never tagged | Anyone pinning a patch in that range | Pin `v0.14.1` or `v0.13.1` |

Support: open an issue at `https://github.com/DocumentDrivenDX/helix`.

## References

- Deployment checklist: [`deployment-checklist.md`](/artifacts/deployment-checklist/)
- Auto-tag workflow: `.github/workflows/release-tag.yml`
- Tag guard: `.github/workflows/release-version-guard.yml`
