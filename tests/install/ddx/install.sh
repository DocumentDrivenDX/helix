#!/usr/bin/env bash
# DDx install: `ddx install helix --local <source> --force`.
#
# Expects the HELIX source tree mounted at /workspace/helix.

set -euo pipefail

echo "ddx version:"
ddx version

echo
if [[ "${TEST_PUBLISHED:-}" == "1" ]]; then
  echo "→ ddx install helix --force"
  INSTALL_LOG="$(mktemp)"
  set +e
  ddx install helix --force >"$INSTALL_LOG" 2>&1
  RC=$?
  set -e
  cat "$INSTALL_LOG"
  if (( RC != 0 )); then
    if grep -q 'scripts/helix' "$INSTALL_LOG"; then
      echo
      echo "SKIP: DDx published installer still requires the retired scripts/helix checkout CLI."
      echo "      HELIX 0.7.0 is content + one routing skill; DDx must update its installer contract."
      touch /tmp/helix-ddx-install-skipped
      rm -f "$INSTALL_LOG"
      exit 0
    fi
    rm -f "$INSTALL_LOG"
    exit "$RC"
  fi
  rm -f "$INSTALL_LOG"
else
  echo "→ ddx install helix --local /workspace/helix --force"
  ddx install helix --local /workspace/helix --force
fi

echo
echo "install complete; checking installed location..."
ls -la ~/.ddx/plugins/helix/skills/helix/ || true
