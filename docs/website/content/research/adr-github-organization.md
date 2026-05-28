---
title: "Architectural Decision Records"
slug: adr-github-organization
generated: true
---
> **Source identity**:

```yaml
ddx:
  id: resource.adr-github-organization
```

# Architectural Decision Records

## Source

- URL: https://adr.github.io/
- Accessed: 2026-05-12

## Summary

The ADR GitHub organization describes an architectural decision as a justified
design choice that addresses architecturally significant requirements. An ADR
captures one decision and its rationale, tradeoffs, and consequences. A
project's ADRs form a decision log that helps teams understand why the
architecture changed over time.

## Relevant Findings

- ADRs should capture the reason for a chosen decision, not only the final
  choice.
- A useful ADR focuses on one architecturally significant decision.
- Tradeoffs and consequences are central; an ADR without them is just a note.
- ADR collections create durable architectural knowledge across iterative work.

## HELIX Usage

This resource informs the Architecture Decision Record artifact. HELIX uses it
to keep ADRs compact, single-decision records that preserve rationale for
agents and humans working from shared context.

## Authority Boundary

This resource does not define HELIX's artifact stack or lifecycle rules. HELIX
keeps ADRs subordinate to architecture for structural coherence and treats
accepted ADRs as write-once history except for status changes.
