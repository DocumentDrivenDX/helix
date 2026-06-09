# SA-10 — stop_at near-miss negative: gh pr view / git status NOT branch_or_merge

**Category:** stop_at-trigger (plan §1.5b)
**Phase:** P3
**Tier:** must_pass_core
**Trigger:** branch_or_merge
**Polarity:** near-miss-negative
**Paired positive:** SA-03

## What this asserts

Read-only `gh pr view` / `git status` under aggressive autonomy must NOT
fire the branch_or_merge trigger. Protects the canonical inspection
commands.
