---
title: "SEI Reasoning About Software Quality Attributes"
slug: sei-quality-attribute-scenarios
generated: true
---
> **Source identity**:

```yaml
ddx:
  id: resource.sei-quality-attribute-scenarios
```

# SEI Reasoning About Software Quality Attributes

## Source

- URL: https://www.sei.cmu.edu/library/reasoning-about-software-quality-attributes/
- Accessed: 2026-05-12

## Summary

The Carnegie Mellon Software Engineering Institute describes quality attributes
such as performance, security, modifiability, reliability, and usability as
major influences on software architecture. SEI guidance emphasizes making these
attributes concrete through scenarios so teams can reason about whether design
choices support the desired quality outcomes.

## Relevant Findings

- Quality attributes materially shape architecture and cannot be treated as
  afterthoughts.
- A quality attribute name is not enough; teams need concrete scenarios or
  practices that explain how the attribute should affect decisions.
- Different quality attributes can interact or conflict, so guidance should
  expose likely side effects and tradeoffs.
- System-independent quality guidance becomes useful when translated into the
  specific project context.

## HELIX Usage

This resource informs the Project Concerns artifact. HELIX uses it to require
concerns to carry actionable practices, area scope, and conflict resolution
rather than a bare list of quality labels.

## Authority Boundary

This resource supports quality-attribute reasoning. It does not replace HELIX
Project Principles, ADRs, Technical Designs, or test plans, all of which own
different levels of decision and verification detail.
