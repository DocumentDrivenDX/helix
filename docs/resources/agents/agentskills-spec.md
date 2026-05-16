---
ddx:
  id: resource.agents.agentskills-spec
---

# Agent Skills Specification (agentskills.io)

## Source

- Spec: https://agentskills.io/specification
- Repo: https://github.com/agentskills/agentskills
- Validator: `skills-ref` (npm package referenced from spec site)
- Origin: Anthropic, released 2025-12-18
- Accessed: 2026-05-15

## Summary

An open standard for packaging AI-agent "skills" as a directory
containing a `SKILL.md` markdown file with YAML frontmatter. Adopted by
30+ tools by March 2026 including Claude Code, OpenAI Codex CLI, Cursor,
VS Code with Copilot, Gemini CLI, and Databricks Genie Code. Provides a
common skill format so a single skill source can be installed across
multiple runtimes without forking.

## File layout

A skill is a directory whose name matches the skill's declared `name:`
frontmatter field:

```
<skill-name>/
  SKILL.md          # required: YAML frontmatter + Markdown body
  scripts/          # optional: helper scripts referenced from SKILL.md
  references/       # optional: heavier content loaded on demand
  assets/           # optional: static assets
```

The parent directory name MUST match `name:` exactly.

## Frontmatter schema

| Field | Required | Constraints |
|---|---|---|
| `name` | yes | 1–64 chars, lowercase `a-z0-9-`, no leading/trailing/consecutive hyphens; matches parent directory |
| `description` | yes | 1–1024 chars; describes what the skill does and when to use it |
| `license` | no | free-form string |
| `compatibility` | no | ≤500 chars; runtime/version notes |
| `metadata` | no | string → string map |
| `allowed-tools` | no | experimental; space-separated tool allowlist |

No separate `manifest.yaml` file. Frontmatter is the manifest.

## Progressive disclosure pattern

The spec recommends keeping `SKILL.md` under ~500 lines / ~5000 tokens.
Heavier content (templates, large reference docs, code) lives in
`references/` and is loaded on demand by the agent rather than at session
start. This keeps the agent's context budget intact while still allowing
skill bodies to refer to substantial supporting content.

## Cross-runtime adoption

Documented adopters as of mid-2026:

| Runtime | Spec compliance | Notes |
|---|---|---|
| Claude Code | full | Skills under `<plugin>/skills/<name>/SKILL.md` inside a plugin |
| OpenAI Codex CLI | full | Skills at `~/.codex/skills/<name>/SKILL.md` |
| Databricks Genie Code | full | Skills at `/Workspace/.assistant/skills/<name>/SKILL.md` |
| Cursor | claimed | Per agentskills.io adopters list |
| VS Code / Copilot | partial | Custom-instructions surface uses Markdown but `applyTo:` glob differs from agentskills spec |
| Gemini CLI | claimed | Per agentskills.io adopters list |

Compliance level should be re-verified per runtime; the spec is open and
implementations vary.

## Skills CLI

A cross-runtime install helper exists at
[github.com/vercel-labs/skills](https://github.com/vercel-labs/skills) and
is invoked as `npx skills`:

```bash
npx skills add <owner>/<repo>                     # install all skills at repo root
npx skills add <owner>/<repo> --list              # enumerate skills in a repo
npx skills add <owner>/<repo> --skill <name>      # install a specific skill
npx skills add <owner>/<repo> -a claude-code      # target a specific agent install path
npx skills remove <name>
```

The CLI writes to local agent skill paths on the machine running it —
`.agents/skills/`, `.claude/skills/`, or `~/.codex/skills/` depending on
the `-a` target. It does NOT write to remote workspaces (e.g. Databricks
`/Workspace/.assistant/skills/`); for those, use the runtime's own
upload tooling.

The Skills CLI is published by Vercel Labs and is referenced from
Databricks' agent-skills documentation as the recommended GitHub-to-local
install path.

## HELIX implications

- HELIX's `skills/helix/SKILL.md` should remain agentskills-compliant.
  Single `name: helix` matching the parent dir name; required
  `description:`; optional `compatibility:` if HELIX needs to declare
  runtime constraints (e.g. "requires read+write+search").
- Heavy reference content (the artifact catalog under `workflows/`)
  should be referenced from the skill body, not inlined. The catalog
  already lives outside the skill directory, which fits the spec's
  progressive-disclosure intent.
- Cross-runtime install via `npx skills add easel/helix` could work for
  local-agent installs (Claude Code, Codex CLI). It does not work for
  Genie Code workspace installs or for DDx; those have their own paths.

## Caveats

- The spec is open and evolving. Adopter compliance is not formally
  certified. Treat per-runtime install docs as authoritative when they
  disagree with the generic spec.
- The `allowed-tools` field is marked experimental and behavior varies.
- Spec versioning is informal at time of writing.
