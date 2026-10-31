#!/usr/bin/env bash
# Slot Registry Integrity: the shipped registry passes, and each rule rejects
# a broken fixture.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
check="$repo_root/scripts/check_concern_slots.py"
tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

python3 "$check" || { echo "FAIL: shipped slot registry has integrity findings" >&2; exit 1; }

concern() { # name slot-or-empty
  mkdir -p "$tmpdir/c/$1"
  if [ -n "$2" ]; then printf '# Concern\n\n## Slot\n%s\n' "$2" >"$tmpdir/c/$1/concern.md"
  else printf '# Concern\n\n## Areas\nall\n' >"$tmpdir/c/$1/concern.md"; fi
}
concern run-a language-runtime
concern run-b language-runtime
concern host-x deploy-target
concern store-x datastore
concern ui-kit ""

expect_fail() { # label registry-body expected-substring
  printf '%s\n' "$2" >"$tmpdir/c/slots.yml"
  if python3 "$check" --concerns "$tmpdir/c" 2>"$tmpdir/err"; then
    echo "FAIL: $1 was accepted" >&2; exit 1
  fi
  grep -q "$3" "$tmpdir/err" || { echo "FAIL: $1 reported: $(cat "$tmpdir/err")" >&2; exit 1; }
}

base='slots:
  language-runtime: { exclusive: true }
  deploy-target: { exclusive: true }
  datastore: { exclusive: true }'

printf '%s\ndefaults:\n  language-runtime: run-a\nprofiles:\n  host-x:\n    when: { deploy-target: host-x }\n    defaults: { language-runtime: run-b, datastore: store-x }\n    compose: [ui-kit]\n' "$base" >"$tmpdir/c/slots.yml"
python3 "$check" --concerns "$tmpdir/c" || { echo "FAIL: valid profile fixture rejected" >&2; exit 1; }

expect_fail "duplicate default" "$base
defaults:
  language-runtime: run-a
  language-runtime: run-b" "duplicate key"
expect_fail "default with wrong slot" "$base
defaults:
  language-runtime: store-x" "## Slot"
expect_fail "unknown concern" "$base
defaults:
  language-runtime: missing" "not a library concern"
expect_fail "profile defaults its trigger slot" "$base
profiles:
  host-x:
    when: { deploy-target: host-x }
    defaults: { deploy-target: host-x }" "own trigger slot"
expect_fail "profile key differs from trigger" "$base
profiles:
  other:
    when: { deploy-target: host-x }" "triggered by"
expect_fail "slot concern under compose" "$base
profiles:
  host-x:
    when: { deploy-target: host-x }
    compose: [store-x]" "put it under defaults"
expect_fail "undeclared slot in concern" "slots:
  language-runtime: { exclusive: true }" "undeclared slot"

echo "concern slot registry: ok"
