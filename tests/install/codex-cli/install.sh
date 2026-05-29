#!/usr/bin/env bash
# Codex CLI install scenario.
#
# Two modes:
#   default (PR-safe): copy skills/helix/ from the mounted local checkout, so
#     the scenario validates THIS revision without fetching from GitHub.
#   TEST_PUBLISHED=1 (post-merge smoke): run the REAL documented command,
#     `npx skills add DocumentDrivenDX/helix -a codex`, which fetches the
#     published skill from GitHub the way the docs tell users to.

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
  echo "→ real Skills CLI install from the published repo"
  npx --yes skills add DocumentDrivenDX/helix -a codex
else
  echo
  echo "→ placing skills/helix/ under ~/.codex/skills/ (PR-safe)"
  mkdir -p ~/.codex/skills
  rm -rf ~/.codex/skills/helix
  cp -r /workspace/helix/skills/helix ~/.codex/skills/
fi

echo
echo "→ also vendoring the workflows catalog at ~/.codex/workflows/"
mkdir -p ~/.codex
ln -sf /workspace/helix/workflows ~/.codex/workflows

echo
echo "install complete; checking installed location..."
ls -la ~/.codex/skills/helix/ | head
