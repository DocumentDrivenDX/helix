# helix-adopt demo

An existing Node.js project (temperature converter) gets HELIX
installed. The agent scans the repo and reports that no governed
artifacts exist yet, then offers two paths in: frame mode (author
from templates) or backfill mode (read code/docs and propose an
artifact graph).

## Files

- `session.jsonl` — committed session record.
- `fixture/` — a small existing project with no HELIX artifacts:
  - `README.md`, `package.json`
  - `src/convert.js` (the actual CLI)
  - `tests/convert.test.js` (two tests using node:test)

The session's "0 files matched" result for `docs/helix/**/*.md` is what
should happen against this fixture.

## Rebuild the cast

```
uv run --locked python scripts/demos/render_session.py docs/demos/helix-adopt/session.jsonl
bash tests/validate-demos.sh
```

## Re-capture from a live agent

```
uv run --locked python scripts/demos/capture_session.py helix-adopt \
    --prompt "I just installed HELIX into this project. Scan what we have and tell me how to get started." \
    --fixture docs/demos/helix-adopt/fixture/
```
