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

# Release Notes — HELIX v0.15.4

## Release Scope

- Release identifier: `v0.15.4`
- Release date: 2026-10-09
- Previous release: `v0.15.3`
- Scope: optional formal-methods concern, adoption and technical-design guidance,
  executable abstract lease model, regression checks and generated references.
- Release owner: HELIX maintainer; annotated version tag triggers existing
  bundle publication, version guard, install smoke and website workflows.

## Audience and Channels

| Audience | Impact | Channel |
|----------|--------|---------|
| HELIX users | Risk-based formal specification and analysis | Concern catalog and plugin |
| Runtime integrators | Scoped assurance and evidence obligations | Practices and adoption reference |
| Website readers | Published concern and design examples | Public reference website |

## Highlights

- Select `formal-methods` for critical interacting state/rules or explicit
  assurance needs. Choose precise specification, executable analysis or
  deductive proof per affected slice; unaffected work records an exclusion.
- Technical designs distinguish safety, liveness, assumptions and bounds,
  reproducible evidence and model/code/test correspondence. Exact shared
  interfaces remain in Contracts; running-system verification still applies.
- The abstract lease example checks 70 reachable states and 109 transitions,
  with ordered recovery witnesses and replayable fencing/lock negative controls.
  It makes no DDx production correctness or liveness claim.

## Required Actions Summary

- Users: update to `v0.15.4`; existing concern selections remain unchanged.
- Adopting teams: record the affected scope, chosen rigor and authority before
  claiming formal assurance. No solver/proof assistant is installed by HELIX.
- Runtime integrators: preserve scope notes and reasoned non-applicability,
  and recheck evidence when mapped behavior or assumptions change.

## Changes and Fixes

| Area | Change | Effect |
|------|--------|--------|
| Concerns | Optional composable formal-methods concern | Critical behavior can be specified and analyzed at a chosen rigor |
| Design and alignment | Conditional specification and assurance criteria | Bounded results remain separate from production verification |
| Examples | Standard-library finite lease explorer and deliberate mutants | Runnable non-vacuity, fencing and lock-lifetime demonstration |
| Validation | Digest propagation, packaged execution and report integrity tests | Selected/unselected/unaffected cases and counterexamples are exercised |
| Integration | Preserve origin's v0.15.3 plan-driven execution changes | Both plan-execution and formal-methods suites run |

## Breaking Changes and Required Actions

No installation or artifact-format breaking changes. Formal methods remain
optional; a selected concern does not require analyzer runs for every slice.
Existing documents remain structurally valid and adoption gaps are scoped.

## Migration or Rollback Guidance

1. Update the plugin or generated bundle to `v0.15.4`.
2. If adopting formal methods, record risk/scope/rigor and use the checklist in
   `workflows/references/formal-methods.md` in the owning technical design.
3. Map any adopted model to implementation and run the chosen-level analysis
   alongside implementation tests and running-system verification.

To roll back the plugin, pin `v0.15.3`. Preserve project-owned specifications,
assurance decisions and historical analysis evidence.

## Known Issues and Support

- The lease model is abstract, finite and UNMAPPED to production code;
  liveness is NOT_CHECKED. Clocks, crashes and external effects are excluded.
- Catalog semantic quality checks are review obligations, not automated proofs.
- Optional deck-render/signing lanes require their external tools; unavailable
  tools are reported as skips, not verification successes.

Support: open an issue in the HELIX repository.

## References

- Deployment checklist: [deployment-checklist.md](deployment-checklist.md)
- Formal methods design: [design-formal-methods.md](../02-design/design-formal-methods.md)
- Adoption reference: `workflows/references/formal-methods.md`
- Concern: `workflows/concerns/formal-methods/`
- Bundle publication: `.github/workflows/release-genie-bundle.yml`
- Version guard: `.github/workflows/release-version-guard.yml`
