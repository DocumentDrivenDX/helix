#!/usr/bin/env bash
# DDx install: `ddx install helix --local <source> --force`.
#
# Expects the HELIX source tree mounted at /workspace/helix.

set -euo pipefail

echo "ddx version:"
ddx --version

echo
echo "→ ddx install helix --local /workspace/helix --force"
ddx install helix --local /workspace/helix --force

echo
echo "install complete; checking installed location..."
ls -la ~/.ddx/plugins/helix/skills/helix/ || true
