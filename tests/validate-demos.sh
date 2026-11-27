#!/usr/bin/env bash
# Validate every committed demo session record and render it to .cast.
#
# Each demo lives at docs/demos/<slug>/session.jsonl. The render is
# deterministic, so this test asserts that re-rendering produces a
# byte-identical cast file (unless the committed cast is intentionally
# stale because session.jsonl was just updated, in which case the test
# rebuilds it).
set -euo pipefail

. "$(dirname "${BASH_SOURCE[0]}")/../scripts/lib/uvpy.sh"

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
demos_root="$repo_root/docs/demos"
cast_root="$repo_root/website/static/demos"
render="$repo_root/scripts/demos/render_session.py"
validate="$repo_root/scripts/demos/validate_session.py"
check_assertions="$repo_root/scripts/demos/check_assertions.py"
capture="$repo_root/scripts/demos/capture_session.py"
capture_fixture="$repo_root/tests/fixtures/demo-capture/sample.stream.jsonl"

fail() {
  printf 'demo validation failed: %s\n' "$*" >&2
  exit 1
}

shopt -s nullglob
sessions=("$demos_root"/*/session.jsonl)
if (( ${#sessions[@]} == 0 )); then
  printf 'no demo session records found under %s\n' "$demos_root"
  exit 0
fi

# Schema-level validation.
uvpy "$validate" "${sessions[@]}" || fail "session schema validation failed"

# Assertion check for demos that ship an assertions.yml.
demo_dirs=()
for s in "${sessions[@]}"; do
  demo_dirs+=("$(dirname "$s")")
done
uvpy "$check_assertions" "${demo_dirs[@]}" || fail "demo assertions failed"

# Render each, compare to committed cast.
for session in "${sessions[@]}"; do
  slug="$(basename "$(dirname "$session")")"
  expected="$cast_root/${slug}.cast"
  rendered="$(mktemp)"
  uvpy "$render" "$session" --output "$rendered" >/dev/null \
    || fail "render failed for $slug"

  if [[ -f "$expected" ]]; then
    if ! diff -q "$rendered" "$expected" >/dev/null 2>&1; then
      fail "rendered $slug differs from committed $expected — re-render and commit"
    fi
    printf 'demo %s: cast matches committed (%d events)\n' "$slug" \
      "$(($(wc -l < "$rendered") - 1))"
  else
    printf 'demo %s: no committed cast yet (rendered ok)\n' "$slug"
  fi
  rm -f "$rendered"
done

# Smoke-test capture_session.py: translate a committed stream-json fixture
# through the script and assert the produced session.jsonl parses cleanly.
smoke_session="$(mktemp)"
uvpy "$capture" helix-smoke \
  --prompt "smoke" \
  --from-stream "$capture_fixture" \
  --output "$smoke_session" >/dev/null \
  || fail "capture_session.py --from-stream failed"
uvpy "$validate" "$smoke_session" >/dev/null \
  || fail "capture_session.py produced a session that fails schema validation"

# Sanity-check the translation: the fixture has 1 user prompt + 2 tool_use +
# 2 tool_result + 2 assistant-text events. After translation the
# session.jsonl should contain matching counts.
uvpy - "$smoke_session" <<'PY' || fail "capture_session.py translation counts wrong"
import json, sys
path = sys.argv[1]
counts = {"tool_call": 0, "tool_result": 0, "assistant": 0, "prompt": 0, "meta": 0}
for line in open(path, encoding="utf-8"):
    line = line.strip()
    if not line: continue
    obj = json.loads(line)
    for k in counts:
        if k in obj:
            counts[k] += 1
            break
expected = {"meta": 1, "prompt": 1, "tool_call": 2, "tool_result": 2, "assistant": 2}
for k, want in expected.items():
    got = counts[k]
    if got != want:
        raise SystemExit(f"{path}: expected {want} {k} events, got {got}")
PY
rm -f "$smoke_session"
printf 'capture smoke test: stream → session translation ok\n'
