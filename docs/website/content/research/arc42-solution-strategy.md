---
title: "arc42 Solution Strategy and Building Block View"
slug: arc42-solution-strategy
generated: true
---
> **Source identity**:

```yaml
ddx:
  id: resource.arc42-solution-strategy
```

# arc42 Solution Strategy and Building Block View

## Source

- URL: https://docs.arc42.org/section-4/
- URL: https://docs.arc42.org/section-5/
- Accessed: 2026-05-12

## Summary

arc42 describes solution strategy as the short explanation of fundamental
decisions and approaches that shape an architecture. Its building block view
describes the system's static decomposition into modules, components,
subsystems, interfaces, and their relationships. Together, these sections help
teams communicate how requirements and constraints translate into structure
without documenting code-level detail.

## Relevant Findings

- Solution strategy should explain the important choices and why they were made
  based on requirements, quality goals, and constraints.
- Building block views make decomposition understandable through abstraction.
- Interfaces and relationships between building blocks are part of the design
  when they are important for understanding the system.
- Useful design documentation stays concise and points to details elsewhere
  rather than duplicating every lower-level decision.

## HELIX Usage

This resource informs the Solution Design artifact. HELIX uses it to keep
feature-level designs focused on alternatives, selected approach,
decomposition, domain model, interfaces, and traceability to requirements.

## Authority Boundary

This resource supports architecture and solution-design documentation. It does
not replace HELIX Architecture, ADR, Contract, or Technical Design artifacts,
which own different levels of structural authority and implementation detail.
