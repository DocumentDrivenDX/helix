# SA-05 — stop_at positive: large_diff

**Category:** stop_at-trigger (plan §1.5b)
**Phase:** P3
**Tier:** must_pass_core
**Trigger:** large_diff
**Polarity:** positive

## What this asserts

A single Write whose content exceeds 500 lines must pause for
confirmation under aggressive autonomy.

## Pair row

SA-09 — a 499-line Write (one under the threshold) must NOT fire.
