---
name: helix-triage
description: Create well-structured tracker issues with validated metadata, governing artifact references, and deterministic acceptance criteria.
argument-hint: '"Title" [--type task|epic|bug|chore] [options...]'
---

# Triage: Create Execution-Ready Issues

Every issue should enter the tracker ready to execute. This skill guides you
through creating issues with the metadata that `helix run` needs to select,
build, and close them.

## When to Use

- Creating new implementation, design, or test issues
- Decomposing an epic into child tasks
- Recording blockers or follow-on work during implementation
- Filing bugs discovered during review or testing

## Required Metadata

The tracker enforces these structural rules at creation time:

| Field | Required For | What To Set |
|-------|-------------|-------------|
| `--labels helix,phase:*` | All issues | `helix` + one of `phase:build`, `phase:deploy`, `phase:iterate`, `phase:design`, `phase:review` |
| `--spec-id` | Tasks | Nearest governing artifact (e.g., `SD-001`, `ADR-048`, `TP-SD-014`) |
| `--acceptance` | Tasks, Epics | Deterministic completion criteria — what must be true when this is done |
| `--description` | Recommended | Work contract: what to do, which files, governing artifact references |
| `--design` | Recommended | Implementation approach: how to do it |

Additional labels to include when applicable:
- `kind:build`, `kind:implementation`, `kind:testing`, `kind:documentation`
- `area:*` for the affected subsystem (e.g., `area:wal`, `area:query`, `area:cli`)

## Steps

1. **Identify the governing artifact.** What spec, design, ADR, or test plan
   authorizes this work? Set `--spec-id` to its ID.

2. **Write deterministic acceptance criteria.** The AC should be verifiable
   by running a specific command or checking a specific condition. Bad:
   "system works correctly." Good: "cargo test -p niflheim-wal passes;
   AC-SD17-003 promoted to active in TP-SD-017.acceptance.toml."

3. **Choose type and labels.**
   - `task` — bounded work with clear completion (most issues)
   - `epic` — collection of tasks sharing a goal (needs child decomposition)
   - `bug` — something broken (no spec-id needed)
   - `chore` — maintenance (no spec-id needed)

4. **Set parent and dependencies.** If this is part of an epic, set `--parent`.
   If it depends on other issues completing first, use `--deps`.

5. **Create the issue.**

```bash
helix tracker create "Implement X" \
  --type task \
  --labels helix,phase:build,kind:implementation,area:wal \
  --spec-id SD-017 \
  --description "Implement the Y component per SD-017 Section 3.2. Governing: SD-017, TP-SD-017, ADR-050." \
  --acceptance "cargo test -p niflheim-wal test_y passes; AC-SD17-005 promoted to active" \
  --parent hx-epic-id \
  --deps hx-dependency-id
```

## Decomposition Pattern

When an epic or large task needs breakdown:

1. Read the parent's acceptance criteria
2. Create child tasks that collectively cover every AC
3. Set `--parent` on each child
4. Each child should be completable in one `helix build` cycle
5. If the parent is a task with 2+ children, consider promoting it to an epic

## References

- Tracker conventions: `workflows/TRACKER.md`
- Label taxonomy: `workflows/TRACKER.md` (Labels section)
- Implementation action: `workflows/actions/implementation.md`
- CLI: `helix tracker create --help`
