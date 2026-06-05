---
ddx:
  id: ADR-EX-001
  type: adr
  methodology: helix
  library_type_version: 1.0.0
  links: []
---

# ADR-EX-001: Use yaml.safe_load for marker parsing

## Context
We need to parse `.helix.yml` from untrusted repos.

## Decision Drivers
- Avoid arbitrary object construction.
- Keep the validator stdlib-friendly (PyYAML is the one allowed dep).

## Considered Options
1. `yaml.safe_load`
2. `yaml.load` with Loader=FullLoader
3. Hand-rolled minimal YAML parser

## Decision
Use `yaml.safe_load`.

## Consequences
- Pro: no code execution risk.
- Con: refuses Python-specific tags; that's a feature, not a bug.

## Status
Accepted.
