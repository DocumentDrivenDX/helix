---
ddx:
  id: resource.agents.ddx-plugins
---

# DDx Plugin Mechanism

## Source

- DDx CLI: `ddx install --help`, `ddx plugin --help` (observed against
  DDx v0.6.2-alpha87-23-g2823959f0)
- Observed install snapshot: `/home/erik/.ddx/plugins/helix/`
- Repo plugin manifest: `.claude-plugin/plugin.json`
- Accessed: 2026-05-16

## Summary

DDx ("document-driven X") provides a `ddx install <name>` command that
installs a plugin from a registry (default: DDx's hosted registry) or
from a local directory. Installed plugins land at one of two paths:

- `<project>/.ddx/plugins/<name>/` — per-project install (default)
- `~/.ddx/plugins/<name>/` — observed user-scoped snapshot

DDx reuses the **Claude Code plugin layout** for plugins it installs:
the same `.claude-plugin/plugin.json` manifest, the same `skills/` and
`hooks/` paths. Plugins built for Claude Code therefore work in DDx
without modification — they're the same artifact.

## Install commands

```bash
ddx install <name>                       # install from registry, default path
ddx install <name> --force               # reinstall even if up to date
ddx install <name> --local <path> --force # install from a local directory
ddx plugin install <name>                # alias under ddx plugin subcommand
```

Persona-level installs:

```bash
ddx install persona/strict-code-reviewer  # install a persona, not a full plugin
```

Global flags relevant to install:

```bash
--config <path>           # alt config file (default: ~/.ddx.yml)
--library-base-path <p>   # override DDx library location
-v, --verbose             # detailed install output
```

There is no observed `ddx install --version <tag>` flag in
`--help` output. Pinning a specific release likely requires
`--local <path>` against a checked-out tag.

## Install paths (observed)

```
~/.ddx/plugins/<name>/         # user-scoped snapshot
~/.ddx/installed_plugins.json  # registry of installed plugins (observed empty)
~/.ddx/known_marketplaces.json # marketplace registry
```

The observed `~/.ddx/plugins/helix/` install at HELIX version 0.3.2
was a directory tree (not a git checkout — no `.git`) of the entire
HELIX repo, mirroring the source layout: `skills/helix/`,
`workflows/`, `.claude-plugin/plugin.json`, etc.

DDx appears to clone or copy the source repo as a snapshot rather than
maintaining a live git working tree. `ddx install <name> --force` is
required to refresh the snapshot.

## Manifest format

DDx reads `.claude-plugin/plugin.json` from the source. Required fields
match the Claude Code plugin spec. See
[claude-code-plugins.md](claude-code-plugins.md) for the full schema.

DDx may consume additional fields beyond Claude Code's set (e.g.
DDx-specific tags or capabilities), but the observed `plugin.json` for
HELIX uses only the Claude Code fields and is consumed without error.

## Component discovery

DDx scans the installed plugin tree for the same components Claude Code
discovers:

- `skills/<name>/SKILL.md`
- `commands/`
- `agents/`
- `hooks/hooks.json`
- `.mcp.json`

Plus DDx-specific reads:

- `workflows/` content (HELIX-specific, but DDx also reads it for its
  own purposes)

## Update / uninstall

Observed `--help` output does not list explicit update or uninstall
subcommands under `ddx install` or `ddx plugin`. Updates are performed
by re-running `ddx install <name> --force`. Uninstall is presumably
manual: delete the plugin directory.

The empty `~/.ddx/installed_plugins.json` observed locally suggests
DDx's install registry is either not used by `ddx install` or was
zeroed at some point. Behavior may have changed between versions.

## Headless / non-interactive

`ddx install <name>` is non-interactive by default. No TTY required.
Suitable for use in Dockerfiles:

```dockerfile
RUN ddx install helix
```

For local-source installs in CI (where the registry is not desired):

```dockerfile
COPY ./helix-src /tmp/helix-src
RUN ddx install helix --local /tmp/helix-src --force
```

## Auth

DDx's registry endpoint and auth model are not visible in `--help`
output. Public-registry installs (`ddx install helix`) appear to
require no authentication in the local environment. Private-registry
or authenticated install flows, if they exist, are not documented in
the CLI help text.

## HELIX implications

- HELIX is already installable via `ddx install helix`. The local
  snapshot at `~/.ddx/plugins/helix/` is currently stale (version
  0.3.2 vs repo 0.3.3); a `ddx install helix --force` against the
  current registry would refresh it.
- DDx-published HELIX releases are gated by:
  - `.claude-plugin/plugin.json` `version` field (currently 0.3.3)
  - Whatever publishing the DDx registry does to pick up new HELIX
    versions (likely tied to git tags; not observed)
- The `just install` recipe now runs `ddx install helix --force` directly.
  The legacy doctor-fix step was dropped when the HELIX CLI wrapper was
  removed.

## Caveats

- DDx-as-publisher of HELIX is a tighter coupling than the no-fork
  policy implies. The HELIX repo IS the DDx plugin source — there is no
  separate DDx wrapper.
- DDx plugin format equals Claude Code plugin format; same content,
  one adapter. This is the right shape and should be preserved.
- The stale `~/.ddx/plugins/helix/` snapshot will continue to contain
  legacy `helix-*` skill directories (helix-align, helix-frame, etc.)
  until the user runs `ddx install helix --force` after a release tag
  newer than the snapshot.
- DDx's update story for installed plugins is `--force`-or-manual;
  there is no observed `ddx update` command in the install help.
