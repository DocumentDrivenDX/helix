# HELIX in Claude Code

This guide installs HELIX as a Claude Code plugin. The canonical
install is the **marketplace flow**: add the HELIX marketplace, then
install the `helix` plugin from it. No `git clone`, no manual symlinks.

For development or CI scenarios that need to test a local checkout
before publishing, a `--plugin-dir` session-load path is documented
below.

## What you are installing

The HELIX repo IS a Claude Code plugin. Its layout:

```
helix/
  .claude-plugin/
    plugin.json            # plugin manifest (name=helix, version=...)
    marketplace.json       # marketplace manifest listing the helix plugin
  skills/
    helix/
      SKILL.md             # the routing skill (agentskills.io-compliant)
  workflows/
    activities/            # artifact-type catalog (7 activities)
    ...
```

When you install the `helix` plugin, Claude Code makes the skill
discoverable as `helix` (callable as `/helix` or by description match)
and the catalog reachable at `workflows/activities/...`.

## Install path A: marketplace (canonical)

Two TUI commands inside Claude Code:

```
/plugin marketplace add https://github.com/DocumentDrivenDX/helix
/plugin install helix@helix
```

Or scripted (Dockerfile-friendly), suitable for use in automation:

```bash
claude plugin marketplace add https://github.com/DocumentDrivenDX/helix
claude plugin install helix@helix --scope user -y
```

After install, the skill is available in any Claude Code session.
Verify with `claude plugin list`:

```
$ claude plugin list
NAME   VERSION  SOURCE
helix  0.5.2    DocumentDrivenDX-helix
```

## Install path B: session-only via `--plugin-dir` (development / CI)

For testing a local HELIX checkout without going through marketplace
distribution:

```bash
# Load a local plugin directory for one session
claude --plugin-dir /path/to/helix
```

Or load a remote `.zip` (Claude Code v2.1.128+):

```bash
claude --plugin-url https://github.com/DocumentDrivenDX/helix/archive/v0.5.2.zip
```

Session-only loads do not persist. Once Claude Code exits, the plugin
is unloaded. Use for verification before tagging a release.

## Install path C: DDx (alternative)

DDx and Claude Code share the same plugin format. If you already use
DDx, `ddx install helix` places HELIX content at `~/.ddx/plugins/helix/`
which is also a valid Claude Code `--plugin-dir` target:

```bash
ddx install helix
claude --plugin-dir ~/.ddx/plugins/helix
```

For permanent install via the marketplace flow, prefer path A.

## Auth in Docker / non-interactive

Claude Code reads `ANTHROPIC_API_KEY` from the environment. No browser
flow is required for `claude -p`:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
claude plugin marketplace add https://github.com/DocumentDrivenDX/helix
claude plugin install helix@helix --scope user -y
echo "List HELIX routing modes" | claude -p
```

## Update

```bash
claude plugin update helix@helix
```

Or set `autoUpdate: true` in the marketplace configuration to auto-pull
new versions of `helix` whenever the marketplace listing's version
bumps. Anthropic-official marketplaces auto-update by default;
third-party marketplaces (including `DocumentDrivenDX/helix`) default to manual.

Versioning falls through:
1. Explicit `version` in `plugin.json` (bumped manually on releases)
2. Falls back to git commit SHA (every commit = new version) when
   `version` is missing

## Uninstall

```bash
claude plugin uninstall helix@helix
# preserve plugin data (e.g., ${CLAUDE_PLUGIN_DATA}):
claude plugin uninstall helix@helix --keep-data
```

Aliases: `remove`, `rm`.

## Verify

In a Claude Code session:

```
/helix check
```

A working install responds with:
1. A short statement that the HELIX router loaded.
2. A list of governing artifacts under `docs/helix/` (or a note that
   none exist yet — that's fine; the skill offers `input` or `frame`).
3. A proposed next action drawn from the routing table.

Or non-interactively:

```bash
echo "What HELIX routing modes are available?" | claude -p
```

Expected: response names align, frame, evolve, review, design,
backfill, validate, polish, check, build, run, commit, release,
experiment, worker (or a faithful subset) and references the
`helix` skill.

## Integration test screencast

The HELIX Claude Code integration test exercises the skill with three scenarios:
install verification, skill-list routing, and bootstrap (SCN-01). See the
screencast:

![HELIX Claude Code Integration Test](../../tests/workflows/claude-code/recordings/INT-CC.gif)

Or run the tests yourself with valid credentials:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
bash tests/workflows/claude-code/run-scenarios.sh
```

