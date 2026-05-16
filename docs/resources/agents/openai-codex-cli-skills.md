---
ddx:
  id: resource.agents.openai-codex-cli-skills
---

# OpenAI Codex CLI Skill Mechanism

## Source

- Skills doc: https://developers.openai.com/codex/skills
- Plugins doc: https://developers.openai.com/codex/plugins
- CLI reference: https://developers.openai.com/codex/cli/reference
- Non-interactive mode: https://developers.openai.com/codex/noninteractive
- Authentication: https://developers.openai.com/codex/auth
- Skills repo: https://github.com/openai/skills
- Installation reference: https://deepwiki.com/openai/skills/3.1-installing-skills
- Docker sandbox: https://docs.docker.com/ai/sandboxes/agents/codex/
- Accessed: 2026-05-15

## Summary

OpenAI Codex CLI adopts the agentskills.io specification for skills.
There is **no native `codex skill install` subcommand**. Skills are
installed by placing a `SKILL.md` directory under one of the discovered
filesystem locations, either manually or via the in-session
`$skill-installer` directive. A separate marketplace mechanism exists
for "plugins" (`codex plugin marketplace ...`) but the marketplace flow
covers plugins, not individual skills.

## Filesystem discovery paths

At session start, Codex scans for skills in this order (repo overrides
user, user overrides admin, admin overrides system):

1. `.agents/skills/` — repo-scoped
2. `~/.codex/skills/` — user-scoped
3. `~/.agents/skills/` — alternate user path
4. `/etc/codex/skills/` — admin-scoped
5. Built-in system skills

Each `SKILL.md` is read for progressive disclosure: only `name`,
`description`, and path are loaded at scan time; the full body is
fetched on demand when the skill is invoked.

`AGENTS.md` is NOT the discovery surface for skills. It carries
free-form agent instructions but does not trigger skill loading.

## Install paths

### A. In-session `$skill-installer` (no Dockerfile use)

Inside a running Codex TUI:

```
$skill-installer <skill-name>
$skill-installer install <github-tree-url>
$skill-installer install the <skill> from <repo>     # natural language form
```

This installs to `~/.codex/skills/<name>/`. Requires an interactive
session.

### B. Manual filesystem placement (Dockerfile-friendly)

Drop the skill tree under one of the discovery paths:

```bash
mkdir -p ~/.codex/skills/helix
cp -r /tmp/helix-source/skills/helix/* ~/.codex/skills/helix/
```

The directory name must match the skill's `name:` frontmatter field
exactly per the agentskills.io spec.

### C. Helper script from `openai/skills`

```bash
python scripts/install-skill-from-github.py \
  --repo <owner>/<repo> \
  --path <subpath> \
  --ref main \
  --dest ~/.codex/skills/<name>
```

This is the closest thing to a scripted install. The script lives in
the openai/skills repository and is referenced from the official
"Installing Skills" doc.

### D. Vercel Labs Skills CLI

```bash
npx skills add owner/repo -a codex
```

The `-a codex` flag targets Codex's install path. This is the
cross-runtime install tool described in [agentskills-spec.md](agentskills-spec.md).

## Enabling / disabling skills

`~/.codex/config.toml` controls per-skill enablement:

```toml
[[skills.config]]
path = "/home/user/.codex/skills/helix/SKILL.md"
enabled = false
```

Changes require restarting the Codex session.

## Plugins (distinct from skills)

Codex has a separate "plugin" concept with marketplace support:

```bash
codex plugin marketplace add <github-url-or-git-url-or-ssh-or-local-dir>
codex plugin marketplace remove <name>
codex plugin marketplace upgrade
```

The TUI `/plugins` slash command lists installed plugins. Plugins
appear to bundle multiple skills and other extensions; individual
skills can still be installed independently.

## Update / uninstall

| Operation | How |
|---|---|
| Update a skill | Re-run the install (helper script or `npx skills add`) — overwrites the directory |
| Uninstall a skill | Delete the directory under `~/.codex/skills/<name>/` |
| Disable without removing | `enabled = false` in `~/.codex/config.toml` |

There is no `codex skill update` or `codex skill remove` subcommand.

## Headless / non-interactive

```bash
codex exec "<prompt>"        # short form: codex e
codex exec -                 # read prompt from stdin
codex exec --json "<prompt>" # structured output
codex exec -o output.txt "<prompt>"
codex exec --ephemeral --skip-git-repo-check "<prompt>"
```

Useful flags:

- `--ephemeral`: don't persist conversation state
- `--ignore-user-config`: bypass `~/.codex/config.toml`
- `--skip-git-repo-check`: run outside a git repo
- `--output-schema <path>`: enforce a JSON schema on the response

Prompt is positional; there is no `-p` flag.

## Auth in containers

```bash
# API key path (preferred for Docker)
export OPENAI_API_KEY=sk-...
# or
export CODEX_API_KEY=sk-...     # alternate name seen in docs

# seed credentials non-interactively
printenv OPENAI_API_KEY | codex login --with-api-key
```

Known issue: GitHub `openai/codex#3286` reports that
`OPENAI_API_KEY` is ignored if `~/.codex/auth.json` already contains
a ChatGPT subscription token. Clear `~/.codex/auth.json` before
relying on the env var.

Alternative for headless: `codex login --device-auth` (out-of-band
device authorization flow).

## HELIX implications

- HELIX's `skills/helix/SKILL.md` already conforms to agentskills.io
  spec and works under Codex.
- For Codex testing in Docker:
  1. Install Codex CLI in the base image
  2. `mkdir -p ~/.codex/skills/helix && cp -r /tmp/helix-src/skills/helix/* ~/.codex/skills/helix/`
  3. Also copy the catalog: `cp -r /tmp/helix-src/workflows /workspace/workflows` (referenced from skill body)
  4. `printenv OPENAI_API_KEY | codex login --with-api-key`
  5. `codex exec --ephemeral "list HELIX routing modes"` — verify
- There is no "one command, install HELIX" path for Codex CLI. The
  closest is `npx skills add easel/helix -a codex` which requires
  Node.js but uses the cross-runtime CLI.

## Caveats

- Docs use both `~/.codex/skills/` and `~/.agents/skills/`. They appear
  to be supported in parallel; pick one consistently for HELIX docs.
- The `$skill-installer` flow is inherently TUI-bound; do not surface
  it as the install path for users running Codex non-interactively.
- Codex CLI Docker sandbox docs at docker.com show OpenAI-recommended
  containerization patterns; consult before authoring a HELIX-specific
  Codex Dockerfile.
