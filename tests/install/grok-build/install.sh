#!/usr/bin/env bash
# Install HELIX into Grok Build from a local checkout (default) or published source.
#
# Env:
#   HELIX_ROOT       path to helix checkout (default: /workspace/helix or repo relative)
#   TEST_PUBLISHED=1 use DocumentDrivenDX/helix instead of local path
#
# Exit:
#   0  install succeeded
#   77 grok CLI not available (caller may treat as skip)
#   1  install failed

set -euo pipefail

if ! command -v grok >/dev/null 2>&1; then
  echo "SKIP: grok not on PATH"
  exit 77
fi

if [[ -n "${HELIX_ROOT:-}" ]]; then
  ROOT="$HELIX_ROOT"
elif [[ -d /workspace/helix ]]; then
  ROOT=/workspace/helix
else
  ROOT="$(cd "$(dirname "$0")/../../.." && pwd -P)"
fi

echo "→ HELIX_ROOT=$ROOT"
grok plugin validate "$ROOT"

set +e
if [[ "${TEST_PUBLISHED:-}" == "1" ]]; then
  echo "→ grok plugin install DocumentDrivenDX/helix --trust"
  out="$(grok plugin install DocumentDrivenDX/helix --trust 2>&1)"
  rc=$?
else
  echo "→ grok plugin install $ROOT --trust"
  out="$(grok plugin install "$ROOT" --trust 2>&1)"
  rc=$?
fi
set -e
printf '%s\n' "$out"
if [[ $rc -ne 0 ]]; then
  if printf '%s\n' "$out" | grep -qiE 'already installed|already exists'; then
    echo "→ plugin already installed; continuing"
  else
    echo "FAIL: grok plugin install exit $rc"
    exit 1
  fi
fi

grok plugin list
echo "install: OK"
