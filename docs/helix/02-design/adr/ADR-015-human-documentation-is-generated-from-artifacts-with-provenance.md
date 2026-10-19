---
ddx:
  id: ADR-015
  status: draft
  authoring:
    home: repo
---

# ADR-015: Human documentation is generated from artifacts, with provenance

## Problem

HELIX artifacts are the system of record: dense, exact, and written in the `artifact-signal` voice for agents carrying context and reviewers tracing intent. Developers, operators, and users need answers in their own vocabulary, so projects either hand-write documentation beside the artifacts, which drifts from them silently, or rewrite the artifacts for readers, which costs the exactness agents and reviewers depend on. Either way nothing tells a project that its documentation has fallen behind the code it describes, and each repository solves it differently.

## Decision

We will generate the pages people read from the artifacts and the code with a `publish` mode, record on each page the exact sources it was built from, and check those records on every change. Specifically:

- Catalog flows (`workflows/publish/flows/`) define the pages each audience needs (developer, operator, user), with each page's reader task, Diátaxis kind (tutorial, how-to, reference, explanation), outline, voice, budget, and source kinds. A project chooses flows and adds pages in `.helix.yml` `publish:`. The audience is ours; the kinds are Diátaxis's, because that taxonomy already answers which page is missing and what a page must leave to another.
- Every page starts with a provenance header naming each source, a path with an optional H2 section, and a digest of the text read (`workflows/references/publishing.md`).
- `skills/helix/scripts/publish_check.py` reports stale pages, missing sources, broken links and paths, unmapped watched files, and prose breaches; staleness, link, and path checks need only the standard library, so any project can gate CI on them.
- `skills/helix/scripts/publish_site.py` builds a static site from the pages with Hugo and a self-contained layout. The Markdown pages stay the record.
- Artifacts keep their voice and are never edited by `publish`. A page follows the code where an artifact disagrees and reports the disagreement for `align`.
- The writing pass (`workflows/references/writing-pass.md`) and the measured prose audit apply to published pages and deliverables, not to artifact types.

## Why We Chose This

### Over hand-written documentation beside the artifacts
A hand-written page has no record of what it was written from, so nothing can say when it goes wrong. Provenance with digests turns "the docs are out of date" from a reader's complaint into a check that fails in the pull request that made them stale, naming the source that moved.

### Over rewriting artifacts for human readers
Applying a readability standard to artifacts trades the exactness agents and reviewers rely on for a voice they do not need, and turns every governing document into a readability exercise. Projections keep each layer in its own voice: the record for agents, the page for people.

### Over a documentation site as the source
A site is one renderer of the pages. Keeping Markdown pages as the record means GitHub renders them with no toolchain, the checks need only the standard library, and a project can adopt the site later or never.

## Consequences

**Good**: Every HELIX project gets the same audiences, page shapes, checks, and site from one `.helix.yml` block. A change to a cited artifact section, configuration file, or code file fails the check until the page is regenerated, so documentation moves with the code. Diagrams come from a project's architecture model, not from hand drawing.

**Trade-offs**: A page that cites a busy code file goes stale often; authors cite the files whose content the page states, not everything they read. The project's `.helix.yml` and the catalog flows are YAML, so the unmapped and prose checks need PyYAML; projects without it still get staleness, link, and path checks. Generation is agent work, so two regenerations of a page differ in wording; the checks, the flow outline, and the writing pass bound the difference.

**Drift signals to watch**: Pages edited by hand without a provenance header; headers stamped without the sources reread; artifacts edited from `publish`; a flow page that cites only artifacts and no code, so it can never go stale against the system it describes.

## Concern Impact

- **No concern impact**: the decision adds a mode, catalog data, and scripts; it selects and overrides no concern.
