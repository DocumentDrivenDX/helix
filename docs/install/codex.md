# HELIX in OpenAI Codex CLI

This guide installs HELIX into the OpenAI Codex CLI — the terminal
agent that reads `AGENTS.md` and runs interactive coding sessions
against a repo.

> GitHub Copilot is a separate target with its own install path. See
> [`copilot.md`](copilot.md).

HELIX ships as content (artifact catalog under `workflows/activities/`)
plus a single routing skill at `skills/helix/SKILL.md`. The repo is also
a Codex plugin: `.codex-plugin/plugin.json` points Codex at the same
skill directory and presentation metadata, while `.claude-plugin/marketplace.json`
is the marketplace listing Codex imports from GitHub.

## What you are installing

Two pieces:

1. **The HELIX plugin** — `.codex-plugin/plugin.json` plus
   `skills/helix/SKILL.md`. Installs as `helix@helix` through the Codex
   plugin manager so Codex can discover the routing skill.
2. **The artifact catalog** — `workflows/activities/00-discover` through
   `06-iterate`. Vendored with the plugin and resolved by the skill from
   the active plugin root or project checkout.

## Install path A: Codex plugin marketplace (recommended)

Install from the HELIX marketplace:

```bash
codex plugin marketplace add DocumentDrivenDX/helix
codex plugin add helix@helix
```

Verify Codex can see the marketplace entry:

```bash
codex plugin list --marketplace helix --available --json
```

Codex installs the plugin from the configured marketplace snapshot. For Git
marketplaces, update the snapshot with:

```bash
codex plugin marketplace upgrade helix
```

## Install path B: Skills CLI fallback

The Vercel Labs Skills CLI (`npx skills`) installs HELIX from GitHub
into Codex's filesystem skill path in one command:

```bash
npx skills add DocumentDrivenDX/helix -a codex
```

This drops `skills/helix/SKILL.md` (and supporting files) into the
Codex skill discovery path (`~/.codex/skills/helix/` or
`~/.agents/skills/helix/` depending on installer version).

Requires Node.js. The Skills CLI also accepts `--list`, `--skill
<name>`, and multi-agent targets (`-a claude-code -a codex` etc). Use
this path when you are on a Codex CLI build that does not yet include
`codex plugin`.

## Install path C: filesystem copy (Dockerfile-friendly)

For scripted/Docker environments without Node:

```bash
# Clone or otherwise place HELIX source somewhere readable
git clone https://github.com/DocumentDrivenDX/helix /tmp/helix-src

# Place the skill where Codex discovers it
mkdir -p ~/.codex/skills/helix
cp -r /tmp/helix-src/skills/helix/* ~/.codex/skills/helix/

# Verify discovery (sub-second; loads frontmatter only)
codex --version
```

The agentskills.io invariant applies: parent directory name
(`helix`) must equal `name:` in the SKILL.md frontmatter. HELIX's
source layout already conforms.

Skills can also live at repo scope (`<repo>/.agents/skills/helix/`)
to override the user-scoped install for that repo.

## Install path D: DDx

If you also use DDx as your runtime:

```bash
ddx install helix
```

DDx places HELIX content at `~/.ddx/plugins/helix/`. For Codex
discovery, symlink the skill subdirectory into the Codex path:

```bash
ln -s ~/.ddx/plugins/helix/skills/helix ~/.codex/skills/helix
```

This keeps a single source updated via `ddx install helix --force`.

## Optional: AGENTS.md pointer at the repo root

For repos that want Codex to mention HELIX explicitly on session
start, add a HELIX section to `AGENTS.md` at the repo root:

```markdown
# Agent Instructions

This repo uses HELIX (methodology + artifact catalog + one routing skill).

- Routing skill: `skills/helix/SKILL.md`
- Artifact catalog: `workflows/activities/` (00-discover through 06-iterate)
- Methodology spec: `workflows/README.md`, `workflows/principles.md`

When the user asks to use HELIX, align documents, frame requirements,
design a change, evolve specs, review work, or otherwise touch
HELIX-governed material, load `skills/helix/SKILL.md` and follow the
routing table inside it. Do not invent new `helix-*` skills.
```

This is supplementary — Codex auto-discovers the skill from
`~/.codex/skills/helix/` regardless of `AGENTS.md` content. The pointer
helps when the user opens a Codex session and is unsure which skills
are available.

Note: Codex CLI does NOT honor `.codex/instructions.md`. The supported
instruction files are `AGENTS.override.md` and `AGENTS.md`, checked in
that order at `~/.codex/`, the git root, and each directory down to
the CWD. Custom fallback filenames can be added via
`project_doc_fallback_filenames` in `~/.codex/config.toml`.

## Verify

