# T22 — docs/helix/ exists but empty (only .gitkeep)

- **Installed:** `helix-library`, `helix`, `helix-infra`
- **Risk:** medium (signal-definition pin)

## Scenario

`docs/helix/02-design/.gitkeep` is the ONLY file under `docs/helix/`.
No real artifact (no `prd.md`, no `adr.md`). No `*.tf`. No
`terraform/`.

## Why it matters

T5's workspace has BOTH a `.gitkeep` AND a real `prd.md`. The signal
that picks helix is the prd.md, not the directory existence. The
design's repo-shape rule is described as "docs/helix/ exists" in
shorthand. A real impl might key on DIRECTORY existence and pass T5
for the wrong reason — and then misbehave on T22. This fixture
isolates the directory-only case so the signal definition (artifact,
not directory) is pinned.

## Pass signature

NO markdown Write (no silent route) AND prose disambiguates or
declares "no signal / no artifact / cannot determine."

## Failure signatures

- Write tool_use fires anywhere → silent route on a no-signal repo.
- Prose silently picks one methodology → directory-existence used
  as signal, contradicting T5's actual contract.
