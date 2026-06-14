#!/usr/bin/env bash
# DDx verify: static skill-layout invariants + optional functional check.

set -euo pipefail

SKILL_ROOT="$HOME/.ddx/plugins/helix/skills/helix"
SHARED_VERIFY="/workspace/helix/tests/install/shared/verify-skill-layout.sh"

if [[ -f /tmp/helix-ddx-install-skipped ]]; then
  echo "SKIP: DDx install was skipped because the current DDx published installer"
  echo "      still requires the retired scripts/helix checkout CLI."
  echo
  echo "ddx scenario: SKIP"
  exit 0
fi

echo "→ static layout checks"
bash "$SHARED_VERIFY" "$SKILL_ROOT"

if [[ "${TEST_FUNCTIONAL:-}" == "1" ]]; then
  echo
  echo "→ functional check skipped: DDx queue/worker flow needs additional setup"
  echo "   (file a follow-up bead if the static check is insufficient)"
fi

echo
echo "ddx scenario: PASS"
