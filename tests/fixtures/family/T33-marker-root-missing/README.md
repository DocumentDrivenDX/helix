# T33 — marker `root:` path missing → M006 hard stop [HIGH RISK]

## Scenario

`.helix.yml` declares `root: docs/helix/` but the docs/helix/
directory does NOT exist in the workspace. Per §1.4 hard-fail rule
6 (S9 review fold), this is M006 — the marker is lying about the
filesystem, which is exactly the typo case the marker was supposed
to prevent.

Companion (deferred small fixture): `--allow-empty-scope` demotes
M006 to warning for fresh repos.

## Why it matters

S9 review item. Without M006, the validator would treat the missing
directory as "zero instances under that scope" and proceed
silently — false-green on a typo. CI runs without
`--allow-empty-scope` and catches dead scopes.

## What passes

- Non-zero exit (M-class).
- `M006` violation citing the methodology id AND the offending
  unresolved path.

## What fails

- Exit 0 (silent treatment of missing path).
- Diagnostic missing the path string.
- Diagnostic missing the methodology id (can't tell which entry).

## Risk

HIGH. The whole point of the marker is to eliminate silent typo
failure modes; if M006 doesn't fire, the marker is decorative.
