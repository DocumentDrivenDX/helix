#!/usr/bin/env bash
# Claude Code verify: static skill-layout check, plus optional functional check.

set -euo pipefail

SKILL_ROOT="$HOME/.claude/plugins/helix/skills/helix"
SHARED_VERIFY="/workspace/helix/tests/install/shared/verify-skill-layout.sh"

echo "→ static layout checks"
bash "$SHARED_VERIFY" "$SKILL_ROOT"

if [[ "${TEST_FUNCTIONAL:-}" == "1" ]]; then
  if [[ -z "${ANTHROPIC_API_KEY:-}" ]]; then
    echo "FAIL: TEST_FUNCTIONAL=1 but ANTHROPIC_API_KEY not set"
    exit 1
  fi
  echo
  echo "→ functional check: ask Claude Code to list HELIX modes"
  RESPONSE="$(echo 'List the HELIX routing modes you can route to. Be concise.' | claude -p 2>&1)"
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
echo "claude-code scenario: PASS"
