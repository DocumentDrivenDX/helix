#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

python3 "$repo_root/scripts/validate_actions.py" || {
  printf 'action prompt validation failed\n' >&2
  exit 1
}
