# Phase 0 — Grok plugin install layout (2026-07-22)

Recorded so PR3 docs and PR4 harness use real paths.

## Commands used

```bash
grok plugin validate /path/to/helix
grok plugin install /path/to/helix --trust
grok plugin list
```

## Results

| Fact | Value |
|------|--------|
| Manifest validate | Passes on HELIX checkout (`name=helix`, skills dir, hooks) |
| Install form | Full-repo copy under `~/.grok/installed-plugins/<id>/` |
| Registry | `~/.grok/installed-plugins/registry.json` with `kind: Local` + `source_path` |
| Plugin list | `helix-<hash>: helix [local: <source>]` |
| Catalog | `workflows/` present at plugin root; **no** `skills/helix/references/` on full-repo install |
| Skill path | `<plugin-root>/skills/helix/SKILL.md` |
| Relative catalog | `<skill-root>/../../workflows/graph.yml` and PRD `template.md` resolve |
| Env vars | `GROK_PLUGIN_ROOT` / `CLAUDE_PLUGIN_ROOT` documented for **hooks**; not assumed always present in agent tool env |

## Decision

**Primary Grok install source: full repository** (git or local path).  
Generated package `references/` floor remains required for slim/offline packages and Genie-style bundles, not for default `grok plugin install` of this repo.

## Fall-through implication

Adopter projects with no local `workflows/` bind catalog via:

1. `../../workflows/` from the installed skill path (full plugin root), or  
2. `references/` when using a generated package install, or  
3. `$GROK_PLUGIN_ROOT` / `$CLAUDE_PLUGIN_ROOT` when the host injects them.
