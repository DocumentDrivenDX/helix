# HELIX Action: Implement Feature

Implement the authorized feature or refinement across its affected producers
and consumers. Preserve governing behavior while improving the coherence and
economy of the resulting system.

## Action Purpose

Deliver the requested outcome with meaningful verification. Evolve existing
concepts before introducing parallel methods or DTOs. A mechanical change across
many callers may leave a simpler system than one new public method.

## When to Use This Action

Use when governing intent is clear and implementation is authorized. Existing
coverage may be sufficient for a refactor or mechanical update; a new failing
test is useful for missing behavior or a regression, not mandatory for every edit.

## Prerequisites

Read the relevant requirements, decisions, affected code and existing tests.
Resolve material intent or compatibility questions that existing authority cannot
settle. Use the project's established development environment and checks.

## Action Workflow

### 1. Implementation Planning

Trace the actual gap through the affected operations, interfaces and callers.
Check existing mechanisms and active work before designing additions. Select
the approach that leaves clear responsibilities and avoids redundant state or
operations. Keep the outcome bounded while carrying its consequences through
the system. Use the existing implementation plan; do not create justification
artifacts for routine choices.

### 2. Incremental Implementation

Implement coherent slices and verify them with appropriate existing or extended
coverage. Use Red-Green-Refactor when a failing test supplies missing evidence.
Consolidate overlapping paths and remove superseded mechanisms as understanding
improves. Revise or retire implementation-coupled or redundant tests while
preserving meaningful proof of required behavior. Do not delete failures to
conceal a regression.

### 3. Implementation Patterns

Extend an existing operation or type when it still owns the responsibility.
New types, methods, caches, indices or wrappers need a distinct purpose or
actual compatibility constraint. Inspect consequences at the boundary where
they occur (see the testing practices) rather than generating a matrix for
every possible test layer.

### 4. Code Quality Assurance

Run the project's applicable tests, build and selected concern checks. Investigate
failures against governing behavior; correct either implementation or mistaken
test assumptions with reviewable rationale. Preserve required compatibility,
security and data-integrity behavior. Test success alone does not establish
that the mechanism is necessary or its cost acceptable.

## Implementation Guidelines

Apply the Build enforcer and `scope-discipline` concern. Do not broaden the requested outcome into unrelated
cleanup or narrow it to whichever single file is easiest to edit.

## Completion

Apply `workflows/concerns/verification/practices.md` using existing acceptance
mappings, test-source citations and observed reports. Keep required runtime,
downstream-consumer and conditional supplemental evidence. Update affected
documentation, summarize consequential simplifications and unresolved decisions,
and stop when the authorized outcome is coherent and verified.

## Source-Code Boundary Baseline

Apply `modularity-and-encapsulation` using the all-autonomy source-code baseline
in `workflows/references/concern-resolution.md` and its concern practices. Source
feature work requires baseline adoption, populated Architecture boundary evidence,
and project-local enforcement sequenced before dependent features. Bounded adoption
work may create these prerequisites. Respect legacy validity, source-free reasons,
classic-layered coupling decisions, and scoped exceptions. Genesis only records
applicability for Frame; do not demand a finished Architecture during scaffolding.
Check/Polish propagate existing decisions rather than silently re-selecting them.
Review actual imports, public APIs, owned types and invariants where the requested
scope includes implementation; structural presence checks do not prove semantics.
