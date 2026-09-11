# Agent Instructions

This is the HELIX repository — the canonical source for the HELIX methodology,
artifact-type catalog, and the single public `helix` routing skill. HELIX is
content plus one skill; execution belongs to a runtime (DDx, Claude Code,
Codex CLI, Databricks Genie).

The governing artifacts of HELIX-the-project live under `docs/helix/`.
Methodology specifications and shared templates live under `workflows/`. Both
are authoritative; the artifact-type catalog (`workflows/activities/*/artifacts/`)
is the canonical shape, and `docs/helix/` is HELIX applied to itself.

This project uses the DDx tracker for its own work items. Issues live in
`.ddx/beads.jsonl`, one JSON object per line. The managed DDx block at the end
of this file covers tracker conventions; HELIX content never names `ddx`
commands (see `lefthook.yml` `check-workflow-paths`).

## Quick Reference

Validation and build:

```bash
just test                     # Run all tests (skills, packaging, digests, actions)
bash tests/validate-skills.sh
bash tests/validate-context-digests.sh
bash tests/validate-demo-fixtures.sh
bash tests/validate-pages-demo-recording.sh

python3 scripts/generate_graph.py      # Regenerate workflows/graph.yml from meta.yml
python3 scripts/generate-reference.py  # Regenerate /artifact-types/, /concerns/, /reference/workflow-modes/
python3 scripts/publish-artifacts.py   # Publish docs/helix/ into /artifacts/
python3 scripts/publish-resources.py   # Publish docs/resources/ into /research/
bash website/scripts/serve-local.sh    # Serve the microsite at http://eitri:1315/helix/
```

The local microsite review server must use the `/helix` base path. Do not
restart it at the domain root; paths such as
`http://eitri:1315/artifact-types/...` are invalid for local review.

Deploy to a Databricks workspace (Genie) as a skill bundle uploaded via the
Databricks SDK (no Databricks CLI required). Full runbook:
[docs/install/databricks-genie.md](docs/install/databricks-genie.md).

```bash
just genie-build                       # assemble dist/genie-bundle/helix/
export DATABRICKS_HOST=https://<workspace>   # or set DATABRICKS_PROFILE
export DATABRICKS_TOKEN=<token>
just genie-install                     # upload to /Workspace/.assistant/skills/helix
just genie-verify                      # offline static checks
```

## HELIX Workflow Notes

When working on HELIX itself in this repo:

- top-level overview: `workflows/README.md`
- methodology reference: `workflows/REFERENCE.md`
- mode contracts: `workflows/modes/<mode>.md` (the skill routes, then loads
  the mode file; `_authoring.md` and `_report.md` are shared)
- marker: `.helix.yml` at the repo root declares the `helix` flow with root
  `docs/helix/`; the skill reads it before any edit
- alignment and backfill are cross-activity actions:
  - `workflows/actions/reconcile-alignment.md`
  - `workflows/actions/backfill-helix-docs.md`
- quality ratchets are documented in `workflows/ratchets.md`. Ratchet
  enforcement scripts and floor fixtures belong in adopting projects, not in
  this repo. This repo defines the pattern and the integration points.

Two layers:

- the portable `helix` skill packaged from `skills/helix/`
- the methodology contract under `workflows/`, read by runtimes and by the
  skill through §Catalog Resolution

## HELIX Skills

The installed HELIX agent skill is:

- `helix` — routes natural HELIX requests to the correct folded workflow mode

Rule: do not add separate public `helix-*` skills. Add or refine a route inside
`skills/helix/SKILL.md` instead.
Published `SKILL.md` files must declare `name` and `description`; add
`argument-hint` when the skill accepts a trailing positional argument such as
a scope, selector, issue ID, or goal.

The skill body must stay runtime-neutral: no tracker vocabulary (`bead`), no
host invocation commands, no test-bench machinery. `tests/validate-skills.sh`
enforces this (PRD R-4).

## Installation

HELIX ships no CLI. It is artifact templates plus the routing skill; queue
control, execution, and operator dispatch belong to the runtime.

### Primary installation (plugin mode)

```bash
claude --plugin-dir /path/to/helix
```

Plugin mode discovers the skill automatically and resolves shared resources
via `${CLAUDE_PLUGIN_ROOT}`. No manual installer step is needed.

Key plugin files:
- Plugin manifest: `.claude-plugin/plugin.json`
- Skills directory: `skills/` (auto-discovered by plugin loader)
- Shared resources: `workflows/`

