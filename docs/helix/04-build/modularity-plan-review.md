---
ddx:
  id: helix.review.modularity-plan
  authoring:
    home: repo
---
# Modularity Execution Plan Review

Reviewed on 2026-10-09 using the user-requested Astra Ultra review. Target:
`docs/helix/04-build/modularity-execution-plan.md`. The review examined the
plan against the repository instructions, concern policy, architecture catalog,
instance validator, and Design/Polish/Genesis contracts. No implementation or
tracker changes were made by this reviewer.

## Initial Findings

The initial verdict was **revise before implementation**. The direction was
sound, but four decisions were needed to make the plan execution-ready.

### P1: Resolve compatibility with classic-layered

The initial Shared Constraints made the baseline composable while fencing
persistence dependencies from the core. Existing
`workflows/concerns/classic-layered/concern.md:82` explicitly permits the
domain/business layer to call concrete repository and ORM types and makes a
composition root optional. Selecting both could create contradictory rules.

Requested fix: distinguish protected domain types/invariants from service
orchestration permitted to call a concrete DAL, define construction ownership
without requiring DI, or explicitly revise classic-layered with adoption
guidance. Include a compatibility fixture.

### P1: Decide the backward-compatibility contract

The initial M2 required a new Architecture section globally, but
`docs/helix/01-frame/features/FEAT-008-artifact-template-quality.md:166` says
existing artifacts remain valid. The instance validator applies required
sections unconditionally and has no legacy/applicability distinction.

Requested fix: use conditional validation or an explicit governed compatibility
change. Preserve historical artifact validity while blocking current source-work
readiness until adoption. Cover existing and source-free architectures.

### P1: Specify the missing-evidence detector

The initial Validation Plan required ownership, dependencies, integration,
construction, and command evidence, but
`skills/helix/scripts/validate-instance.py:209` checks only heading presence for
required sections. The call sequence at line 353 does not execute catalog
`quality_checks`. A heading-only document could therefore pass a structural
check without the promised evidence.

Requested fix: name the validator changes and the evidence structure they check.
Exercise empty sections, missing/blank cells, missing integration disposition,
missing command, and unjustified N/A. Assign semantic correctness to review.

### P2: Define precedence and allow adoption work

The initial readiness gate did not say whether project overrides could remove
the baseline or whether the work needed to install the gate could execute while
it was missing. FEAT-006 FR-4 at
`docs/helix/01-frame/features/FEAT-006-concerns-practices-context-digest.md:431`
and `workflows/references/concern-resolution.md:81` give project overrides full
precedence.

Requested fix: define the evidence floor, permissible substitutions, and scoped
exceptions. Allow bounded baseline/adoption/checker work before the gate exists;
block dependent feature work. Exceptions need ownership, exact scope,
rationale, authority, alternative verification, and a review/removal trigger.
Enlarging a baseline must not hide new debt.

## Initial Non-blocking Refinements

- Complete Polish with concrete paths and validation commands for each slice.
- Genesis should record applicability and initial selection, leaving completed
  architecture to Design. Its READY contract at
  `workflows/actions/genesis.md:110` means ready for Frame.

## Revised Plan Dispositions

The revised plan was reread after the author incorporated the findings.

| Finding | Disposition |
|---|---|
| Classic-layered compatibility | Resolved in the plan. It distinguishes domain types/invariants, orchestration, and integration representations; records deliberate coupling under classic-layered; and requires a construction policy without forcing inversion or a composition root. |
| Backward compatibility | Resolved in the plan. Legacy Architecture instances without Module Boundaries remain structurally valid. Current source work requires adoption evidence for readiness. Present sections are checked, and new templates contain the section. |
| Missing-evidence detection | Resolved in the plan. M2 names a new `module_boundaries` automated rule in the real instance validator. Validation covers empty/incomplete sections and the required evidence, with semantic review explicitly separate from structural checks. |
| Precedence and adoption | Resolved in the plan. Overrides cannot silently erase evidence; departures require scoped, governed exceptions. Bounded adoption/checker work can run before the floor exists, while dependent feature work cannot. New debt cannot be concealed by widening baselines. |
| Polish specificity | Resolved in the plan. The decomposition names the concern/reference/spec files, catalog artifacts, workflow gates, validator, tests, and publication surfaces, with commands attached to the slices. |
| Genesis scope | Resolved in the plan. M3 limits Genesis to applicability and preserves ready-for-Frame semantics. |

## Verdict

**No remaining blocking plan findings. Proceed to implementation.**

This verdict approves the revised execution contract, not an implementation.
The planned implementation review must verify the actual rule behavior,
classic-layered compatibility, exception handling, workflow readiness gates,
and regression evidence before landing.
