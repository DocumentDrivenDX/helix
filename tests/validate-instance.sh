#!/usr/bin/env bash
# Exercise skills/helix/scripts/validate-instance.py against catalog examples
# (expect exit 0) and a deliberately broken PRD fixture (expect exit 1 with
# specific check ids).
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
validator="$repo_root/skills/helix/scripts/validate-instance.py"
fixtures="$repo_root/tests/fixtures/validate-instance"
tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

fail() { echo "FAIL: $*" >&2; exit 1; }

# Catalog examples that satisfy their own validation block must pass.
for example in \
  01-frame/artifacts/prd \
  02-design/artifacts/adr \
  06-iterate/artifacts/status-report \
  01-frame/artifacts/feature-registry \
  01-frame/artifacts/risk-register \
  03-test/artifacts/story-test-plan \
  06-iterate/artifacts/metric-definition; do
  path="$repo_root/workflows/activities/$example/example.md"
  python3 "$validator" "$path" >"$tmpdir/out" 2>&1 \
    || fail "$example/example.md should validate cleanly:
$(cat "$tmpdir/out")"
  grep -q "type=${example##*/} " "$tmpdir/out" \
    || fail "$example/example.md should resolve to type ${example##*/}:
$(cat "$tmpdir/out")"
done

# Broken PRD: missing required section, leftover placeholder, failed catalog regex.
if python3 "$validator" "$fixtures/broken-prd.md" --catalog "$repo_root/workflows" >"$tmpdir/broken.out" 2>&1; then
  fail "broken-prd.md should exit 1"
fi
for check in required_sections.success_criteria placeholder automated_checks.0; do
  grep -Eq "^BLOCKING +$check " "$tmpdir/broken.out" \
    || fail "broken-prd.md output should contain blocking check '$check':
$(cat "$tmpdir/broken.out")"
done

# JSON output carries the same findings and a summary.
python3 - "$validator" "$fixtures/broken-prd.md" <<'PYEOF' || fail "json output shape is wrong"
import json, subprocess, sys
proc = subprocess.run([sys.executable, sys.argv[1], sys.argv[2], "--format", "json"], capture_output=True, text=True)
data = json.loads(proc.stdout)
assert proc.returncode == 1, proc.returncode
assert data["type"] == "prd" and data["catalog"] and data["instance"], data
checks = {f["check"] for f in data["findings"] if f["severity"] == "blocking"}
assert {"required_sections.success_criteria", "placeholder", "automated_checks.0"} <= checks, checks
assert data["summary"]["blocking"] == len([f for f in data["findings"] if f["severity"] == "blocking"]) >= 3, data["summary"]
assert all(f["check"] == "placeholder" and f["line"] for f in data["findings"] if f["check"] == "placeholder"), "placeholder findings need a line"
PYEOF

# Unresolvable type is a usage error (exit 2), not a validation failure.
printf -- '---\nddx:\n  id: X-1\n  authoring:\n    home: repo\n---\n# untyped\n' >"$tmpdir/untyped.md"
if python3 "$validator" "$tmpdir/untyped.md" --catalog "$repo_root/workflows" >"$tmpdir/untyped.out" 2>&1; then
  fail "untyped instance should not validate"
fi
grep -q "could not resolve the artifact type" "$tmpdir/untyped.out" \
  || fail "untyped instance should report an unresolvable type"

# --type resolves it; the near-empty document then fails on required_sections.
python3 "$validator" "$tmpdir/untyped.md" --catalog "$repo_root/workflows" --type prd >"$tmpdir/typed.out" 2>&1 && \
  fail "--type prd on an empty document should still fail required_sections"
grep -q "type=prd " "$tmpdir/typed.out" || fail "--type should select the prd type"

echo "OK: validate-instance.py passes catalog examples, rejects the broken PRD fixture, and errors on unresolvable types"
