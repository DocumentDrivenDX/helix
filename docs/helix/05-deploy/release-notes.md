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

# Release Notes — HELIX v0.18.0

## Release Scope

- Release identifier: `v0.18.0`
- Release date: 2026-10-19
- Previous release: `v0.17.0`
- Scope: simplification through execution feedback, living documents, grounded
  system context, supervision guidance and explicit stops for consequential actions.
- Release owner: HELIX maintainer; published through the release PR workflow.

## Audience and Channels

| Audience | Impact | Channel |
|----------|--------|---------|
| HELIX users | Less pressure to add mechanisms, tests and process documents | Plugin and generated bundles |
| Project maintainers | Scoped alignment can suggest evidence-backed simplification | Workflow catalog and website |
| Runtime integrators | Clearer authorization boundaries and review summaries | Routing skill and shared guidance |

## Highlights

- Execution feedback should consolidate and remove unnecessary mechanisms as
  system responsibilities become clear. Judge the resulting system rather than
  the number of edited files; necessary caller updates belong to the change.
- Reuse meaningful tests and retire redundant implementation-coupled coverage.
  Remove blanket Red-state requirements, fixed coverage percentages and
  mandatory process files from the affected gates. Parameter count is a cohesion
  review signal rather than a reason to create another API.
- Require observed proof at the layer appropriate to the changed behavior.
  Real client and downstream-consumer checks remain required for affected
  integrations; internal refinements need no duplicate runtime matrix.
- Treat committed specifications as living intent. Address material gaps while
  preserving authority; lifecycle labels and missing links do not create work.
- Read system context before designing changes. Give reviewers concrete summaries
  of changed behavior, observed evidence and reversal options. Consequential
  actions retain explicit authorization boundaries.

## Required Actions Summary

- Update the plugin or bundle to `v0.18.0`.
- Review project-owned gates on the next scoped change. HELIX does not rewrite
  local coverage targets, contractual requirements or independent audit policy.
- Use component-scoped alignment to identify duplicated mechanisms, excessive
  verification or comments that repeat the design. Findings remain advisory
  unless they expose a governing violation or material risk.

## Changes and Fixes

| Area | Change | Effect |
|------|--------|--------|
| Design and Build | Prefer coherent existing interfaces; remove generic architecture and process-file prescriptions | Avoid parallel APIs and unnecessary specification work |
| Testing and verification | Scope proof to behavior and risk; permit reuse and retirement of redundant tests | Reduce test matrices while retaining meaningful evidence |
| Alignment | Inspect relevant implementation for a named component and distinguish simplification advice from blockers | Identify waste without automatically creating work |
| Authoring | Use descriptive names and concise language-native API documentation | Avoid copying design rationale throughout source comments |
| Living documents | Preserve desired-state authority and reconcile relevant drift | Avoid lifecycle and linkage housekeeping |
| Context and supervision | Read system context and report concrete evidence and reversal options | Make agent work easier to assess |
| Authorization | Stop before unauthorized one-way actions and stack additions | Keep consequential decisions with the operator |

## Breaking Changes and Required Actions

Workflow defaults change; plugin installation and bundle formats are unchanged.
Projects that intentionally enforce stricter verification or documentation rules
retain those rules until their owners revise them. No artifact migration or
bulk test deletion is required.

## Migration or Rollback Guidance

1. Update to `v0.18.0` and apply the revised guidance to the next bounded task.
2. Reconcile local conflicts in the relevant existing artifacts. Preserve
   required behavior, compatibility commitments and meaningful evidence.

To roll back, pin `v0.17.0`; preserve project-owned artifacts and historical
proof. HELIX requires no DDx installation or compatibility gate.

## Known Issues and Support

- Deterministic validation checks packaging and contracts; it does not establish
  that agents will produce simpler work. No behavioral benchmark improvement is claimed.
- Optional deck-render and attestation checks require their local tools;
  unavailable tooling is not evidence of a successful check.

Support: open an issue in the HELIX repository.

## References

- Deployment checklist: [deployment-checklist.md](deployment-checklist.md)
- Release changes: https://github.com/DocumentDrivenDX/helix/compare/v0.17.0...v0.18.0
- Bundle publication: `.github/workflows/release-genie-bundle.yml`
- Version guard: `.github/workflows/release-version-guard.yml`
