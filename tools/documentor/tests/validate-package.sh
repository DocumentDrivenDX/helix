#!/usr/bin/env bash
# The package builds as a wheel that carries its catalog, and the CLI answers from it.
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fail() { echo "FAIL: $*" >&2; exit 1; }
tmpdir="$(mktemp -d)"; trap 'rm -rf "$tmpdir"' EXIT
cd "$repo_root"
uv build --quiet --out-dir "$tmpdir/dist" >/dev/null 2>&1 || fail "uv build failed"
wheel="$(ls "$tmpdir"/dist/*.whl)"
for member in documentor/catalog/helix/voice.yml documentor/catalog/helix/publish/audiences/developer.yml documentor/catalog/traits/significant.yml documentor/catalog/ci/github-actions.yml documentor/architecture/js/stage.mjs documentor/deliverable/render-deck.js documentor/deliverable/deck-qa.py documentor/deliverable/lib/script.js documentor/deliverable/icons/ documentor/deliverable/package.json; do
  python3 -m zipfile -l "$wheel" | grep -q "$member" || fail "the wheel lacks $member"
done
uv run --isolated --no-project --with "$wheel" documentor --version | grep -q "^documentor .*HELIX catalog packaged" || fail "an installed documentor reads its packaged catalog"
uv run --isolated --no-project --with "$wheel" documentor --catalog "$repo_root/../../workflows" --version | grep -q "HELIX catalog live" \
  || fail "--catalog names the HELIX catalog to read"
uv run --isolated --no-project --with "$wheel" documentor --catalog "$tmpdir" --version >/dev/null 2>&1 && fail "--catalog refuses a directory that is no HELIX catalog"
uv run --isolated --no-project --with "$wheel" documentor detect --help >/dev/null || fail "the installed CLI should run detect"
echo "OK: the wheel carries the catalog and the CLI answers from a clean environment"
