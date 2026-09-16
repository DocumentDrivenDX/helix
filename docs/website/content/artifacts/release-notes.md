---
title: "Release Notes — HELIX v0.13.0"
slug: release-notes
weight: 480
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
    self_hash: 08d5d2fde105ded3c68f345694d6254b9970dd40859cbfdf809747667dd84c3f
    deps:
      deployment-checklist: 78c9688645de24f33182dca537e13d0fb180abb4773ab85b48468e495a92bad1
    reviewed_at: "2026-09-16T03:20:07Z"
```

# Release Notes — HELIX v0.13.0

## Release Scope

- Release identifier or version: `v0.13.0`
- Release date: 2026-09-15 (operator-driven; tagged at the merge commit)
- Rollout window or environment: HELIX plugin (Claude Code marketplace,
  Codex plugin, Databricks Genie bundle, Grok Build) and the public website
  at `https://documentdrivendx.github.io/helix/`
- Release owner: HELIX maintainer cutting the tag
- Source commit or build: the tag's merge commit (tag `v0.13.0`); previous release
  `v0.12.0` at `c1c66f25` (2026-08-21)

## Audience and Channels

| Audience | Why they care | Delivery channel |
|----------|---------------|------------------|
| HELIX plugin users | The `present` mode turns governed artifacts into decks; the routing skill is a router with one contract file per mode; execution-era doctrine is gone | Plugin repo tag; marketplace update |
| Website readers | Decks and Briefs and Anti-slop pages, a generated rule reference, the deck PDF | GitHub Pages rebuild |
| Adopters who vendored `workflows/` | Mode contracts, the deliverable type, the stop-trigger file, and the shipped references floor changed shape | Re-sync `workflows/` |
| HELIX maintainers | The eval harness, the deck render lane, and the portability gate change what `just test` proves | This file and `evals/README.md` |

## Highlights

- **Human-facing outputs.** A `present` mode and a `deliverable` artifact
  type project governed artifacts into client-ready decks: brief, corpus
  inventory with scope and coverage controls, storyboard with the
  titles-only test, headline and shape passes ported from sloptimizer,
  slide patterns with figures and icons, four looks, a PPTX renderer, and a
  gate that rasterizes every slide for inspection (FEAT-018, R-12).
- **Router split.** `skills/helix/SKILL.md` only routes (348 lines, from
  1,246); each mode's contract is `workflows/modes/<mode>.md`, shipped in the
  references floor with the actions, templates, stop triggers, principles,
  and a report shape runtimes can consume.
- **Execution-era cleanup.** The execution engine doctrine, the state
  machine, the family-test bench, and the execution-ready-bead machinery are
  removed; the skill body uses only the PRD's primitives and a gate enforces
  it (R-4).
- **Evaluation.** `evals/` runs nine briefs headlessly against a fixed corpus
  with deterministic checks and a judged rubric; results for this release
  are committed under `evals/results/`.
- **Schema.** `ddx.authoring.home` is required and tool-native checkout is
  defined (#37).

## Required Actions Summary

- Plugin users: update the plugin; the new mode and type resolve from the
  packaged catalog.
- Adopters who vendored `workflows/`: re-sync it; `library/skill-prompts/`
  no longer exists and stop triggers live at `workflows/stop-triggers.yml`.
- Maintainers: the deck render lane needs node with pptxgenjs (`npm ci` in
  `skills/helix/scripts`), LibreOffice, and pdftoppm to run in full; it
  skips with a message without them.

## Changes and Fixes

### New or Improved

| Area | What changed | Who is affected |
|------|--------------|-----------------|
| Catalog | `deliverable` type (deck) under `06-iterate`; `workflows/deliverables/` holds the theme with four looks, slide patterns, deck flows, deck craft, visual specs, and source mappings | Teams presenting to sponsors, clients, or executives |
| Skill | `present` mode; router split into per-mode contracts; `_report.md` shape with review and converge fan-in; three autonomy levels per ADR-003; stop triggers shipped in the floor | Every `/helix` user |
| Scripts | `check-deliverable.py` (title, shape, restatement, vocabulary, number, coverage checks), `render-deck.js` with requirable libraries, `deck-qa.py`, `corpus-inventory.py`, `validate-instance.py` | Hosts rendering or gating deliverables |
| Evals | `scripts/run-eval.py` with nine briefs, delta validation, and a judge | Maintainers |
| Site | Decks and Briefs, Anti-slop, and the generated Anti-slop Rules reference; the deck PDF published beside its script | Website readers |
| Docs | One install guide with a section per host; PRD R-12 and FEAT-018; metrics dashboard rebuilt around the PRD's metrics; 51 working documents archived | Adopters and maintainers |

### Fixes

| Issue or symptom | Resolution | User or operator impact |
|------------------|------------|-------------------------|
| Skill body named host tools and env roots | Rewritten in the PRD's primitives; `validate-skills.sh` fails on tool names and env roots | Portable skill body across hosts |
| Stop triggers referenced a path the floor did not ship | Moved to `workflows/stop-triggers.yml` and shipped as `references/stop-triggers.yml` | Packaged installs resolve them |
| Renderer dropped table rows and hid unfit text | Rows are clamped and reported; unfit text and cut Visual specs make the render exit non-zero after writing | Honest deck renders |
| Sloptimizer port drifted from upstream | `tests/validate-headline-sync.sh` vendors the fixture and four phrase lists and fails on drift | Same title rules on every host |

## Breaking Changes and Required Actions

- `workflows/EXECUTION.md`, `workflows/DDX.md`, the state machine and
  rules, `actions/implementation.md`, `actions/check.md`, `workflows/legacy/`,
  `library/skill-prompts/`, and the family-test bench are removed. Runtimes
  that read them must read the mode contracts and `stop-triggers.yml`
  instead.
- `workflows/references/bead-first.md` is `work-item-first.md`.
- Artifact frontmatter requires `ddx.authoring.home` (#37).
- One-pager and brief kinds are declared in `meta.yml` but not built; the
  present mode produces decks only until the backlog item lands.

## Migration or Rollback Guidance

- Migration: pull the tag; regenerate the site (`generate-reference.py`,
  `publish-artifacts.py`, `publish-resources.py`).
- Rollback: install the `v0.12.0` tag. Deliverable scripts stay valid
  Markdown; only their catalog binding and gate are lost.

## Known Issues and Support

| Issue | Who is affected | Workaround or next step |
|------|------------------|-------------------------|
| One-pager, brief, and HTML render targets are not built | Teams wanting a document rather than a deck | Backlog item with the precise gap; write the brief as a deck script for now |
| The eval's investor-deck brief fails the shape gate on a reversal the skill wrote, and the survey brief needs an 1,800-second budget | Maintainers reading the eval | Recorded in `evals/results/`; the mode text names the coverage vocabulary and the shape rules |
| Innsigle content seals are in review (PR #39) and ship in the next release | Website readers expecting a signed colophon | Next release |
| Georgia and Trebuchet are absent on stock Linux LibreOffice, so the raster substitutes them there | Hosts rasterizing decks on Linux | `deck-qa.py` notes the missing typeface; use the `technical` or `classic` look |

Support: open an issue at `https://github.com/DocumentDrivenDX/helix`.

## References

- Deployment checklist: [`deployment-checklist.md`](/artifacts/deployment-checklist/)
- Features: `docs/helix/01-frame/features/FEAT-018-deliverables.md`
- Requirements: `docs/helix/01-frame/prd.md` (R-4, R-12)
- Evaluation: `evals/README.md`, `evals/results/20260915-2202/summary.md`
- Commit range: `git log v0.12.0..v0.13.0`
