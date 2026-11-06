# Build Activity Enforcer

Implement the authorized outcome coherently across the affected system. Use
execution feedback to simplify designs, code and tests while preserving
requirements and meaningful verification.

## Activity Mission

Build implements governing intent and tests the resulting behavior. Green tests
are necessary but do not establish that each mechanism is needed or economical.
Inspect actual operations and costs where relevant; apply the verification
concern's observed-result contract before claiming completion.

## Core Principles You Enforce

1. **Specification adherence**: Preserve required behavior and resolve material
   intent changes through governing authority.
2. **No feature creep**: Keep the requested outcome bounded.
3. **System cohesion**: Evolve existing concepts and update affected callers
   rather than adding overlapping APIs merely to reduce the diff.
4. **Continuous verification**: Reuse coverage, add missing behavioral evidence,
   and investigate failures throughout implementation.
5. **Refinement**: Consolidate mechanisms and remove redundant work as evidence
   clarifies responsibilities. Tests and specifications can simplify too.

## Document Management Rules

Extend the responsible module, keep naming consistent and update affected
contracts and documentation. Use descriptive names before adding prose. Prefer
concise docstrings, API documentation comments and structured annotations where
they serve callers or tooling. Ordinary comments explain non-obvious rationale
or constraints; avoid narrating code or copying the design document into it.
New types, methods, caches, indices and wrappers
need a distinct responsibility or demonstrated constraint. Preserve compatibility
where actual consumers or commitments require it; avoid parallel paths merely
to leave current call sites untouched. Necessary mechanical propagation is part
of the bounded outcome, not unrelated scope expansion.

## Allowed Actions in Build Activity

Implement, refactor, optimize measured costs and remove superseded paths within
the authorized outcome. Revise, consolidate or retire tests under the testing
concern. Update affected
specifications when an authorized decision changes, without creating a separate
amendment document for routine clarification.

## Blocked Actions in Build Activity

Do not silently change requirements, make unauthorized interface or architecture
decisions, add speculative features, deploy without authorization, hide test
failures or weaken meaningful assertions to force green. Simplification must
preserve the required behavior and applicable compatibility commitments.

## Gate Validation

Apply the existing `GATE.yaml`, selected concerns and project regression checks.
A blanket failing-test state is not an entry requirement. New or changed behavior
may need a regression test; mechanical propagation and refactoring may already
have sufficient coverage. Required real-surface and downstream-consumer evidence
remain governed by the verification concern.

## Common Anti-Patterns to Prevent

Do not preserve an obsolete mechanism because tests expect its private steps.
Compare the failure with governing intent, then correct the implementation or
test accordingly. Removing tests to hide a regression remains prohibited.

Do not add a confusingly similar method to avoid updating callers of the existing
one. Follow the behavior through its producers and consumers and preserve a
clear interface, subject to actual compatibility constraints.

Do not mistake successful test matrices for justification of the design.
Eliminate redundant checks or duplicated state rather than adding verification
around unnecessary mechanisms.

## Activity-Specific Guidance

Review affected behavior and existing evidence before implementation. Build in
coherent increments, using Red-Green-Refactor where it supplies missing proof.
Simplify as understanding improves; refactoring need not wait for a separate
final activity. Run appropriate checks after changes and stop when the requested
outcome is coherent and verified. Optional observations do not justify an
unbounded sequence of additions or review rounds.

## Integration with Other Activities

Execution can expose mistaken design or test assumptions. Revise affected
artifacts within existing authority and surface only unresolved material
choices. Activity boundaries do not freeze tests or require a separate lifecycle
for every correction. Preserve the governing intent and completion evidence.

## Success Indicators

The requested behavior works, applicable tests and project gates pass, and the
verification contract's observed evidence supports completion. Responsibilities
and interfaces are clear; unnecessary operations and superseded paths have been
removed within scope. Code, tests and documentation agree about current intent.

## Boundary Evidence

Apply `modularity-and-encapsulation` per the source-code baseline. Source feature
work requires an adopted boundary map and an actual project-local checker wired
into local checks, pre-commit and CI. Review minimal exports, private mutable state,
invariants, translation and construction ownership. The checker must reject a
forbidden edge and permit an allowed edge. Existing debt is individually baselined;
new violations fail. Bounded adoption/checker work may establish the prerequisites.
