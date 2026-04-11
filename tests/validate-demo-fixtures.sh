#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
demo_script="$repo_root/docs/demos/helix-concerns/demo.sh"
agent_fixture="$repo_root/docs/demos/helix-concerns/agent-dictionary/343d7e245e903303.json"

fail() {
  printf 'demo fixture validation failed: %s\n' "$*" >&2
  exit 1
}

assert_contains() {
  local path="$1"
  local needle="$2"
  local message="$3"

  [[ -f "$path" ]] || fail "missing file: $path"
  grep -Fq "$needle" "$path" || fail "$message"
}

assert_not_contains() {
  local path="$1"
  local needle="$2"
  local message="$3"

  [[ -f "$path" ]] || fail "missing file: $path"
  if grep -Fxq "$needle" "$path"; then
    fail "$message"
  fi
}

assert_fixture_prompt() {
  local path="$1"
  local expected_prompt="$2"
  local expected_hash="$3"

  python3 - "$path" "$expected_prompt" "$expected_hash" <<'PYEOF'
import hashlib
import json
import sys

path, expected_prompt, expected_hash = sys.argv[1:4]
with open(path, encoding="utf-8") as fh:
    payload = json.load(fh)

prompt = payload.get("prompt")
prompt_hash = payload.get("prompt_hash")
prompt_len = payload.get("prompt_len")

if prompt != expected_prompt:
    raise SystemExit("fixture prompt text does not match the expected review command")
if prompt_hash != expected_hash:
    raise SystemExit("fixture prompt_hash does not match the expected prompt hash")
if prompt_len != len(expected_prompt):
    raise SystemExit("fixture prompt_len does not match the prompt text length")
if hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16] != expected_hash:
    raise SystemExit("fixture prompt hash is not the SHA-256 truncation of the prompt text")
PYEOF
}

expected_command='ddx bead create "drift: <description>" --type task --labels helix,phase:build,review-finding,area:testing'
stale_command='ddx bead create "drift: <description>" --type task --labels helix,phase:build,review-finding'
expected_prompt=$'Read docs/helix/01-frame/concerns.md first — it declares typescript-bun.\n\nReview the last commit (git diff HEAD~1) for concern drift.\nThe typescript-bun concern says:\n- Use bun:test, NOT Vitest or Jest\n- Use Biome, NOT ESLint or Prettier\n- Use Bun.serve(), NOT Express or Node http\n\nCheck every file in the diff. Report any imports, tools, or patterns\nthat violate the declared concerns. Be specific about which file and\nline has the drift.\n\nCreate a tracker issue for each drift finding:\nddx bead create "drift: <description>" --type task --labels helix,phase:build,review-finding,area:testing'
expected_hash='343d7e245e903303'

[[ ! -e "$repo_root/docs/demos/helix-concerns/agent-dictionary/e049bf7ab8d7b559.json" ]] \
  || fail "stale helix-concerns replay fixture should be removed after prompt hash changes"

assert_contains \
  "$demo_script" \
  "$expected_command" \
  "helix-concerns demo should file review findings with an area label"
assert_fixture_prompt "$agent_fixture" "$expected_prompt" "$expected_hash"
assert_not_contains \
  "$demo_script" \
  "$stale_command" \
  "helix-concerns demo should not retain the stale unlabeled review-finding command"

printf 'validated demo fixtures\n'
