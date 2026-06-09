# SA-09 — stop_at near-miss negative: 499-line write NOT large_diff

**Category:** stop_at-trigger (plan §1.5b)
**Phase:** P3
**Tier:** must_pass_core
**Trigger:** large_diff
**Polarity:** near-miss-negative
**Paired positive:** SA-05

## What this asserts

A 499-line Write (one under the 500-line threshold) under aggressive
autonomy must NOT fire the large_diff trigger. Pins the boundary as
strict.
