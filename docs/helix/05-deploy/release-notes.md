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

# Release Notes — HELIX v0.15.1

## Release Scope

- Release identifier: `v0.15.1`
- Release date: 2026-10-09
- Previous release: `v0.15.0` (2026-10-04)
- Scope: HELIX routing skill, concern and artifact catalog, generated plugin
  packages, Databricks Genie bundle, and public reference website.
- Release owner: HELIX maintainer; the approved release pull request triggers
  the existing auto-tag and publication workflows.

## Audience and Channels

| Audience | Impact | Channel |
|----------|--------|---------|
| HELIX users | Explicit module boundaries, configuration ownership and code-shape guidance | Versioned plugin and concern catalog |
| Runtime integrators | Source feature readiness includes boundary adoption and verification evidence | Mode contracts and concern practices |
| Website readers | New concerns and principle documents, refreshed artifact references | Public website |

## Highlights

- **Modularity and encapsulation from the start.** Every project with handwritten
  source, including libraries, selects the baseline at every autonomy level.
  Architecture records module/type ownership, public APIs, allowed and forbidden
  dependencies, integration owners, construction policy, and a boundary-check
  command. Dependent feature work requires adoption; bounded adoption work may
  establish those prerequisites. Architectural style remains selectable.
- **Central configuration with explicit owners.** Python, TypeScript, Rust, Go
  and Scala concerns require a typed configuration boundary and startup
  validation. Guidance distinguishes operator-injected settings, non-secret
  environment files, and defaults. Next.js environment-module access and
  Databricks bundle-managed non-secret configuration have explicit exceptions.
- **Code shape ceilings.** The new composable concern sets strict greenfield
  size/complexity defaults, editing-time and pre-commit checks, and a ratchet
  that prevents ceilings from rising to accommodate oversized code.
- **Principles made explicit.** New documents explain evidence over confidence,
  human authority and agent autonomy, linked artifacts, intent over inference,
  and feedback from execution.

## Required Actions Summary

- Users: update to `v0.15.1`. Source projects adopt the modularity baseline
  explicitly before dependent feature work. Source-free work records a reason
  for non-applicability; existing selections are not silently overwritten.
- Runtime integrators: propagate boundary evidence and project-local checker
  requirements through Design, Polish, Check, review and runtime handoff.
- Operators: follow owner-layered configuration and selected code-shape concern
  practices when creating or updating source projects.

## Changes and Fixes

| Area | Change | Effect |
|------|--------|--------|
| Concerns | Modularity baseline and code-shape ceilings | Ownership, encapsulation, dependency rules and size limits become explicit |
| Configuration | Central typed config and owner-layered sources across language concerns | Environment reads and vendor configuration stop spreading through application logic |
| Design and Build | Boundary evidence in templates, plans, review and gates | Work is checked before it is declared execution-ready |
| Instance validation | Populated boundary evidence checked when the section is present | Empty fields, noncanonical heading variants and duplicate boundary sections fail |
| Regression coverage | Boundary fixtures and allowed/forbidden import controls run locally and in CI | Structure checks and actual project-checker demonstrations remain distinct |
| Documentation | New principle documents and regenerated projections | Published guidance agrees with the source catalog |

## Breaking Changes and Required Actions

No artifact-format or installation breaking change. Legacy Architecture instances
without Module Boundaries remain structurally valid. Current source feature
readiness has a new evidence obligation: explicitly adopt the baseline and
boundary checks. Tiny programs may use a one-row map; classic-layered projects
retain deliberate concrete data-access coupling and local construction.

Configuration and code-shape practices apply when their concerns are selected.
Existing code-shape adoption records current ceilings and tightens them as code
is split. Existing dependency debt is individually inventoried; baselines must
not be widened to hide new violations. Scoped exceptions require authority,
owner, rationale, alternative verification and a review/removal trigger.

## Migration or Rollback Guidance

1. Update the plugin or install a bundle from `v0.15.1`.
2. For source projects, record baseline applicability and schedule bounded
   adoption work for module maps and stack-appropriate dependency checks.
3. Apply selected configuration/code-shape practices and verify their local,
   pre-commit and CI commands.

To roll back the plugin, pin `v0.15.0`. Keep project-owned boundary decisions and
adoption evidence; changing plugin versions does not remove them.

## Known Issues and Support

- Structural validation proves populated evidence, not semantic correctness.
  Review must assess invariants, visibility, type leakage and dependency direction;
  adopting projects supply the actual import checker.
- The small Python import fixture demonstrates negative controls; it is not a
  comprehensive language dependency analyzer.
- Repository-history citation warnings remain advisory.

Support: open an issue in the HELIX repository.

## References

- Deployment checklist: [deployment-checklist.md](deployment-checklist.md)
- Modularity concern: `workflows/concerns/modularity-and-encapsulation/`
- Code-shape concern: `workflows/concerns/code-shape-ceilings/`
- Selection and adoption: `workflows/references/concern-resolution.md`
- Release automation: `.github/workflows/release-tag.yml`
- Version guard: `.github/workflows/release-version-guard.yml`
