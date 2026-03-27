---
name: helix-check
description: Run the HELIX queue-drain decision action. Use when the user wants `helix check` behavior.
argument-hint: "[scope]"
disable-model-invocation: true
---

# Check

Execute the HELIX `check` action and return the required decision markers.

## Steps

1. Read and apply `workflows/actions/check.md`.
2. Use `$ARGUMENTS` as the scope when provided, otherwise default to repo scope.
3. Evaluate the queue and planning stack conservatively.
4. Return the exact `NEXT_ACTION` line and the exact next command.

## Constraints

- Do not guess past missing evidence.
- Prefer `WAIT` or `GUIDANCE` over unsafe execution.
- Do not dispatch implementation, alignment, or backfill silently.
