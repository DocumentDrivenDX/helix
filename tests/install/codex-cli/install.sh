#!/usr/bin/env bash
# Codex CLI install scenario.
#
# Two modes:
#   default (PR-safe): copy skills/helix/ from the mounted local checkout, so
#     the scenario validates THIS revision without fetching from GitHub.
#   TEST_PUBLISHED=1 (post-merge smoke): run the REAL documented command,
#     `codex plugin marketplace add DocumentDrivenDX/helix` and
#     `codex plugin add helix@helix`, which fetch the published plugin from
#     GitHub the way the docs tell users to.

set -euo pipefail

if command -v codex >/dev/null 2>&1; then
  echo "codex version: $(codex --version 2>&1 | head -1)"
fi

if [[ -n "${OPENAI_API_KEY:-}" ]]; then
  printenv OPENAI_API_KEY | codex login --with-api-key || \
    echo "(non-fatal: codex login --with-api-key not available in this version)"
fi

if [[ "${TEST_PUBLISHED:-}" == "1" ]]; then
  echo
  echo "→ real Codex plugin install from the published repo"
  codex plugin marketplace add DocumentDrivenDX/helix
  codex plugin add helix@helix
  SKILL_ROOT="$(find "$HOME/.codex/plugins/cache" -path '*/skills/helix' -type d 2>/dev/null | sort -V | tail -1 || true)"
else
  echo
  echo "→ placing skills/helix/ under ~/.codex/skills/ (PR-safe)"
  mkdir -p ~/.codex/skills
  rm -rf ~/.codex/skills/helix
  cp -r /workspace/helix/skills/helix ~/.codex/skills/
  SKILL_ROOT="$HOME/.codex/skills/helix"
fi

echo
echo "→ also vendoring the workflows catalog at ~/.codex/workflows/"
mkdir -p ~/.codex
ln -sf /workspace/helix/workflows ~/.codex/workflows

echo
echo "install complete; checking installed location..."
if [[ -z "${SKILL_ROOT:-}" || ! -d "$SKILL_ROOT" ]]; then
  echo "FAIL: installed helix skill not found"
  find "$HOME/.codex" -maxdepth 6 -type d 2>/dev/null | sort | sed -n '1,120p'
  exit 1
fi
echo "skill root: $SKILL_ROOT"
ls -la "$SKILL_ROOT" | head