### Other runtimes

Per-runtime install guides live under `docs/install/` (DDx, Claude Code,
Codex, Copilot, Databricks Genie, Grok). For working on HELIX itself, the
project-local `.agents/skills` and `.claude/skills` entries are symlinks to
`skills/`, so edits are live immediately.

## Demo Recording

Demos live in `docs/demos/helix-*/` and produce asciinema `.cast` files for
the microsite. Each demo supports two modes:

| Mode | Env Vars | Description |
|------|----------|-------------|
| **Record** | `DEMO_RECORD=1 DEMO_HARNESS=claude` | Runs with real Claude, saves agent responses + project fixtures |
| **Replay** | `DEMO_HARNESS=virtual` | Replays recorded responses via DDX virtual agent — no API keys |

```bash
# Record golden responses (requires Claude API key)
cd /tmp && mkdir demo && cd demo
DEMO_RECORD=1 HELIX_DEMO_RECORDING=1 bash /path/to/helix/docs/demos/helix-quickstart/demo.sh

# Replay without API keys
cd /tmp && mkdir replay && cd replay
DEMO_HARNESS=virtual HELIX_DEMO_RECORDING=1 bash /path/to/helix/docs/demos/helix-quickstart/demo.sh
```

Each demo stores:
- `agent-dictionary/*.json` — recorded prompt→response pairs (DDX virtual agent format)
- `fixtures/` — project files the agent would create, applied during virtual replay

After recording, zero the `delay_ms` fields so replay is instant. Use python
(NOT `ddx jq` — it corrupts multi-byte UTF-8):

```python
import json, glob
for f in glob.glob('docs/demos/helix-*/agent-dictionary/*.json'):
    with open(f, 'r') as fh: data = json.load(fh)
    data['delay_ms'] = 0
    with open(f, 'w') as fh: json.dump(data, fh, indent=2, ensure_ascii=False)
```

The GitHub Actions pages workflow (`pages.yml`) records all 4 demos using the
virtual agent and builds the Hugo site — no API keys or Docker needed in CI.

## Testing Requirements for HELIX Changes

If you change the routing skill, an action prompt, or catalog metadata, run
the skills validation (`bash tests/validate-skills.sh`). It checks packaging,
frontmatter limits, catalog/graph/table drift, references resolution, and
the runtime-neutrality gate.

If you change context-digest assembly or validation behavior, also run the
context-digest validator:

- `scripts/refresh_context_digests.py`
- `scripts/validate_context_digests.py`
- `workflows/references/context-digest.md`
- `workflows/actions/input.md`
- `workflows/actions/fresh-eyes-review.md`
- `workflows/actions/reconcile-alignment.md`

If you change demo scripts, replay agent fixtures, or demo validation wiring,
also run the demo-fixture validator:

- `docs/demos/*/demo.sh`
- `docs/demos/*/agent-dictionary/*.json`
- `tests/validate-demo-fixtures.sh`
- `justfile` entries that wire demo validation into shared test lanes

If you change the Pages demo-recording workflow or its deterministic validator,
also run the Pages demo-recording validator:

- `.github/workflows/pages.yml`
- `.github/workflows/test.yml`
- `scripts/record_pages_demos.sh`
- `tests/validate-pages-demo-recording.sh`

Required checks:

```bash
just test
git diff --check
```

The skills checks are intentionally deterministic:

- they assert HELIX ships no CLI wrapper (the runtime owns execution)
- they validate skill packaging, metadata, and `workflows/` reference resolution
- they avoid live Codex or Claude calls

## Non-Interactive Shell Commands

**ALWAYS use non-interactive flags** with file operations to avoid hanging on confirmation prompts.

Shell commands like `cp`, `mv`, and `rm` may be aliased to include `-i` (interactive) mode on some systems, causing the agent to hang indefinitely waiting for y/n input.

**Use these forms instead:**
```bash
# Force overwrite without prompting
cp -f source dest           # NOT: cp source dest
mv -f source dest           # NOT: mv source dest
rm -f file                  # NOT: rm file

# For recursive operations
rm -rf directory            # NOT: rm -r directory
cp -rf source dest          # NOT: cp -r source dest
```

**Other commands that may prompt:**
- `scp` - use `-o BatchMode=yes` for non-interactive
- `ssh` - use `-o BatchMode=yes` to fail instead of prompting
- `apt-get` - use `-y` flag
- `brew` - use `HOMEBREW_NO_AUTO_UPDATE=1` env var

