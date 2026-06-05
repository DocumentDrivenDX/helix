#!/usr/bin/env bash
# Smoke test: prove the Docker harness itself works.
#
# Sends a trivial prompt ("What is 2+2?") into the clean consumer fixture
# with helix-library + helix product plugins installed. Asserts:
#   - run-probe.sh exits 0
#   - response prose contains "4"
#   - no write-class tool was invoked
#
# This does NOT validate skill activation — that is Bucket A's job.
# It only proves the container boots, plugins mount, claude -p runs, and
# stream-json comes back parsable.

set -euo pipefail

cd "$(dirname "$0")"
HARNESS_DIR="$PWD"
FAMILY_TEST_DIR="$(cd "$HARNESS_DIR/.." && pwd)"
REPO_ROOT="$(cd "$FAMILY_TEST_DIR/.." && pwd)"

IMAGE="${PROBE_IMAGE:-family-test-claude:latest}"

# 1. Ensure image exists. Build if needed.
if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
    echo "→ building $IMAGE"
    docker build \
        --build-arg "HOST_UID=$(id -u)" \
        --build-arg "HOST_GID=$(id -g)" \
        -t "$IMAGE" \
        -f "$HARNESS_DIR/Dockerfile.claude" \
        "$HARNESS_DIR"
fi

# 2. Set up a temp evidence dir. Must live under a host path docker can
# bind-mount; on OrbStack Linux VMs the Linux-side $TMPDIR (/tmp,
# /home/erik/.cache) is NOT visible to the macOS docker daemon, so we
# place it under family-test/.tmp/ which is bind-mountable both ways.
TMP_ROOT="$FAMILY_TEST_DIR/.tmp"
mkdir -p "$TMP_ROOT"
EVIDENCE_DIR="$(mktemp -d -p "$TMP_ROOT" smoke.XXXXXX)"
trap 'rm -rf "$EVIDENCE_DIR"' EXIT
EVIDENCE_FILE="$EVIDENCE_DIR/smoke.jsonl"

PROMPT_FILE="$EVIDENCE_DIR/prompt.txt"
cat >"$PROMPT_FILE" <<'EOF'
What is 2+2? Answer with just the number.
EOF

# 3. Run the probe.
FIXTURE="$FAMILY_TEST_DIR/consumer/clean"
PLUGINS="$FAMILY_TEST_DIR/library,$FAMILY_TEST_DIR/methodology-product"

echo "→ running probe (fixture=$FIXTURE)"
set +e
bash "$HARNESS_DIR/run-probe.sh" \
    "$FIXTURE" \
    "$PLUGINS" \
    "$PROMPT_FILE" \
    "$EVIDENCE_FILE"
PROBE_RC=$?
set -e

echo "→ probe exit: $PROBE_RC"
echo "→ evidence: $EVIDENCE_FILE ($(wc -l <"$EVIDENCE_FILE") lines)"

# 4. If the probe couldn't run claude (auth missing / network down),
# distinguish that from a real failure. We treat rc=3 (claude non-zero)
# as a known limitation only if the evidence file looks empty or contains
# an auth error in stderr.
if [[ $PROBE_RC -eq 3 ]]; then
    # Auth errors land in the stream-json evidence (assistant message +
    # "error":"authentication_failed"), not stderr. Check both.
    AUTH_FAIL=0
    if [[ -s "$EVIDENCE_FILE" ]] && grep -qE 'authentication_failed|Not logged in|Please run /login' "$EVIDENCE_FILE"; then
        AUTH_FAIL=1
    fi
    if [[ -s "$EVIDENCE_FILE.stderr" ]] && grep -qiE 'unauthor|api key|credential|forbidden|401|403' "$EVIDENCE_FILE.stderr"; then
        AUTH_FAIL=1
    fi
    if [[ $AUTH_FAIL -eq 1 ]]; then
        echo "SMOKE: auth missing (rc=3, evidence shows auth error)"
        echo "       harness scaffold is correct; live run blocked on credentials."
        echo "evidence excerpt:"
        head -c 400 "$EVIDENCE_FILE"
        echo
        # Treat as a soft-pass: harness is GO for Phase 3 once auth is provided.
        exit 0
    fi
    echo "FAIL: probe rc=3 but no auth error detected"
    echo "evidence head:"
    head -c 500 "$EVIDENCE_FILE" || true
    echo
    echo "stderr head:"
    head -20 "$EVIDENCE_FILE.stderr" || true
    exit 1
fi

if [[ $PROBE_RC -ne 0 ]]; then
    echo "FAIL: probe exited rc=$PROBE_RC"
    echo "stderr:"
    head -20 "$EVIDENCE_FILE.stderr" || true
    exit 1
fi

# 5. Assertions.
# Auth-failure short-circuit: if claude returned an auth error in the
# stream-json (even with rc=0), report it as a known limitation rather
# than a harness failure.
if grep -qE 'authentication_failed|Not logged in|Please run /login' "$EVIDENCE_FILE"; then
    echo "SMOKE: auth missing (evidence shows auth error)"
    echo "       harness scaffold is correct; live run blocked on credentials."
    echo "evidence excerpt:"
    head -c 400 "$EVIDENCE_FILE"
    echo
    exit 0
fi

echo "→ asserting prose contains '4'"
if ! python3 "$HARNESS_DIR/assertions.py" "$EVIDENCE_FILE" contains "4" >/dev/null; then
    echo "FAIL: prose does not contain '4'"
    echo "prose:"
    python3 "$HARNESS_DIR/assertions.py" "$EVIDENCE_FILE" prose
    exit 1
fi
echo "  ok"

echo "→ asserting no writes"
if ! python3 "$HARNESS_DIR/assertions.py" "$EVIDENCE_FILE" no-writes >/dev/null; then
    echo "FAIL: a write-class tool was invoked"
    exit 1
fi
echo "  ok"

echo
echo "SMOKE: PASS — harness GO for Phase 3"
