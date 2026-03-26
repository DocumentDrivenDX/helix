# Agent Instructions

This is the HELIX repository — the canonical source for the HELIX workflow
methodology, action prompts, skills, CLI, and execution contract.

This project uses the **built-in HELIX tracker** for issue tracking.
Issues are stored in `.helix/issues.jsonl` — one JSON object per line.

The workflow definitions live under `workflows/`. Treat those docs as
the source of truth for the workflow contract.

## Quick Reference

```bash
helix tracker ready           # Find available work
helix tracker show <id>       # View issue details
helix tracker update <id> --claim  # Claim work
helix tracker close <id>      # Complete work
helix tracker status          # Check tracker health
bash tests/helix-cli.sh       # Deterministic HELIX wrapper tests
helix run                     # Run bounded HELIX execution loop
helix check                   # Decide next HELIX action
helix plan                    # Create design document through iterative refinement
helix polish                  # Refine issues before implementation
helix next                    # Show recommended next issue
helix review                  # Fresh-eyes review of recent work
helix spawn                   # Launch multi-agent swarm (requires ntm)
```

## HELIX Workflow Notes

When working on HELIX itself in this repo:

- top-level overview: `workflows/README.md`
- operator loop and automation: `workflows/EXECUTION.md`
- tracker conventions: `workflows/TRACKER.md`
- command summary: `workflows/REFERENCE.md`

Key rules:

- Use the built-in tracker (`helix tracker`); do not use external issue trackers.
- For ready-work detection, use `helix tracker ready`, not manual JSONL parsing.
- Keep `implementation` single-shot and bounded to one issue per run.
- Use `check` when the ready queue drains to decide whether to implement,
  align, backfill, wait, ask for guidance, or stop.
- Keep alignment and backfill as separate cross-phase actions:
  - `workflows/actions/reconcile-alignment.md`
  - `workflows/actions/backfill-helix-docs.md`
- Quality ratchets are documented in `workflows/ratchets.md`. Ratchet
  enforcement scripts and floor fixtures belong in adopting projects, not in
  this repo. This repo defines the pattern and the integration points in
  action prompts and enforcers.

## HELIX Skills

Installed agent skills mirror CLI commands exactly:

- `helix-run` <-> `helix run`
- `helix-implement` <-> `helix implement`
- `helix-check` <-> `helix check`
- `helix-align` <-> `helix align`
- `helix-backfill` <-> `helix backfill`
- `helix-plan` <-> `helix plan`
- `helix-polish` <-> `helix polish`
- `helix-next` <-> `helix next`
- `helix-review` <-> `helix review`
- `helix-spawn` <-> `helix spawn`
- `helix-experiment` <-> `helix experiment`

Rule: public skill names are `helix-<command>`, and `<command>` must match the
CLI subcommand exactly.

## HELIX CLI

This repo now ships a small HELIX wrapper CLI:

- script source: `scripts/helix`
- tracker library: `scripts/tracker.sh`
- local launcher install: `scripts/install-local-skills.sh`
- installed command: `~/.local/bin/helix`

Useful commands:

```bash
helix plan auth                       # create design document
helix polish                          # refine issues before implementation
helix run --review-every 5
helix implement
helix check repo
helix align auth
helix backfill repo
helix next                            # show recommended next issue
helix review                          # fresh-eyes review of last commit
helix spawn --count 3                 # launch multi-agent swarm
helix experiment hx-abc123            # one experiment iteration
helix experiment --close              # squash-merge and close session
helix tracker create "Title" --type task --labels helix,phase:build
helix tracker ready --json            # machine-readable ready queue
helix tracker status                  # tracker health summary
```

`helix run` is the preferred operator loop. It:

- loops only while true ready HELIX execution work exists
- executes one bounded implementation pass at a time
- runs `check` when the queue drains
- can run periodic alignment reviews

Do not replace this with an unconditional `while true` loop.

## Testing Requirements for HELIX Changes

If you change any of the following, run the HELIX wrapper harness:

- `scripts/helix`
- `scripts/tracker.sh`
- `scripts/install-local-skills.sh`
- `workflows/actions/check.md`
- `workflows/actions/implementation.md`
- `workflows/actions/reconcile-alignment.md`
- `workflows/EXECUTION.md`
- other docs that materially change the HELIX execution contract

Required checks:

```bash
bash tests/helix-cli.sh
git diff --check
```

The wrapper tests are intentionally deterministic:

- they use temporary git workspaces
- they stub `codex` and `claude`
- they verify queue draining, periodic alignment, auto-alignment, dry-run
  output, tracker operations, and launcher installation behavior

Prefer these deterministic tests over live Codex or Claude calls when
validating wrapper behavior.

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

1. `helix plan [scope]` — create comprehensive design document
2. `helix polish [scope]` — refine issues against the plan
3. `helix run` — execute the implementation loop

## Swarm Execution (optional)

If `ntm` is installed, `helix spawn [--count N]` launches multiple agents in
tmux sessions with staggered starts. Agents are fungible — any agent picks any
issue. Issue claiming via `helix tracker update --claim` provides advisory locking.

## Metric-Driven Optimization

For performance tuning, bundle size reduction, or other measurable optimization:

1. Create a `phase:iterate` issue with the optimization goal
2. `helix experiment [issue-id|goal]` — runs one experiment iteration
3. The `helix-experiment` skill loops the action autonomously
4. All existing tests must pass after every iteration — tests are the spec
5. Prefer simpler solutions; do not add complexity for marginal gains
6. At session close, the experiment branch is squash-merged and performance
   ratchet floors are updated if thresholds are met

Experiments are operator-invoked. `helix check` does not auto-dispatch them.

## Issue Tracking with helix tracker

**IMPORTANT**: This project uses the **built-in HELIX tracker** for ALL issue tracking. Do NOT use markdown TODOs, task lists, or external trackers.

### Quick Start

**Check for ready work:**

```bash
helix tracker ready --json
```

**Create new issues:**

```bash
helix tracker create "Issue title" --type task --description "Detailed context" --priority 1
helix tracker create "Issue title" --labels helix,phase:build --spec-id TP-036
```

**Claim and update:**

```bash
helix tracker update <id> --claim
helix tracker update <id> --priority 1
```

**Complete work:**

```bash
helix tracker close <id>
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

1. **Check ready work**: `helix tracker ready` shows unblocked issues
2. **Claim your task**: `helix tracker update <id> --claim`
3. **Work on it**: Implement, test, document
4. **Discover new work?** Create linked issue and add dependency
5. **Complete**: `helix tracker close <id>`

### Important Rules

- Use `helix tracker` for ALL task tracking
- Use `--json` flag for programmatic use
- Check `helix tracker ready` before asking "what should I work on?"
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
