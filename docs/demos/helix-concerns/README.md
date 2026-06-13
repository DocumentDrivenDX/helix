# helix-concerns demo

The fixture declares `typescript-bun` as the project's tech-stack
concern (Bun runtime, `bun:test`, Biome, `bun` script runner). The
code drifts from that contract in three places. The `helix` skill
should report all three.

## Files

- `session.jsonl` — committed session record. Source of truth.
- `fixture/` — minimal Bun project with planted drift:
  - `docs/helix/01-frame/concerns.md` — declares typescript-bun
  - `src/server.ts` — drifts: `import http from "http"` (concern requires `Bun.serve()`)
  - `tests/health.test.ts` — drifts: `import { describe, it } from "vitest"` (concern requires `bun:test`)
  - `package.json` — drifts: `"scripts": { "test": "vitest" }`

## Rebuild the cast

```
python3 scripts/demos/render_session.py docs/demos/helix-concerns/session.jsonl
bash tests/validate-demos.sh
```

## Re-capture from a live agent

```
python3 scripts/demos/capture_session.py helix-concerns \
    --prompt "Run /helix align against the typescript-bun concern. Report every drift signal you find and propose a remediation plan." \
    --fixture docs/demos/helix-concerns/fixture/
```
