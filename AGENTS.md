# Agent Instructions

This is the HELIX repository — the canonical source for the HELIX workflow
methodology, action prompts, skills, CLI, and execution contract.

This project uses the **built-in HELIX tracker** for issue tracking.
Issues are stored in `.ddx/beads.jsonl` — one JSON object per line.

The workflow definitions live under `workflows/`. Treat those docs as
the source of truth for the workflow contract.

## Quick Reference

```bash
helix tracker ready           # Find available tracked work
helix tracker ready --execution # Find execution-safe work for helix run
helix tracker show <id>       # View issue details
helix tracker update <id> --claim  # Claim work
helix tracker close <id>      # Complete work
helix tracker status          # Check tracker health
bash tests/helix-cli.sh       # Deterministic HELIX wrapper tests
bash tests/validate-skills.sh # Deterministic HELIX skill package validation
just test                     # Run all tests (CLI + skills)
helix run                     # Run bounded HELIX execution loop
helix frame [scope]           # Create product vision, PRD, feature specs
helix design [scope]          # Create design document through iterative refinement
helix build [selector]        # Run one bounded build pass
helix check [scope]           # Decide next HELIX action
helix review [scope]          # Fresh-eyes review of recent work
helix align [scope]           # Top-down reconciliation audit
helix evolve "requirement"    # Thread a requirement through the artifact stack
helix triage "Title"          # Create well-structured tracker issues
helix commit [issue-id]       # Commit with HELIX format + build gate
helix polish [scope]          # Refine issues before implementation
helix next                    # Show recommended next issue
```

## Operational Guide

### Starting a background run

```bash
nohup helix run > /tmp/helix-run.stdout.log 2> /tmp/helix-run.stderr.log &
echo $! > /tmp/helix-run.pid
```

Defaults are reasonable: cross-model review (codex builds, claude reviews),
review threshold 100 lines, alignment every 15 cycles, 45-min timeout.

### Monitoring a run

```bash
# Is it running?
kill -0 $(cat /tmp/helix-run.pid) 2>/dev/null && echo "RUNNING" || echo "STOPPED"

# Progress
grep "^helix:" /tmp/helix-run.stderr.log | grep -E "cycle|complete|tokens" | tail -10

# Why did it stop?
grep "═══\|stopping\|BLOCKER" /tmp/helix-run.stderr.log | tail -5
```

### Consolidating related issues

Before a run, group related issues into epics. The run loop's epic focus
mode will stay on one epic and batch its children:

```bash
# Create epic
epic=$(helix tracker create "Epic: ..." --type epic ...)
# Wire children
helix tracker update hx-child1 --parent $epic
helix tracker update hx-child2 --parent $epic
# Supersede duplicates
helix tracker update hx-old --superseded-by hx-new
helix tracker close hx-old
```

### Known operational gotchas

- **Codex sandbox bypasses pre-commit hooks** — the run loop has a build
  gate that catches broken code, but the agent should also run
  `lefthook run pre-commit` before pushing (Phase 8 in implementation.md).
- **Skill YAML front matter** — quote values containing colons or pipes,
  otherwise codex's skill loader silently rejects them.
- **Stale in-progress claims** — after a crashed run, unclaim manually:
  `helix tracker list --status in_progress --json | jq -r '.[].id'`
  then `helix tracker update <id> --status open --assignee ""`

## HELIX Workflow Notes

When working on HELIX itself in this repo:

- top-level overview: `workflows/README.md`
- operator loop and automation: `workflows/EXECUTION.md`
- tracker conventions: `helix tracker --help` (DDx FEAT-004)
- command summary: `workflows/REFERENCE.md`

Key rules:

- Use the built-in tracker (`helix tracker`); do not use external issue trackers.
- For general ready-work detection, use `helix tracker ready`, not manual JSONL parsing.
- For execution selection or `helix run` reasoning, use `helix tracker ready --execution`.
- Keep `implementation` single-shot and bounded to one issue per run.
- Use `check` when the ready queue drains to decide whether to build,
  design, polish, align, backfill, wait, ask for guidance, or stop.
- Keep alignment and backfill as separate cross-phase actions:
  - `workflows/actions/reconcile-alignment.md`
  - `workflows/actions/backfill-helix-docs.md`
- Quality ratchets are documented in `workflows/ratchets.md`. Ratchet
  enforcement scripts and floor fixtures belong in adopting projects, not in
  this repo. This repo defines the pattern and the integration points in
  action prompts and enforcers.

Think about HELIX in two layers:

- portable skills packaged from `.agents/skills`
- the stricter HELIX workflow and CLI contract defined under `workflows/` and
  executed through `helix`

## HELIX Skills

Installed agent skills mirror CLI commands exactly:

- `helix-run` <-> `helix run`
- `helix-build` <-> `helix build`
- `helix-check` <-> `helix check`
- `helix-align` <-> `helix align`
- `helix-backfill` <-> `helix backfill`
- `helix-design` <-> `helix design`
- `helix-polish` <-> `helix polish`
- `helix-evolve` <-> `helix evolve`
- `helix-triage` <-> `helix triage`
- `helix-next` <-> `helix next`
- `helix-review` <-> `helix review`
- `helix-experiment` <-> `helix experiment`

Rule: public skill names are `helix-<command>`, and `<command>` must match the
CLI subcommand exactly.
Published `SKILL.md` files must declare `name` and `description`; add
`argument-hint` when the mirrored CLI command accepts a trailing positional
argument such as a scope, selector, issue ID, or goal.

## HELIX CLI

This repo now ships a small HELIX wrapper CLI:

- canonical project skill path: `.agents/skills`
- script source: `scripts/helix`
- tracker library: `scripts/tracker.sh`
- local launcher install: `scripts/install-local-skills.sh`
- installed command: `~/.local/bin/helix`
- canonical user skill path: `~/.agents/skills`
- Claude compatibility path: `~/.claude/skills`

Useful commands:

```bash
helix design auth                     # create design document
helix polish                          # refine issues before implementation
helix run --review-every 5
helix build
helix check repo
helix align auth
helix backfill repo
helix next                            # show recommended next issue
helix review                          # fresh-eyes review of last commit
helix experiment hx-abc123            # one experiment iteration
helix experiment --close              # squash-merge and close session
helix tracker create "Title" --type task --labels helix,phase:build
helix tracker ready --json            # machine-readable ready queue
helix tracker ready --json --execution # machine-readable execution-safe queue
helix tracker status                  # tracker health summary
```

`helix run` is the preferred operator loop. It:

- loops only while true ready HELIX execution work exists
- may route to `helix design` or `helix polish` when supervisory state requires
  bounded planning or issue refinement before implementation resumes
- executes one bounded implementation pass at a time
- may run `helix review` after a successful implementation pass when review
  automation is enabled
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

If you change published skill packaging or metadata, also run the skill package
validator:

- `skills/*/SKILL.md`
- `.agents/skills`
- docs that change the HELIX skill packaging contract

If you change docs that redefine how portable skills and the HELIX workflow
contract are presented publicly, run both harnesses.

Required checks:

```bash
bash tests/helix-cli.sh
bash tests/validate-skills.sh
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

1. `helix design [scope]` — create comprehensive design document
2. `helix polish [scope]` — refine issues against the plan
3. `helix run` — execute the implementation loop

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
helix tracker ready --json --execution
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
