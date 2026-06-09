#!/usr/bin/env bash
# Run a skill-activation probe via the opencode CLI.
#
# opencode (v1.3+) discovers skills via ancestor walk:
#   <cwd-or-ancestor>/.claude/skills/<name>/SKILL.md
#   <cwd-or-ancestor>/.agents/skills/<name>/SKILL.md
#   $HOME/.claude/skills/...  $HOME/.agents/skills/...
# No --plugin-dir flag. We mount HELIX SKILL.md under <fixture>/.claude/skills/
# per-run; the agent-recommended path.
#
# Usage:
#   run-probe-opencode.sh <fixture-dir> <plugins-spec> <prompt-file> <evidence-file> [<cwd-rel>]
#
# Arguments mirror run-probe.sh:
#   fixture-dir   absolute path; agent cwd. We write .claude/skills/ under it.
#   plugins-spec  comma-separated host paths to methodology plugins. For each
#                 path, every skills/<id>/ entry is mounted under
#                 <fixture>/.claude/skills/<id>/. Use "" to install none.
#   prompt-file   absolute path to a prompt file
#   evidence-file absolute path on host for NDJSON event capture
#   cwd-rel       optional subdir under fixture-dir
#
# Model selection: HELIX_PROBE_MODEL forwarded to `opencode run -m`.
# Default model:   opencode/grok-code (cheap, fast; override at the runner).
#
# Authentication: opencode picks up ~/.local/share/opencode/auth.json AND
# provider-specific env vars (ANTHROPIC_API_KEY, OPENAI_API_KEY, etc.). The
# script does NOT enforce auth presence — opencode will report a clean error
# at run time if credentials are missing for the selected model.
#
# Exit codes:
#   0  opencode exited cleanly; evidence file populated with NDJSON
#   1  bad arguments
#   3  opencode exited non-zero (evidence file still written for inspection)

set -euo pipefail

if [[ $# -lt 4 || $# -gt 5 ]]; then
    echo "usage: $0 <fixture-dir> <plugins-spec> <prompt-file> <evidence-file> [<cwd-rel>]" >&2
    exit 1
fi

FIXTURE_DIR="$1"
PLUGINS_SPEC="$2"
PROMPT_FILE="$3"
EVIDENCE_FILE="$4"
CWD_REL="${5:-}"

if [[ ! -d "$FIXTURE_DIR" ]]; then
    echo "FAIL: fixture-dir does not exist: $FIXTURE_DIR" >&2
    exit 1
fi
if [[ ! -f "$PROMPT_FILE" ]]; then
    echo "FAIL: prompt-file does not exist: $PROMPT_FILE" >&2
    exit 1
fi
if ! command -v opencode >/dev/null 2>&1; then
    echo "FAIL: opencode CLI not found on PATH" >&2
    exit 1
fi

mkdir -p "$(dirname "$EVIDENCE_FILE")"
: > "$EVIDENCE_FILE"

# Mount methodology plugin skills under <fixture>/.claude/skills/<id>/.
# Use symlinks so updates to the source plugin propagate without re-copying.
SKILLS_ROOT="$FIXTURE_DIR/.claude/skills"
mkdir -p "$SKILLS_ROOT"
MOUNTED=()
cleanup() {
    for sk in "${MOUNTED[@]+"${MOUNTED[@]}"}"; do
        rm -f "$sk" 2>/dev/null || true
    done
}
trap cleanup EXIT

if [[ -n "$PLUGINS_SPEC" ]]; then
    IFS=',' read -r -a PLUGIN_PATHS <<<"$PLUGINS_SPEC"
    for p in "${PLUGIN_PATHS[@]}"; do
        [[ -d "$p/skills" ]] || continue
        for sk in "$p/skills"/*/; do
            [[ -d "$sk" ]] || continue
            name="$(basename "$sk")"
            target="$SKILLS_ROOT/$name"
            ln -sfn "${sk%/}" "$target"
            MOUNTED+=("$target")
        done
    done
fi

WORKDIR="$FIXTURE_DIR"
if [[ -n "$CWD_REL" ]]; then
    WORKDIR="$FIXTURE_DIR/$CWD_REL"
fi
if [[ ! -d "$WORKDIR" ]]; then
    echo "FAIL: working dir does not exist: $WORKDIR" >&2
    exit 1
fi

MODEL="${HELIX_PROBE_MODEL:-opencode/grok-code}"

# Read prompt then run opencode. We pass the prompt as a positional arg to
# `opencode run`, not via stdin — opencode's headless mode expects argv.
PROMPT="$(cat "$PROMPT_FILE")"

set +e
cd "$WORKDIR" && opencode run "$PROMPT" --format json -m "$MODEL" \
    >"$EVIDENCE_FILE" 2>"$EVIDENCE_FILE.stderr"
RC=$?
set -e

if [[ $RC -ne 0 ]]; then
    echo "WARN: opencode exited rc=$RC; evidence still written to $EVIDENCE_FILE" >&2
    exit 3
fi

echo "OK: evidence written to $EVIDENCE_FILE"
exit 0
