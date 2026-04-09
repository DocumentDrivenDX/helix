---
dun:
  id: contract
  depends_on:
    - architecture
---
# Contract

**Contract ID**: [CONTRACT-XXX | API-XXX]
**Type**: [boundary | HTTP API | CLI | library | protocol | event | schema]
**Status**: [draft | complete]
**Related**: [ADR / SD / TD / FEAT references]

## Purpose

[Why this contract exists and what it governs.]

## Scope and Boundaries

- In scope:
- Out of scope:
- Owning system or team:

## Normative Surface

| Element | Type / Shape | Required | Rules | Notes |
|---------|---------------|----------|-------|-------|
| [field, command, message, endpoint] | [type] | [yes/no] | [units, enum, constraints] | [notes] |

## Precedence and Compatibility

- Versioning:
- Ordering or precedence:
- Backward-compatibility rules:

## Error Semantics

| Condition | Error / Outcome | Retry | Recovery Expectation |
|-----------|------------------|-------|----------------------|
| [condition] | [error] | [yes/no] | [recovery] |

## Examples

```text
[Example request / response / payload / invocation]
```

## Validation Checklist

- [ ] Normative fields and rules are explicit.
- [ ] Compatibility and precedence rules are explicit.
- [ ] Error handling is explicit.
- [ ] At least one executable test can be derived from this contract.
