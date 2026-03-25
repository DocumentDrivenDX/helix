# HELIX Implementation Plan: helix-cli

**Status**: backfilled
**Backfill Date**: 2026-03-25

## Implementation Boundaries

- Keep `scripts/helix` as the single wrapper entrypoint.
- Keep tracker mechanics in `scripts/tracker.sh`.
- Keep installation concerns in `scripts/install-local-skills.sh`.
- Keep wrapper verification in `tests/helix-cli.sh`.
- Treat `workflows/` action files as the source of truth for delegated action
  behavior.

## Build Rules

1. Change command routing, prompts, or loop behavior in `scripts/helix`.
2. Change tracker storage and queue semantics in `scripts/tracker.sh`.
3. Change local setup behavior in `scripts/install-local-skills.sh`.
4. Add or update deterministic tests in `tests/helix-cli.sh` for any wrapper
   behavior change.
5. Update user-facing command docs when the CLI surface or safety contract
   changes.

## Required Validation

When wrapper behavior or the HELIX execution contract changes, run:

```bash
bash tests/helix-cli.sh
git diff --check
```

## Operational Notes

- Agent selection is runtime-configurable through `HELIX_AGENT`,
  `--agent`, `--claude`, and `--codex`.
- `HELIX_LIBRARY_ROOT` can redirect the workflow library root.
- `HELIX_TRACKER_DIR` can redirect the tracker directory.
- Session stderr is tee'd into `.helix-logs/`.

## Follow-On Expectations

- Any change that affects `backfill`, `check`, or `run` should preserve the
  machine-readable contracts consumed by automation.
- Any change that affects tracker readiness must preserve dependency-aware
  queue behavior.
- Any change that affects installation must preserve creation of
  `~/.local/bin/helix`.

## Evidence

- `scripts/helix:17-37`
- `scripts/helix:40-94`
- `scripts/helix:250-305`
- `scripts/helix:451-519`
- `scripts/tracker.sh:7-18`
- `scripts/tracker.sh:265-420`
- `scripts/install-local-skills.sh:35-67`
- `tests/helix-cli.sh:440-447`
- `tests/helix-cli.sh:637-665`
- `workflows/REFERENCE.md:149-154`
