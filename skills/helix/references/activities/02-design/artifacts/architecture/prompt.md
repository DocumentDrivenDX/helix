# Architecture Documentation Generation Prompt

Document the architecture views that the team actually needs to build, review,
operate, and evolve the system.

## Purpose

Architecture is the **highest-authority structural artifact** in the Design
activity. Its unique job is to describe the durable system shape: boundaries,
containers, externally visible integrations, deployment topology, critical data
flows, quality attributes, and structural tradeoffs.

For what belongs at this level versus Solution Design and Technical Design, see
the zoom-stack matrix in `workflows/activities/02-design/README.md`.

## Reference Anchors

Use these local resource summaries as grounding:

- `docs/resources/c4-model.md` grounds context, container, component, and
  deployment views as audience-specific structural diagrams.
- `docs/resources/sei-quality-attribute-scenarios.md` grounds measurable
  quality attributes and tradeoff reasoning.
- `docs/resources/microsoft-azure-well-architected-framework.md` grounds
  cross-cutting reliability, security, operations, performance, and cost
  tradeoffs.

## Focus
- Include only the C4 views that add information; omit empty or duplicate views.
- Keep boundaries, deployment shape, data flow, and quality attributes visible.
- Annotate major tradeoffs or constraints directly on the relevant view or summary.
- Remove generic architecture commentary.

## Boundary Test

See the zoom-stack matrix in `workflows/activities/02-design/README.md` for
which decisions belong at the system, feature, and story levels.

## Completion Criteria
- The views are understandable at a glance.
- Key boundaries and tradeoffs are visible.
- The document stays implementation-relevant.
- Containers name real technologies, not generic roles.
- Quality attributes have measurable targets and verification methods.
- Deployment names actual infrastructure shape, scaling, and backup approach.
- Major decisions link to ADRs or include an inline decision note.
