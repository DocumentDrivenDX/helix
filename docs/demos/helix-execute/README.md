# helix-execute demo

The hand-off to the runtime. DDx selects the next ready bead
(bead-001), routes it through the configured harness, the agent executes
inside a throwaway worktree, the deterministic acceptance gate fires,
a reviewer checks the result, and evidence is appended on merge. HELIX stays
offstage — its job was the artifacts.

## Files

- `session.jsonl` — committed session record.
- `fixture/` — post-plan state ready for execution:
  - `.ddx/beads.jsonl` — four beads (bead-001..004) with governing
    artifact pointers, deterministic acceptance criteria, evidence
    expectations, and per-bead cost caps. bead-001 + bead-002 +
    bead-004 are `ready`; bead-003 is `blocked` on its predecessors.
  - `docs/helix/01-frame/features/FEAT-001-csv-ingest.md` —
    the FEAT the beads trace back to.

## Rebuild the cast

```
python3 scripts/demos/render_session.py docs/demos/helix-execute/session.jsonl
bash tests/validate-demos.sh
```

## Re-capture from a live agent

The execute scenario is a runtime demo, not an alignment-skill demo.
To re-capture, drive a real `ddx bead execute <id>` invocation
against this fixture and translate its event stream — `capture_session.py`
is geared at Claude sessions, not raw runtime output, so this
session is the one demo most likely to stay hand-edited.
