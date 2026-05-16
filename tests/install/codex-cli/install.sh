#!/usr/bin/env bash
# Codex CLI install: filesystem copy into ~/.codex/skills/helix/.
#
# Uses the manual copy path rather than `npx skills add easel/helix -a codex`
# so the test exercises a locally-mounted HELIX source (the marketplace path
# requires fetching from GitHub).

set -euo pipefail

if command -v codex >/dev/null 2>&1; then
  echo "codex version: $(codex --version 2>&1 | head -1)"
fi

if [[ -n "${OPENAI_API_KEY:-}" ]]; then
  printenv OPENAI_API_KEY | codex login --with-api-key || \
    echo "(non-fatal: codex login --with-api-key not available in this version)"
fi

echo
echo "→ placing skills/helix/ under ~/.codex/skills/"
mkdir -p ~/.codex/skills
rm -rf ~/.codex/skills/helix
cp -r /workspace/helix/skills/helix ~/.codex/skills/

echo
echo "→ also vendoring the workflows catalog at ~/.codex/workflows/"
mkdir -p ~/.codex
ln -sf /workspace/helix/workflows ~/.codex/workflows

echo
echo "install complete; checking installed location..."
ls -la ~/.codex/skills/helix/ | head
