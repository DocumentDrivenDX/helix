# helix align demo

A HELIX-governed project has a PRD saying API-keys-only and an ADR
proposing a pivot to OAuth. The `helix` skill walks the artifact
graph from the highest-authority artifact down and reports three findings plus a plan
ordered by which artifact governs which.

## Files

- `session.jsonl` — committed session record. Source of truth.
- `fixture/` — minimal repo state the session runs against:
  - `docs/helix/00-discover/product-vision.md`
  - `docs/helix/01-frame/prd.md` (R-3: API-key only)
  - `docs/helix/01-frame/features/FEAT-001-auth.md`
  - `docs/helix/02-design/adr/ADR-002-oauth-pivot.md`
    (proposes OAuth, supersedes ADR-001)

The contradiction between PRD R-3 and ADR-002 is what `/helix align` should
find.

## Rebuild the cast

From the repo root:

```
python3 scripts/demos/render_session.py docs/demos/helix-align/session.jsonl
bash tests/validate-demos.sh
```

The render is deterministic — the same `session.jsonl` always
produces the same `.cast`.

## Re-capture from a live agent

```
python3 scripts/demos/capture_session.py helix-align \
    --prompt "Run /helix align on this project and produce an authority-ranked plan to resolve any contradictions." \
    --fixture docs/demos/helix-align/fixture/
```

The captured `session.jsonl` will overwrite the committed one. Review
the diff before committing — `capture_session.py` translates the live
event stream verbatim, so narrations may need light editing for
clarity before they're shipped.
