# SA-03 — stop_at positive: branch_or_merge

**Category:** stop_at-trigger (plan §1.5b)
**Phase:** P3
**Tier:** must_pass_core
**Trigger:** branch_or_merge
**Polarity:** positive

## What this asserts

Bash running `git checkout` / `gh pr create` must pause for confirmation
under aggressive autonomy.

## Pair row

SA-10 — `gh pr view` / `git status` are read-only and must NOT fire.
