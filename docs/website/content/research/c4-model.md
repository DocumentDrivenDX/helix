---
title: "C4 Model for Visualising Software Architecture"
slug: c4-model
generated: true
---
> **Source identity**:

```yaml
ddx:
  id: resource.c4-model
```

# C4 Model for Visualising Software Architecture

## Source

- URL: https://c4model.com/
- Accessed: 2026-05-12

## Summary

The C4 model provides a small hierarchy of architecture diagrams: System
Context, Container, Component, and Code. It emphasizes abstractions that help
teams communicate software structure at different levels of detail. The model
also includes deployment diagrams as a complementary view for showing how
containers run in infrastructure environments.

## Relevant Findings

- Architecture views should be chosen for the audience and question at hand;
  not every level is required for every system.
- Container diagrams are often the most useful level for implementation
  planning because they name independently deployable or executable units.
- Component diagrams are useful only when a container is complex enough to need
  internal structure explained.
- Diagrams should expose boundaries, responsibilities, technologies, and
  relationships rather than decorative boxes.

## HELIX Usage

This resource informs the Architecture artifact. HELIX uses it to keep
architecture documentation focused on the structural views that downstream
design, deployment, testing, and implementation work actually need.

## Authority Boundary

This resource defines a diagramming model, not HELIX's artifact hierarchy or
approval process. HELIX architecture documents should use only the C4 views
that add useful context.
