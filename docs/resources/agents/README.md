---
ddx:
  id: resource.agents.index
---

# Agent Plugin/Skill Mechanisms — Research Index

This directory captures verified research on how third-party content
(skills, plugins, instructions, MCP servers) is packaged, installed,
discovered, and tested for the AI coding agents HELIX targets as
runtimes.

## Why this exists

HELIX ships per-runtime install guides under [`docs/install/`](../../install/).
Those are user-facing how-tos. This directory holds the engineer-facing
mechanism reference: what commands exist, what manifests are required,
what paths skills load from, what headless test surfaces exist, and what
is undocumented or moving.

When the install docs and these research notes disagree, the install
docs are the source of truth for user instructions; these notes are the
source of truth for the underlying mechanisms.

## Cross-runtime standard

- [Agent Skills specification (agentskills.io)](agentskills-spec.md) —
  the open spec adopted by Claude Code, Codex CLI, Cursor, VS Code /
  Copilot, Gemini CLI, and Databricks Genie Code. This is the
  convergence point for `SKILL.md`-format skills.

## Per-runtime mechanism notes

- [Claude Code plugins](claude-code-plugins.md) — marketplace-mediated
  install, `.claude-plugin/plugin.json` manifest, scripted-install
  support, headless `claude -p`.
- [OpenAI Codex CLI skills](openai-codex-cli-skills.md) — filesystem
  scan from `~/.codex/skills/`, no native install command, in-session
  `$skill-installer`, headless `codex exec`.
- [GitHub Copilot instructions](github-copilot-instructions.md) —
  `.github/copilot-instructions.md` auto-discovered across most
  surfaces; GitHub App extensions retired (Nov 2025), replaced by MCP;
  Copilot CLI (`gh copilot`) is the headless surface.
- [Databricks Genie Code skills](databricks-genie-code-skills.md) —
  workspace-resident skills under `/Workspace/.assistant/skills/`,
  agentskills.io-compliant frontmatter, no public chat API for
  end-to-end testing.
- [DDx plugins](ddx-plugins.md) — `ddx install <name>` registry path,
  reuses Claude Code plugin layout, install location at
  `.ddx/plugins/<name>/` (per-project) and `~/.ddx/plugins/<name>/`
  (user-scoped snapshot).

## Maintenance

Each note carries an "Accessed" date in its source list. When an agent's
docs change in ways that affect HELIX's install path, refresh the
relevant note and update the corresponding `docs/install/<runtime>.md`.

These notes are not normative HELIX content; they are external-source
captures. HELIX's normative content (catalog and routing skill) stays
runtime-neutral per PRD R-4.