Open a Codex session in the repo and ask the verification question
non-interactively:

```bash
codex exec --ephemeral "What HELIX routing modes are available, and where is the routing skill?"
```

For plugin installs, first confirm the plugin is installed:

```bash
codex plugin list --marketplace helix --json
```

The installed plugin root should resolve under
`~/.codex/plugins/cache/helix/helix/<version>/`.

A correct runtime response:
1. Mentions the HELIX skill or the installed `helix@helix` plugin.
2. Lists routing modes: input, frame, align, evolve, design, backfill,
   review, polish, check/next, build, run, commit, release, experiment,
   worker (or a faithful subset).

For fallback filesystem skill installs, if Codex does not mention the skill
file, check:
- `ls ~/.codex/skills/helix/SKILL.md` confirms the file is in place
- `cat ~/.codex/config.toml | grep -A1 skills` does not have
  `enabled = false` for the HELIX entry

Disable a skill without removing files:

```toml
[[skills.config]]
path = "/home/<you>/.codex/skills/helix/SKILL.md"
enabled = false
```

Restart Codex after config changes.

## Activation phrasing (by name, not slash)

Codex CLI has no `/helix` slash-command surface. Activate HELIX by **naming the
skill or describing the work** in the prompt — this is also the correct pattern
for headless `codex exec` runs, where slash-style commands are inert:

```bash
codex exec --ephemeral "Use the helix skill to align the PRD with the designs"
```

The routing table in [`skills/helix/SKILL.md`](../../skills/helix/SKILL.md) is
the same regardless of phrasing; only activation differs across runtimes. See
[FEAT-013](../helix/01-frame/features/FEAT-013-runtime-install-coverage.md) for
per-runtime activation coverage.

## Auth in Docker / non-interactive

Codex requires authentication. For containerized use:

```bash
# Set the API key
export OPENAI_API_KEY=sk-...           # or CODEX_API_KEY=sk-...

# Seed credentials without browser flow
printenv OPENAI_API_KEY | codex login --with-api-key
```

Known issue: if `~/.codex/auth.json` already contains a cached
ChatGPT login, the `OPENAI_API_KEY` env var is ignored. Clear
`~/.codex/auth.json` first.

Alternative: `codex login --device-auth` for device-flow authorization
when `--with-api-key` is unavailable.

## Update / uninstall

Plugin update:

```bash
codex plugin marketplace upgrade helix
codex plugin add helix@helix
```

Plugin uninstall:

```bash
codex plugin remove helix@helix
```

For fallback skill installs there are no native `codex skill update` or
`codex skill remove` commands. Update by re-running the Skills CLI or
filesystem copy. Uninstall by deleting `~/.codex/skills/helix/` or setting
`enabled = false` in `~/.codex/config.toml`.

## What Codex can do for HELIX

All HELIX modes are available with Codex CLI:

- Read/write markdown, search files, multi-file edits, multi-turn
  reasoning: yes
- Shell execution (for `build`, `run`, `commit`, `release`,
  `experiment`, `worker` modes): yes
- Bead tracker discipline: yes, when DDx is also installed
- Long-running operator loop: possible; pair with `ddx work` for
  durable queue drain

For the full HELIX-plus-runtime experience, install DDx alongside
Codex and use `ddx work` to drive the queue while Codex handles
individual bead executions.

## Refresh: keeping your HELIX tree current

Refresh is a first-class HELIX mode that brings every artifact instance
under a project HELIX tree up to date with the current canonical
templates and prompts. Codex CLI currently runs Refresh in one session.
For parallel activity fan-out, pair Codex with a runtime such as DDx that
can dispatch one worker per activity directory. Both paths use the same
HELIX methodology.

## Integration tests

HELIX integration with Codex CLI is validated by the test harness at
`tests/workflows/codex-cli/` (see [README](../../tests/workflows/codex-cli/README.md)).
The harness exercises skill activation, routing, and behavioral correctness via
`codex exec`. Screencast: [`INT-CX.gif`](../../tests/workflows/codex-cli/recordings/INT-CX.gif).

## See also

- [`skills/helix/SKILL.md`](../../skills/helix/SKILL.md) — routing skill
- [docs/resources/agents/openai-codex-cli-skills.md](../resources/agents/openai-codex-cli-skills.md)
  — Codex CLI mechanism research notes
- [docs/resources/agents/agentskills-spec.md](../resources/agents/agentskills-spec.md)
  — cross-runtime SKILL.md standard
- [Install README index](README.md)
- Companion install guides: [Claude Code](claude-code.md),
  [GitHub Copilot](copilot.md), [Databricks Genie Code](databricks-genie.md)
- Integration test harness: [`tests/workflows/codex-cli/`](../../tests/workflows/codex-cli/)
