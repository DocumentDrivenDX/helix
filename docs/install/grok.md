# HELIX in Grok Build

This guide installs HELIX as a **Grok Build plugin**. The deliverable is the
routing skill plus the methodology catalog — not a CLI or tracker. Queue and
execution stay with your runtime (for example DDx) when you use one.

Phase 0 layout probe notes (full-repo install paths) live at
[`tests/install/grok-build/phase0-layout.md`](../../tests/install/grok-build/phase0-layout.md).

## What you are installing

| Piece | Role |
|-------|------|
| `skills/helix/SKILL.md` | Single public HELIX router (`/helix` or description match) |
| `workflows/` (full-repo install) | Artifact templates, prompts, graph, voice, concerns |
| `skills/helix/references/` (generated package only) | Same catalog floor for slim installs |

Adopter projects **need not vendor templates**. Prefer only:

```
adopter-repo/
  .helix.yml
  docs/helix/…          # instance artifacts
```

If project-local `workflows/` is absent, the skill **falls through** to the
plugin catalog (see skill §Catalog Resolution). Project-local `workflows/`
remains valid for self-host and intentional forks and **outranks** the
installed plugin when present.

## Install path A: local checkout (development)

```bash
grok plugin validate /path/to/helix
grok plugin install /path/to/helix --trust
grok plugin list
```

Observed layout (Phase 0): full tree under
`~/.grok/installed-plugins/<id>/` with `skills/helix/SKILL.md` and
`workflows/graph.yml` at the plugin root. Catalog binds via
`<skill-root>/../../workflows/…`.

## Install path B: GitHub source

```bash
grok plugin install DocumentDrivenDX/helix --trust
# pin optional: DocumentDrivenDX/helix@v0.11.0
```

Use a full-repo install so `workflows/` is present. If a future install shape
ships only the skill subtree without `workflows/` or `references/`, install
the **generated package** from `scripts/build-plugin-package.sh` instead
(`dist/plugin-package/helix/`).

## Install path C: session-only

```bash
grok --plugin-dir /path/to/helix
```

Session load does not persist after exit.

## Trust and enablement

Install with `--trust` so hooks and skills activate. Grok also sets
`GROK_PLUGIN_ROOT` / `CLAUDE_PLUGIN_ROOT` for plugin hooks (and documents
Claude aliases). Skills may fall through to those env roots when relative
paths do not bind.

If a plugin is listed but inactive, enable it via Grok plugin UI or
`[plugins].enabled` in `~/.grok/config.toml` for your Grok version.

## Verify

```bash
grok plugin list
grok inspect          # skill name helix; prefer source under installed helix plugin
grok plugin details helix
```

In a session:

```
/helix check
```

Or natural language: “Use the helix skill to list workflow modes.”

Expect engagement (skill load), then a short routing response naming modes
such as frame, grill, align, design, evolve, review, polish, check.

**Headless / non-interactive:** name the skill in the prompt; do not rely on
slash expansion if the host does not expand `/helix` outside the TUI.

## Update / uninstall

```bash
grok plugin update helix
grok plugin uninstall helix --confirm
```

## Catalog resolution (summary)

Fall-through order (first bind wins):

1. Marker `graph:` / `catalog:` pointer  
2. Project-local `workflows/` (self-host / intentional vendor)  
3. `../../workflows/` from this skill (full plugin / checkout)  
4. `$GROK_PLUGIN_ROOT` / `$CLAUDE_PLUGIN_ROOT` → `workflows/` then `skills/helix/references/`  
5. `references/` floor beside `SKILL.md`  
6. Fail closed  

Missing project `workflows/` is **not** an error when a later step binds.

## Engagement (dual-path)

- Claude Code / skill-tool hosts: `Skill(helix)` first tool action (unchanged).  
- Grok Build: first action loads the HELIX skill body (`/helix` or read).  

## Troubleshooting

| Symptom | Check |
|---------|--------|
| Multiple `helix` skills | Prefer the skill from the installed `helix` plugin path; ignore legacy DDx `helix-workflow` / `helix-alignment-review` for routing |
| Catalog not found | Confirm `workflows/graph.yml` or `skills/helix/references/graph.yml` under the install root |
| Plugin listed but inactive | Trust/enable the plugin; reinstall with `--trust` |
| Untrusted hooks | Install with `--trust` or trust via Plugins UI |

## Relation to Claude Code and Codex

HELIX remains one skill + one catalog. Claude Code and Codex keep their own
install guides and marketplace flows. This page only documents **Grok discovery
and invocation**. Do not fork methodology content per runtime.
