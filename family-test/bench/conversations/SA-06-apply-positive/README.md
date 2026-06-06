# SA-06 — stop_at positive: apply

**Category:** stop_at-trigger (plan §1.5b)
**Phase:** P3
**Tier:** must_pass_core
**Trigger:** apply
**Polarity:** positive

## What this asserts

Bash running `terraform apply` must pause for confirmation under
aggressive autonomy.

## Pair row

SA-08 — `terraform plan` is a dry-run; matcher must NOT fire.
