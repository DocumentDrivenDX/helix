---
ddx:
  id: FEAT-004
  depends_on:
    - helix.prd
    - FEAT-002
  review:
    self_hash: 47becbfdcc27c6c7cda3ea4c9f2edd049f313c4fa2063325f6dc6816129cdc82
    deps:
      FEAT-002: a423a845f2d8f6dcdbc1d0536b9ce733ca42d7adaef32c06683a59aac96b7912
      helix.prd: e11b46de6300cc84460245fcfd6739210ce38406a76f90e32d26685938302eb1
    reviewed_at: "2026-06-14T02:49:03Z"
---
# Feature Specification: FEAT-004 - Plugin Packaging

**Feature ID**: FEAT-004
**Status**: Draft
**Priority**: P1
**Owner**: HELIX maintainers

## Overview

HELIX is currently installed via `scripts/install-local-skills.sh`, which
creates symlinks from `~/.claude/skills/` and `~/.agents/skills/` back into
the repo checkout. This works but has operational problems: new skills are
invisible until the installer is re-run, the symlinks are absolute paths tied
to a single checkout location, and the approach bypasses Claude Code's native
plugin discovery entirely.

This feature makes HELIX a proper Claude Code plugin so that skills, the CLI,
shared workflow resources, and hooks are discovered automatically through the
plugin manifest — no manual installer step required.

## Problem Statement

- **Current situation**: `install-local-skills.sh` symlinks each skill into
  `~/.claude/skills/` and `~/.agents/skills/`, and installs a CLI launcher
  into `~/.local/bin`. Adding a new skill has no
  effect until the installer is re-run. Users hit "Unknown skill" errors with
  no indication that a reinstall is needed.
- **Pain points**:
  1. Silent skill discovery failures — new skills exist on disk but are not
     registered.
  2. Absolute symlinks break when the repo moves or is checked out elsewhere.
  3. No versioning, no manifest, no way for Claude Code to reason about HELIX
     as a coherent package.
  4. `the HELIX skill` is installed via a side-channel (`~/.local/bin`) rather than
     through the plugin `bin/` PATH injection.
  5. Enterprise and multi-repo deployments have no standard distribution path.
- **Desired outcome**: `claude --plugin-dir ./path-to-helix` (or a plugin
  install) makes all HELIX skills, the CLI, and shared resources available
  immediately — no symlinks, no re-running installers, no absolute paths.

## Design

### Plugin layout

The HELIX repo root *is* the plugin root. No separate build or copy step:

```
helix/                              # plugin root
├── .claude-plugin/
│   └── plugin.json                 # manifest
├── skills/                         # single public skill, auto-discovered
│   └── helix/
│       └── SKILL.md
├── workflows/                      # shared resource library
│   ├── actions/
│   ├── EXECUTION.md
│   ├── ratchets.md
│   └── ...
├── bin/                            # added to Bash PATH by plugin loader
│   └── helix                       # CLI entrypoint (thin wrapper)
├── scripts/                        # implementation scripts
│   ├── helix                       # actual CLI
│   ├── tracker.sh
│   └── install-local-skills.sh     # legacy, dev convenience only
├── settings.json                   # plugin default settings (optional)
└── hooks/
    └── hooks.json                  # plugin hooks (optional)
```

### Manifest (`plugin.json`)

```json
{
  "name": "helix",
  "version": "0.6.1",
  "description": "HELIX methodology, artifact catalog, and routing skill for AI-assisted development.",
  "author": {
    "name": "DocumentDrivenDX",
    "url": "https://github.com/DocumentDrivenDX"
  },
  "repository": "https://github.com/DocumentDrivenDX/helix",
  "license": "MIT",
  "skills": "./skills/"
}
```

Key decisions:
- `skills` points to the existing `skills/` directory — no move needed.
- The `helix` skill (`skills/helix/SKILL.md`) is discovered automatically.
  The plugin loader adds `bin/` to `PATH` automatically.
