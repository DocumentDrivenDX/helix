---
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
---

# Release Notes — HELIX v0.21.0

## Release Scope

- Release identifier: `v0.21.0`
- Release date: 2026-11-06
- Previous release: `v0.20.0`
- Scope: graph profiles, so one HELIX framework governs a technology-intelligence
  graph (the Technology Atlas) beside a software-delivery graph; four new or
  generalized artifact types; pinned, reproducible publications.
- Release owner: HELIX maintainer; published through the release PR workflow.

## Audience and Channels

| Audience | Impact | Channel |
|----------|--------|---------|
| Teams keeping a technology atlas | A `technology-atlas` profile, types, and pinning | Plugin and bundles |
| Existing HELIX users | None: a marker without `profile:` behaves as before | Plugin and bundles |

## Highlights

- A flow in `.helix.yml` takes an optional `profile:`. `technology-atlas` selects
  `component-profile`, `technology-assessment`, `position-paper`, `decision-brief`,
  `adr`, and `deliverable`, with advisory authority across graphs.
- New artifact types `technology-assessment`, `position-paper`, and `decision-brief`.
  `component-profile` gains a `reusable` scope for briefs that name no project.
- `ddx.links` is defined: `{id, kind, authority?, rev?, graph?}`. A link that
  claims `governing` authority under an advisory-only profile is a blocking
  finding; `contradicts` is reported and never fails validation.
- `validate-instance.py --tier publish` applies a profile's publish tier and requires
  pinned `rev` values on a deliverable's or brief's source links.
  `pin-sources.py` pins, checks drift, and materializes sources.

## Required Actions Summary

- None for existing flows.
- A deliverable's `ddx.authoring.export` is now one path string, as the schema and
  DDx require; a list is a warning in `check-deliverable.py`.

## Changes and Fixes

### New or Improved

| Area | What changed | Who is affected |
|------|--------------|-----------------|
| Profiles | `workflows/profiles/`, `generate_graph.py --profile`, per-profile graph | Atlas authors |
| Types | `technology-assessment`, `position-paper`, `decision-brief`; reusable `component-profile` | Atlas authors |
| Links | `ddx.links` vocabulary and authority check | Anyone using cross-flow references |
| Publications | Pinned sources and `--tier publish` | Authors of deliverables |

### Fixes

| Issue or symptom | Resolution | User or operator impact |
|------------------|------------|-------------------------|
| DDx rejected a deliverable whose `authoring.export` was a list | The template, example, and present action use one path string | `ddx doc audit` passes on deliverables |
| A pre-commit job pointed at a missing script | Removed | Commits no longer print an error |

## Breaking Changes and Required Actions

There are no breaking changes and no migrations.

| Change | Impact | Required action | Deadline or trigger |
|--------|--------|-----------------|---------------------|
| `authoring.export` is a string | A deliverable listing several renders | Keep the primary render in `export`; list all under Render | Next `ddx doc audit` |

## Migration or Rollback Guidance

### Upgrade or Migration

1. Update the plugin. Add `profile: technology-atlas` to a flow only for an atlas.

### Rollback or Hold Guidance

- Pin `v0.20.0` to roll back; markers with `profile:` would then be ignored.
- Ask for help in the HELIX repository's issues.

## Known Issues and Support

| Issue | Who is affected | Workaround or next step |
|------|------------------|-------------------------|
| `graph:` references are recorded and pinned, not fetched | Cross-repository publications | The runtime (DDx) or the atlas tooling resolves them |
| No projection to UMF or `umf-visual` | Atlas explorer | Deferred until those contracts are reviewed |

Support: open an issue in the HELIX repository.

## References

- Deployment checklist: [deployment-checklist.md](deployment-checklist.md)
- Design: SD-003, ADR-017, ADR-018
- Release changes: https://github.com/DocumentDrivenDX/helix/compare/v0.20.0...v0.21.0
- Bundle publication: `.github/workflows/release-genie-bundle.yml`
- Version guard: `.github/workflows/release-version-guard.yml`
