#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

validator="python3 scripts/validate_surface_leakage.py"
fixtures="tests/fixtures/surface-leakage"

tmp_output="$(mktemp)"
trap 'rm -f "$tmp_output"' EXIT

echo "Checking allowed surface-leakage fixtures..."
$validator "$fixtures/allowed"

echo "Checking disallowed surface-leakage fixtures..."
if $validator "$fixtures/disallowed" >"$tmp_output" 2>&1; then
  echo "FAIL: disallowed fixtures should produce SURFACE_LEAK findings" >&2
  exit 1
fi

grep -Fq "SURFACE_LEAK" "$tmp_output" || {
  echo "FAIL: validator did not emit SURFACE_LEAK findings" >&2
  cat "$tmp_output" >&2
  exit 1
}

grep -Fq "prd-command-fr.md" "$tmp_output" || {
  echo "FAIL: PRD leakage fixture was not reported" >&2
  cat "$tmp_output" >&2
  exit 1
}

grep -Fq "feature-endpoint.md" "$tmp_output" || {
  echo "FAIL: Feature Spec leakage fixture was not reported" >&2
  cat "$tmp_output" >&2
  exit 1
}

grep -Fq "story-payload-ac.md" "$tmp_output" || {
  echo "FAIL: User Story leakage fixture was not reported" >&2
  cat "$tmp_output" >&2
  exit 1
}

grep -Fq "td-inline-api.md" "$tmp_output" || {
  echo "FAIL: Technical Design inline API fixture was not reported" >&2
  cat "$tmp_output" >&2
  exit 1
}

echo "OK: surface-leakage validator fixtures pass"
