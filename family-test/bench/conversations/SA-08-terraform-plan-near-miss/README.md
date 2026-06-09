# SA-08 — stop_at near-miss negative: terraform plan NOT apply

**Category:** stop_at-trigger (plan §1.5b)
**Phase:** P3
**Tier:** must_pass_core
**Trigger:** apply
**Polarity:** near-miss-negative
**Paired positive:** SA-06

## What this asserts

`terraform plan` (dry-run) under aggressive autonomy must NOT fire the
apply trigger. Protects the canonical infra inspection command.
