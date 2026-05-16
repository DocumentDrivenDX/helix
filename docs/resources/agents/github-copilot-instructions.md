---
ddx:
  id: resource.agents.github-copilot-instructions
---

# GitHub Copilot Extension Mechanism

## Source

- Repository custom instructions: https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions
- Support matrix: https://docs.github.com/en/copilot/reference/custom-instructions-support
- MCP in Copilot: https://docs.github.com/en/copilot/concepts/context/mcp
- Cloud agent + MCP: https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/extend-coding-agent-with-mcp
- Copilot CLI reference: https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference
- Copilot CLI auth: https://docs.github.com/en/copilot/how-tos/copilot-cli/set-up-copilot-cli/authenticate-copilot-cli
- GitHub App extensions deprecation: https://github.blog/changelog/2025-09-24-deprecate-github-copilot-extensions-github-apps/
- `gh copilot` GA: https://github.blog/changelog/2026-01-21-install-and-use-github-copilot-cli-directly-from-the-github-cli/
- Accessed: 2026-05-15

## Summary

GitHub Copilot accepts three live mechanisms for third-party
domain-specific behavior: **repository custom instructions**,
**Model Context Protocol (MCP) servers**, and **Copilot CLI plugins**.
The legacy **GitHub App extensions** path was deprecated September 2025
and fully disabled November 10, 2025. For a methodology like HELIX,
the canonical path is repository custom instructions, with MCP servers
as a future enhancement when tool calls are needed.

## Available mechanisms (2026)

| Mechanism | Status | What it is |
|---|---|---|
| `.github/copilot-instructions.md` | active | Repo-wide markdown auto-injected as system context |
| `.github/instructions/*.instructions.md` with `applyTo:` glob | active | Path-scoped instructions |
| `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` | active (subset of surfaces) | Cloud agent + Copilot CLI + VS Code chat read these |
| MCP servers | active | Tool/content servers via Model Context Protocol |
| Copilot CLI plugins | active (GA Jan 2026) | CLI-specific plugin marketplace |
| GitHub App extensions | **dead (disabled Nov 10 2025)** | Replaced by MCP |

## Repository custom instructions (canonical path for HELIX)

### Files and discovery

```
<repo-root>/
  .github/
    copilot-instructions.md      # global, applies to all requests in repo
    instructions/                # optional
      <name>.instructions.md     # frontmatter applyTo: glob scopes the file
```

`copilot-instructions.md` is plain Markdown — no frontmatter required.

`.github/instructions/<name>.instructions.md` requires frontmatter with
an `applyTo:` glob:

```markdown
---
applyTo: "src/**"
---

# Frontend-specific Copilot instructions
...
```

### Surface coverage

`.github/copilot-instructions.md` is read across:

- VS Code, JetBrains, Xcode, Eclipse Copilot Chat
- github.com Copilot Chat
- Copilot cloud agent
- Copilot code review
- Copilot CLI (`gh copilot`)

`.github/instructions/*.instructions.md` with `applyTo:` is read by
fewer surfaces: cloud agent + code review only on github.com chat; full
coverage in IDE chat and Copilot CLI.

`AGENTS.md` is read by cloud agent, VS Code chat, and Copilot CLI only —
NOT by github.com Copilot Chat or most IDE chat surfaces.

### Install path

There is no install command. Commit the file to the repo. Auto-discovery
applies as soon as the file is on disk and the personal "use custom
instructions" toggle is on for code review (default: on).

### What it supports

Plain Markdown context. No tool calls, no routing logic execution, no
arbitrary file loading. The agent receives the instruction file as
system context for every request against that repo.

## MCP servers

### Status

Live across VS Code, Visual Studio, JetBrains, Xcode, Eclipse, Copilot
CLI, and the cloud agent. The current path for tool-using extensions
after the GitHub App deprecation.

### Install paths (two distinct flows)

**IDE / CLI flows:**
- User-level config files (per-IDE — e.g. VS Code settings JSON, JetBrains config)
- GitHub MCP Registry: https://github.com/mcp

**Cloud agent flow:**
- Admin pastes MCP server config into repo Settings → Copilot → Cloud agent → MCP configuration
- No `.mcp.json`-in-repo auto-install for the cloud agent
- Requires admin approval per server

### When to use for HELIX

Only when HELIX needs to call tools — for example, exposing the
artifact catalog as MCP resources, or providing alignment-check tools.
For methodology-only HELIX (markdown content + routing rules), the
custom instructions path is sufficient.

## Copilot CLI plugins

The `gh copilot` CLI went GA in January 2026 with its own plugin
marketplace. The legacy `gh-copilot` gh extension is retired.

```bash
gh copilot --version
```

Plugins extend the CLI itself; relevant for distributing CLI tools
that integrate with Copilot, not for methodology distribution.

## Headless testing surface

**Copilot CLI is the headless surface:**

```bash
copilot --headless --port 4321        # runs Copilot as a local server
gh copilot                            # bootstrap
```

Custom instructions (`.github/copilot-instructions.md`) and `AGENTS.md`
are honored by Copilot CLI. Other surfaces (IDE chat, github.com
Copilot Chat) are not scriptable.

The legacy `gh-copilot` gh extension is retired.

## Auth in CI/container

Per Copilot CLI auth docs, set one of:

- `COPILOT_GITHUB_TOKEN` — Copilot-specific token
- `GH_TOKEN` or `GITHUB_TOKEN` — fall-through if no Copilot token set
- Fine-grained PAT with **"Copilot Requests"** account permission
- GitHub App user-to-server token

Token holder must have an active Copilot license (Pro/Business/Enterprise).

BYOK (bring-your-own-key) mode is available but loses `/delegate` and
built-in GitHub MCP. For most testing, use a Copilot license + PAT.

## HELIX implications

Best fit for HELIX is **repository custom instructions**:

- Author `.github/copilot-instructions.md` at the HELIX repo root
  pointing Copilot at `skills/helix/SKILL.md` (the routing skill body)
  and `workflows/activities/` (the catalog).
- For HELIX content in adopter repos, ship a template
  `.github/copilot-instructions.md` users can copy or include via
  symlink. The HELIX install doc at `docs/install/codex.md` already
  describes this.
- Optional per-path scoping with `.github/instructions/*.instructions.md`
  for narrowing HELIX guidance to specific subtrees (e.g. only apply
  Frame-mode guidance to `docs/helix/01-frame/`).
- An MCP server packaging is feasible if HELIX needs to expose
  templates as MCP resources, but it is not required.

## Testing in Docker

```bash
docker run --rm \
  -e GH_TOKEN=$GH_TOKEN \
  -v /path/to/helix:/workspace \
  github/cli:latest \
  gh copilot suggest "list HELIX routing modes from skills/helix/SKILL.md"
```

Caveats:

- Requires a real Copilot license attached to the token
- Bills the token holder's Copilot account
- The CLI may behave differently from IDE Copilot Chat; testing only
  validates the CLI surface

## Caveats

- GitHub App extensions are gone — do not invest there
- Cloud agent MCP config requires manual web UI paste, no
  `.mcp.json`-in-repo auto-load
- Custom instructions are static text; cannot execute routing logic.
  The skill's runtime behavior depends on Copilot's interpretation of
  the instructions, not on imperative skill discovery
- `AGENTS.md` is read by Copilot CLI + cloud agent + VS Code chat, NOT
  by github.com Copilot Chat — coverage is partial
