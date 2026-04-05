# Concern: Demo Reels (Asciinema)

## Category
demo

## Areas
all

## Components

- **Recording tool**: Asciinema (`asciinema rec`) — terminal session recording
- **Playback**: asciinema-player (JavaScript, embedded in microsite)
- **Static export**: GIF via `agg` (asciinema gif generator) for README/social
- **Reproducible capture**: Docker container with pinned dependencies
- **Demo scripts**: Shell scripts that drive the recorded session

## Constraints

- Recordings are `.cast` files (asciinema v2 format, JSON lines)
- Cast files live in `website/static/demos/` for microsite embedding and
  in `docs/demos/<name>/recordings/` as source-of-truth archives
- Demo scripts live in `docs/demos/<name>/demo.sh` with a companion
  `Dockerfile` and `README.md`
- GIF exports go alongside cast files for use in README and social previews
- Recordings must be reproducible — re-running the demo script in the Docker
  container should produce equivalent output
- Do not record interactive sessions manually — always use a scripted demo
- Terminal dimensions: 100 columns x 30 rows (standard for readable recordings)
- Playback speed: 1.5x default in the asciinema-player embed

## Demo Script Requirements

Every demo must include these files in `docs/demos/<name>/`:

| File | Purpose |
|------|---------|
| `demo.sh` | Shell script that drives the demo end-to-end |
| `Dockerfile` | Reproducible environment for recording |
| `README.md` | What it demonstrates, prerequisites, how to run |
| `recordings/` | Directory for `.cast` and `.gif` output |

### demo.sh conventions

- `#!/usr/bin/env bash` with `set -euo pipefail`
- Define helper functions: `narrate()` for section titles, `run()` for
  visible command execution, `show_file()` for file previews
- Use `sleep` between sections for pacing in recordings
- Print visible section headers (`narrate "ACT N: Title"`) so the viewer
  can follow the narrative structure
- Support both Docker and local execution — auto-detect environment
- Include retry logic for network-dependent commands (API calls, installs)
- Exit non-zero on failure — broken demos must not produce recordings

### Narrative structure

A demo reel tells a story. Structure it as acts:

1. **Setup** — Install tools, initialize project, show starting state
2. **Core workflow** — Demonstrate the main capability step by step
3. **Verification** — Show that the result is correct (tests pass, output matches)
4. **Summary** — Recap what happened, show final state

Each act should be self-explanatory to a viewer watching the recording at
1.5x speed without audio. Use section headers and visible command output
as narration.

### What to include in a demo

- The tool's primary workflow from start to finish
- Real commands that a user would actually type
- Visible output that proves the tool works
- File previews that show generated artifacts
- A verification step that confirms correctness
- A final summary showing the end state

### What NOT to include

- Long build times or dependency installation (fast-forward or pre-install)
- Error recovery (unless error handling IS the demo topic)
- Configuration that distracts from the main workflow
- Pauses longer than 3 seconds without visible activity

## Dockerfile Pattern

```dockerfile
FROM ubuntu:24.04

RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates jq <project-deps> \
    && rm -rf /var/lib/apt/lists/*

# Install asciinema
RUN pipx install asciinema
ENV PATH="/root/.local/bin:$PATH"

# Install project tools (including the agent CLI)
RUN npm install -g @anthropic-ai/claude-code

# Git identity for commits inside the container
RUN git config --global user.name "Demo" \
    && git config --global user.email "demo@project.dev" \
    && git config --global init.defaultBranch main

ENV SHELL=/bin/bash TERM=xterm-256color

WORKDIR /workspace

COPY demo.sh /usr/local/bin/demo.sh
RUN chmod +x /usr/local/bin/demo.sh

ENTRYPOINT ["/usr/local/bin/demo.sh"]
```

## Agent Credential Mounting

Demo containers that invoke AI agents (via `ddx agent run` or `claude -p`)
need the user's Claude CLI credentials mounted into the container. The Claude
CLI stores authentication in two locations:

| Host path | Container path | Mode | Purpose |
|-----------|---------------|------|---------|
| `~/.claude.json` | `/root/.claude.json` | `ro` | CLI config and session metadata |
| `~/.claude/` | `/root/.claude/` | `rw` | Auth tokens, session state, cache |

The `~/.claude/` mount must be **read-write** because the Claude CLI writes
session state during execution. The `~/.claude.json` config file can be
read-only.

Additional optional mounts:

| Host path | Container path | Mode | Purpose |
|-----------|---------------|------|---------|
| Project repo | `/helix` (or `/project`) | `ro` | Source repo for skill/workflow access |
| DDx binary | `/usr/local/bin/ddx` | `ro` | DDx CLI (if not installed in image) |
| Recordings dir | `/recordings` | `rw` | Asciinema output extraction |

### Complete `docker run` command

```bash
docker run --rm \
  -v ~/.claude.json:/root/.claude.json:ro \
  -v ~/.claude:/root/.claude \
  -v $(pwd):/helix:ro \
  -v $(pwd)/../ddx/ddx:/usr/local/bin/ddx:ro \
  -v $(pwd)/docs/demos/<name>/recordings:/recordings \
  <project>-demo
```

This pattern is fully autonomous — an agent or CI job can build and run the
container without interactive authentication. The user's existing Claude CLI
session is reused.

### Agent harness

Demo scripts should use `ddx agent run` as the harness rather than invoking
`claude -p` directly:

```bash
ddx agent run \
  --harness claude \
  --permissions unrestricted \
  --text "$prompt"
```

This routes through DDx's agent abstraction, which provides output capture,
token tracking, and session logging. The `--permissions unrestricted` flag
is required for demos that create files and run commands.

## Microsite Embedding

Use the `asciinema` Hugo shortcode (see `hugo-hextra` concern):

```markdown
{{</* asciinema src="demo-name" cols="100" rows="30" */>}}
```

The shortcode loads asciinema-player from CDN and plays `static/demos/<src>.cast`
with monokai theme, autoplay, and 1.5x speed.

Copy the `.cast` file to `website/static/demos/` after recording.

## Recording Workflow

1. Build the Docker image:
   ```bash
   docker build -t <project>-demo docs/demos/<name>/
   ```
2. Run with credential and recording mounts:
   ```bash
   docker run --rm \
     -v ~/.claude.json:/root/.claude.json:ro \
     -v ~/.claude:/root/.claude \
     -v $(pwd):/helix:ro \
     -v $(pwd)/../ddx/ddx:/usr/local/bin/ddx:ro \
     -v $(pwd)/docs/demos/<name>/recordings:/recordings \
     <project>-demo
   ```
3. Review the cast file: `asciinema play recordings/<file>.cast`
4. Generate GIF: `agg recordings/<file>.cast recordings/<file>.gif`
5. Copy cast to microsite: `cp recordings/<file>.cast website/static/demos/`
6. Embed in content with `asciinema` shortcode

Steps 1-2 are fully autonomous and can be run by an agent with access to
the user's home directory. Steps 3-6 are post-processing that can also
be automated.

## When to use

Any project that needs to demonstrate a CLI workflow, developer tool, or
terminal-based process. Demo reels are more effective than screenshots for
showing multi-step workflows and more maintainable than screen recordings
because they can be regenerated from scripts.

## ADR References
