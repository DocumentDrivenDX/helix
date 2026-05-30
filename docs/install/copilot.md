# HELIX in GitHub Copilot

This guide installs HELIX into a GitHub Copilot-using repo. HELIX is
content + one routing skill; Copilot reads the routing rules and
catalog through repo-scoped instruction files.

The HELIX repo ships a `.github/copilot-instructions.md` at the repo
root. Adopter repos can copy or include this file (and the rest of
HELIX) and Copilot will pick it up automatically across every
Copilot surface that supports custom instructions.

## What you are installing

Two repo-resident artifacts:

1. **The instruction file** — `.github/copilot-instructions.md`. Plain
   Markdown auto-injected as Copilot system context. The HELIX repo
   ships this file; copy it into your adopter repo verbatim.
2. **The HELIX content** — `skills/helix/SKILL.md` (routing skill) and
   `workflows/activities/` (artifact catalog). Vendor or include via
   submodule.

HELIX does not require any GitHub Copilot extension or App. The
custom-instructions path is the canonical install today.

> The legacy **Copilot Extensions (GitHub Apps)** path was sunset on
> 2025-09-24 and fully disabled on 2025-11-10. Do not invest there.
> See [Copilot research notes](../resources/agents/github-copilot-instructions.md).

## Install

### Step 1 — get HELIX content into the repo

Either:

- **Vendor** the routing skill and catalog at the conventional paths:
  ```
  <repo>/
    skills/helix/SKILL.md
    workflows/activities/00-discover/
    workflows/activities/01-frame/
    ...
    workflows/activities/06-iterate/
  ```
- **Or** install via DDx: `ddx install helix` (DDx places HELIX content
  under `.ddx/plugins/helix/`; you may need to symlink
  `.ddx/plugins/helix/skills/helix` into `skills/helix` for Copilot to
  discover it from the repo root).

### Step 2 — commit `.github/copilot-instructions.md`

Copy this file from the HELIX repo (or symlink it from a vendored HELIX
checkout):

```
<repo>/.github/copilot-instructions.md
```

That file points Copilot at `skills/helix/SKILL.md` and
`workflows/activities/` and states the HELIX conventions (single
public skill, no fork, runtime-neutral).

No install command needed. Copilot reads the file automatically.

### Step 3 (optional) — path-scoped instructions

For per-subtree HELIX guidance, add files under
`.github/instructions/` with `applyTo:` frontmatter:

```markdown
---
applyTo: "docs/helix/01-frame/**"
---
# Frame-mode HELIX guidance for these paths
...
```

Path-scoped instructions are read by VS Code/JetBrains/Xcode/Eclipse
Copilot Chat, the cloud agent, code review, and Copilot CLI. They are
NOT read by github.com Copilot Chat.

## Surface coverage

`.github/copilot-instructions.md` is read by:

- VS Code, JetBrains, Xcode, Eclipse Copilot Chat
- github.com Copilot Chat
- Copilot cloud agent
- Copilot code review
- Copilot CLI (`gh copilot`)

`AGENTS.md` (also at the repo root) is read by Copilot cloud agent +
VS Code Copilot Chat + Copilot CLI — but NOT by github.com Copilot
Chat or most IDE chat surfaces. Use `.github/copilot-instructions.md`
as the primary path; `AGENTS.md` is supplementary.

## Verify

In any Copilot surface with the repo open and instruction file
discoverable, ask:

```
What HELIX routing modes are available, and where is the routing
skill in this repo?
```

A correct install:
1. Lists modes (input, frame, align, evolve, design, backfill,
   review, polish, check/next, build, run, commit, release,
   experiment, worker) or a faithful subset.
2. Cites `skills/helix/SKILL.md` as the routing skill.
3. Mentions reading `.github/copilot-instructions.md` (when prompted
   explicitly).

A broken install responds with generic Copilot guidance that does not
reference the HELIX skill.

### Headless verification with Copilot CLI

For CI/Docker use, the `gh copilot` CLI (GA January 2026) honors
`.github/copilot-instructions.md`:

```bash
export GITHUB_TOKEN=<personal access token with Copilot license>
gh copilot suggest "list the HELIX routing modes from skills/helix/SKILL.md"
```

The token holder must have an active Copilot license (Pro/Business/
Enterprise). For non-interactive verification, parse the response for
expected mode names.

See [Workflow integration test](../workflows/copilot-cli/) for a complete
harness that exercises skill activation across three scenarios
(install-verify, skill-list, bootstrap) with vhs recording. Run with:

```bash
bash tests/workflows/copilot-cli/run-scenarios.sh
```

## What Copilot can and cannot do for HELIX

| Mode | Copilot Chat (IDE/web) | Copilot CLI | Cloud agent |
|---|---|---|---|
| `input`, `frame`, `align`, `evolve`, `validate`, `review`, `backfill`, `polish`, `check`/`next` | yes (read + write Markdown) | yes | yes |
| `design` | yes | yes | yes |
| `build`, `run`, `commit`, `release`, `experiment`, `worker` | limited — chat surface, no persistent execution loop | partial — shell available but no DDx integration | yes via cloud agent + MCP, if configured |

Execution-oriented modes (`build`, `run`, `commit`, `release`,
`experiment`, `worker`) assume a runtime. Pair Copilot with DDx (or
another runtime) for the full HELIX loop; use Copilot solo for
methodology-only HELIX work (alignment, framing, evolve, review,
polish).

## Refresh: keeping your HELIX tree current

Refresh is a first-class HELIX mode that brings every artifact instance
under a project HELIX tree up to date with the current canonical
templates and prompts. GitHub Copilot does not have a sub-agent dispatch
mechanism, so Refresh runs sequentially: each activity directory is
processed in order (00-discover, then 01-frame, …, through 06-iterate).
For large artifact trees where parallel processing would be beneficial,
consider using DDx or another execution runtime alongside Copilot for
faster turnaround.

## Optional: MCP server

If you need HELIX to expose tool calls (artifact catalog queries,
alignment checkers), package those as an MCP server and register it
with Copilot per [GitHub's MCP guide](https://docs.github.com/en/copilot/concepts/context/mcp).
MCP is overkill for methodology-only HELIX and is not required for
the install paths above.

Cloud-agent MCP servers must be configured via repo Settings →
Copilot → Cloud agent → MCP configuration (web UI paste). There is no
`.mcp.json`-in-repo auto-install for the cloud agent.

## See also

- [`.github/copilot-instructions.md`](../../.github/copilot-instructions.md)
  — the HELIX repo's own instruction file (copy verbatim into adopter
  repos)
- [docs/resources/agents/github-copilot-instructions.md](../resources/agents/github-copilot-instructions.md)
  — Copilot mechanism research notes
- [Install README index](README.md)
- Companion install guides: [Claude Code](claude-code.md),
  [OpenAI Codex CLI](codex.md), [Databricks Genie Code](databricks-genie.md),
  DDx (use `ddx install helix`)