To verify the negative control (skill not invoked when not allowed):

```bash
bash tests/workflows/claude-code/run-scenarios.sh --no-skill
```

## How invocation works

Users state intent; the skill routes. Supported shapes:

- `/helix` — invoke with no arguments, the router asks for intent.
- `/helix align this PRD with the design docs` — invoke with inline intent.
- Natural-language ask: "use HELIX to evolve the auth requirement
  through the spec stack". Claude Code matches by skill description.

### Interactive vs headless activation

The `/helix` slash form is an **interactive-session** convenience. In headless
/ non-interactive runs (`claude -p "..."`, CI, or any pipe), slash commands are
inert — they are not expanded. To activate HELIX headlessly, phrase the request
**by skill name or description** so the skill matches:

```bash
# Headless: name the skill / describe the work — do NOT rely on "/helix ..."
echo "Use the helix skill to align docs/helix/01-frame/prd.md with the designs" | claude -p
```

Rule of thumb: interactive → `/helix <mode>`; headless → name "helix" (or
describe HELIX work) in the prompt. The routing table in
[`skills/helix/SKILL.md`](../../skills/helix/SKILL.md) is identical for both;
only the activation phrasing differs. See
[FEAT-013](../helix/01-frame/features/FEAT-013-runtime-install-coverage.md) for
the per-runtime activation coverage.

Claude Code resolves the `helix` skill through the plugin loader. The
marketplace flow copies the plugin into a per-version directory under the
local plugin cache, with persistent plugin state in a sibling data tree
(per Anthropic's [plugin reference](https://code.claude.com/docs/en/plugins-reference)):

- `~/.claude/plugins/cache/<version-dir>/skills/helix/` — the installed
  plugin. The exact `<version-dir>` name is an internal detail of the
  loader, not a stable path you should script against.
- `~/.claude/plugins/data/<id>/` — plugin state, where `<id>` is the
  install identifier with non-`[a-zA-Z0-9_-]` characters replaced by `-`.
- Session `--plugin-dir <path>` loads the directory directly for one
  session, bypassing the cache.

Use `claude plugin list` to confirm the install rather than checking a
path; the loader location is an implementation detail.

The router then consults its internal routing table in
`skills/helix/SKILL.md` and picks a mode. Each mode has a workflow
contract in the same file.

When a routed mode needs a template, prompt, or quality rubric, it
opens the matching file under
`workflows/activities/<activity>/artifacts/<type>/`. For example,
framing a PRD reads
`workflows/activities/01-frame/artifacts/prd/template.md` and
`prompt.md`.

## Per-runtime contract

HELIX assumes only the minimum runtime contract from the PRD: read
markdown, write markdown, search files, and optionally execute a
shell command. Claude Code provides all of these. If you see HELIX
skill or workflow content that hard-codes a runtime command in its
normative body, that is a bug against PRD R-4 and should be filed.

## Refresh: keeping your HELIX tree current

Refresh is a first-class HELIX mode that brings every artifact instance
under a project HELIX tree up to date with the current canonical
templates and prompts. Claude Code supports Refresh through the Agent
tool: when you invoke Refresh, Claude Code dispatches parallel sub-agents
per activity directory (00-discover, 01-frame, …, 06-iterate) for faster
processing of large artifact trees. Refresh also runs sequentially if you
prefer; both paths use the same underlying HELIX methodology.

## See also

- [`skills/helix/SKILL.md`](../../skills/helix/SKILL.md) — routing skill
- [`.claude-plugin/plugin.json`](../../.claude-plugin/plugin.json) — manifest
- [`.claude-plugin/marketplace.json`](../../.claude-plugin/marketplace.json)
  — marketplace listing
- [docs/resources/agents/claude-code-plugins.md](../resources/agents/claude-code-plugins.md)
  — Claude Code plugin mechanism research notes
- [Install README index](README.md)
- Companion install guides: [OpenAI Codex CLI](codex.md),
  [GitHub Copilot](copilot.md), [Databricks Genie Code](databricks-genie.md)
