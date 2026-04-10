#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
validator="$repo_root/scripts/validate_deploy_artifact_graph.py"
artifacts_dir="$repo_root/workflows/phases/05-deploy/artifacts"

fail() {
  printf 'deploy artifact validation failed: %s\n' "$*" >&2
  exit 1
}

assert_contains() {
  local haystack="$1"
  local needle="$2"
  local message="$3"

  if [[ "$haystack" != *"$needle"* ]]; then
    fail "$message"$'\n'"expected to find: $needle"$'\n'"in output: $haystack"
  fi
}

run_validator() {
  python3 "$validator" "$@"
}

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

pass_output="$(run_validator --artifacts-dir "$artifacts_dir" 2>&1)" \
  || fail "expected current deploy artifact graph to validate, got: $pass_output"
assert_contains "$pass_output" "validated deploy artifact graph" \
  "validator should report success for the checked-in deploy artifact graph"

later_dir="$tmpdir/later-edge"
mkdir -p "$later_dir"
cp -rf "$artifacts_dir"/. "$later_dir"/
python3 - "$later_dir/monitoring-setup/meta.yml" <<'PYEOF'
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
needle = "    - input: Architecture\n      type: artifact\n      path: architecture\n      required: false\n      note: \"Service boundaries and dependencies that affect signal design\"\n"
replacement = "    - input: Release Notes\n      type: artifact\n      path: release-notes\n      required: false\n      note: \"Invalid fixture: later deploy artifact dependency\"\n"
if needle not in text:
    raise SystemExit(f"expected fixture block not found in {path}")
path.write_text(text.replace(needle, replacement, 1), encoding="utf-8")
PYEOF

set +e
later_output="$(run_validator --artifacts-dir "$later_dir" 2>&1)"
later_status=$?
set -e
[[ $later_status -ne 0 ]] || fail "validator should fail when a deploy artifact requires a later artifact"
assert_contains "$later_output" "requires later deploy artifact release-notes" \
  "later-artifact fixture should mention the invalid dependency"

cycle_dir="$tmpdir/cycle"
mkdir -p "$cycle_dir"
cp -rf "$artifacts_dir"/. "$cycle_dir"/
python3 - "$cycle_dir/monitoring-setup/meta.yml" <<'PYEOF'
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
needle = "    - input: Architecture\n      type: artifact\n      path: architecture\n      required: false\n      note: \"Service boundaries and dependencies that affect signal design\"\n"
replacement = "    - input: Runbook\n      type: artifact\n      path: runbook\n      required: false\n      note: \"Invalid fixture: creates a deploy dependency cycle\"\n"
if needle not in text:
    raise SystemExit(f"expected fixture block not found in {path}")
path.write_text(text.replace(needle, replacement, 1), encoding="utf-8")
PYEOF

set +e
cycle_output="$(run_validator --artifacts-dir "$cycle_dir" 2>&1)"
cycle_status=$?
set -e
[[ $cycle_status -ne 0 ]] || fail "validator should fail when deploy artifacts contain a cycle"
assert_contains "$cycle_output" "deploy artifact dependency cycle detected" \
  "cycle fixture should report the dependency cycle"

printf 'validated deploy artifact graph checks\n'
