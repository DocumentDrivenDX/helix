# T28 — nested .helix.yml emits M010 warning [HIGH RISK]

## Scenario

Workspace has a valid root `.helix.yml` and a stray
`services/api/.helix.yml` (nested marker). Per design §1.1 the
upward walk from cwd resolves to the root marker; the validator
then scans the whole tree and emits **M010** for each stray nested
marker. v1 ignores them; v2 may flip M010 to error.

## Why it matters

Without M010, a user who creates `services/api/.helix.yml` thinking
it overrides for that subtree gets silent ignore — the failure mode
this whole design exists to prevent. Phase 4 review S1 fold:
explicit warning, with path listed.

## What passes

- Exit 0 (warnings don't raise exit code under default flags).
- `M010` warning record citing `services/api/.helix.yml`.
- Active methodology still resolved from the root marker.

## What fails

- M010 missing → silent ignore (regression).
- Exit nonzero on default flags (M010 is W-class, not error).
- Root marker not activated (over-fire).

## Risk

HIGH. The nested-marker case is the central S1 review finding;
silence here re-opens the failure mode the marker exists to close.
