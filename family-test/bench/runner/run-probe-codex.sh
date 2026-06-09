#!/usr/bin/env bash
# Run a skill-activation probe via the OpenAI Codex CLI.
#
# Analogous to family-test/docker/run-probe.sh but invokes `codex exec --json`
# directly on the host (no Docker). Codex has no plugin loader — the
# methodology tree is VENDORED into a per-run $CODEX_HOME under
# $CODEX_HOME/skills/<name>/.
#
# Usage:
#   run-probe-codex.sh <fixture-dir> <plugins-spec> <prompt-file> <evidence-file> [<cwd-rel>]
#
# Arguments mirror run-probe.sh:
#   fixture-dir   absolute path used as the agent's working root (codex -C)
#   plugins-spec  comma-separated list of host paths. Each path is treated as
#                 a methodology-plugin root; we vendor its `skills/<id>/`
#                 entries into $CODEX_HOME/skills/<id>/. Use "" to install
#                 none.
#   prompt-file   absolute path to a file containing the prompt
#   evidence-file absolute path on host where JSONL events are written
#   cwd-rel       optional subdir under fixture-dir to use as the working root
#
# Model selection: HELIX_PROBE_MODEL env var forwarded to `codex exec --model`.
#
# Authentication: OPENAI_API_KEY env required (codex picks it up). The script
# exits 1 with "auth missing" if neither $OPENAI_API_KEY nor a populated
# ~/.codex/auth.json is present.
#
# Exit codes:
#   0  codex exited cleanly; evidence-file contains JSONL
#   1  bad arguments OR auth missing
#   3  codex exited non-zero (assertions should still inspect evidence)
#
# This script does NOT make pass/fail judgments about probe content.

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

if ! command -v codex >/dev/null 2>&1; then
    echo "FAIL: codex CLI not found on PATH" >&2
    exit 1
fi

# Auth check. codex falls back to ~/.codex/auth.json when env unset, so we
# accept either signal.
AUTH_OK=0
if [[ -n "${OPENAI_API_KEY:-}" ]]; then
    AUTH_OK=1
elif [[ -f "${HOME}/.codex/auth.json" ]] \
     && grep -q -E '"OPENAI_API_KEY"|"tokens"' "${HOME}/.codex/auth.json" 2>/dev/null; then
    AUTH_OK=1
fi
if [[ $AUTH_OK -eq 0 ]]; then
    echo "FAIL: codex auth missing (set OPENAI_API_KEY or run 'codex login')" >&2
    exit 1
fi

mkdir -p "$(dirname "$EVIDENCE_FILE")"
: > "$EVIDENCE_FILE"

# Build a per-run CODEX_HOME so the host config is not contaminated by
# methodology vendoring. Copy auth.json + config.toml if present so codex
# can authenticate; otherwise rely on $OPENAI_API_KEY.
#
# codex refuses to create helper binaries under tmpfs-style temp dirs
# (warns then errors on PATH update). Use a non-tmp scratch area under the
# evidence-file's parent so it lives on a real fs the runner already trusts.
CODEX_PROBE_ROOT="${HELIX_CODEX_PROBE_ROOT:-$(dirname "$EVIDENCE_FILE")/.codex-probe}"
mkdir -p "$CODEX_PROBE_ROOT"
RUN_CODEX_HOME="$(mktemp -d "$CODEX_PROBE_ROOT/run-XXXXXX")"
cleanup() {
    rm -rf "$RUN_CODEX_HOME" 2>/dev/null || true
}
trap cleanup EXIT

if [[ -f "${HOME}/.codex/auth.json" ]]; then
    cp "${HOME}/.codex/auth.json" "$RUN_CODEX_HOME/auth.json"
fi
if [[ -f "${HOME}/.codex/config.toml" ]]; then
    cp "${HOME}/.codex/config.toml" "$RUN_CODEX_HOME/config.toml"
fi

# Vendor methodology skills. Each plugin path is expected to look like the
# family-test layout: <plugin>/skills/<skill-id>/SKILL.md (mirrors codex's
# install scenario). We symlink each <skill-id> dir into
# $CODEX_HOME/skills/<skill-id>/.
mkdir -p "$RUN_CODEX_HOME/skills"
mkdir -p "$RUN_CODEX_HOME/workflows"
if [[ -n "$PLUGINS_SPEC" ]]; then
    IFS=',' read -r -a PLUGIN_PATHS <<<"$PLUGINS_SPEC"
    for p in "${PLUGIN_PATHS[@]}"; do
        if [[ ! -d "$p" ]]; then
            echo "FAIL: plugin path is not a directory: $p" >&2
            exit 1
        fi
        if [[ -d "$p/skills" ]]; then
            for sk in "$p/skills"/*/; do
                [[ -d "$sk" ]] || continue
                name="$(basename "$sk")"
                # symlink the skill dir (avoid stale link if name collides)
                ln -sfn "${sk%/}" "$RUN_CODEX_HOME/skills/$name"
            done
        fi
        # Side-vendoring the workflow tree (codex install scenario does this).
        if [[ -d "$p/workflows" ]]; then
            ln -sfn "$p/workflows" "$RUN_CODEX_HOME/workflows/$(basename "$p")"
        fi
    done
fi

# Resolve working root.
WORKDIR="$FIXTURE_DIR"
if [[ -n "$CWD_REL" ]]; then
    WORKDIR="$FIXTURE_DIR/$CWD_REL"
fi
if [[ ! -d "$WORKDIR" ]]; then
    echo "FAIL: working dir does not exist: $WORKDIR" >&2
    exit 1
fi

MODEL_ARG=()
if [[ -n "${HELIX_PROBE_MODEL:-}" ]]; then
    MODEL_ARG=(--model "${HELIX_PROBE_MODEL}")
fi

# Run codex with:
#   --json                    JSONL event stream to stdout
#   --skip-git-repo-check     fixture dirs may not be git repos
#   --sandbox read-only       agent may READ workspace files (incl. SKILL.md)
#                             but CANNOT write/exec/git. This prevents the
#                             sandbox-escape pattern we saw with workspace-write
#                             + bypass-approvals: codex ran `ddx bead close`,
#                             `git push`, etc. against the live repo.
#   -c approval_policy=never  auto-approve under sandbox without hanging
#   -C <workdir>              agent cwd
#   --ephemeral               no persisted session
#
# Trade-off: read-only means codex cannot create artifacts. For routing-evals
# (which only need the agent's skill-engagement decision), this is correct.
# If a future probe needs codex to write, set HELIX_CODEX_SANDBOX=workspace-write
# explicitly to opt into the looser sandbox for that run.
CODEX_SANDBOX="${HELIX_CODEX_SANDBOX:-read-only}"
set +e
CODEX_HOME="$RUN_CODEX_HOME" codex exec \
    --json \
    --skip-git-repo-check \
    --sandbox "$CODEX_SANDBOX" \
    -c 'approval_policy="never"' \
    --ephemeral \
    "${MODEL_ARG[@]}" \
    -C "$WORKDIR" \
    < "$PROMPT_FILE" \
    >"$EVIDENCE_FILE" 2>"$EVIDENCE_FILE.stderr"
RC=$?
set -e

if [[ $RC -ne 0 ]]; then
    echo "WARN: codex exited rc=$RC; evidence still written to $EVIDENCE_FILE" >&2
    exit 3
fi

echo "OK: evidence written to $EVIDENCE_FILE"
exit 0
