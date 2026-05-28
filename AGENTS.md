# Agent Instructions

This is the HELIX repository — the canonical source for the HELIX methodology,
artifact-type catalog, and umbrella `helix` routing skill. HELIX is content +
one public skill; execution lives in a runtime (DDx today, Databricks Genie and
Claude Code in progress).

The governing artifacts of HELIX-the-project live under `docs/helix/`.
Methodology specifications and shared templates live under `workflows/`. Both
are authoritative; the artifact-type catalog (`workflows/activities/*/artifacts/`)
is the canonical shape, and `docs/helix/` is the worked example of HELIX
applied to itself.

This project uses the DDx tracker for execution work. Issues live in
`.ddx/beads.jsonl` — one JSON object per line.

## Direction note

HELIX is collapsing in scope. The deliverable is methodology + artifact
templates + one public `helix` skill that routes to folded workflow modes.
The old `helix-*` skill directories have been folded into `skills/helix/`;
queue control, beads, and execution belong to the runtime (DDx). See
`docs/helix/00-discover/product-vision.md` and `docs/helix/01-frame/prd.md`
for the target shape. The Quick Reference below is what works **today** while
the collapse proceeds — many of those commands will be removed.

## Quick Reference

DDx-owned (the runtime primitives — these stay):

```bash
ddx bead ready           # Find available tracked work
ddx bead ready --execution # Find execution-safe work
ddx bead show <id>       # View issue details
ddx bead update <id> --claim  # Claim work
ddx bead close <id>      # Complete work
ddx bead status          # Tracker health
ddx work                 # Primary queue-drain surface
ddx bead execute <id>    # One bounded bead execution
ddx doc prose            # Prose-quality check
```

HELIX ships no checkout CLI. It is artifact templates plus the routing skill;
runtimes (DDx, Claude Code, Codex CLI, Genie) own execution. Operators
interact through `/helix <mode>` slash commands or runtime CLIs such as
`ddx work` and `ddx bead`.

Validation and build:

```bash
just test                     # Run all tests (skills + state rules + digests)
bash tests/validate-state-rules.sh
bash tests/validate-context-digests.sh
bash tests/validate-demo-fixtures.sh
bash tests/validate-pages-demo-recording.sh
bash tests/validate-skills.sh

python3 scripts/generate-reference.py  # Regenerate /artifact-types/ and /concerns/ from workflows/
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

## Operational Guide

### Starting a background run

```bash
nohup ddx work > /tmp/ddx-work.stdout.log 2> /tmp/ddx-work.stderr.log &
echo $! > /tmp/ddx-work.pid
```

Defaults are reasonable: agent selection is driven by DDx harness discovery,
review threshold 100 lines, alignment every 15 cycles, 45-min timeout.

### Monitoring a run

```bash
# Is it running?
kill -0 $(cat /tmp/ddx-work.pid) 2>/dev/null && echo "RUNNING" || echo "STOPPED"

# Progress
grep -E "cycle|complete|tokens" /tmp/ddx-work.stderr.log | tail -10

