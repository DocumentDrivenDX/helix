#!/usr/bin/env bash
# Exercise skills/helix/scripts/validate-instance.py against catalog examples
# (expect exit 0) and a deliberately broken PRD fixture (expect exit 1 with
# specific check ids).
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python3 "$repo_root/tests/test_document_history.py"
python3 "$repo_root/tests/test_living_documents.py"
validator="$repo_root/skills/helix/scripts/validate-instance.py"
fixtures="$repo_root/tests/fixtures/validate-instance"
tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

fail() { echo "FAIL: $*" >&2; exit 1; }

# Every catalog example must satisfy its own type's validation block and
# resolve to the type whose directory it lives in.
count=0
for path in "$repo_root"/workflows/activities/*/artifacts/*/example*.md; do
  type_id="$(basename "$(dirname "$path")")"
  rel="${path#"$repo_root"/workflows/activities/}"
  python3 "$validator" "$path" >"$tmpdir/out" 2>&1 \
    || fail "$rel should validate cleanly:
$(cat "$tmpdir/out")"
  grep -q "type=$type_id " "$tmpdir/out" \
    || fail "$rel should resolve to type $type_id:
$(cat "$tmpdir/out")"
  count=$((count + 1))
done
[ "$count" -ge 50 ] || fail "expected to validate every catalog example, ran $count"

# Optional UX sections: each fixture fills its type's optional sections and must validate.
ux=0
for path in "$fixtures"/ux/*.md; do
  type_id="$(basename "$path" .md)"
  python3 "$validator" "$path" --catalog "$repo_root/workflows" >"$tmpdir/out" 2>&1 \
    || fail "ux/$type_id.md should validate cleanly:
$(cat "$tmpdir/out")"
  grep -q "type=$type_id " "$tmpdir/out" || fail "ux/$type_id.md should resolve to type $type_id"
  ux=$((ux + 1))
done
[ "$ux" -eq 9 ] || fail "expected 9 optional-section fixtures, ran $ux"

# Broken PRD: missing required section, leftover placeholder, failed catalog regex.
if python3 "$validator" "$fixtures/broken-prd.md" --catalog "$repo_root/workflows" >"$tmpdir/broken.out" 2>&1; then
  fail "broken-prd.md should exit 1"
fi
for check in required_sections.success_criteria placeholder pattern_checks.0; do
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
assert {"required_sections.success_criteria", "placeholder", "pattern_checks.0"} <= checks, checks
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

# Prose audit (workflows/voice.yml limits and phrase lists; workflows/references/writing-pass.md).
# Artifacts are the system of record and are not audited; a deliverable is a projection people read,
# and its example meets its voice profile. Guide pages are checked by documentor
# (tests/validate-publish.sh).
audited=0
for path in "$repo_root"/workflows/activities/*/artifacts/*/example*.md; do
  grep -q "audience: human" "$(dirname "$path")/meta.yml" || continue
  audited=$((audited + 1))
  rel="${path#"$repo_root"/workflows/activities/}"
  python3 "$validator" "$path" --strict-prose >"$tmpdir/strict.out" 2>&1 \
    || fail "$rel should meet its voice profile's prose rules:
$(grep 'prose\.' "$tmpdir/strict.out")"
done
[ "$audited" -ge 1 ] || fail "expected the deliverable example to be audited, ran $audited"

# A breach is a warning by default and blocking with --strict-prose; a quoted phrase and a
# generated block are not read.
prose="$tmpdir/prose.md"
cp "$repo_root/workflows/activities/06-iterate/artifacts/deliverable/example.md" "$prose"
{
  printf '\nThis document serves as the guide, and her token is checked when the gateway and the store and the queue and the cache and the scheduler and the worker and the index all agree on the same request at the same time.\n'
  printf '\nWrite "is", not "serves as".\n'
  printf '\n<!-- architecture-view: context -->\nThis document serves as a generated block.\n<!-- /architecture-view -->\n'
} >>"$prose"
python3 "$validator" "$prose" --catalog "$repo_root/workflows" >"$tmpdir/prose.out" 2>&1 \
  || fail "prose findings should be warnings without --strict-prose:
$(cat "$tmpdir/prose.out")"
for check in prose.sentence; do
  grep -Eq "^WARNING +$check " "$tmpdir/prose.out" || fail "expected warning $check:
$(cat "$tmpdir/prose.out")"
done
for phrase in '"this document"' '"serves as"' '"her"'; do
  grep -F "prose.avoid  $phrase" "$tmpdir/prose.out" >/dev/null || fail "expected avoided phrase $phrase:
$(cat "$tmpdir/prose.out")"
done
[ "$(grep -cF 'prose.avoid  "serves as"' "$tmpdir/prose.out")" -eq 1 ] \
  || fail "a quoted phrase and a generated block must not be matched:
$(cat "$tmpdir/prose.out")"
if python3 "$validator" "$prose" --catalog "$repo_root/workflows" --strict-prose >"$tmpdir/strict.out" 2>&1; then
  fail "--strict-prose should make prose findings blocking"
fi
grep -Eq "^BLOCKING +prose\.sentence " "$tmpdir/strict.out" || fail "--strict-prose should report blocking prose.sentence"

# An agent-read type (an ADR) is not audited; a project's .helix.yml can make findings blocking and
# list paths to skip.
project="$tmpdir/project"
mkdir -p "$project/docs/helix/02-design/adr" "$project/docs/helix/04-build"
decided="$project/docs/helix/02-design/adr/ADR-900-decided.md"
sed 's/^  id: \(.*\)$/  id: \1\
  status: accepted/' "$repo_root/workflows/activities/02-design/artifacts/adr/example.md" >"$decided"
grep -q "^  status: accepted$" "$decided" || fail "test setup: could not mark the ADR accepted"
printf '\nThis document serves as a record that is decided and will not be rewritten by anyone at all for any reason whatsoever in any case.\n' >>"$decided"
python3 "$validator" "$decided" --catalog "$repo_root/workflows" --strict-prose >"$tmpdir/decided.out" 2>&1 \
  || fail "an agent-read type should not be audited:
$(cat "$tmpdir/decided.out")"
grep -q "prose\." "$tmpdir/decided.out" && fail "an agent-read type produced prose findings"
cp "$prose" "$project/docs/helix/02-design/overview.md"
printf 'prose:\n  strict: true\n  exempt:\n    - "docs/helix/04-build/*"\n' >"$project/.helix.yml"
if python3 "$validator" "$project/docs/helix/02-design/overview.md" --catalog "$repo_root/workflows" --type deliverable >"$tmpdir/project.out" 2>&1; then
  fail ".helix.yml prose.strict should make findings blocking"
fi
cp "$prose" "$project/docs/helix/04-build/log.md"
python3 "$validator" "$project/docs/helix/04-build/log.md" --catalog "$repo_root/workflows" --type deliverable >"$tmpdir/exempt.out" 2>&1
grep -q "prose\." "$tmpdir/exempt.out" && fail "a path listed in .helix.yml prose.exempt should not be audited"

echo "OK: validate-instance.py passes all $count catalog examples and $ux optional-section fixtures, holds the deliverable to its voice profile, rejects the broken PRD fixture, and errors on unresolvable types"
