# Solution Design Generation Prompt

Create a solution design that maps requirements to a concrete approach.

## Purpose

Solution Design is the **feature-level design artifact**. Its unique job is to
translate a Feature Specification into a selected technical approach, domain
model, component decomposition, interface usage, and requirement-to-design
traceability.

It applies Architecture, ADRs, Contracts, and Concerns to one feature or
cross-component capability. For what belongs at this level versus Architecture
and Technical Design, see the zoom-stack matrix in
`workflows/activities/02-design/README.md`.

## Reference Anchors

Use these local resource summaries as grounding:

- `docs/resources/arc42-solution-strategy.md` grounds feature-level approach,
  decomposition, interfaces, and concise design rationale.
- `docs/resources/c4-model.md` grounds component and interaction views that
  support feature-level decomposition.

## Focus
- Create a feature-level artifact named `docs/helix/02-design/solution-designs/SD-XXX-[name].md`.
- Show the main options and why the chosen one wins.
- Keep the domain model, decomposition, and tradeoffs concise.
- Cover cross-component system behavior and feature-level structure.
- Preserve only the decisions needed by build and test.
- Stay within the feature scope defined in the zoom-stack matrix
  (`workflows/activities/02-design/README.md`); update the governing artifact
  first if the feature forces a change at a higher level.

## Boundary Test

See the zoom-stack matrix in `workflows/activities/02-design/README.md` for
which decisions belong at the system, feature, and story levels.

## Completion Criteria
- Requirements are mapped.
- Tradeoffs are explicit.
- The chosen approach is clear.
- The output is clearly feature-level and disambiguated from a technical
  design.
- Every P0 requirement has a corresponding design element and test strategy.
