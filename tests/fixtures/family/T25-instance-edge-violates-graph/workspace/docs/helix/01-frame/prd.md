---
ddx:
  id: PRD-001
  type: prd
  methodology: helix
  library_type_version: 1.0.0
  links:
    - { kind: requires, to: FEAT-001 }
---

# PRD-001 — Test PRD

`requires` is NOT in the graph for (prd, feature-specification); only
`informs` is. Validator must emit G201 naming the bad edge.
