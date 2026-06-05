#!/usr/bin/env bash
# Run all Bucket A skill-activation probes against the Docker harness.
#
# Requires:
#   - family-test-claude:latest image built (see family-test/docker/)
#   - Valid Claude credentials (CLAUDE_CREDENTIALS_FILE or ~/.claude/.credentials.json)
#
# Writes per-probe stream-json to family-test/probe-evidence/bucket-a/<id>.stream.jsonl
# Writes per-probe assertion summary to family-test/probe-evidence/bucket-a/<id>.summary.txt
# Prints final per-probe verdict.

set -uo pipefail

REPO=/Users/erik/Projects/helix
FT="$REPO/family-test"
HARNESS="$FT/docker/run-probe.sh"
ASSERT="$FT/docker/assertions.py"
EVIDENCE="$FT/probe-evidence/bucket-a"
FIXTURES="$FT/probe-fixtures/bucket-a"
PROMPTS="$FIXTURES/prompts"

LIB="$FT/library"
PRODUCT="$FT/methodology-product"
INFRA="$FT/methodology-infra"
BOTH="$LIB,$PRODUCT,$INFRA"
LIB_ONLY="$LIB"
PRODUCT_PLUS_INFRA="$LIB,$PRODUCT,$INFRA"

mkdir -p "$EVIDENCE"

# Prefer fresh creds copied into bind-mountable path.
if [[ -f /home/erik/.claude/.credentials.json && ! -f /Users/erik/Projects/helix/family-test/.tmp/fresh-creds.json ]]; then
    mkdir -p /Users/erik/Projects/helix/family-test/.tmp
    cp /home/erik/.claude/.credentials.json /Users/erik/Projects/helix/family-test/.tmp/fresh-creds.json
    chmod 600 /Users/erik/Projects/helix/family-test/.tmp/fresh-creds.json
fi
export CLAUDE_CREDENTIALS_FILE="${CLAUDE_CREDENTIALS_FILE:-/Users/erik/Projects/helix/family-test/.tmp/fresh-creds.json}"

run_probe() {
    local id="$1"
    local fixture="$2"
    local plugins="$3"
    local prompt="$4"
    local evidence="$EVIDENCE/$id.stream.jsonl"
    echo "→ $id (fixture=$(basename "$fixture"))"
    bash "$HARNESS" "$fixture" "$plugins" "$prompt" "$evidence" 2>&1 | tail -2
    echo "  evidence: $evidence ($(wc -l <"$evidence") lines)"
}

# A4 requires running with cwd inside a subdir of the fixture.
# We bypass run-probe.sh and do the docker call inline.
run_probe_in_subdir() {
    local id="$1"
    local fixture="$2"
    local subdir="$3"   # relative path under fixture
    local plugins="$4"
    local prompt_file="$5"
    local evidence="$EVIDENCE/$id.stream.jsonl"
    echo "→ $id (fixture=$(basename "$fixture"), subdir=$subdir)"

    local IMAGE="family-test-claude:latest"
    local AUTH_MOUNT
    AUTH_MOUNT="-v $CLAUDE_CREDENTIALS_FILE:/home/probe/.claude/.credentials.json:ro"

    local PLUGIN_MOUNTS=()
    local PLUGIN_DIRS_ARGS=""
    IFS=',' read -r -a PLUGIN_PATHS <<<"$plugins"
    for p in "${PLUGIN_PATHS[@]}"; do
        local name; name="$(basename "$p")"
        PLUGIN_MOUNTS+=(-v "$p:/plugins-src/$name:ro")
        PLUGIN_DIRS_ARGS="$PLUGIN_DIRS_ARGS --plugin-dir /plugins-src/$name"
    done

    local BOOTSTRAP='
set -euo pipefail
cd "/workspace/'"$subdir"'"
exec claude -p '"$PLUGIN_DIRS_ARGS"' --output-format stream-json --verbose < /probe/prompt
'

    : > "$evidence"
    docker run --rm \
        $AUTH_MOUNT \
        "${PLUGIN_MOUNTS[@]}" \
        -v "$fixture:/workspace" \
        -v "$prompt_file:/probe/prompt:ro" \
        "$IMAGE" \
        bash -c "$BOOTSTRAP" \
        >"$evidence" 2>"$evidence.stderr"
    echo "  evidence: $evidence ($(wc -l <"$evidence") lines)"
}

echo "=== Bucket A probes ==="

# A1a — happy path: marker + plugin installed → activates helix
run_probe "a1a" "$FT/consumer/clean" "$LIB,$PRODUCT" "$PROMPTS/a1a.txt"

# A1b — control: marker present but methodology plugin NOT installed
run_probe "a1b" "$FT/consumer/clean" "$LIB_ONLY" "$PROMPTS/a1b.txt"

# A1c — functional: no telegraph (asks for PRD)
run_probe "a1c" "$FT/consumer/clean" "$LIB,$PRODUCT" "$PROMPTS/a1c.txt"

# A2 — no marker, no heuristic → JSON {active: []}
run_probe "a2" "$FIXTURES/a2-no-marker-no-heuristic" "$LIB,$PRODUCT" "$PROMPTS/a2.txt"

# A2b — no marker, heuristic present → banner
run_probe "a2b" "$FIXTURES/a2b-heuristic-no-marker" "$LIB,$PRODUCT" "$PROMPTS/a2b.txt"

# A3 — scope respect (cwd outside scoped methodology root)
run_probe "a3" "$FIXTURES/a3-scope-respect" "$LIB,$PRODUCT" "$PROMPTS/a3.txt"

# A4 — multi-methodology cwd routing
run_probe_in_subdir "a4-helix" "$FIXTURES/a4-multi" "docs/helix" "$LIB,$PRODUCT,$INFRA" "$PROMPTS/a4-helix.txt"
run_probe_in_subdir "a4-infra" "$FIXTURES/a4-multi" "infra"      "$LIB,$PRODUCT,$INFRA" "$PROMPTS/a4-infra.txt"

# A5 — explicit prefix wins / membership = authorization
run_probe "a5" "$FIXTURES/a5-prefix-membership" "$LIB,$PRODUCT,$INFRA" "$PROMPTS/a5.txt"

# A6 — malformed marker + heuristic → STOP not fall back
run_probe "a6" "$FIXTURES/a6-malformed" "$LIB,$PRODUCT" "$PROMPTS/a6.txt"

echo "=== done ==="