**`ddx jq` UTF-8 warning:** `ddx jq` corrupts multi-byte UTF-8 characters
(e.g., em-dash `—`) when rewriting JSON files. Use python for JSON
manipulation of files that may contain non-ASCII text.

## Destructive Command Guard

NEVER run these commands without explicit user request:

| Blocked | Safe Alternative |
|---------|-----------------|
| `git reset --hard` | `git stash` |
| `git push --force` | `git push --force-with-lease` |
| `git clean -f` | `git clean -i` or explicit file removal |
| `git checkout .` / `git restore .` | Specify files explicitly |
| `rm -rf /` or broad recursive deletes | Targeted removal with confirmation |

Pre-commit hooks must remain enabled. Do not use `--no-verify`.

## Plan-First Development

For new features or major work:

1. `/helix design [scope]` — create the design document
2. `/helix polish [scope]` — decompose the plan into implementable work items,
   then refine them
3. the runtime executes the work (for DDx, see `docs/install/ddx.md`)

Step 2 is mandatory. Without polish, agents encounter undecomposed epics
during build and attempt ad-hoc decomposition, producing poor breakdowns.

## Session Completion

When ending a work session: file issues for remaining work, run the quality
gates if content changed, update issue status, commit, and push. Work left
uncommitted or unpushed is stranded.

<!-- DDX-AGENTS:START -->
<!-- Managed by ddx init / ddx update. Edit outside these markers. -->

# DDx

This project uses [DDx](https://github.com/DocumentDrivenDX/ddx) for
document-driven development. Use the `ddx` skill for beads, work,
review, agents, and status — every skills-compatible harness (Claude
Code, OpenAI Codex, Gemini CLI, etc.) discovers it from
`.claude/skills/ddx/` and `.agents/skills/ddx/`.

## Default Interactive Mode

Broad conversational DDx prompts — queue orientation, planning, review,
guidance folding, spec alignment, and bead breakdown — use
`interactive-steward` / `queue_steward`. Explicit worker commands
(`ddx work`, `ddx try <id>`, "execute bead `<id>`") route to
`bead_execution`. Explicit code/doc edit requests route to
`direct_user_implementation`. Explicit review-only requests route to
`review`.

`DDX_MODE=bead_execution` overrides only the interactive queue-steward default.
It **never** overrides tracker, merge, commit, safety, or verification policy —
those apply in every mode.

### Mutation policy

- **read / plan / fresh-eyes review / fold guidance / align specs** — non-mutating
  by default; no tracker writes, no code edits.
- **Tracker mutation** (e.g. `ddx bead create`, `ddx bead update`) requires an
  explicit durable-output verb: "create a bead", "file this as work",
  "break down into beads".
- **Code edits** require explicit implementation intent ("fix this",
  "implement X") or `bead_execution` mode.

## Files to commit

After modifying any of these paths, stage and commit them:

- `.ddx/beads.jsonl` — work item tracker
- `.ddx/config.yaml` — project configuration
- `.agents/skills/ddx/` — the ddx skill (shipped by ddx init)
- `.claude/skills/ddx/` — same skill, Claude Code location
- `docs/` — project documentation and artifacts

## Conventions

- Use `ddx bead` for work tracking (not custom issue files).
- Documents with `ddx:` frontmatter are tracked in the document graph.
- Run `ddx doctor` to check environment health.
- Run `ddx doc stale` to find documents needing review.

## Merge Policy

Branches containing `ddx try` or `ddx work` commits
carry a per-attempt execution audit trail:

- `chore: update tracker (execute-bead <TIMESTAMP>)` — attempt heartbeats
- `Merge bead <bead-id> attempt <TIMESTAMP>- into <branch>` — successful lands
- `feat|fix|...: ... [ddx-<id>]` — substantive bead work

Bead records store `closing_commit_sha` pointers into this history. Any
SHA rewrite breaks the trail. **Never squash, rebase, or filter** these
branches. Use only:

- `git merge --ff-only` when the target is a strict ancestor, or
- `git merge --no-ff` when divergence exists

Forbidden on execute-bead branches: `gh pr merge --squash`,
`gh pr merge --rebase`, `git rebase -i` with fixup/squash/drop,
`git filter-branch`, `git filter-repo`, and `git commit --amend` on
any commit already in the trail.
<!-- DDX-AGENTS:END -->
