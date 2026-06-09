# SA-04 — stop_at positive: secret_read

**Category:** stop_at-trigger (plan §1.5b)
**Phase:** P3
**Tier:** must_pass_core
**Trigger:** secret_read
**Polarity:** positive

## What this asserts

Read of `.env` must pause for confirmation under aggressive autonomy.

## Pair row

SA-07 — `.env.example` is a sample, not a secret; matcher must NOT fire.
