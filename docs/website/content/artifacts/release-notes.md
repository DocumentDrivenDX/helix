---
title: "Release Notes — HELIX v0.12.0"
slug: release-notes
weight: 470
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
```

# Release Notes — HELIX v0.12.0

## Release Scope

- Release identifier or version: `v0.12.0`
- Release date: 2026-08-21 (operator-driven; tag commit `c1c66f25`)
- Rollout window or environment: HELIX plugin (Claude Code marketplace,
  Codex plugin, Databricks Genie bundle, Grok Build) and the public website
  at `https://documentdrivendx.github.io/helix/`
- Release owner: HELIX maintainer cutting the tag
- Source commit or build: `c1c66f25` (tag `v0.12.0`); previous release
  `v0.11.0` at `1553a431` (2026-07-22)

## Audience and Channels

| Audience | Why they care | Delivery channel |
|----------|---------------|------------------|
| HELIX plugin users | New iterate-activity artifact types (roadmap, iteration plan, status report) and the grill mode change what `/helix` can author | Plugin repo tag; marketplace update |
| Website readers | The artifact-type reference and workflow-mode pages regenerate from the catalog and the skill | GitHub Pages rebuild |
| HELIX maintainers | The deliverable-over-machinery principle and lean plan defaults change how plans and work items are shaped | This file and `workflows/principles.md` |

## Highlights

- **Human-iteration documentation family.** Roadmap, iteration plan, and
  status report join the catalog under `06-iterate`, with the skip test
  that authors each one only when there is coordination to do
  (FEAT-017).
- **Grill mode** (`v0.11.0`, carried into this release): a
  one-question-at-a-time interview that stress-tests a plan or design
  before any artifact is drafted.
- **Deliverable-over-machinery principle** and lean plan defaults in
  `workflows/principles.md`: process exists to reduce the risk of a wrong
  ship, never as the deliverable.
- **Catalog fall-through for plugin installs**: adopters without local
  templates bind the generated `references/` floor beside the skill;
  project-local catalogs keep rank above an installed plugin.
- **Dual-path engagement**: skill-tool hosts invoke the skill; hosts without
  a skill tool load the skill body. Grok Build install guide added.

## Required Actions Summary

- None for plugin users; update the plugin and the new types resolve from
  the packaged catalog.
- Maintainers regenerate the site after pulling: `python3
  scripts/generate-reference.py` and `python3 scripts/publish-artifacts.py`.

## Changes and Fixes

### New or Improved

| Area | What changed | Who is affected |
|------|--------------|-----------------|
| Catalog | `roadmap`, `iteration-plan`, `status-report` (iterate); `market-analysis`, `data-flow-analysis` (discover) | Teams planning human iterations or framing a market |
| Skill | `grill` mode; desired-state rule in align; dual-path engagement; catalog fall-through | Every `/helix` user |
| Methodology | Deliverable-over-machinery principle; lean plan defaults; downstream-consumer verification; scope-discipline build gate | Maintainers and adopters shaping plans and work items |
| Install | Grok Build guide; no-local-template doctrine | Adopters on Grok Build or without a vendored catalog |

### Fixes

| Issue or symptom | Resolution | User or operator impact |
|------------------|------------|-------------------------|
| Evolve missed canonical `ddx.links` edges | Traversal follows `ddx.links` first, legacy fields as fallback | Impact graphs are complete |
| Copilot smoke test could not find the catalog | Catalog path exposed to the smoke check | Green install checks on Copilot |
| Codex rejected `hooks/hooks.json` | Unknown `version` field dropped | Clean Codex plugin load |

## Breaking Changes and Required Actions

- None. Artifact frontmatter, marker shape, and mode names from `v0.11.0`
  are unchanged.

## Migration or Rollback Guidance

- Migration: pull the tag; no artifact edits are needed. Projects that
  vendored `workflows/` re-sync it to pick up the new types.
- Rollback: install the `v0.11.0` tag. Artifacts authored with the three
  new iterate types stay valid Markdown; only their catalog binding is lost
  until the types return.

## Known Issues and Support

| Issue | Who is affected | Workaround or next step |
|------|------------------|-------------------------|
| Alignment and validation reports are prose tables with no machine-readable shape | Runtimes filing work from reports | A YAML report block lands in the next release |
| The skill body is over 1,200 lines and carries bench-specific language | Hosts with small context budgets | The next release splits it into a router plus per-mode contracts |

Support: open an issue at `https://github.com/DocumentDrivenDX/helix`.

## References

- Deployment checklist: [`deployment-checklist.md`](/artifacts/deployment-checklist/)
- Feature: `docs/helix/01-frame/features/FEAT-017-iteration-documentation.md`
- Principles: `workflows/principles.md`
- Commit range: `git log v0.11.0..v0.12.0`
