# Concern: Modularity and Encapsulation

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