- Skills reference shared resources via `${CLAUDE_PLUGIN_ROOT}/workflows/`.
- No `commands/` directory — HELIX uses skills exclusively.

### Resource resolution

Skills currently reference `workflows/` via relative paths that assume the repo
root is reachable from the skill directory. The plugin model formalizes this:

- **Inside skill prompts**: Use `${CLAUDE_PLUGIN_ROOT}/workflows/` for
  references that must resolve at runtime.
- **Inside the CLI**: `$HELIX_ROOT` (already used) resolves to the plugin root
  when invoked via the plugin `bin/` path.
- **Validation**: The skill package validator (`tests/validate-skills.sh`) must
  verify that every `workflows/` reference in a SKILL.md can resolve from the
  plugin root.

### Relationship to `install-local-skills.sh`

The installer becomes a **development convenience** for contributors who want
HELIX skills available outside of `--plugin-dir` mode (e.g., when working in
other repos). It is no longer the primary installation path.

The installer should:
1. Detect whether the plugin manifest exists.
2. Print a recommendation to use `--plugin-dir` or `plugin install` instead.
3. Continue with symlink installation for users who explicitly want it.

### Installation modes

| Mode | Mechanism | Use case |
|------|-----------|----------|
| Plugin (local) | `claude --plugin-dir /path/to/helix` | Primary — development and daily use |
| Plugin (installed) | `claude plugin install helix` | Distribution — when marketplace is available |
| Plugin (project) | `.claude/settings.json` with plugin reference | Team — checked into adopting repos |
| Symlink (legacy) | `scripts/install-local-skills.sh` | Development convenience only |

### Skill namespacing

When installed as a plugin, the skill is namespaced as `/helix:helix`. The
unqualified name (`/helix`) continues to work when no other plugin provides
a conflicting skill name.

## Requirements

### Functional Requirements

1. The HELIX repo must contain a `.claude-plugin/plugin.json` manifest that
   declares HELIX as a Claude Code plugin.
2. `the HELIX skill` must be a thin wrapper that resolves `HELIX_ROOT` to
   `${CLAUDE_PLUGIN_ROOT}` and delegates to `the HELIX skill`.
3. All HELIX skills must be discoverable through the plugin's `skills/`
   directory without manual symlink installation.
4. Shared resources in `workflows/` must be accessible from skills via
   `${CLAUDE_PLUGIN_ROOT}/workflows/`.
5. Adding a new skill (creating `skills/<name>/SKILL.md`) must make it
   available immediately in the next Claude Code session — no reinstall step.
6. `install-local-skills.sh` must remain functional as a development
   convenience but must not be the documented primary installation path.
7. The skill package validator must verify plugin layout integrity: manifest
   exists, skills resolve, shared resources reachable.
8. Plugin hooks (if any) must be declared in `hooks/hooks.json` and loaded
   by the plugin system.

### Non-Functional Requirements

- **Portability**: The plugin must work regardless of the repo's absolute path.
- **Zero-copy**: The repo root *is* the plugin root — no build step or file
  duplication.
- **Backward compatibility**: Existing `install-local-skills.sh` users must
  not be broken. The installer continues to work but prints a deprecation
  notice.
- **Testability**: Plugin layout validation must be deterministic and runnable
  in CI.

## User Stories

### US-001: Install HELIX as a plugin [FEAT-004]
**As a** HELIX operator
**I want** to add HELIX to my Claude Code session with `--plugin-dir`
**So that** all skills, the CLI, and shared resources are available immediately

**Acceptance Criteria:**
- [ ] Given a HELIX checkout, when `claude --plugin-dir /path/to/helix` starts,
  then all HELIX skills appear in the skill list.
- [ ] Given the plugin is loaded, when the user invokes `/the HELIX skill`, then the
  skill executes with access to `workflows/` resources.
