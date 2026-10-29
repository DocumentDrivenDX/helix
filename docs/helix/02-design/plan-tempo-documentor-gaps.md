---
ddx:
  id: plan-tempo-documentor-gaps
  authoring:
    home: repo
---
# Tempo-driven HELIX and documentor corrections

## Scope and decisions

The operator authorized triage and implementation of seven adoption gaps.
Tempo is read-only reference material; do not edit it. Preserve the existing
uncommitted HELIX schema/publication work and compose with it.

1. Extend scaffold section linking to Hextra menu entries and home cards after
   generated content exists. Preserve existing entries, require a real output
   directory, and make repeated linking byte-stable.
2. Add upstream UMF TableSpec 1.0 detection, deterministic columns/keys/FK
   reference and entity graph, and automatic discovery into the existing UMF
   schema browser publisher. Keep tablespec pipeline detection separate; when
   both traits are selected, its guidebook occupies data/pipeline-tables while
   UMF owns data/tables. Do not duplicate the browser implementation.
3. Init proposes reviewable design-stage skips when HELIX docs exist without
   application source, and operational data mode when UMF tables have no pipeline
   signal. Operational overview uses data-design, not analytics data-architecture.
   Existing publish configuration remains operator authority. Missing-artifact
   reports intentionally show affected page keys beside artifact types.
4. Ship a separate Pages deployment workflow and update the check/refresh pin to
   v0.19.1. Tempo run 40952714352 successfully built and deployed; the new template
   also passes the deployment base URL to Hugo and scopes deployment permissions.
   Repository-specific locked dependency installs remain adoption configuration.
5. Genesis and Frame seed applicable software quality defaults, distinguish
   future software from permanently source-free work, allow reasoned pruning,
   and preserve the existing mandatory source-code evidence floor.
6. Document complete project-owned concern/practice files and slot overrides
   for Azure/Entra rather than shipping unverified provider-specific practices.
7. Data Design references authoritative per-table UMF YAML, the upstream browser,
   relationship checks and a publication step. Keep rationale in prose and exact
   schema structure in YAML; browser rendering does not prove schema validity.

## Verification and completion

Run documentor Python regressions (section linking, UMF detection/generation/
publication discovery/coexistence, profile boundaries), the complete documentor
suite, skill/catalog checks and `just test`; inspect diff whitespace. Record any
failed gate with its exact cause, keeping unrelated checkout changes intact.
Do not publish a release or edit Tempo. A later release is needed before Tempo
can consume the changes using a pinned tag.

## Completion evidence

- Full documentor suite passed, including all shell regressions, 81 Python tests
  (eight new Tempo-gap regressions), wheel build and isolated installation.
- HELIX `just test` passed; its InnSigle gate reported a skip because the CLI
  could not resolve through the restricted npm environment. Architecture tour
  rendering also reported its existing optional skip without Chromium.
- Skill validation, packaged documentor catalog parity, generated reference
  refresh and diff whitespace checks passed.
- Tempo's existing Pages build and deployment succeeded in GitHub Actions run
  40952714352. The catalog adaptation has local structural coverage; no new
  workflow run was triggered and no Tempo files were changed.
- Upstream schema/browser infrastructure was committed independently as
  `24a6e12b` while this work was in progress. This change extends that commit;
  it does not replace its schema publisher or include its unrelated edits.
- Remaining adoption: release these fixes, update Tempo's pinned tool version,
  remove corresponding workarounds there, and run Tempo's per-type Frame/Design
  validation. Those Tempo edits and a release are outside this change.
