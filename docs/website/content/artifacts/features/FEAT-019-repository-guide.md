---
title: "Feature Specification: FEAT-019 — Repository guide"
slug: FEAT-019-repository-guide
weight: 170
activity: "Frame"
source: "01-frame/features/FEAT-019-repository-guide.md"
generated: true
collection: features
---

> **Example from HELIX's own docs.** This generated page comes from `docs/helix/`. Use it to see the method in practice; start with the [artifact-type catalog](/artifact-types/) for reusable templates. Historical plans and reports may describe retired architecture.

> **Source identity** (from `01-frame/features/FEAT-019-repository-guide.md`):

```yaml
ddx:
  id: FEAT-019
  authoring:
    home: repo
  depends_on:
    - helix.prd
  status: draft
```

# Feature Specification: FEAT-019 — Repository guide

**Feature ID**: FEAT-019
**Status**: Draft
**Priority**: P1
**Owner**: HELIX maintainers
**Covered PRD Subsystem(s)**: Routing skill (guide mode), catalog (audiences, voice)
**Covered PRD Requirements**: R-13
**Cross-Subsystem Rationale**: The mode is the skill's; the audiences and voice profiles are catalog data; the deterministic machinery is a host tool outside HELIX (documentor).

## Overview

PRD R-13 requires that a repository HELIX governs gets documentation for the
people who build on, run, and use it, in one shape across repositories, kept
current by the change that would make it stale. FEAT-019 is the `guide` mode
(`workflows/modes/guide.md`), the audience specifications
(`workflows/publish/audiences/`), the `onboarding` and `public-site` voice
profiles with measurable limits (`workflows/voice.yml`), the writing pass
(`workflows/references/writing-pass.md`), and the publishing contract
(`workflows/references/publishing.md`): audiences, page kinds, the provenance
header, the `.helix.yml` `publish:` and `handling:` schema, and the checks.

## Ideal Future State

A developer who has never seen the repository finds an overview, the
architecture, one request traced through the code, and a guide to the first
change; an operator finds what deploys where, every setting and where its
value comes from, and the routine procedures; a user completes a first session
that works as written; a data consumer finds the datasets, their lineage, and
what each metric means. Every page is a projection of the artifacts and the
code with a header naming what it was built from, and a change to any of that
fails the check until the page catches up. Every repository has the same
audiences and page shapes; each adds only what is particular to it.

## Boundaries

- **Pages are projections.** The guide never edits an artifact. A disagreement
  between an artifact and the code is followed in the code's favour and
  reported for `align`.
- **Page kinds are Diátaxis's.** Each page has one of tutorial, how-to,
  reference, explanation, with a reader task, an outline, and a budget counted
  in prose units.
- **Four kinds of work.** Generated (from structured sources, never by hand),
  written (by an agent, then evaluated by a reader who is not its writer),
  existing (adopted unchanged), delegated (a tool the repository already has).
  A written page counts as current only after evaluation.
- **Provenance.** `<!-- helix:publish ... -->` and `<!-- helix:source path[#section] sha256:16hex -->`
  are the contract; what the check blocks on and warns about is the table in
  `publishing.md`.
- **Script policy.** The deterministic steps are optional host tooling, as
  for `present`: documentor (`tools/documentor/` in the HELIX repository)
  implements them and pins a HELIX version. Without it the agent does each
  step by hand, stamps `sha256:-` where it cannot digest, and says so in the
  handoff. Nothing is skipped silently.
- **DDx boundary.** A `helix:source` digest is page-to-source provenance,
  keyed by path and section; a `ddx.review.deps` hash is artifact-to-artifact,
  keyed by artifact id. Pages are not graph nodes and carry no `ddx:`
  frontmatter; the record lives in the page header, as `ddx.review` lives in
  frontmatter, so there is no second store (CONTRACT-001).
- **Distribution.** documentor lives in the HELIX repository under
  `tools/documentor/`, outside the skill: plug-in packaging copies only
  `skills/helix/`, so no install carries it. An adopting repository runs it
  from a HELIX release tag with `uvx --from
  "git+https://github.com/DocumentDrivenDX/helix@<tag>#subdirectory=tools/documentor"`;
  nothing is vendored and no template is copied. The skill's catalog carries no
  stack-specific traits or generators: those are documentor's and the adopting
  repository's.
- **Out of scope.** Estate views across repositories (`tools/documentor/docs/helix/02-design/adr/ADR-002`),
  field guides and presentation rendering, agent-driven bootstrap of artifacts
  from code, hosting of the site.

## Acceptance

- Given a repository with `.helix.yml` `publish:` naming an audience, when a
  cited section changes, then the check reports the page `stale` and exits
  non-zero, and passes after the page is regenerated and reviewed.
- Given a host without documentor, when `guide` runs, then the pages are
  written with their headers, the unstamped sources carry `sha256:-`, and the
  handoff names the steps done by hand.
- Given two repositories of different shape (an application and a data
  pipeline), when `guide` runs on both, then both have the same audience
  sections and page kinds, and differ only in the pages their traits add.

## Pilots

praxis-harness (a Databricks application; thirteen pages, written and checked),
synaptiq-northstar-idr (a data pipeline with a nested HELIX root), tablespec (a
library with an existing documentation site, adopted through it).