# Why did it stop?
grep "═══\|stopping\|BLOCKER" /tmp/ddx-work.stderr.log | tail -5
```

### Consolidating related issues

Before a run, group related issues into epics. The run loop's epic focus
mode will stay on one epic and batch its children:

```bash
# Create epic
epic=$(ddx bead create "Epic: ..." --type epic ...)
# Wire children
ddx bead update hx-child1 --parent $epic
ddx bead update hx-child2 --parent $epic
# Supersede duplicates
ddx bead update hx-old --superseded-by hx-new
ddx bead close hx-old
```

### Known operational gotchas

- **Codex sandbox bypasses pre-commit hooks** — the run loop has a build
  gate that catches broken code, but the agent should also run
  `lefthook run pre-commit` before pushing (Activity 8 in implementation.md).
- **Skill YAML front matter** — quote values containing colons or pipes,
  otherwise codex's skill loader silently rejects them.
- **`asciinema rec` masks child failures** — the recorder can exit `0` and
  write a non-empty `.cast` even when the wrapped demo command fails. Pages
  or demo validation must capture and assert the child exit status explicitly;
  checking only the recorder exit code or `test -s` on the cast is not enough.
- **Stale in-progress claims** — after a crashed run, unclaim manually:
  `ddx bead list --status in_progress --json | ddx jq -r '.[].id'`
  then `ddx bead update <id> --status open --assignee ""`

## HELIX Workflow Notes

When working on HELIX itself in this repo:

- top-level overview: `workflows/README.md`
- operator loop and automation: `workflows/EXECUTION.md`
- tracker conventions: `ddx bead --help` (DDx FEAT-004)
- command summary: `workflows/REFERENCE.md`

Key rules:

- Use the built-in tracker (`ddx bead`); do not use external issue trackers.
- For general ready-work detection, use `ddx bead ready`, not manual JSONL parsing.
- For execution selection or `ddx work` reasoning, use `ddx bead ready --execution`.
- Keep `implementation` single-shot and bounded to one issue per run.
- Use `check` when the ready queue drains to decide whether to build,
  design, polish, align, backfill, wait, ask for guidance, or stop.
- Keep alignment and backfill as separate cross-activity actions:
  - `workflows/actions/reconcile-alignment.md`
  - `workflows/actions/backfill-helix-docs.md`
- Quality ratchets are documented in `workflows/ratchets.md`. Ratchet
  enforcement scripts and floor fixtures belong in adopting projects, not in
  this repo. This repo defines the pattern and the integration points in
  action prompts and enforcers.

Think about HELIX in two layers:

- portable skills packaged from `.agents/skills`
- the stricter HELIX workflow contract defined under `workflows/` and executed
  by runtimes (DDx, Claude Code, Codex CLI, Genie)

HELIX operates as a **double helix** — two interleaved cycles:

- **Planning helix**: review → plan → validate (creates and refines beads)
- **Execution helix**: execute → measure → report (claims beads, does work,
  records results, creates follow-on beads)

Every action that modifies files must be governed by a bead (bead-first
principle). Planning-helix beads use `kind:planning` label. Measurement
results are recorded on beads. Report creates follow-on beads that feed
back into the planning helix. See `workflows/EXECUTION.md` for details.

## HELIX Skills

The installed HELIX agent skill is:

- `helix` — routes natural HELIX requests to the correct folded workflow mode

Rule: do not add separate public `helix-*` skills. Add or refine a route inside
`skills/helix/SKILL.md` instead.
Published `SKILL.md` files must declare `name` and `description`; add
`argument-hint` when the skill accepts a trailing positional argument such as
a scope, selector, issue ID, or goal.

## Installation

HELIX ships no checkout CLI. It is artifact templates plus the routing skill;
queue control, execution, alignment, and operator dispatch belong to the
runtime (DDx today) or installed skills, not to this repository.

### Primary installation (plugin mode)

```bash
claude --plugin-dir /path/to/helix
```

Plugin mode discovers all skills automatically and resolves shared resources
via `${CLAUDE_PLUGIN_ROOT}`. No manual installer step is needed.

Key plugin files:
- Plugin manifest: `.claude-plugin/plugin.json`
- Skills directory: `skills/` (auto-discovered by plugin loader)
- Shared resources: `workflows/`

### DDx plugin install

For use in other repos, install via DDx:

```bash
ddx install helix
```

This creates:
- `~/.ddx/plugins/helix` — plugin files
- Skills into `~/.agents/skills` and `~/.claude/skills`

### Development install

For working on HELIX itself, use `--local` to create symlinks instead of
copies:

```bash
git clone https://github.com/DocumentDrivenDX/helix.git
cd helix
ddx install helix --local . --force
```

This symlinks the plugin and skills so edits to your checkout are immediately
reflected. Use DDx installation commands to repair stale plugin or skill links.

Key paths:
- canonical project skill path: `.agents/skills`, `.claude/skills` (symlinks to `skills/`)
- plugin symlink: `~/.ddx/plugins/helix`
- user skill paths: `~/.agents/skills`, `~/.claude/skills`

Useful commands:

```bash
ddx bead create "Title" --type task --labels helix,activity:build
ddx bead ready --json            # machine-readable ready queue
ddx bead ready --json --execution # machine-readable execution-safe queue
ddx bead status                  # tracker health summary
```

Runtime operations such as `ddx work` and `ddx bead execute <id>` are
provided by DDx, not this repository. Operator-facing methodology routing
runs through the `/helix <mode>` skill modes.

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

If you change any of the following, run the deterministic skills validation
(`bash tests/validate-skills.sh`):

- `workflows/actions/check.md`
- `workflows/actions/implementation.md`
- `workflows/actions/reconcile-alignment.md`
- `workflows/EXECUTION.md`
- other docs that materially change the HELIX execution contract

If you change story/project state detection rules or examples, also run the
state-rule validator:

- `workflows/state-rules.yml`
- `workflows/state-machine.yaml`
- `tests/validate-state-rules.sh`
- docs that materially change the HELIX state detection contract

If you change published skill packaging or metadata, also run the skill package
validator:

- `skills/*/SKILL.md`
- `.agents/skills`
- docs that change the HELIX skill packaging contract

If you change context-digest assembly or validation behavior, also run the
context-digest validator:

- `scripts/refresh_context_digests.py`
- `scripts/validate_context_digests.py`
- `workflows/references/context-digest.md`
- `workflows/actions/input.md`
- `workflows/actions/fresh-eyes-review.md`
- `workflows/actions/reconcile-alignment.md`
- docs that materially change the FEAT-006 context-digest propagation contract

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

If you change docs that redefine how portable skills and the HELIX workflow
contract are presented publicly, run both harnesses.

Required checks:

```bash
bash tests/validate-state-rules.sh
bash tests/validate-context-digests.sh
bash tests/validate-demo-fixtures.sh
bash tests/validate-pages-demo-recording.sh
bash tests/validate-skills.sh
git diff --check
```

The skills checks are intentionally deterministic:

- they assert HELIX ships no checkout CLI wrapper (the runtime owns execution)
- they validate skill packaging, metadata, and `workflows/` reference resolution
- they avoid live Codex or Claude calls when validating checkout behavior

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

1. `/helix design [scope]` — create comprehensive design document
2. `/helix polish [scope]` — **decompose the plan into implementable beads**, then refine
3. `ddx work` — execute the implementation loop

**Step 2 is mandatory.** Without polish, agents encounter undecomposed epics
during build and attempt ad-hoc decomposition, producing poor breakdowns.
`/helix check` enforces this by recommending `POLISH` when plans exist
without corresponding beads.

## Metric-Driven Optimization

For performance tuning, bundle size reduction, or other measurable optimization:

1. Create a `activity:iterate` issue with the optimization goal
2. `/helix experiment [issue-id|goal]` — runs one experiment iteration
3. The HELIX skill loops the experiment action autonomously
4. All existing tests must pass after every iteration — tests are the spec
5. Prefer simpler solutions; do not add complexity for marginal gains
6. At session close, the experiment branch is squash-merged and performance
   ratchet floors are updated if thresholds are met

Experiments are operator-invoked. `/helix check` does not auto-dispatch them.

## Issue Tracking with ddx bead

**IMPORTANT**: This project uses the **built-in HELIX tracker** for ALL issue tracking. Do NOT use markdown TODOs, task lists, or external trackers.

### Quick Start

**Check for ready work:**

```bash
ddx bead ready --json
ddx bead ready --json --execution
```

**Create new issues:**

```bash
ddx bead create "Issue title" --type task --description "Detailed context" --priority 1
ddx bead create "Issue title" --labels helix,activity:build --spec-id TP-036
```

**Claim and update:**

```bash
ddx bead update <id> --claim
ddx bead update <id> --priority 1
```

**Complete work:**

```bash
ddx bead close <id>
```

### Issue Types

- `bug` - Something broken
- `feature` - New functionality
- `task` - Work item (tests, docs, refactoring)
- `epic` - Large feature with subtasks
- `chore` - Maintenance (dependencies, tooling)

### Priorities

- `0` - Critical (security, data loss, broken builds)
- `1` - High (major features, important bugs)
- `2` - Medium (default, nice-to-have)
- `3` - Low (polish, optimization)
- `4` - Backlog (future ideas)

### Workflow for AI Agents

1. **Check ready work**: `ddx bead ready` shows unblocked issues
2. **Claim your task**: `ddx bead update <id> --claim`
3. **Work on it**: Implement, test, document
4. **Discover new work?** Create linked issue and add dependency
5. **Complete**: `ddx bead close <id>`

### Important Rules

- Use `ddx bead` for ALL task tracking
- Use `--json` flag for programmatic use
- Check `ddx bead ready` before asking "what should I work on?"
- Do NOT create markdown TODO lists
- Do NOT use external issue trackers
- Do NOT duplicate tracking systems

## Landing the Plane (Session Completion)

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO GIT REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds

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
