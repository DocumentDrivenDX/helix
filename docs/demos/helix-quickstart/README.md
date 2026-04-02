# HELIX Quickstart Demo

A scripted demonstration of the full HELIX lifecycle: install → frame → design → build → review.

Builds a tiny Node.js temperature converter from scratch, driven entirely by HELIX artifacts and the tracker.

## Prerequisites

- Docker
- Claude Code credentials (`~/.claude/`)

## Run

```bash
# From the helix repo root:

# Build the demo container
docker build -t helix-demo docs/demos/helix-quickstart/

# Run with recording (Docker)
docker run --rm \
  -v ~/.claude.json:/root/.claude.json:ro \
  -v ~/.claude:/root/.claude \
  -v $(pwd):/helix:ro \
  -v $(pwd)/docs/demos/helix-quickstart/recordings:/recordings \
  helix-demo

# Run without recording (Docker)
docker run --rm \
  -v ~/.claude.json:/root/.claude.json:ro \
  -v ~/.claude:/root/.claude \
  -v $(pwd):/helix:ro \
  -e HELIX_DEMO_RECORDING=1 \
  helix-demo

# Run locally (no Docker) — fastest, uses your existing claude auth
cd /tmp && bash path/to/helix/docs/demos/helix-quickstart/demo.sh
```

**Note:** Docker runs need `~/.claude.json` (auth token) AND `~/.claude/`
(writable, for session state). The local run uses your existing setup.

## What It Does

| Act | Phase | What Happens |
|-----|-------|-------------|
| 1 | Install | Install HELIX skills and CLI from the repo |
| 2 | Setup | Initialize git repo, tracker, and AGENTS.md |
| 3 | Frame | Agent creates product vision, PRD, and feature spec |
| 4 | Design | Agent creates technical design, then tracker issues |
| 5 | Build | Red: write failing tests. Green: implement to pass. |
| 6 | Verify | Run tests, check acceptance criteria |
| 7 | Review | Agent reviews all work for gaps |

## Recordings

Asciinema recordings are saved to `recordings/`. Play them:

```bash
asciinema play recordings/helix-quickstart-*.cast
```

## Run Locally (no Docker)

```bash
cd /tmp
bash /path/to/helix/docs/demos/helix-quickstart/demo.sh
```

Requires: git, jq, node, npm, claude CLI, helix CLI.
