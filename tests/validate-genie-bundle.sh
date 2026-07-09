#!/usr/bin/env bash
# Validate that the generated Databricks Genie bundle is self-contained and
# reflects the canonical source catalog under workflows/.

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

fail() {
  printf 'genie bundle validation failed: %s\n' "$*" >&2
  exit 1
}

bundle_parent="$(mktemp -d)"
expected_refs="$(mktemp -d)"
trap 'rm -rf "$bundle_parent" "$expected_refs"' EXIT

bash "$repo_root/scripts/build-genie-bundle.sh" --out "$bundle_parent" >/dev/null
python3 "$repo_root/scripts/sync_references.py" "$expected_refs" >/dev/null

bundle_root="$bundle_parent/helix"

[[ -f "$bundle_root/SKILL.md" ]] || fail "missing bundle SKILL.md"
[[ -f "$bundle_root/library/skill-prompts/stop-at-triggers.yml" ]] || \
  fail "missing bundle library prompt"
[[ ! -e "$bundle_root/workflows" ]] || \
  fail "Genie bundle must not carry a duplicate workflows/ tree"

if ! diff -r "$expected_refs" "$bundle_root/references" >/dev/null 2>&1; then
  diff -r "$expected_refs" "$bundle_root/references" >&2 || true
  fail "bundle references differ from workflows/ source; run scripts/build-genie-bundle.sh"
fi

bash "$repo_root/tests/install/shared/verify-skill-layout.sh" "$bundle_root" >/dev/null

echo "validated generated Genie bundle"
