---
title: "OWASP Threat Modeling Cheat Sheet"
slug: owasp-threat-modeling-cheat-sheet
generated: true
---
> **Source identity**:

```yaml
ddx:
  id: resource.owasp-threat-modeling-cheat-sheet
```

# OWASP Threat Modeling Cheat Sheet

## Source

- URL: https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html
- Accessed: 2026-05-12

## Summary

The OWASP Threat Modeling Cheat Sheet describes threat modeling as a structured
way to identify, communicate, and address security design concerns. It stresses
understanding data flows, trust boundaries, components, assets, assumptions,
and threats before selecting mitigations. It uses STRIDE as an illustrative
method, while noting that other methods may also apply.

## Relevant Findings

- Threat modeling should start with the system design, data flows, and trust
  boundaries.
- Data flow diagrams are a common way to reason about where data moves and
  where trust changes.
- STRIDE categories can help identify threats systematically.
- The output should connect threats to mitigations and security requirements.
- Missing trust boundaries or unclear assumptions are themselves threat-model
  findings.

## HELIX Usage

This resource informs the Threat Model artifact. HELIX uses it to keep threat
modeling grounded in assets, data flows, trust boundaries, assumptions,
prioritized threats, and mitigations that can flow into security design and
tests.

## Authority Boundary

This resource supports application threat modeling. It does not replace
project-specific compliance analysis, security requirements, penetration
testing, or operational incident response.
