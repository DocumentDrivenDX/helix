#!/usr/bin/env bash
# Deliverable gate: the catalog example passes check-deliverable.py and a
# broken script is rejected with the expected check ids.
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
checker="$repo_root/skills/helix/scripts/check-deliverable.py"
example="$repo_root/workflows/activities/06-iterate/artifacts/deliverable/example.md"
broken="$repo_root/tests/fixtures/validate-deliverable/broken-deck.md"
fail() { printf 'deliverable validation failed: %s\n' "$*" >&2; exit 1; }
python3 "$checker" "$example" >/dev/null || fail "catalog deliverable example does not pass check-deliverable.py"
out="$(python3 "$checker" "$broken" 2>&1 || true)"
for id in title.claim title.slop horizontal_logic vocabulary numbers.sourced visual.generic deck.order render.inspected placeholder; do
  grep -Fq "$id" <<<"$out" || fail "broken fixture should report $id; got: $out"
done
if python3 "$checker" "$broken" >/dev/null 2>&1; then fail "broken fixture should exit non-zero"; fi
echo "OK: check-deliverable.py passes the catalog example and rejects the broken deck fixture"
