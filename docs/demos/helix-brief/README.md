# helix-brief demo

A fresh project with one sentence of intent ("Build a CSV-to-Parquet
ingest pipeline for a healthcare claims processor") gets a full
governing-artifact brief authored from HELIX templates: vision →
PRD → concerns → first feature spec.

## Files

- `session.jsonl` — committed session record.
- `fixture/` — an empty project with only a README stub stating the
  intent. The session creates everything else.

## Rebuild the cast

```
uv run --locked python scripts/demos/render_session.py docs/demos/helix-brief/session.jsonl
bash tests/validate-demos.sh
```

## Re-capture from a live agent

```
uv run --locked python scripts/demos/capture_session.py helix-brief \
    --prompt "Build a CSV-to-Parquet ingest pipeline for a healthcare claims processor. Author the HELIX brief: vision, PRD, concerns, and the first feature spec." \
    --fixture docs/demos/helix-brief/fixture/
```
