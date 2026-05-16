#!/usr/bin/env bash
# Codex CLI verify: static skill-layout check + optional functional check.

set -euo pipefail

SKILL_ROOT="$HOME/.codex/skills/helix"
SHARED_VERIFY="/workspace/helix/tests/install/shared/verify-skill-layout.sh"

echo "→ static layout checks"
bash "$SHARED_VERIFY" "$SKILL_ROOT"

if [[ "${TEST_FUNCTIONAL:-}" == "1" ]]; then
  if [[ -z "${OPENAI_API_KEY:-}" ]]; then
    echo "FAIL: TEST_FUNCTIONAL=1 but OPENAI_API_KEY not set"
    exit 1
  fi
  if ! command -v codex >/dev/null 2>&1; then
    echo "FAIL: TEST_FUNCTIONAL=1 but codex CLI not installed in image"
    exit 1
  fi
  echo
  echo "→ functional check: codex exec --ephemeral"
  RESPONSE="$(codex exec --ephemeral --skip-git-repo-check \
      "List the HELIX routing modes you can route to. Be concise." 2>&1 || true)"
  echo "response excerpt:"
  echo "$RESPONSE" | head -20
  EXPECTED=("align" "frame" "evolve" "review" "design")
  MISSING=()
  for mode in "${EXPECTED[@]}"; do
    if ! grep -qiF "$mode" <<<"$RESPONSE"; then
      MISSING+=("$mode")
    fi
  done
  if (( ${#MISSING[@]} > 0 )); then
    echo "FAIL: response missing expected modes: ${MISSING[*]}"
    exit 1
  fi
  echo "ok: response names align/frame/evolve/review/design"
fi

echo
echo "codex-cli scenario: PASS"
