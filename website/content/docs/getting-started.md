---
title: Getting Started
weight: 1
prev: /docs
next: /docs/workflow
---

Get HELIX installed and running your first supervised build session.

## Install

{{< tabs >}}

{{< tab name="Plugin (recommended)" >}}
Load HELIX as a Claude Code plugin — no installation step required:

```bash
# From any project directory:
claude --plugin-dir /path/to/helix

# Or add to your project's .claude/settings.json:
# { "plugins": ["/path/to/helix"] }
```

All skills, the CLI, and shared resources are available immediately.
{{< /tab >}}

{{< tab name="Symlink installer" >}}
```bash
git clone https://github.com/easel/helix
cd helix
scripts/install-local-skills.sh
```

This creates skill symlinks in `~/.claude/skills/` and installs the `helix`
CLI to `~/.local/bin/helix`.
{{< /tab >}}

{{< /tabs >}}

**Requirements:** Bash, jq, git, and either `claude` or `codex` CLI.

## Initialize a Project

```bash
cd your-project
ddx init                    # Set up DDx document library
helix frame                 # Create vision, PRD, feature specs
```

HELIX uses DDx for document management and issue tracking. `helix frame`
starts the planning process by creating the governing artifacts that drive
everything downstream.

## Run the Autopilot

```bash
helix run
```

`helix run` is HELIX's supervisory autopilot. It reads the tracker, selects
the highest-leverage next action, executes it, and repeats until human input
is needed or no work remains.

Key flags:

```bash
helix run --agent claude        # Use Claude as the agent
helix run --summary             # Concise output for background monitoring
helix run --max-cycles 10       # Stop after 10 completed build cycles
helix run --review-every 5      # Periodic alignment review
```

## Run Individual Commands

You can also drive HELIX interactively:

```bash
helix design auth               # Design the auth system
helix build                     # One bounded build pass
helix review                    # Fresh-eyes review of recent work
helix check                     # What should happen next?
helix align                     # Top-down reconciliation audit
helix evolve "add OAuth"        # Thread a requirement through the stack
helix triage "Fix login bug"    # Create a well-structured tracker issue
helix status                    # Lifecycle snapshot
```

## Monitor a Background Run

```bash
# Launch in the background
helix run --agent claude --summary --max-cycles 10 &

# Check progress
helix status

# Read failure details
cat .helix-logs/helix-*.log | tail -50
```

## Next Steps

- Read about the [HELIX workflow](../workflow) and how phases work
- See the full [CLI reference](../cli)
- Watch the [demo](../demos) of a complete HELIX lifecycle
