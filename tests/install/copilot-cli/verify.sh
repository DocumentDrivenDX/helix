#!/usr/bin/env bash
# Copilot CLI verify: presence of instruction file + optional functional check.
#
# Copilot does not install a "skill" file the way Claude Code / Codex do.
# The static check here is: `.github/copilot-instructions.md` exists,
# references the routing skill and the catalog, and is not empty.

set -euo pipefail

SCRATCH=/tmp/copilot-helix-adopter
INSTR="$SCRATCH/.github/copilot-instructions.md"
SHARED_VERIFY="/workspace/helix/tests/install/shared/verify-skill-layout.sh"

echo "→ static checks"

if [[ ! -f "$INSTR" ]]; then
  echo "FAIL: $INSTR not present"
  exit 1
fi
echo "ok: $INSTR exists ($(wc -l < "$INSTR") lines)"

if ! grep -q 'skills/helix/SKILL.md' "$INSTR"; then
  echo "FAIL: instructions do not reference skills/helix/SKILL.md"
  exit 1
fi
echo "ok: instructions reference the routing skill"

if ! grep -q 'workflows/activities' "$INSTR"; then
  echo "FAIL: instructions do not reference workflows/activities/"
  exit 1
fi
echo "ok: instructions reference the artifact catalog"

# Also run the shared layout check on the vendored skill copy.
bash "$SHARED_VERIFY" "$SCRATCH/skills/helix"

if [[ "${TEST_FUNCTIONAL:-}" == "1" ]]; then
  if [[ -z "${GH_TOKEN:-}" ]]; then
    echo "FAIL: TEST_FUNCTIONAL=1 but GH_TOKEN not set"
    exit 1
  fi
  if ! gh extension list 2>/dev/null | grep -q copilot; then
    echo "→ installing gh copilot extension"
    gh extension install github/gh-copilot || \
      echo "(non-fatal: gh-copilot extension install failed)"
  fi
  echo
  echo "→ functional check: gh copilot suggest (from adopter repo)"
  cd "$SCRATCH"
  RESPONSE="$(gh copilot suggest "List the HELIX routing modes from skills/helix/SKILL.md" 2>&1 || true)"
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
echo "copilot-cli scenario: PASS"
