---
ddx:
  id: helix.design.ux-sdk-governance
  authoring:
    home: repo
---
# UX behavior and SDK governance

## Scope and authority

The operator authorized reusable UX implementation guidance and integration
with the ai-design-system SDK on 2026-10-11. This design refines the concern
propagation contract and DESIGN.md / story-test-plan catalog. ADR-011 remains
authoritative for Radix/shadcn ownership; this change separates its behavioral
baseline from that implementation choice without transferring its prescription.
No SDK source changes, new public skill, runtime CLI, tracker mutations, or
component-library slot are required.

## Decisions

- Add ux-interaction-patterns as the neutral behavioral baseline. ux-radix
  keeps its existing name and composes the baseline automatically at concern
  loading and context-digest assembly; existing selections retain behavior.
- ai-design-system explicitly composes the same baseline. SDK package choice
  is independent of framework and hosting. Record conflicts with Radix/shadcn
  and AppKit in the existing project-override mechanism. Do not infer a second
  component kit from React or Databricks hosting.
- Distinguish native navigation from composite widgets, and modal from
  non-modal overlays. Keep optional patterns conditional on actual product needs.
- DESIGN.md accepts external versioned token references as well as local values.
  Keep rationale in ADRs, component wiring in TDs, and executable assertions in STPs.
- An optional UX Coverage section in an STP maps six categories to the existing
  AC test matrix or concrete exclusions; it does not duplicate that matrix. Legacy omission remains structurally valid; affected new UX work cannot
  be called ready without adopting the map or recording reviewed exclusion.
  Structure checks do not prove tests exist or ran, semantic quality, or UI behavior.
- SDK lint/audit covers presentation adoption. Interaction tests cover behavior.
  SDK-owned warnings are assigned to the SDK team, not silently ignored or
  fixed by overriding SDK internals.

## Acceptance and verification

1. Existing ux-radix and new SDK selections inject the neutral baseline for
   UI/frontend work; API-only work and unselected concerns remain unaffected.
2. SDK composition preserves installed-version guidance, explicit library
   conflicts, styling/toolchain overrides, and scoped exceptions.
3. Local and SDK DESIGN examples pass the real instance validator.
4. STP examples with applicable and excluded UX evidence pass; missing fields,
   missing applicable patterns, empty cells, duplicate IDs, invalid dispositions,
   and unexplained exclusions fail with UX-specific findings. Legacy omission passes.
5. Review and build instructions require observed interaction test and SDK audit
   results, with scope, versions, commands, exit codes, routes, themes and exceptions.
6. Catalog packaging and generated references include both concerns and the new
   example. Run just test, artifact-schema validation, context-digest validation,
   pre-commit hooks and git diff --check. No consumer pilot is claimed by these tests.

## Ordered implementation plan

1. Add neutral and SDK concerns, narrow the Radix adapter, update framework and
   AppKit references and resolver composition. Verify digest propagation tests.
2. Update DESIGN template/prompt/meta and add an external-SDK example.
3. Add STP UX Coverage format, structural validator, and negative controls.
4. Thread readiness and evidence through selection, review and verification.
5. Regenerate graph/reference/public artifacts, run repository gates, review the
   final diff with Astra, resolve findings, commit, push and create a PR.

## Review decisions

Astra's initial review required explicit baseline composition, compatibility for
existing selections, pattern-appropriate semantics, concrete SDK/library conflict
resolution and an honest structural/runtime evidence boundary. All are adopted.
A new exclusive slot is deferred: existing override policy is sufficient for
this bounded integration and avoids migration of unrelated component concerns.

## Implementation review

Astra ultra reviewed the plan and final implementation. Findings resolved:
explicit legacy adapter composition; pattern-appropriate semantics; optional
structural coverage without duplicate AC ownership; external token alternatives;
phase-correct entry versus completion evidence; formatting-only cells rejected;
nav non-applicability; SDK guidance/audit retention under realistic compact
selection with scoped overrides. Final verdict: PASS, no remaining blockers.
The reviewer independently ran all 16 UX governance tests and git diff --check.
Its final ordering note was applied to concern-resolution's numbered procedure.
Runtime consumer UX remains an adopting-project verification obligation.

## Completion evidence — 2026-10-11

Environment: isolated local worktree based on origin/main; Python 3.12 with
PyYAML supplied by uv. This is methodology/validator work, so no consumer app
URL or SDK runtime audit is claimed.

Observed commands and results:

- `uv run --with pyyaml --python 3.12 just test`: exit 0, including 16 UX
  governance tests and all 57 catalog examples. Optional deck-render lane
  skipped because pptxgenjs was unavailable. Existing Innsigle stale/unsealed
  warnings match the baseline; seal verification and site build passed.
- `uv run --with pyyaml --python 3.12 bash tests/validate-website-generated.sh`:
  exit 0; 57 concerns and 55 artifact types current and complete.
- Artifact-schema validation: exit 0; graph and public references regenerated.
- `lefthook run pre-commit`: exit 0; plugin, authoring and portable path gates
  passed. The advisory removed CC-revalidation script warning is pre-existing.
- `git diff --check`: exit 0. Astra independently ran the 16 focused tests and
  checked the diff; final review verdict PASS.

Negative controls exercised missing categories, duplicate sections/AC IDs,
unknown patterns/dispositions, blank/formatted-only evidence cells, missing
exclusion reasons, unresolved ACs, and missing navigation applicability.
Positive controls cover legacy omission, explicit exclusions, external tokens,
multiple AC references, adapter propagation and realistic SDK composition.
These establish coverage integrity and propagation, not a consumer's runtime UX.
All ordered implementation steps are complete; remaining adopting-project
work is to select the concern, map actual behavior, and record real tests/audit.