- [ ] Given the plugin is loaded, when  is run in Bash, then the
  CLI is on PATH and functional.

### US-002: Add a new skill without reinstalling [FEAT-004]
**As a** HELIX maintainer
**I want** new skills to be available in the next session after I create the file
**So that** I do not need to remember to re-run an installer

**Acceptance Criteria:**
- [ ] Given a new `skills/helix-foo/SKILL.md` is created, when a new Claude
  Code session starts with the plugin, then `/helix-foo` is available.
- [ ] Given the old installer has not been re-run, when the plugin is loaded,
  then the new skill is still available.

### US-003: Team distribution via project settings [FEAT-004]
**As a** team lead adopting HELIX for a project
**I want** to declare HELIX as a plugin dependency in `.claude/settings.json`
**So that** all team members get HELIX skills automatically

**Acceptance Criteria:**
- [ ] Given `.claude/settings.json` references the HELIX plugin, when a team
  member starts Claude Code in the project, then HELIX skills are available.
- [ ] Given the plugin is loaded from project settings, when the team member
  invokes `ddx work`, then the CLI and shared resources resolve correctly.

### US-004: Validate plugin layout [FEAT-004]
**As a** HELIX maintainer
**I want** CI to catch broken plugin layouts before merge
**So that** users never get a plugin that silently fails

**Acceptance Criteria:**
- [ ] Given `tests/validate-skills.sh` runs, when the plugin manifest is
  missing or malformed, then the test fails with a clear error.
- [ ] Given a skill references a `workflows/` resource that does not exist,
  when the validator runs, then it reports the broken reference.

## Edge Cases and Error Handling

- **Plugin loaded without `workflows/`**: Skills must fail clearly with
  "HELIX shared resources not found at ${CLAUDE_PLUGIN_ROOT}/workflows/"
  rather than silently producing degraded output.
- **Both plugin and symlink install active**: Plugin takes precedence (Claude
  Code's plugin skills override user-level skills of the same name). The
  symlink install becomes a no-op when the plugin is active.
- **Repo moved after symlink install**: Symlinks break (existing behavior).
  Plugin mode is unaffected since it uses the current plugin root.
- **Multiple HELIX versions**: If two plugin dirs both provide `helix-*`
  skills, Claude Code's plugin precedence rules apply. Users should not load
  two HELIX plugins simultaneously.

## Success Metrics

- HELIX is loadable as a Claude Code plugin with zero manual setup beyond
  `--plugin-dir`.
- New skills are available in the next session without any installer step.
- `install-local-skills.sh` is no longer referenced in primary documentation
  as the installation path.
- Plugin layout validation runs in CI and catches broken layouts.

## Constraints and Assumptions

- The HELIX repo root doubles as the plugin root — no separate packaging step.
- Claude Code's plugin loader must support `bin/` PATH injection and
  `${CLAUDE_PLUGIN_ROOT}` variable resolution in skill prompts.
- The plugin manifest format follows the Claude Code plugin specification.
- Marketplace distribution is a future concern — local `--plugin-dir` is
  sufficient for V1.

## Dependencies

- **FEAT-002**: CLI feature spec (installation section needs updating)
- **SD-001**: Solution design (packaging component needs plugin layout)
- **helix.prd**: PRD packaging requirements
- Claude Code plugin specification (external dependency)

## Out of Scope

- Marketplace publishing workflow
- Plugin auto-update mechanism
- Plugin configuration UI
- Enterprise managed-settings distribution (future, once marketplace exists)

## Open Questions

- Does `${CLAUDE_PLUGIN_ROOT}` resolve inside SKILL.md reference paths, or
  only in hook commands and MCP configs? If not, skills may need a different
  mechanism to locate `workflows/`.
- Should the plugin declare MCP servers (e.g., for tracker access) or keep
  tracker interaction purely CLI-based?
- What is the right versioning strategy — semver tied to HELIX releases, or
  independent plugin version?
