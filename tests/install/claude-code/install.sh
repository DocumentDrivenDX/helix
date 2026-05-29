#!/usr/bin/env bash
# Claude Code install scenario.
#
# Two modes:
#   default (PR-safe): load the mounted local checkout as a plugin, so the
#     scenario validates THIS revision's loader without depending on the
#     published marketplace.
#   TEST_PUBLISHED=1 (post-merge smoke): run the REAL marketplace flow the docs
#     tell users to run — `claude plugin marketplace add DocumentDrivenDX/helix`
#     then `claude plugin install helix@helix`. This exercises the genuine
#     HTTPS clone and catches regressions like an SSH-only plugin source.

set -euo pipefail

echo "claude version:"
claude --version

if [[ "${TEST_PUBLISHED:-}" == "1" ]]; then
  echo
  echo "→ real marketplace install from the published repo (HTTPS clone)"
  claude plugin marketplace add DocumentDrivenDX/helix
  claude plugin install helix@helix --scope user -y
else
  echo
  echo "→ loading the local checkout as a Claude Code plugin (PR-safe)"
  mkdir -p ~/.claude/plugins
  ln -sf /workspace/helix ~/.claude/plugins/helix
fi

echo
echo "claude plugin list:"
claude plugin list 2>&1 || echo "(non-fatal: plugin list may require API key)"
