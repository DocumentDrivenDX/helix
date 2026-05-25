---
ddx:
  id: FEAT-008
  depends_on:
    - helix.prd
    - FEAT-006
  review:
    self_hash: 55c3f5b337e66301e666cdb14967f0ecee4d9eaffae50aa774a44b4ba343a3fd
    deps:
      FEAT-006: 1711c08bf5e041cd041c762594f278d35744351d4a25b8251566de2dd778abd3
      FEAT-016: 226872932728d635279abac06206be77cee1075d787aae7760010941adb9c1e1
      helix.prd: 2b22383538b33c6ecee57f43d85128dfef7d56254766b757aa36439e35f2bfc9
    reviewed_at: "2026-05-25T23:05:20Z"
---
# Feature Specification: FEAT-008 — Artifact Template Quality and Completeness

**Feature ID**: FEAT-008
**Status**: Draft
**Priority**: P1
**Owner**: HELIX maintainers

## Overview

HELIX artifact templates (Vision, PRD, Feature Spec, Solution Design,
Technical Design, ADR, Test Plan) should be self-documenting and
machine-interpretable. Each template must include clear instructions,
agent-oriented generation prompts, review checklists, and relationship
declarations that allow the artifact graph to be constructed automatically.

## Problem Statement

- **Current situation**: Templates exist under
  `.ddx/plugins/helix/workflows/activities/*/artifacts/*/template.md` but vary
  in completeness. Some include generation prompts, others don't. Review
  checklists are absent. Relationship declarations are embedded in meta.yml
  but not surfaced to agents or reviewers.
- **Pain points**:
  1. Agents produce artifacts with missing or weak sections because templates
     don't explain what belongs in each section.
  2. Adversarial review has no structured checklist, so reviewers apply
     inconsistent criteria.
  3. The artifact graph (Vision → PRD → Specs → Designs → Tests) cannot be
     constructed automatically because relationship declarations are
     inconsistent across templates.
  4. New HELIX users don't know what a "good" artifact looks like because
     templates lack examples.

## Functional Requirements

### FR-1: Section Instructions

Each artifact template must include a brief instruction block (HTML comment
or frontmatter annotation) for every section, explaining what belongs there
and what does not.

### FR-2: Generation Prompts

Each artifact template must include or reference a generation prompt that
agents can use to draft the artifact from higher-level governing artifacts.
The prompt must specify which upstream artifacts to read and what context to
synthesize.

### FR-3: Review Checklists

Each artifact template must include a review checklist that adversarial
review agents use to evaluate the artifact. The checklist must be specific
to the artifact type (e.g., "Does the PRD define success metrics?" rather
than generic "Is this complete?").

### FR-4: Relationship Declarations

Each artifact template must declare its upstream dependencies and downstream
artifacts in a machine-readable format (frontmatter `depends_on` and
`enables` fields), so the artifact graph can be traversed programmatically.

### FR-5: Exemplar Artifacts

Each artifact type must include at least one exemplar — a fully worked
example of a well-written artifact — either inline in the template or as a
companion file. Exemplars should be drawn from real HELIX projects where
possible.

### FR-6: AC↔Test Traceability Is a Template Requirement

Templates must bake in acceptance-criteria-to-test traceability so that
coverage is mechanically checkable rather than asserted in prose:

1. **Stable AC IDs**: user-story acceptance criteria carry stable identifiers
   of the form `US-<n>-AC<m>` (e.g. `US-001-AC1`). The ID survives edits so
   downstream artifacts and tests can reference a specific criterion by name.
2. **Given/When/Then shape**: every acceptance criterion is a single
   Given/When/Then, one precondition, one action, one observable outcome —
   compound criteria are split.
3. **Story-level mapping matrix**: the story test plan owns the per-criterion
   matrix that maps each `US-<n>-AC<m>` to the failing test(s) that prove it,
   keyed by the stable AC ID. The test-plan template does **not** duplicate this
   matrix — it **aggregates** strategy and allocates criteria to test layers
   (contract / integration / unit / E2E).
4. **Layer allocation**: the aggregating test plan records which layer verifies
   each criterion class, so reviewers can see that no P0 criterion is unallocated.

This requirement complements the honesty property in [[FEAT-016]]: stable AC IDs
let the claims-vs-reality check resolve "this criterion is covered by test X"
against a specific, named referent rather than against prose.

