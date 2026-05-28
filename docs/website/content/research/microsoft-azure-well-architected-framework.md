---
title: "Microsoft Azure Well-Architected Framework"
slug: microsoft-azure-well-architected-framework
generated: true
---
> **Source identity**:

```yaml
ddx:
  id: resource.microsoft-azure-well-architected-framework
```

# Microsoft Azure Well-Architected Framework

## Source

- URL: https://learn.microsoft.com/en-us/azure/well-architected/what-is-well-architected-framework
- Accessed: 2026-05-12

## Summary

Microsoft's Azure Well-Architected Framework organizes workload guidance around
five cross-cutting pillars: reliability, security, cost optimization,
operational excellence, and performance efficiency. Each pillar provides
recommended practices, risks, tradeoffs, checklists, and design guidance. The
framework emphasizes that workload architecture and implementation are related
but distinct: cross-cutting guidance shapes decisions, while implementation
choices still depend on business requirements and constraints.

## Relevant Findings

- Cross-cutting concerns need explicit ownership because every workload must
  balance reliability, security, operations, performance, cost, and related
  tradeoffs.
- Useful concern guidance includes practices, risks, and tradeoffs rather than
  only naming a quality area.
- Concern relevance depends on workload context; teams should prioritize the
  guidance that applies to their business goals and maturity.
- Practices can have costs and dependencies, so concern selection should avoid
  adopting guidance that is irrelevant or premature.

## HELIX Usage

This resource informs the Project Concerns artifact. HELIX uses it to keep
active cross-cutting domains visible to agents while preserving the boundary
between guidance, architecture decisions, and implementation work.

## Authority Boundary

This resource is Azure-centered and does not define HELIX's concern library or
artifact hierarchy. HELIX concerns may include technology stacks, quality
attributes, conventions, and project-specific operating guidance beyond Azure
workloads.
