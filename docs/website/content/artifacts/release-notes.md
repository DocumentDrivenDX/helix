---
title: "Release Notes — HELIX v0.23.0"
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

# Release Notes — HELIX v0.23.0

## Release Scope

- Release identifier: `v0.23.0`
- Release date: 2026-11-10
- Previous release: `v0.22.0`
- Scope: reader views on the technology brief, weights and a table of limits on position
  papers, spikes and a `measured` source class in the technology atlas, a `views.yml`
  catalogue, and the removal of the CI evidence gate.
- Release owner: HELIX maintainer; published through the release PR workflow.

## Audience and Channels

| Audience | Impact | Channel |
|----------|--------|---------|
| Teams keeping a technology atlas | New sections and blocks; existing briefs and papers get warnings, not failures | Plugin and bundles |
| Existing HELIX users | None outside the `component-profile`, `position-paper`, and `tech-spike` types | Plugin and bundles |
| HELIX maintainers | Pull requests no longer need recorded install evidence | Repository CI |

## Highlights

- A technology brief (`component-profile` with `scope: reusable`) closes with a `## Views`
  section: Risk & Compliance, Finance, IT Operations, and Apps Dev. Each gives a one-sentence
  answer to that reader's first question and points to the sections that carry the facts.
- A `position-paper` may say how much each criterion counts in a `weights:` list, on a scale
  of `decisive`, `important`, `minor`. `assessment-tables.py` makes the Decision Criteria
  table from it. Only a position paper has a weight.
- `## Limits of the Position` holds a table of when the other option wins: Condition, Option
  that wins, Evidence. The template gains an optional `## Transition Path`.
- The `technology-atlas` profile takes `tech-spike` at `spikes/TS-{number}-{subject}.md`. A
  spike with `scope: reusable` runs on public inputs, records its test setup and how to
  reproduce it, and recommends nothing. It links the brief it tests with kind `answers` and
  the open question's number.
- A brief may cite such a spike as a source of class `measured`. It counts as independent
  corroboration for the configuration measured, and the Confidence grade says so.
- A flow may keep a `views.yml` beside `criteria.yml`; a criterion's `view:` is then checked
  against it.

## Required Actions Summary

- None to keep validating. A brief with no Views section and a position paper with no Limits
  table each get a warning at both tiers and still publish.
- Add the Views section and the Limits table at each document's next revision.

## Changes and Fixes

### New or Improved

| Area | What changed | Who is affected |
|------|--------------|-----------------|
| Briefs | `## Views` section and the `reader_views` check; `by_scope` may replace `automated_checks` | Atlas authors |
| Position papers | `weights:` list, generated Decision Criteria table, Limits table, optional Transition Path | Atlas authors |
| Spikes | `tech-spike` in the atlas profile, `reusable` scope, `answers` link with `question` | Atlas authors |
| Sources | `measured` class, and its place in the Confidence grade | Authors of briefs |
| Catalogues | `views.yml`; a criterion's `view:` is checked against it; a `weight` in `criteria.yml` is rejected | Atlas authors |
| CI | The evidence gate, `scripts/verify-full.sh`, and the committed evidence file are removed | Maintainers |

### Fixes

| Issue or symptom | Resolution | User or operator impact |
|------------------|------------|-------------------------|
| A position paper written to the v0.22.0 template failed the new Limits check at the publish tier | A missing table is a warning; a table that is present is checked for its columns and a row | Existing papers publish unchanged |

## Breaking Changes and Required Actions

There are no breaking changes and no migrations. A document that validated under `v0.22.0`
validates under `v0.23.0` at both tiers.

Three things block only where a document uses the new feature:

- A Views section that drops or empties one of the four headings.
- A Limits table with other columns or no rows.
- A `weights:` entry that is not `decisive`, `important`, or `minor`, or that names a
  criterion no `supported_by` assessment has a finding for; a weight on an assessment or in
  `criteria.yml`; an `answers` link with no `question` number; a `**RECOMMENDATION**:` line in
  a reusable spike.

## Migration or Rollback Guidance

### Upgrade or Migration

1. Update the plugin. Expect one `views` warning per brief and one `limits_table` warning per
   position paper.
2. Clear each warning when the document is next revised.

### Rollback or Hold Guidance

- Pin `v0.22.0` to roll back; the new sections and blocks would then go unchecked.
- Ask for help in the HELIX repository's issues.

## Known Issues and Support

| Issue | Who is affected | Workaround or next step |
|------|------------------|-------------------------|
| ADR-018 and SD-003 list the link kinds and do not yet name `answers` | Readers of the design record | The profile, validator, and schema reference are current |
| The four view headings are fixed in the check and template, not read from `views.yml` | A flow with other views | Keep the four headings in briefs |
| A weight's finding is read from the assessment as it stands, not at its pinned revision | Authors of weights | Run `pin-sources.py check` to see a source that changed |
| An `answers` link is not checked against the brief's Open Questions table | Authors of spikes | Check the number by hand |

Support: open an issue in the HELIX repository.

## References

- Deployment checklist: [deployment-checklist.md](/artifacts/deployment-checklist/)
- Pull requests: #120, #121, #122, #123, #124, #125, #126
- Release changes: https://github.com/DocumentDrivenDX/helix/compare/v0.22.0...v0.23.0
- Bundle publication: `.github/workflows/release-genie-bundle.yml`
- Version guard: `.github/workflows/release-version-guard.yml`
