#!/usr/bin/env bash
# Claude Code install: marketplace add + plugin install.
#
# For CI we use `--plugin-dir` (session-only) against the mounted source,
# which exercises the same loader as the marketplace flow without requiring
# the marketplace to be in sync with HEAD.

set -euo pipefail

echo "claude version:"
claude --version

# Marketplace flow against the mounted source.
# claude plugin marketplace add /workspace/helix
# claude plugin install helix@helix --scope user -y
# For CI sandboxes, use --plugin-dir which loads the local checkout directly:

echo
echo "→ symlinking the local checkout as a Claude Code plugin"
mkdir -p ~/.claude/plugins
ln -sf /workspace/helix ~/.claude/plugins/helix

echo
echo "claude plugin list:"
claude plugin list 2>&1 || echo "(non-fatal: plugin list may require API key)"
