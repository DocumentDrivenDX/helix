---
ddx:
  id: resource.agents.claude-code-plugins
---

# Claude Code Plugin Mechanism

## Source

- Plugin reference: https://code.claude.com/docs/en/plugins-reference.md
- CLI reference: https://code.claude.com/docs/en/cli-reference.md
- Marketplace docs: https://code.claude.com/docs/en/plugin-marketplaces.md
- Accessed: 2026-05-15

## Summary

Claude Code installs third-party plugins through a **marketplace
indirection**. There is no direct `claude plugin install <github-url>`
command. To distribute a plugin from GitHub, the author creates a
marketplace repository containing a `.claude-plugin/marketplace.json`
manifest that lists one or more plugins, then users add that marketplace
and install plugins from it by name.

Session-only loads from a directory or `.zip` URL are supported for
development and CI.

## Install paths

### A. Marketplace-based (canonical for distribution)

Two-step user flow:

```bash
# 1. add a marketplace (one time, per user)
/plugin marketplace add owner/repo
# also accepts: owner/repo, https URL with .git, or local path

# 2. install a plugin from that marketplace
/plugin install plugin-name@marketplace-name
```

Non-TUI equivalent suitable for scripts / Dockerfiles:

```bash
claude plugin marketplace add owner/repo
claude plugin install plugin-name@marketplace-name --scope user -y
```

### B. Session-only load (development / CI)

```bash
claude --plugin-dir ./path/to/plugin           # local directory
claude --plugin-dir ./plugin.zip               # local zip
claude --plugin-url https://example.com/x.zip  # remote zip (v2.1.128+)
```

These do not persist the plugin; they load it for the session only.
Useful for testing a plugin before publishing it through a marketplace.

### C. Official Anthropic marketplace submission

Submit via in-app forms:
- claude.ai: https://claude.ai/settings/plugins/submit
- Console: https://platform.claude.com/plugins/submit

Not required for third-party distribution.

## Plugin manifest (`.claude-plugin/plugin.json`)

Location: at the plugin root, in the `.claude-plugin/` subdirectory.

Required field: `name` (kebab-case). All other fields are optional but
recommended:

| Field | Purpose |
|---|---|
| `name` | kebab-case identifier (required) |
| `description` | user-visible description |
| `version` | semver; used by the update mechanism |
| `author` | object with `name` and `url` |
| `homepage` | URL |
| `repository` | URL |
| `license` | license identifier |
| `skills` | path to skills directory (default: `./skills/`) |
| `commands` | path to slash commands directory |
| `agents` | path to agents directory |
| `hooks` | path to hooks manifest (default: `./hooks/hooks.json`) |

The manifest is optional if all components live at default paths.

## Component discovery

Components live at the plugin root, NOT inside `.claude-plugin/`:

```
my-plugin/
  .claude-plugin/
    plugin.json
  skills/
    my-skill/
      SKILL.md         # agentskills.io-compliant
  commands/            # legacy flat-file slash commands
  agents/
  hooks/
    hooks.json
  .mcp.json            # MCP server config
  .lsp.json            # LSP server config
```

Skills, commands, agents, hooks, MCP, and LSP are all discovered by
filesystem scan from these standard paths.

## Marketplace manifest (`.claude-plugin/marketplace.json`)

A marketplace is itself a repository. Its manifest lists plugins
available through it:

```json
{
  "name": "easel-helix",
  "description": "HELIX methodology marketplace",
  "plugins": [
    {
      "name": "helix",
      "source": "easel/helix",
      "description": "HELIX methodology + alignment skill"
    }
  ]
}
```

Plugins can be sourced from the same repo, a different GitHub repo, or
a path. The exact schema is at the marketplace docs URL above.

## Update / uninstall

| Operation | Command |
|---|---|
| Update one | `claude plugin update plugin-name@marketplace-name` |
| Auto-update | `autoUpdate: true` in marketplace settings; official Anthropic marketplaces auto-update by default |
| Uninstall | `/plugin uninstall plugin-name@marketplace-name` (aliases: `remove`, `rm`) |
| Preserve data | `--keep-data` preserves `${CLAUDE_PLUGIN_DATA}` |

Version resolution for updates:
1. Explicit `version` in `plugin.json` (author must bump manually)
2. Falls back to git commit SHA (every commit is a new version)

## Headless / non-interactive

Yes:

```bash
echo "<prompt>" | claude -p
claude -p "<prompt>"
```

Works with `ANTHROPIC_API_KEY` env var, no login or TTY required.
Plugins loaded via marketplace install are available in `-p` mode.
Skills can be referenced as `/<plugin-name>:<skill-name>`.

## Auth in containers

- `ANTHROPIC_API_KEY` environment variable.
- No browser flow required.
- `claude --version` works without auth; `claude -p` requires the key.

## HELIX implications

- HELIX's repo IS a plugin (`.claude-plugin/plugin.json` exists at
  root). To make it installable via the marketplace path, HELIX also
  needs a marketplace manifest — either in the same repo
  (`.claude-plugin/marketplace.json` listing `helix` as the single
  plugin) or in a separate marketplace repo.
- For one-step install, the most ergonomic shape:
  - Repo root contains both `.claude-plugin/plugin.json` AND
    `.claude-plugin/marketplace.json`.
  - User runs: `/plugin marketplace add easel/helix` then
    `/plugin install helix@helix`.
- For CI/Docker testing of HELIX-on-Claude-Code, use `--plugin-dir` to
  load the local checkout directly without going through a marketplace
  add.

## Caveats

- `.claude-plugin/plugin.json` description field in the HELIX repo is
  currently stale ("supervisory autopilot..."). Update before tagging a
  release.
- The `--plugin-url` flag (remote zip load) is new (v2.1.128, ~May
  2026). Older Claude Code versions only support `--plugin-dir`.
- Component paths inside `.claude-plugin/` are NOT discovered; keep
  skills/commands/agents at the plugin root.
