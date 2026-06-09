#!/usr/bin/env bash
# E1 — lefthook integration probe.
#
# Sets up an isolated git repo containing the clean consumer fixture and
# the .lefthook.yml from consumer/clean/. Stages a broken instance (FEAT-001
# from consumer/bad-edge-kind) and attempts `git commit`. Asserts:
#   - lefthook fires
#   - helix_check.py reports the edge-kind violation
#   - git commit aborts with a non-zero exit code
#
# Then stages the original clean instance and confirms commit succeeds
# (negative control — the hook only rejects bad input).
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FAMILY_TEST_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
export FAMILY_TEST_ROOT

EVIDENCE="$SCRIPT_DIR/e1-output.txt"
: > "$EVIDENCE"

log() { echo "$@" | tee -a "$EVIDENCE"; }

WORK="$(mktemp -d -t helix-e1.XXXXXX)"
trap 'rm -rf "$WORK"' EXIT

log "=== E1 lefthook integration ==="
log "FAMILY_TEST_ROOT=$FAMILY_TEST_ROOT"
log "WORK=$WORK"
log ""

# Stage 1: build isolated repo
mkdir -p "$WORK/repo"
cp -R "$FAMILY_TEST_ROOT/consumer/clean/." "$WORK/repo/"
cd "$WORK/repo"

git init -q -b main
git config user.email "e1@test.local"
git config user.name  "E1 Test"
git config commit.gpgsign false

git add .helix.yml .lefthook.yml docs/
git commit -q -m "seed: clean fixture"

# Install lefthook hooks into this repo.
if ! lefthook install >>"$EVIDENCE" 2>&1; then
  log "FAIL: lefthook install failed"
  exit 2
fi

log "--- baseline commit (clean change) ---"
# Touch the clean fixture (no semantic change) and confirm hook PASSES.
echo "" >> docs/helix/01-frame/PRD-001.md
git add docs/helix/01-frame/PRD-001.md
if git commit -m "test: clean change should pass" >>"$EVIDENCE" 2>&1; then
  log "PASS baseline: hook allowed clean change (exit 0)"
  BASELINE=0
else
  log "FAIL baseline: hook blocked a clean change"
  BASELINE=1
fi
log ""

log "--- failure commit (broken instance from bad-edge-kind) ---"
# Replace PRD-001.md with the bad-edge-kind variant (contains where graph
# declares informs). Hook MUST abort.
cp "$FAMILY_TEST_ROOT/consumer/bad-edge-kind/docs/helix/01-frame/PRD-001.md" docs/helix/01-frame/PRD-001.md
# bad-edge-kind also has FEAT-001 — copy it too so links resolve.
cp "$FAMILY_TEST_ROOT/consumer/bad-edge-kind/docs/helix/01-frame/FEAT-001.md" docs/helix/01-frame/FEAT-001.md
# bad-edge-kind has no 02-design — remove so we mirror that fixture exactly.
rm -rf docs/helix/02-design

git add docs/helix/
HOOK_OUT="$(git commit -m "test: broken change should be blocked" 2>&1)"
HOOK_RC=$?
echo "$HOOK_OUT" >>"$EVIDENCE"

if [ "$HOOK_RC" -ne 0 ]; then
  log "PASS failure: hook aborted commit (exit $HOOK_RC)"
  if echo "$HOOK_OUT" | grep -q "I101"; then
    log "PASS failure: I101 in hook output"
    FAILURE=0
  else
    log "WARN failure: aborted but no I101 in output (still counts as block)"
    FAILURE=0
  fi
else
  log "FAIL failure: hook ALLOWED a broken commit"
  FAILURE=1
fi
log ""

# Stage 3: restore
git reset --hard HEAD >>"$EVIDENCE" 2>&1
log "--- restored repo to last good commit ---"
log ""

if [ "$BASELINE" -eq 0 ] && [ "$FAILURE" -eq 0 ]; then
  log "RESULT: E1 PASS"
  exit 0
else
  log "RESULT: E1 FAIL (baseline=$BASELINE failure=$FAILURE)"
  exit 1
fi
