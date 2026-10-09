---
ddx:
  id: CONTRACT-XXX
  authoring:
    home: repo
---

# Contract

**Contract ID**: [CONTRACT-XXX | API-XXX]
**Type**: [boundary | HTTP API | CLI | library | protocol | event | schema]
**Version**: [v1]
**Status**: [draft | complete]
**Related**: [ADR / SD / TD / FEAT references]

## Purpose

[Why this contract exists and what it governs.]

## Scope and Boundaries

- In scope:
- Out of scope:
- Owning system or team:

## Normative Surface

Use MUST, MUST NOT, MAY, and SHOULD intentionally. Every field, command,
message, endpoint, or payload element named here is part of the contract.

| Element | Type / Shape | Required | Rules | Notes |
|---------|---------------|----------|-------|-------|
| [field, command, message, endpoint] | [type] | [yes/no] | [units, enum, constraints] | [notes] |

## Precedence and Compatibility

- Versioning:
- Ordering or precedence:
- Backward-compatibility rules:
- Deprecation rules:

## Error Semantics

| Condition | Error / Outcome | Retry | Recovery Expectation |
|-----------|------------------|-------|----------------------|
| [condition] | [error] | [yes/no] | [recovery] |

## Examples

```text
[Example request / response / payload / invocation]
```

## Non-Normative Notes

[Optional rationale or implementation guidance. Nothing in this section changes
the contract.]

## Telemetry and Diagnostic Surfaces (when applicable)

When this Contract governs diagnostics, define the local event/schema version,
exact mapping to the adopted OTel model, Resource/scope identity, severity,
timestamps/units and event catalog. Specify conditional trace context separately
from namespaced run/attempt IDs. Pin OTel/semantic-convention/integration versions.
Define capture/query input and output, access scope, bounds, source references,
ordering/snapshot/cursor behavior during concurrent writes and rotation, loss
reporting, compatibility and recovery. Include traced and untraced examples.
Do not treat JSONL as OTLP. See `workflows/references/agent-diagnostics.md`.
