# Tracker Usage

Use the built-in HELIX tracker only. Issues are stored in `.helix/issues.jsonl`.

## Review Epic

```bash
helix tracker create "HELIX alignment review: <scope>" \
  --type epic \
  --labels helix,phase:review,kind:review \
  --spec-id <closest-governing-artifact>
```

## Review Issue

```bash
helix tracker create "Review <functional area>" \
  --type task \
  --parent <review-epic-id> \
  --labels helix,phase:review,kind:review,area:<area>
```

## Execution Issue

```bash
helix tracker create "<deterministic follow-up work>" \
  --type task \
  --labels helix,phase:<phase>,kind:<kind> \
  --spec-id <closest-governing-artifact>
```

Add blockers with:

```bash
helix tracker dep add <blocked-id> <blocker-id>
```

Use:

- `helix tracker ready` for unblocked work
- `helix tracker blocked` for blocked work
- `helix tracker show <id>` for context
- `helix tracker update <id> --claim` to claim work
- `helix tracker close <id>` when complete
