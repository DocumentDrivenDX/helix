#!/usr/bin/env bash
# Claude Code verify: static skill-layout check, plus optional functional check.
#
# Two install modes use different on-disk layouts:
#   default (PR symlink): install.sh writes ~/.claude/plugins/helix → /workspace/helix,
#     so the skill is at ~/.claude/plugins/helix/skills/helix.
#   TEST_PUBLISHED=1 (real marketplace): Claude Code copies the plugin under
#     ~/.claude/plugins/cache/<version-dir>/ — exact subdir is loader-defined.

set -euo pipefail

SHARED_VERIFY="/workspace/helix/tests/install/shared/verify-skill-layout.sh"

if [[ "${TEST_PUBLISHED:-}" == "1" ]]; then
  SKILL_ROOT="$(ls -d "$HOME"/.claude/plugins/cache/*/skills/helix 2>/dev/null | head -1)"
  if [[ -z "$SKILL_ROOT" ]]; then
    echo "FAIL: no skill found under ~/.claude/plugins/cache/*/skills/helix"
    echo "contents of ~/.claude/plugins/cache/:"
    ls -la "$HOME/.claude/plugins/cache/" 2>/dev/null || echo "(cache dir missing)"
    exit 1
  fi
  echo "→ marketplace skill resolved at: $SKILL_ROOT"
  echo "→ claude plugin list:"
  claude plugin list 2>&1 || echo "(non-fatal: plugin list may require API key)"
else
  SKILL_ROOT="$HOME/.claude/plugins/helix/skills/helix"
fi

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
