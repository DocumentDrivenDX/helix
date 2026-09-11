# Install HELIX

HELIX is a methodology, an artifact-type catalog, and one routing skill. It
is not a CLI, a tracker, or a runtime. Installing HELIX means making the
skill and the catalog discoverable from the tool you already use. This is
the one install guide. The [per-host sections](#per-host-notes) hold only
what differs on each host: the install command, where the skill lands, how
to invoke it, and host-specific limits.

## What you get

Every install ships the same two pieces:

- [`skills/helix/SKILL.md`](../../skills/helix/SKILL.md): the single
  routing skill. Public name `helix`, one routing table, and one contract
  per mode in `workflows/modes/<mode>.md`. There are no separate public
  `helix-*` skills.
- The catalog. A source checkout or full-repo plugin install resolves it
  from [`workflows/`](../../workflows/). A packaged install (Codex package
  copy, Genie bundle, slim plugin packages) resolves the same bytes from a
  generated `skills/helix/references/` floor that
  `scripts/sync_references.py` produces from `workflows/` at package time:
  `activities/`, `concerns/`, `modes/`, `actions/`, `templates/`,
  `deliverables/`, `graph.yml`, and `voice.yml`. The floor is build output,
  validated byte-for-byte against `workflows/`, never a second source of
  truth.

The skill and catalog are identical across hosts. When this guide and the
skill or catalog disagree, the skill and catalog govern.

Adopter projects do not vendor templates. A project needs only the marker
and its instance documents (by convention under `docs/helix/`). When
project-local `workflows/` is absent, catalog resolution falls through to
the installed plugin. A project-local `workflows/` remains valid for
self-hosting and intentional forks and outranks the plugin when present.

## Minimal runtime contract

A HELIX-compliant runtime can:

1. Read markdown files from the project's filesystem.
2. Write markdown files to the project's filesystem.
3. Search files by path or pattern across the project.
4. Optionally execute a shell command for verification or the
   execution-oriented modes.

That is the full contract. HELIX assumes no tracker, queue, execution loop,
IDE integration, or language toolchain. Items 1 through 3 are required and
cover alignment, framing, design, evolve, validate, and review. Item 4 is
optional; only `build`, `run`, `commit`, and `release` use it. This is the
binding form of PRD R-4 (runtime-neutral content).

## The marker

`.helix.yml` at the repository root declares which flows are active and
the scope root each one owns. The skill walks up from the working
directory to the repository root, reads the first marker it finds, and
binds the graph before any write. A minimal marker:

```yaml
flows:
  - id: helix
    root: docs/helix/
```

Optional keys: `graph:` (or `catalog:`) points at a catalog (step 1
below); `autonomy:` sets the default level and may add stop triggers under
`autonomy.stop_at_extensions:`. With no marker but a `docs/helix/` tree,
the skill engages by heuristic and says so. The full discipline is the
skill's "Activation Discipline" section.

## How the skill finds the catalog

The skill resolves mode contracts, templates, prompts, graph, voice, and
concerns in this fall-through order; the first source that binds wins, and
everything loads from that same bind:

1. The marker's `graph:` or `catalog:` pointer.
2. In-tree project `workflows/` (self-hosting or an intentional vendor),
   found by walking up from the working directory to the marker.
3. `../../workflows/` from the real path of `SKILL.md`: a source checkout,
   a `--plugin-dir` tree, or a full-repo plugin install.
4. `$GROK_PLUGIN_ROOT` or `$CLAUDE_PLUGIN_ROOT`, trying `workflows/` then
   `skills/helix/references/` under that root.
5. The generated `references/` floor beside `SKILL.md`.
6. Fail closed with a diagnostic listing every path tried.

A missing project `workflows/` is not an error when a later step binds.
The order is the same on every host; the host only decides which step
binds first.

## Invoking the skill

Engagement is the first tool action of the turn, in one of two shapes:

- Hosts with a skill tool (Claude Code, Codex CLI) invoke the `helix`
  skill through that tool. Interactively, `/helix <mode>` does this and
  `/helix` alone asks for intent.
- Hosts without a skill tool (Copilot, Genie Code, Grok Build chat) load
  the `SKILL.md` body first: `/helix`, skill auto-load, or a read of the
  file.

Headless and piped runs (`claude -p`, `codex exec`, CI) do not expand slash
commands. Name the skill or describe the work instead:

```text
Use the helix skill to align docs/helix/01-frame/prd.md with the designs.
```

Chat-only hosts (Copilot Chat, Genie Code) have no working directory.
Modes that enumerate the project tree (refresh and similar batch
operations) need the project root named in the prompt; the skill's
"Project Root Resolution" section requires this rather than guessing.

## Autonomy

HELIX expresses an autonomy policy; the runtime supplies the agency. Three
levels control how often a workflow pauses, never which activities run:
`low` asks before each step and each downstream artifact; `medium` (the
default) creates deterministic non-conflict artifacts and pauses on
ambiguity or conflict; `high` creates downstream artifacts without pausing
unless a hard stop blocks, recording assumptions instead of asking.
Precedence: a level named in the prompt, then the marker's `autonomy:`
block, then `medium`. Stop triggers (marker edits, branch or merge
operations, secret reads, large diffs, `apply`-class commands) are a hard
floor at every level; the full table is the skill's "Autonomy" section.

## Verification

On any host, open a session in a repo where the skill is discoverable and
ask:

```text
What HELIX routing modes are available, and where is the routing skill?
```

A working install names modes (input, frame, align, evolve, design,
backfill, review, polish, check, build, run, commit, release, experiment,
worker, or a faithful subset) and cites `skills/helix/SKILL.md`. A broken
install answers with generic guidance that never mentions the skill. In
interactive hosts `/helix check` does the same and proposes a next action.

For source checkouts, run the deterministic packaging checks:

```bash
bash tests/validate-skills.sh
```

`tests/install/` holds the per-host Docker smoke scenarios
(`just install-test`) and `tests/workflows/<host>/` the recorded
integration scenarios. Refresh (bringing every instance up to date with
current templates) fans out per activity on DDx and Claude Code; the other
hosts run it sequentially unless an external runtime fans out.

## Per-host notes

### Claude Code

Inside a session:

```text
/plugin marketplace add https://github.com/DocumentDrivenDX/helix
/plugin install helix@helix
```

Scripted (Dockerfile or CI):

```bash
claude plugin marketplace add https://github.com/DocumentDrivenDX/helix
claude plugin install helix@helix --scope user -y
```

- Lands under `~/.claude/plugins/cache/<version-dir>/` (loader-internal
  name; confirm with `claude plugin list`, not a path). Catalog binds at
  step 3.
- Session-only for development: `claude --plugin-dir /path/to/helix` or
  `claude --plugin-url <zip-url>` (v2.1.128+). Neither persists.
- Invoke with `/helix <mode>`; headless via
  `echo "Use the helix skill to ..." | claude -p` with `ANTHROPIC_API_KEY`
  set. All four contract items are satisfied, so every mode runs.
- Update: `claude plugin update helix@helix` (third-party marketplaces
  default to manual). Uninstall: `claude plugin uninstall helix@helix`.
- Recorded scenarios: `tests/workflows/claude-code/run-scenarios.sh`.

### OpenAI Codex CLI

```bash
codex plugin marketplace add DocumentDrivenDX/helix
codex plugin add helix@helix
```

- Lands under `~/.codex/plugins/cache/helix/helix/<version>/`; confirm
  with `codex plugin list --marketplace helix --json`.
- Fallback without `codex plugin` (older builds, Dockerfiles): build the
  generated package with `bash scripts/build-plugin-package.sh --out <dir>`
  and copy `<dir>/helix/skills/helix/` to `~/.codex/skills/helix/` (or
  `<repo>/.agents/skills/helix/` for one repo). The package carries the
  `references/` floor; a bare `skills/helix/` copied from a source checkout
  has no catalog.
- No slash surface. Invoke by name: `codex exec --ephemeral "Use the helix
  skill to ..."`. Auth: `OPENAI_API_KEY` plus `codex login --with-api-key`
  (clear a cached ChatGPT login in `~/.codex/auth.json` first). All four
  contract items are satisfied.
- Codex reads `AGENTS.md`, not `.codex/instructions.md`; an `AGENTS.md`
  line naming the `helix` skill helps orientation but is not required.
- Update: `codex plugin marketplace upgrade helix && codex plugin add
  helix@helix`. Uninstall: `codex plugin remove helix@helix`; filesystem
  installs are removed by deleting the directory or setting
  `enabled = false` under `[[skills.config]]` in `~/.codex/config.toml`.
- Recorded scenarios: `tests/workflows/codex-cli/run-scenarios.sh`.

### GitHub Copilot

There is no install command. Two repo-resident pieces:

1. HELIX content in the adopter repo: vendor `skills/helix/` and
   `workflows/` (or add the HELIX repo as a submodule) so
   `skills/helix/SKILL.md` and `workflows/activities/` are reachable from
   the repo root.
2. A committed `.github/copilot-instructions.md`. The HELIX repo's own
   [file](../../.github/copilot-instructions.md) is a thin pointer that
   tells Copilot to read `skills/helix/SKILL.md` and the mode files; copy
   it verbatim. `tests/validate-install-consistency.sh` keeps it a pointer
   rather than a fork of the skill.

- Copilot has no skill tool: the instruction file makes reading `SKILL.md`
  the first action, and the catalog binds at step 2 or 3.
- Chat surfaces (IDE and github.com) are chat-only: name the project root
  for refresh and other tree-wide modes. They also have no persistent
  shell, so `build`, `run`, `commit`, `release`, `experiment`, and
  `worker` are limited; pair with DDx or use the cloud agent.
- Every Copilot surface reads the file (IDE chat, github.com chat, cloud
  agent, code review, CLI); `AGENTS.md` reaches fewer, so keep the
  instruction file primary.
- Headless: `gh copilot suggest "..."` with a `GITHUB_TOKEN` carrying a
  Copilot license. Recorded scenarios:
  `tests/workflows/copilot-cli/run-scenarios.sh`.
- The legacy Copilot Extensions (GitHub Apps) path was retired in November
  2025; MCP servers are not needed for methodology work.

### Grok Build

```bash
grok plugin install DocumentDrivenDX/helix --trust
# pin a release: DocumentDrivenDX/helix@v0.12.0
```

Local checkout: `grok plugin validate /path/to/helix`, then
`grok plugin install /path/to/helix --trust`. Session-only:
`grok --plugin-dir /path/to/helix`.

- Lands as a full-repo copy under `~/.grok/installed-plugins/<id>/` with
  `workflows/` at the plugin root, so the catalog binds at step 3; Grok
  also sets `GROK_PLUGIN_ROOT` for step 4. If a future install shape ships
  only the skill subtree, install the generated package from
  `scripts/build-plugin-package.sh` instead.
- Trust: `--trust` activates hooks and skills. A plugin listed but
  inactive is enabled through the Grok plugin UI or `[plugins].enabled` in
  `~/.grok/config.toml`; reinstalling with `--trust` also clears an
  untrusted-hooks state.
- Verify with `grok plugin list` and `grok plugin details helix`, then
  `/helix check` or "Use the helix skill to list workflow modes." If
  several `helix` skills are listed, prefer the one under the installed
  `helix` plugin and ignore legacy DDx `helix-workflow` or
  `helix-alignment-review` entries.
- Update: `grok plugin update helix`. Uninstall:
  `grok plugin uninstall helix --confirm`. Layout probe:
  `tests/install/grok-build/phase0-layout.md`.

### Databricks Genie Code

From a dev box or CI, with `DATABRICKS_HOST` and `DATABRICKS_TOKEN` (or
`DATABRICKS_PROFILE`) set:

```bash
curl -fsSL https://github.com/DocumentDrivenDX/helix/releases/latest/download/genie-install -o /tmp/genie-install
chmod +x /tmp/genie-install
/tmp/genie-install            # --shared for workspace-wide (admin)
```

From a Databricks notebook the kernel already carries workspace auth; the
Python-cell form, installer flags, ACLs on shared installs, distribution,
the manual path, and Genie-specific verification prompts are in the deploy
runbook, [databricks-genie.md](databricks-genie.md). `just genie-build`,
`just genie-install`, and `just genie-verify` wrap it.

- Lands at `/Workspace/.assistant/skills/helix/` (shared) or
  `/Users/<email>/.assistant/skills/helix/` (user-scoped) as a bundle with
  the `references/` floor, so the catalog binds at step 5. Genie discovers
  skills by directory scan; start a new Agent-mode chat after installing.
- Chat-only: name the project root for tree-wide modes, and prefix a
  prompt with `@helix` if Genie does not pick the skill itself.
- The shell surface is constrained, so `build` and `run` usually pair with
  a Databricks job, notebook, or CI pipeline. Writes go through the
  workspace (Repos integration for git-backed folders). DDx is not part of
  the install.

### DDx

```bash
ddx install helix
ddx doctor
```

DDx is the reference runtime and owns the tracker, queue, execution loop,
dispatch, and evidence capture. `ddx install helix` clones HELIX into
`~/.ddx/plugins/helix/` in the Claude Code plugin format, so the same tree
is also a valid `claude --plugin-dir` target. Invoke through
`/helix <mode>` in the agent harness and `ddx work` for queue drain. All
DDx commands, tracker conventions, and the adapter boundary are in
[ddx.md](ddx.md).

## No-fork policy

The per-host sections exist so adopters can install HELIX, not to
localize or rewrite it. The normative skill body lives in
`skills/helix/SKILL.md` and the catalog source in `workflows/`, nowhere
else; host notes may quote them for orientation but never carry a
divergent copy, and generated `references/` floors are build output, not
normative content. A host that needs a shim (a manifest, a wrapper
instruction file, packaging metadata) keeps it in its host section or its
own adapter file, marked as host-specific; it does not get pushed into
`skills/` or `workflows/`. A host note that introduces HELIX behavior the
other hosts do not share is a bug against PRD R-4 and R-7; file it as an
alignment finding.

## See also

- [`docs/resources/agents/`](../resources/agents/README.md):
  engineer-facing notes on each host's plugin or skill mechanism.
- [`workflows/README.md`](../../workflows/README.md),
  [`workflows/principles.md`](../../workflows/principles.md),
  [`workflows/ratchets.md`](../../workflows/ratchets.md): methodology
  overview and invariants.
- [`docs/helix/01-frame/prd.md`](../helix/01-frame/prd.md): R-4
  (runtime-neutral content), R-7 (per-runtime packages), and the
  Constraints section behind the minimal runtime contract.
- [FEAT-013](../helix/01-frame/features/FEAT-013-runtime-install-coverage.md)
  and [TD-013](../helix/02-design/technical-designs/TD-013-multi-runtime-install.md):
  feature spec and technical design behind the install matrix.
