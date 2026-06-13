# helix review demo

A second agent audits the work for DDx work item `bead-OAUTH-03` against the same
security-architecture artifact that authorized it. The implementation
*looks* fine, but the review catches three real findings: missing §4
revocation enforcement, no test for the revocation path, and a raw
refresh token logged to stdout in the error path.

## Files

- `session.jsonl`: committed session record.
- `fixture/`: post-build state of the bead:
  - `.ddx/beads.jsonl`: bead-OAUTH-03 record, status `in_review`,
    with governing-artifact pointers
  - `docs/helix/02-design/security-architecture.md`: §3.2 token
    lifecycle + §4 revocation
  - `src/auth/refresh.ts`: implementation with two real bugs
    (missing revocation check, token leak in error log)
  - `tests/auth/refresh_test.ts`: covers happy path, expiry,
    rotation, replay; intentionally missing the revocation test

The session's three findings map directly to these defects.

## Rebuild the cast

```
python3 scripts/demos/render_session.py docs/demos/helix-review/session.jsonl
bash tests/validate-demos.sh
```

## Re-capture from a live agent

```
python3 scripts/demos/capture_session.py helix-review \
    --prompt "Use /helix review on bead-OAUTH-03 against its governing artifacts. Report every finding, file follow-on runtime work for blocking ones, and flag warnings." \
    --fixture docs/demos/helix-review/fixture/
```
