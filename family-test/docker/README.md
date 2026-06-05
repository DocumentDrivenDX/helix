# family-test Docker harness

Reproducible container for Bucket A (skill activation) and Bucket C
(frontmatter round-trip) probes. Pinned `claude` CLI, no preinstalled
plugins, non-root user matching host UID:GID so mounted volumes write
back cleanly.

## Files

| File                  | Purpose |
|-----------------------|---------|
| `Dockerfile.claude`   | Image with claude CLI + jq + python3, non-root `probe` user. |
| `run-probe.sh`        | Mounts fixture + plugins, runs `claude -p --output-format stream-json`, writes evidence file. |
| `assertions.py`       | Stdlib-only stream-json parser + assertion helpers. |
| `smoke-test.sh`       | Self-test for the harness itself (NOT a skill-activation test). |

## Build

```sh
docker build \
    --build-arg HOST_UID=$(id -u) \
    --build-arg HOST_GID=$(id -g) \
    -t family-test-claude:latest \
    -f family-test/docker/Dockerfile.claude \
    family-test/docker/
```

Optional build args:

- `CLAUDE_VERSION` (default `2.1.163`)
- `CLAUDE_INSTALL_URL` (default `https://claude.ai/install.sh`)

## Authentication

The harness accepts either path:

1. **Env var (recommended for CI):**
   ```sh
   export ANTHROPIC_API_KEY=sk-ant-...
   ```
   `run-probe.sh` forwards this into the container.

2. **Mounted credentials (recommended for local dev with an authed CLI):**
   ```sh
   # No env var needed — run-probe.sh auto-detects this file.
   ls ~/.claude/.credentials.json
   ```
   The file is mounted read-only at `/home/probe/.claude/.credentials.json`.

If neither is available, `run-probe.sh` prints a WARN and lets `claude -p`
fail with the actual auth error in the evidence stderr file.

## Smoke test

```sh
bash family-test/docker/smoke-test.sh
```

Sends `"What is 2+2?"` into the clean consumer fixture with both family-test
plugins installed. Asserts the container can run `claude -p` end-to-end and
that the stream-json is parsable. This proves the **harness** works — it
does NOT prove skill activation. Bucket A does that.

## Running a real probe

```sh
bash family-test/docker/run-probe.sh \
    family-test/consumer/clean \
    family-test/library,family-test/methodology-product \
    path/to/prompt.txt \
    path/to/evidence.jsonl
```

Then inspect the evidence with the assertion helpers:

```sh
python3 family-test/docker/assertions.py evidence.jsonl skill-activated helix
python3 family-test/docker/assertions.py evidence.jsonl no-writes
python3 family-test/docker/assertions.py evidence.jsonl first-read '\.helix\.yml$'
python3 family-test/docker/assertions.py evidence.jsonl prose
python3 family-test/docker/assertions.py evidence.jsonl json
```

Or import from a Python probe runner:

```python
from assertions import (
    load_events, assert_skill_activated, assert_no_writes,
    assert_first_relevant_read, extract_prose, parse_json_response,
)
events = load_events("evidence.jsonl")
assert assert_skill_activated(events, "helix")
```

## Plugin layout

`run-probe.sh` symlinks each comma-separated path in the plugins-spec into
`~/.claude/plugins/<basename>` inside the container. Each path must contain
`.claude-plugin/plugin.json`. The container starts with NO plugins — every
run begins from a clean state.

## Temp file location

Bind-mounted paths (fixture, prompt, plugins, evidence) must live under a
location the docker daemon can see. On macOS hosts running an OrbStack
Linux VM, the Linux-side `/tmp` and `$HOME/.cache` are NOT visible to the
macOS docker daemon — only paths under `/Users/...` work. The smoke test
and probes use `family-test/.tmp/` (gitignored) for this reason.

## Known limitations

- The `claude` CLI is installed from `claude.ai/install.sh`; if Anthropic
  rotates that URL, override via `--build-arg CLAUDE_INSTALL_URL=...`.
- Skill activation is non-deterministic. Probes should retry or use majority-
  vote across multiple runs (see validation plan §Bucket A).
