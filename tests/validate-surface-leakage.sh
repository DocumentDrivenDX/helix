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

echo "Checking allowed retired-public-surface fixtures..."
$validator --retired-public-surfaces \
  --retired-allow-glob "tests/fixtures/surface-leakage/retired-public/allowed/historical/**" \
  "$fixtures/retired-public/allowed"

echo "Checking disallowed retired-public-surface fixtures..."
if $validator --retired-public-surfaces \
  "$fixtures/retired-public/disallowed" >"$tmp_output" 2>&1; then
  echo "FAIL: disallowed retired public surface fixtures should produce RETIRED_PUBLIC_SURFACE findings" >&2
  exit 1
fi

grep -Fq "RETIRED_PUBLIC_SURFACE" "$tmp_output" || {
  echo "FAIL: retired public surface validator did not emit RETIRED_PUBLIC_SURFACE findings" >&2
  cat "$tmp_output" >&2
  exit 1
}

for fixture in env-routing.md sibling-skill.md scope-selector.md missing-script.md spec-status.md; do
  grep -Fq "$fixture" "$tmp_output" || {
    echo "FAIL: retired public surface fixture was not reported: $fixture" >&2
    cat "$tmp_output" >&2
    exit 1
  }
done

grep -Fq "SURFACE_LEAK" "$tmp_output" && {
  echo "FAIL: retired public surface failures must not use SURFACE_LEAK class" >&2
  cat "$tmp_output" >&2
  exit 1
}

echo "OK: surface-leakage validator fixtures pass"