> **Note**: template-conformance (FR-1..FR-5) catches *missing or weak*
> sections. It does not catch a well-formed artifact that asserts an untrue
> claim (a phantom test, an invented coverage figure). That honesty property is
> governed by [[FEAT-016]] — Artifact Honesty (Claims-vs-Reality).

### FR-7: Decomposition Coverage (Story-per-FR, ADR-per-decision)

Templates bake in decomposition expectations so rigor is reproducible rather
than left to runtime taste:

1. **Story per functional requirement**: PRD functional requirements carry stable
   `FR-n` IDs and **every `FR-n` maps to ≥1 user story** `US-n`. A story may cover
   several `FR-n`s but should not bundle *unrelated* requirements without recorded
   justification. The FR→story mapping is a **coverage floor**, enforced as a
   blocking gap by reconcile-alignment (Acceptance Criteria Validation) — extra
   stories are always welcome; only a `FR-n` with no story is a finding.
2. **ADR per material decision**: a material architecture/technology decision
   should be recorded in an ADR. This is an **expectation, not a hard gate** —
   "material" is too fuzzy to gate deterministically, so reviewers surface a
   missing ADR as a recommendation rather than a blocking failure.

This is a floor on minimum rigor (decomposition + traceability), not a cap and not
a promise of equal total depth across runtimes.

### FR-8: Interface-Quality Guidelines and the DESIGN.md Artifact

Templates and concern practices must govern interface-quality so a UI is built
with a legible, consistent design system rather than left to runtime taste:

1. **Required visual cues (`ux-radix`)**: the current page MUST show a visible
   active state **and** `aria-current="page"` on the active nav item; interactive
   elements express their states **where applicable** (hover + focus-visible for
   enabled controls; disabled where disablement exists; loading for async
   actions; empty/error for data/form/content surfaces). `aria-current` is both a
   UX and an accessibility cue — keep it consistent with `a11y-wcag-aa`.
2. **The DESIGN.md artifact**: a governed, project-level artifact
   (`workflows/activities/02-design/artifacts/design-system/`, output
   `docs/helix/02-design/DESIGN.md`) captures the app's concrete
   **interface-system** decisions — navigation model + active-state convention,
   visual hierarchy, the applicable interaction states, and tokens
   (color/spacing/type). It is the app-specific *instance* of these guidelines,
   **not** a mirror of the concern library, and explicitly **excludes** runtime
   architecture, data flow, component implementation internals, and ADR material
   (those live in architecture/solution-design/ADRs).
3. **Mechanized visual-cue verification**: a UI web app's browser e2e MUST assert
   `aria-current="page"` on the active nav item for ≥1 route (**required,
   non-optional**). An active class/style may be asserted *additionally* but is
   **never a substitute** for `aria-current`; no pixel/screenshot assertions for
   this gate. This makes "does it show me where I am?" a checkable gate that
   feeds the `verification` concern.

## Non-Functional Requirements

### NFR-1: Template Size

Templates including instructions and checklists must remain under 200 lines
to avoid overwhelming agents with boilerplate.

### NFR-2: Backward Compatibility

Existing artifacts must remain valid. New template features are additive.

## Acceptance Criteria

1. Every artifact template under `workflows/activities/*/artifacts/*/template.md`
   includes section instructions, a generation prompt reference, and a review
   checklist.
2. Every artifact template declares `depends_on` and `enables` relationships
   in its meta.yml.
3. At least one exemplar artifact exists for each artifact type.
4. `/helix review` can load the review checklist for the artifact type being
   reviewed and evaluate against it.
5. User-story acceptance criteria carry stable `US-<n>-AC<m>` IDs in
   Given/When/Then form; the story test plan maps each AC ID to concrete
   failing tests; the project test plan aggregates strategy and allocates
   criteria to test layers without duplicating the story-level matrix.
6. The `ux-radix` practices require current-location feedback (visible active
   state + `aria-current="page"`) and the where-applicable interaction states; a
   governed `design-system` artifact (DESIGN.md) exists with the non-goal section
   excluding architecture/data-flow/impl-internals/ADR material; and a UI web
   app's browser e2e asserts `aria-current="page"` on the active nav for ≥1 route
   (required, never substituted by a class/style or screenshot assertion).

## Constraints

- Templates must work with the existing DDX artifact management system.
- Relationship declarations must be compatible with the existing `ddx`
  frontmatter format.

## Out of Scope

- Automated artifact graph visualization (future work).
- Enforcing template compliance at write time (advisory only for now).
