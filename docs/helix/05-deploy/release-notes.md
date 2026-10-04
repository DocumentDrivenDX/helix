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

# Release Notes — HELIX v0.15.0

## Release Scope

- Release identifier or version: `v0.15.0`
- Release date: 2026-10-03 (operator-driven; tagged by CI)
- Rollout window or environment: HELIX plugin (Claude Code marketplace, Codex
  plugin, Databricks Genie bundle, Grok Build) and the public website at
  `https://documentdrivendx.github.io/helix/`
- Release owner: HELIX maintainer cutting the tag
- Previous release: `v0.14.1` (2026-10-01)

## Audience and Channels

| Audience | Why they care | Delivery channel |
|----------|---------------|------------------|
| HELIX plugin users | Edits stay scoped to the request, artifacts state current intent, and routine work no longer files tracker items or emits status trailers | Plugin repo tag; marketplace update |
| Runtime integrators | The `helix_report` block and work-item creation are now opt-in | This file; `workflows/modes/_report.md`; `workflows/references/work-item-first.md` |
| Website readers | Workflow-mode, artifact-type, and project-artifact pages are regenerated | GitHub Pages rebuild |

## Highlights

- **HELIX documents describe desired state.** Specifications, decisions, and
  designs state what the system should do and why. Execution status belongs
  to the runtime's work tracker and history belongs to source control. An
  accepted decision sets direction; it does not claim the system implements
  it, and missing code does not make a specification invalid.
- **Work stays scoped to the request.** Authoring, `align`, and `evolve` read
  the target and the authorities that can affect it rather than traversing the
  whole project. An implementation audit happens only when explicitly
  requested, through `project-audit`, within a named scope.
- **Process ceremony is opt-in.** Routine framing, alignment, and review no
  longer create tracker items, gates, migration ledgers, fixed critique
  rounds, or status trailers. Work items are created when the user asks or the
  runtime requires them; the structured `helix_report` block is produced on
  request. Assessment criteria and real defect checks are unchanged.
- **One current ADR per decision.** A changed decision, including a reversal,
  is rewritten in place with the replaced option under alternatives. A
  superseding ADR is created only when the user asks to keep the earlier
  decision as its own record. The ADR template no longer has a Supersession
  section.
- **Instance validation warns on repository-history citations.**
  `validate-instance.py` flags pull-request numbers, pull-request and commit
  URLs, and commit hashes in artifacts. It is a warning, and it ignores
  transaction wording, release versions, migration revisions, and content
  digests.

## Required Actions Summary

- Users: none. Existing artifacts remain valid; validation may now warn on
  pull-request or commit citations in artifact bodies.
- Runtime integrators: request the `helix_report` block explicitly if you
  parse it, and require tracker-backed execution explicitly if you rely on
  HELIX creating work items.
- Operators: none. CI creates the release tag after approval.

## Changes and Fixes

### New or Improved

| Area | What changed | Who is affected |
|------|--------------|-----------------|
| Skill and mode contracts | Context reads bounded to the request; `_report.md` optional; work-item creation opt-in; the opt-in rule stated once; `SKILL.md` about 15% shorter with routing and invariants unchanged | HELIX users; runtime integrators |
| Action procedures | `frame`, `report`, `input`, `measure`, and `experiment` touch work items only when a runtime work item governs the run; high autonomy records assumptions instead of filing speculative items; trailers optional; `align`, `evolve`, `review`, `converge`, `backfill`, and `project-audit` procedures cut by roughly 80 percent | HELIX users |
| Artifact catalog | Templates and prompts drop delivery bookkeeping; optional sections may be omitted without N/A entries; ADRs keep one current record | HELIX users |
| Ratchets | Lowering a floor records the change and its justification where the floor is defined, or in an ADR | Maintainers |
| Validation | Repository-history warning in `validate-instance.py`; a regression test keeps HELIX's own documents free of such citations | HELIX users; maintainers |
| Evaluation | Three briefs cover a narrow desired-state edit, an accepted decision before code, and an explicit implementation audit; the evolve rubric rewards one current ADR | Maintainers |

### Fixes

| Issue or symptom | Resolution | User or operator impact |
|------------------|------------|-------------------------|
| A tag pushed by `release-tag.yml` started no publish workflows, because a tag pushed with the default token does not trigger tag workflows | `release-tag.yml` dispatches the Genie bundle, install smoke, and Pages workflows on the new tag | A CI-created release publishes its bundles and site |

## Breaking Changes and Required Actions

- `align`, `validate`, `refresh`, `check`, `project-audit`, `review`, and
  `converge` no longer end every response with a `helix_report` block. A
  runtime that parses the block must ask for structured output.
- Framing and alignment no longer acquire or create work items by default. A
  runtime that depends on HELIX-created items must require tracker-backed
  execution.

## Migration or Rollback Guidance

- Migration: pull the tag. Artifacts need no changes; a validation warning
  about a repository citation can be resolved by moving the citation to source
  control or the tracker.
- Rollback: install the `v0.14.1` tag. The website rebuilds from `main` and
  is not pinned to a tag.

## Known Issues and Support

| Issue | Who is affected | Workaround or next step |
|------|------------------|-------------------------|
| `v0.13.2` and `v0.13.3` are skipped: the `v0.13.2` tag carries `0.13.1` manifests and `0.13.3` was never tagged | Anyone pinning a patch in that range | Pin `v0.15.0` or `v0.13.1` |
| The repository-history warning cannot distinguish an upstream project's pull request from this repository's own | Artifacts citing upstream fixes | Treat the warning as advisory |

Support: open an issue at `https://github.com/DocumentDrivenDX/helix`.

## References

- Deployment checklist: [`deployment-checklist.md`](deployment-checklist.md)
- Desired-state authoring design: [`design-desired-state-authoring.md`](../02-design/design-desired-state-authoring.md)
- Auto-tag workflow: `.github/workflows/release-tag.yml`
- Tag guard: `.github/workflows/release-version-guard.yml`
