#!/usr/bin/env bash
# Run a skill-activation probe inside the Docker harness.
#
# Usage:
#   run-probe.sh <fixture-dir> <plugins-spec> <prompt-file> <evidence-file> [<cwd-rel>]
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
# Model selection: set the HELIX_PROBE_MODEL env var to the claude model id
# (e.g. `claude-haiku-4-5`, `claude-sonnet-4-6`). Defaults to whatever the
# container's claude CLI picks. Routing-evals + Haiku-default policy lives in
# the runner (helix_bench.py), which sets this env var per invocation.
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

# Ensure the bench probe image exists. OrbStack (and some Docker configs)
# garbage-collect locally-built unused images after ~30 minutes idle, which
# breaks multi-row bench loops mid-flight. Rebuild on demand if the image
# is missing — ~1-2s overhead when cached, vs the 4-5 min per-probe wall
# time, so the cost is acceptable. The Dockerfile lives next to this
# script so the build is reproducible.
if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
    DOCKERFILE_DIR="$(dirname "$(realpath "${BASH_SOURCE[0]}")")"
    if [[ -f "$DOCKERFILE_DIR/Dockerfile.claude" ]]; then
        echo "INFO: $IMAGE missing locally — rebuilding from $DOCKERFILE_DIR/Dockerfile.claude" >&2
        if ! docker build -q -t "$IMAGE" -f "$DOCKERFILE_DIR/Dockerfile.claude" "$DOCKERFILE_DIR" >&2; then
            echo "FAIL: docker build of $IMAGE failed" >&2
            exit 2
        fi
    else
        echo "WARN: $IMAGE missing AND Dockerfile.claude not found at $DOCKERFILE_DIR" >&2
        # Proceed; docker run will surface the same error visibly.
    fi
fi

# Build auth args.
# Credential file selection: prefer CLAUDE_CREDENTIALS_FILE if set
# (must be a docker-bind-visible path), else fall back to common
# locations. On macOS+OrbStack, /home/erik/... is NOT bind-mountable;
# /Users/erik/... is. Probe both.
AUTH_ARGS=()
# Auth strategy (2026-06-05 finding):
# - ANTHROPIC_API_KEY env (Console API keys, sk-ant-api03-…) works as x-api-key
# - Long-lived OAuth token from `claude setup-token` (sk-ant-oat01-…) is sent
#   as Bearer by claude CLI ONLY when read from disk creds, NOT via the env
# - Disk creds: claude refuses if expiresAt < now (even with a long-lived token);
#   we synthesize a creds file with a far-future expiresAt at run time
TOKEN_FILE="${HELIX_PROBE_TOKEN_FILE:-/Users/erik/.cache/family-test-auth/token}"
HOST_CLAUDE_JSON="${HELIX_PROBE_HOST_CLAUDE_JSON:-/Users/erik/.cache/family-test-auth/host-claude.json}"
GEN_CREDS=""
if [[ -n "${ANTHROPIC_API_KEY:-}" ]]; then
    AUTH_ARGS+=(-e "ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY")
elif [[ -f "$TOKEN_FILE" ]]; then
    # Build a credentials.json with the long-lived token + far-future expiresAt.
    # Must live under /Users/* on OrbStack so the docker daemon can bind-mount it
    # (Linux-VM-side /tmp/ is invisible to the macOS-side daemon).
    GEN_DIR="/Users/erik/.cache/family-test-auth"
    mkdir -p "$GEN_DIR"
    GEN_CREDS="$GEN_DIR/probe-creds-$$-$RANDOM.json"
    chmod 600 "$GEN_CREDS" 2>/dev/null || true
    python3 - "$TOKEN_FILE" "$GEN_CREDS" <<'PY'
import json, sys, time
tok = open(sys.argv[1]).read().strip()
creds = {"claudeAiOauth": {
    "accessToken": tok,
    "refreshToken": "",
    "expiresAt": int((time.time() + 365*24*3600) * 1000),
    "scopes": ["user:file_upload","user:inference","user:mcp_servers","user:profile","user:sessions:claude_code"],
    "subscriptionType": "max",
    "rateLimitTier": "max-claude-2x",
}}
json.dump(creds, open(sys.argv[2], "w"))
PY
    AUTH_ARGS+=(-v "$GEN_CREDS:/home/probe/.claude/.credentials.json")
    if [[ -f "$HOST_CLAUDE_JSON" ]]; then
        AUTH_ARGS+=(-v "$HOST_CLAUDE_JSON:/probe/host-claude.json:ro")
    fi
fi
trap '[[ -n "$GEN_CREDS" ]] && rm -f "$GEN_CREDS"' EXIT

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
MODEL_ARG=""
MODEL_ENV_PASS=()
if [[ -n "${HELIX_PROBE_MODEL:-}" ]]; then
    MODEL_ARG=" --model ${HELIX_PROBE_MODEL}"
    MODEL_ENV_PASS+=(-e "HELIX_PROBE_MODEL=${HELIX_PROBE_MODEL}")
fi
BOOTSTRAP='
set -euo pipefail
if [[ -f /probe/host-claude.json ]]; then
    cp /probe/host-claude.json ~/.claude.json
    chmod 600 ~/.claude.json
fi
exec claude -p '"$PLUGIN_DIRS_ARGS$MODEL_ARG"' --output-format stream-json --verbose < /probe/prompt
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
    "${MODEL_ENV_PASS[@]}" \
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
