---
title: "Modularity and Encapsulation"
slug: modularity-and-encapsulation
generated: true
aliases:
  - /reference/glossary/concerns/modularity-and-encapsulation
---

**Category:** Quality Attributes · **Areas:** all

## Description

## Category
quality-attribute

## Areas
all

## Boundary

This is the source-code baseline: deliberate module ownership, public surfaces,
private implementation, and checkable dependency rules. It composes with any
`architecture-style`; it does not select one or prescribe rings, microservices,
repository interfaces, or a dependency injection container.

- Architecture styles own macro dependency direction and inversion. This concern
  requires the chosen rules to be explicit and enforced, including deliberate
  coupling accepted by `classic-layered`.
- `domain-driven-design` owns modeling and invariants. This concern owns which
  module exposes and protects those types and behavior.
- `code-shape-ceilings` bounds size and complexity. Small files can still violate
  boundaries; size checks do not replace dependency checks.
- `testing` owns test strategy; this concern requires boundary negative controls.

## Constraints

- Every module has a coherent responsibility and owns its types and state.
  Export the smallest useful public API; callers must not reach into internals
  or mutate state in ways that bypass invariants.
- Classify domain types/invariants separately from application orchestration,
  transport data, persistence representations, and vendor integration types.
  Prefer pure domain types independent of services and integration frameworks.
  Pure computational libraries are not forbidden merely because they are external.
- Record permitted and forbidden dependency edges and reject cycles. A scoped
  exception needs authority and alternative verification; never silently permit
  a cycle or widen a baseline to hide new debt.
- Each external integration has a named owning module. Translate vendor data,
  errors, and transport representations at its boundary. Avoid spreading SDK
  imports through unrelated modules or a generic shared-types dumping ground.
- Document where concrete implementations are constructed and wired. Inversion
  styles require a composition root; classic-layered may use deliberate local
  construction and concrete data-access dependencies. Record that coupling and
  its implications rather than imposing inversion under another name.
- Language visibility/package rules and project-local dependency checks enforce
  boundaries where possible. Record remaining semantic review obligations;
  a heading or import check alone does not prove encapsulation.

## When to use

Every project with handwritten source code, including libraries and single-file
programs, at low, medium, and high autonomy. Source-free documentation or wholly
generated products record non-applicability with a reason. Unknown applicability
must be resolved before feature work is execution-ready. See the source-code
baseline in `workflows/references/concern-resolution.md` for adoption and precedence.

## Drift Signals (anti-patterns to reject in review)

- SDK, ORM, or transport imports spread through unrelated modules
- Core types owned by a service or vendor package; integration DTOs reused as
  the domain model without a deliberate coupling decision
- Public mutable internals, bypassable invariants, import cycles, private APIs
  accessed across modules, or unrelated responsibilities in a shared utility
- A declared boundary with no checker or review evidence; a checker with no
  forbidden-edge negative control
- Baselines widened or exceptions added simply to make new violations pass

## Artifact Impact

- CONCERNS: baseline selection and applicability at every autonomy level; source-free reason
- ARCHITECTURE: Module Boundaries map, integration ownership, construction policy,
  allowed/forbidden dependencies, and concrete boundary-check command
- CONTRACT: exact shared public interfaces where a shared surface exists
- TD: affected modules/types, public-surface impact, governing Contract references,
  dependency rules applied, and focused invariant tests
- IMPLEMENTATION_PLAN: boundary map/adoption and checker scaffold before dependent
  feature work, local/pre-commit/CI wiring, and named verification evidence
- TEST_PLAN: permitted and forbidden import controls, cycle/private-access checks
  where supported, invariant tests, core isolation when promised by the style,
  adapter contract tests, and explicit remaining review obligations
- ADR: deliberate coupling, scoped exceptions, or existing-project adoption decisions

## Practices by activity

Agents working in any of these activities inherit the practices below through runtime work context, such as a DDx bead context digest.

## Frame

Resolve the source-code baseline in `workflows/references/concern-resolution.md`
at every autonomy level. Select this composable concern for handwritten source,
including libraries. Record applicability, source, and `areas: all`; source-free
projects record why it does not apply. Do not force an architecture-style filler.

## Design

Write `## Module Boundaries` in Architecture. Use this structural evidence format:

- `**Source Applicability**: source; <reason>` or `source-free; <reason>`.
- For source projects, a table with columns `Module`, `Responsibility / Owned Types`,
  `Public API`, `Allowed Dependencies`, and `Forbidden Dependencies`. Each row
  names actual packages/files and has nonempty values. Explicit `None; <reason>`
  is valid; a small project may have one row.
- `**Integration Owners**: <external system -> owning module; translation location>`.
  If absent, state `None; <reason>`.
- `**Construction Policy**: <wiring owner/location and approach>`. Local construction
  is valid under classic-layered; inversion styles retain their composition rules.
- `**Boundary Check**: <concrete project-local command>`; it must enforce the map.

Source-free documents need only applicability and reason in this section. Legacy
artifacts without the section remain structurally valid; current source feature
work requires adoption before execution readiness. The instance validator checks
structure and populated fields when the section exists. Review checks correctness,
including type ownership, API visibility, invariants, translation, and style fit.

Do not copy normative signatures into Architecture or TD. Shared interface details
belong in Contracts; module maps may name APIs and reference their Contract IDs.

## Build

Establish the map and a stack-appropriate dependency checker before dependent
feature work. Use one command in local checks, pre-commit, and CI; prove both an
allowed dependency passes and a forbidden dependency fails. Test the real checker,
not a test-only clone. Use compiler/package visibility where available; supplement
unsupported checks with explicitly named review evidence.

Changes add code to its owning module, not whichever orchestrator is convenient.
New external integrations get a named module. Preserve minimal exports and avoid
passing mutable internal state across public interfaces.

## Test

- Run the actual import checker against allowed and forbidden edges; prove cycle
  and private-access detection where the chosen tool supports them.
- Test invariants through public APIs, including mutation/invalid-state rejection
  where applicable. Check vendor/ORM/transport shapes do not leak into APIs unless
  deliberately accepted by the selected architecture style.
- Where isolation or substitution is promised, run core behavior without live
  integrations and exercise the adapter contract with a fake implementation.
- Record unsupported static checks as semantic review obligations. Do not claim
  regex presence checks prove dependency direction or runtime behavior.

## Existing-project adoption

Inventory specific violations by source and target, with owner and remediation
work. Baseline only existing violations; unchanged debt may remain while new edges
fail. Baseline/adoption/checker work may execute before the gate exists; dependent
feature work is not ready. Tighten the baseline as remediation lands.

Overrides may adapt enforcement mechanisms. Departures require an exception with
exact scope, owner, governing authority, rationale, alternative verification, and
review/removal trigger. A blanket directory exclusion or larger baseline used to
hide new violations is not valid adoption.

## Review and Align

Compare current imports and public surfaces with the map and Contracts within the
requested scope. Report missing baseline, incomplete boundary evidence, unmeasured
checker gates, and new violations as blocking readiness findings. Preserve legacy
artifact validity and report adoption gaps separately from structural validation.
