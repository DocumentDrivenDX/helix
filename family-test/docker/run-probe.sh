#!/usr/bin/env bash
# Run a skill-activation probe inside the Docker harness.
#
# Usage:
#   run-probe.sh <fixture-dir> <plugins-spec> <prompt-file> <evidence-file>
#
# Arguments:
#   fixture-dir   absolute path on host to mount at /workspace
#   plugins-spec  comma-separated list of host paths to symlink into
#                 ~/.claude/plugins/<basename> inside the container. Each
#                 path must be a directory containing .claude-plugin/plugin.json.
#                 Use "" to install no plugins.
#   prompt-file   absolute path to a file containing the prompt to send via
#                 `claude -p`. Read by the container, NOT executed.
#   evidence-file absolute path on host where stream-json output is written.
#                 Parent dir must exist and be writable by the host user.
#
# Authentication: the script forwards either:
#   - ANTHROPIC_API_KEY (env)        OR
#   - ~/.claude/.credentials.json    (mounted read-only)
# At least one must be available; otherwise the probe will fail at claude -p.
#
# Exit codes:
#   0  claude exited cleanly; evidence-file contains stream-json
#   1  bad arguments
#   2  docker run failed (image missing, mount failure)
#   3  claude exited non-zero (probe assertions should still inspect evidence)
#
# This script does NOT make pass/fail judgments about probe content.
# Use assertions.py for that.

set -euo pipefail

if [[ $# -lt 4 || $# -gt 5 ]]; then
    echo "usage: $0 <fixture-dir> <plugins-spec> <prompt-file> <evidence-file> [<cwd-rel>]" >&2
    exit 1
fi

FIXTURE_DIR="$1"
PLUGINS_SPEC="$2"
PROMPT_FILE="$3"
EVIDENCE_FILE="$4"
CWD_REL="${5:-}"    # optional subdirectory under fixture to use as cwd

if [[ ! -d "$FIXTURE_DIR" ]]; then
    echo "FAIL: fixture-dir does not exist: $FIXTURE_DIR" >&2
    exit 1
fi
if [[ ! -f "$PROMPT_FILE" ]]; then
    echo "FAIL: prompt-file does not exist: $PROMPT_FILE" >&2
    exit 1
fi

mkdir -p "$(dirname "$EVIDENCE_FILE")"
: > "$EVIDENCE_FILE"

IMAGE="${PROBE_IMAGE:-family-test-claude:latest}"

# Build auth args.
# Credential file selection: prefer CLAUDE_CREDENTIALS_FILE if set
# (must be a docker-bind-visible path), else fall back to common
# locations. On macOS+OrbStack, /home/erik/... is NOT bind-mountable;
# /Users/erik/... is. Probe both.
AUTH_ARGS=()
if [[ -n "${ANTHROPIC_API_KEY:-}" ]]; then
    AUTH_ARGS+=(-e "ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY")
fi

CRED_FILE="${CLAUDE_CREDENTIALS_FILE:-}"
if [[ -z "$CRED_FILE" ]]; then
    for candidate in \
        "/Users/$(id -un)/.claude/.credentials.json" \
        "$HOME/.claude/.credentials.json"
    do
        if [[ -f "$candidate" ]]; then
            CRED_FILE="$candidate"
            break
        fi
    done
fi
if [[ -n "$CRED_FILE" && -f "$CRED_FILE" ]]; then
    AUTH_ARGS+=(-v "$CRED_FILE:/home/probe/.claude/.credentials.json:ro")
fi

if [[ ${#AUTH_ARGS[@]} -eq 0 ]]; then
    echo "WARN: no ANTHROPIC_API_KEY and no readable .credentials.json" >&2
    echo "WARN: claude -p will likely fail at auth step" >&2
fi

# Plugin mount args. Each entry in PLUGINS_SPEC is mounted into the
# container and loaded via `claude --plugin-dir` (the supported install
# mechanism — symlinking under ~/.claude/plugins/ does NOT actually
# register plugins; `installed_plugins.json` is the registry).
PLUGIN_MOUNTS=()
PLUGIN_DIRS_ARGS=""
if [[ -n "$PLUGINS_SPEC" ]]; then
    IFS=',' read -r -a PLUGIN_PATHS <<<"$PLUGINS_SPEC"
    for p in "${PLUGIN_PATHS[@]}"; do
        if [[ ! -d "$p" ]]; then
            echo "FAIL: plugin path is not a directory: $p" >&2
            exit 1
        fi
        if [[ ! -f "$p/.claude-plugin/plugin.json" ]]; then
            echo "FAIL: plugin path missing .claude-plugin/plugin.json: $p" >&2
            exit 1
        fi
        name="$(basename "$p")"
        PLUGIN_MOUNTS+=(-v "$p:/plugins-src/$name:ro")
        PLUGIN_DIRS_ARGS="$PLUGIN_DIRS_ARGS --plugin-dir /plugins-src/$name"
    done
fi

# Build the in-container bootstrap. Reads prompt from /probe/prompt, writes
# stream-json to stdout, captured by docker -> EVIDENCE_FILE on host.
BOOTSTRAP='
set -euo pipefail
exec claude -p '"$PLUGIN_DIRS_ARGS"' --output-format stream-json --verbose < /probe/prompt
'

# Run claude. We need stdin from prompt file AND capture stdout to evidence.
# Mount prompt as /probe/prompt (read-only). Mount fixture as /workspace.
set +e
WORKDIR="/workspace"
if [[ -n "$CWD_REL" ]]; then
    WORKDIR="/workspace/$CWD_REL"
fi

docker run --rm \
    "${AUTH_ARGS[@]}" \
    "${PLUGIN_MOUNTS[@]}" \
    -v "$FIXTURE_DIR:/workspace" \
    -v "$PROMPT_FILE:/probe/prompt:ro" \
    -w "$WORKDIR" \
    "$IMAGE" \
    bash -c "$BOOTSTRAP" \
    >"$EVIDENCE_FILE" 2>"$EVIDENCE_FILE.stderr"
RC=$?
set -e

if [[ $RC -eq 125 || $RC -eq 126 || $RC -eq 127 ]]; then
    echo "FAIL: docker run failed (rc=$RC). stderr:" >&2
    cat "$EVIDENCE_FILE.stderr" >&2 || true
    exit 2
fi

if [[ $RC -ne 0 ]]; then
    echo "WARN: claude exited rc=$RC; evidence still written to $EVIDENCE_FILE" >&2
    exit 3
fi

echo "OK: evidence written to $EVIDENCE_FILE"
exit 0
