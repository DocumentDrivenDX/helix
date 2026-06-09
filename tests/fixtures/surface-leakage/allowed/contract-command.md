---
ddx:
  id: CONTRACT-001
---

# Contract

## Purpose

Defines the CLI surface.

## Scope and Boundaries

- In scope: command invocation.

## Normative Surface

| Command | Type | Required | Rules |
|---------|------|----------|-------|
| `tool run --flag value` | CLI | yes | exits with status code 2 on invalid input |

```json
{"status": "ok"}
```

## Error Semantics

| Condition | Error / Outcome | Retry | Recovery Expectation |
|-----------|------------------|-------|----------------------|
| Invalid input | exit code 2 | no | Fix the flag value |
