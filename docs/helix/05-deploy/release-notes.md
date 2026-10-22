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

# Release Notes — HELIX v0.19.0

## Release Scope

- Release identifier: `v0.19.0`
- Release date: 2026-10-22
- Previous release: `v0.18.0`
- Scope: documentation for people. A HELIX repository can now write the guide its readers
  need from its artifacts. It checks that guide on every change and publishes it as a site.
- Release owner: HELIX maintainer; published through the release PR workflow.

## Audience and Channels

| Audience | Impact | Channel |
|----------|--------|---------|
| HELIX users | A `guide` mode and an optional tool, documentor, that write, check, and publish documentation for people | Plugin, install README |
| Project maintainers | A deploy gate that checks the guide is current, and a site built from the repository | Workflow catalog and website |
| Present mode users | Decks and briefs render through documentor | Plugin and documentor |

## Highlights

- The `guide` mode plans a repository's documentation by reader (developer, operator, user,
  data) in the `.helix.yml` `publish:` block. Every page cites its sources, and a page goes
  stale when a source changes.
- documentor, released with HELIX, does the deterministic work. It detects what the repository
  is, generates reference pages, and has one model write each page and another evaluate it.
  It checks every page in CI and builds the site.
- Sites are built from sections: the guide, the governed record of `docs/helix`, and
  sections the project generates. Each site also says how it was made and which HELIX
  artifacts would improve it. HELIX's own site is built this way.
- Architecture diagrams come from a model whose every part cites the code. documentor can draft
  that model from compose files, Databricks bundles, migrations, and package manifests. It can
  also present a view step by step and explain how several repositories fit together.
- A site, its diagrams, and its decks can wear one theme from DocumentDrivenDX/ux-builder
  (`publish.theme`).

## Required Actions Summary

- Update the plugin or bundle to `v0.19.0`.
- To use documentor, install it from the same release:
  `uv tool install "git+https://github.com/DocumentDrivenDX/helix@v0.19.0#subdirectory=tools/documentor"`,
  then run `documentor doctor`. Every step also works by hand without it.
- If a project has `developer-guide` artifact instances, move each to
  `docs/guide/developer/developer-guide.md` and adopt it (`documentor adopt`); the type is retired.
- If a script calls the deck or brief renderers under `skills/helix/scripts/`, call
  `documentor deck render` or `documentor doc render` instead.

## Changes and Fixes

| Area | Change | Effect |
|------|--------|--------|
| Guide mode | New mode: plan, generate, write, evaluate, check, and publish the guide by reader | Documentation for people is planned and kept current like any artifact |
| documentor | New host tool in `tools/documentor`, versioned with the plugin | One command line for guide pages, sites, diagrams, decks, and briefs |
| Deploy gate | `guide_current` replaces the check that `README.md` and `CHANGELOG.md` exist | The gate checks that pages match their sources, not that two files exist |
| Artifact types | `solution-overview` added; `developer-guide` retired; `release-notes` and `status-report` audited as human prose | One home for each document, written for its reader |
| Architecture | Model views, model drafting, presentations, and the estate; the model format moves to `workflows/references/architecture-model.md` | Diagrams that fail the build when the code changes under them |
| Generators | Reference pages for CI pipelines, tasks, database schemas, compose services, CLIs, APIs, MCP tools, and more | Pages no one writes by hand |
| Present mode | Deck and brief renderers move into documentor | The skill keeps only its validators |
| Website | HELIX's site is assembled by documentor, with a developer guide | `scripts/publish-artifacts.py` is removed |

## Breaking Changes and Required Actions

| Change | Impact | Required action | Deadline or trigger |
|--------|--------|-----------------|---------------------|
| The `developer-guide` type is retired | Its instances no longer validate as a type | Move each instance into the guide and adopt it | Next validation run |
| Deck and brief renderers left the skill | Direct calls to `skills/helix/scripts/render-*.js` fail | Use `documentor deck render` and `documentor doc render` | Next deck render |
| The deploy gate checks `guide_current` | A project with `publish:` must have a current guide to pass | Run `documentor check` and fix what it reports | Next deploy |

Projects without a `publish:` block keep the deploy gate's manual documentation review. No
artifact migration is required beyond the retired type.

## Migration or Rollback Guidance

### Upgrade or Migration

1. Update to `v0.19.0`.
2. Optional: install documentor, run `documentor init` in a repository, read the proposed
   `publish:` block, then `documentor init --write` and `documentor build --write`.
3. Add the CI template documentor ships (`documentor check` on every pull request).

### Rollback or Hold Guidance

- Pause adoption when `documentor check` fails and the deploy gate blocks a release. Remove
  the `publish:` block to return to the manual review.
- Roll back by pinning `v0.18.0`. Guide pages are plain Markdown and stay readable.
- Ask for help in the HELIX repository's issues.

## Known Issues and Support

| Issue | Who is affected | Workaround or next step |
|------|------------------|-------------------------|
| Writing pages needs an agent and its credentials | `documentor write` users | Run it where the agent is signed in; the CI check needs no agent |
| The evaluating model sometimes returns no verdict | `documentor write` users | Run `write` again, or evaluate with `documentor prompt --reviewer` and record it with `documentor review` |
| Presentations and screenshots need Node and Chrome | `documentor tour --render` and `site --shots` users | `documentor doctor` names what is missing; Eraser installs itself |
| Optional deck-render and attestation checks need their local tools | Maintainers | Unavailable tooling is not evidence of a passing check |

Support: open an issue in the HELIX repository.

## References

- Deployment checklist: [deployment-checklist.md](deployment-checklist.md)
- Release changes: https://github.com/DocumentDrivenDX/helix/compare/v0.18.0...v0.19.0
- Bundle publication: `.github/workflows/release-genie-bundle.yml`
- Version guard: `.github/workflows/release-version-guard.yml`
