#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

python3 "$repo_root/scripts/validate_actions.py" || {
  printf 'action prompt validation failed\n' >&2
  exit 1
}

python3 "$repo_root/scripts/helix_evolve_impact.py" \
  --docs-root "$repo_root/tests/fixtures/evolve-impact/canonical-links/docs/helix" \
  --entry FEAT-001 \
  --require-upstream \
  --require-downstream \
  --expect-edge-field ddx.links \
  >/dev/null || {
    printf 'canonical ddx.links evolve impact validation failed\n' >&2
    exit 1
  }

python3 "$repo_root/scripts/helix_evolve_impact.py" \
  --docs-root "$repo_root/tests/fixtures/evolve-impact/legacy-fields/docs/helix" \
  --entry FEAT-LEGACY \
  --require-upstream \
  --require-downstream \
  --expect-edge-field ddx.depends_on \
  --expect-edge-field depends_on \
  >/dev/null || {
    printf 'legacy evolve impact compatibility validation failed\n' >&2
    exit 1
  }
