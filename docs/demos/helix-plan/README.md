# helix plan demo

The brief is written and aligned. `/helix align` produces an authority-ranked
planning gap list. Each gap names the destination artifact, deliverable shape,
next workflow mode, and evidence references so a runtime or operator can
continue without guessing.

## Files

- `session.jsonl` — committed session record.
- `fixture/` — post-brief artifact set for a CSV-to-Parquet
  healthcare-claims pipeline:
  - `docs/helix/00-discover/product-vision.md`
  - `docs/helix/01-frame/prd.md` (R-1..R-5)
  - `docs/helix/01-frame/concerns.md` (go-std + security-owasp)
  - `docs/helix/01-frame/features/FEAT-001-csv-ingest.md` with
    US-INGEST-1..4

The session deliberately stops before runtime work exists. Its output routes
missing implementation work to `polish` after design and test artifacts exist.

## Rebuild the cast

```
python3 scripts/demos/render_session.py docs/demos/helix-plan/session.jsonl
bash tests/validate-demos.sh
```

## Re-capture from a live agent

```
python3 scripts/demos/capture_session.py helix-plan \
    --prompt "Use /helix align to produce authority-ranked planning gaps with destination artifacts, deliverable shapes, next modes, and evidence references." \
    --fixture docs/demos/helix-plan/fixture/
```
