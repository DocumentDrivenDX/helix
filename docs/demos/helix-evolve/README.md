# helix evolve demo

The product-vision scenario, made concrete: a team adds OAuth to a
service whose PRD says API-keys-only. One sentence in; `/helix evolve`
walks the artifact graph from the highest-authority artifact down and produces
six ordered steps spanning security architecture, ADRs, feature specs, designs,
tests, and DDx work items.

## Files

- `session.jsonl`: committed session record. Source of truth.
- `fixture/`: minimal API-key-only artifact set the evolve runs against:
  - `docs/helix/01-frame/prd.md`: R-3 says API-key only (non-goal: OAuth)
  - `docs/helix/01-frame/features/FEAT-AUTH.md`: API-key flow
  - `docs/helix/02-design/security-architecture.md`: API-key threat model

The session record's prompt is "Add OAuth login alongside the existing
API-key auth." The skill should flag that PRD R-3 must change, propose a
new ADR, and decompose downstream artifacts before any code changes.

## Rebuild the cast

```
python3 scripts/demos/render_session.py docs/demos/helix-evolve/session.jsonl
bash tests/validate-demos.sh
```

## Re-capture from a live agent

```
python3 scripts/demos/capture_session.py helix-evolve \
    --prompt "Use /helix evolve to add OAuth login alongside the existing API-key auth. Thread the change through the artifact graph from the highest-authority artifact down." \
    --fixture docs/demos/helix-evolve/fixture/
```
