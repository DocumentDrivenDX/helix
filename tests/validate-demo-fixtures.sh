#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
demo_script="$repo_root/docs/demos/helix-concerns/demo.sh"
fixture_dir="$repo_root/docs/demos/helix-concerns/agent-dictionary"

fail() {
  printf 'demo fixture validation failed: %s\n' "$*" >&2
  exit 1
}

assert_fixture_matches_demo_prompt() {
  local script_path="$1"
  local agent_dictionary_dir="$2"
  local expected_command="$3"
  local stale_command="$4"

  python3 - "$script_path" "$agent_dictionary_dir" "$expected_command" "$stale_command" <<'PYEOF'
import hashlib
import json
from pathlib import Path
import sys

script_path = Path(sys.argv[1])
fixture_dir = Path(sys.argv[2])
expected_command = sys.argv[3]
stale_command = sys.argv[4]

start_marker = "agent_run <<'REVIEW_PROMPT'"
end_marker = "REVIEW_PROMPT"

script_lines = script_path.read_text(encoding="utf-8").splitlines()
capturing = False
found_end = False
prompt_lines = []
for line in script_lines:
    if capturing:
        if line.strip() == end_marker:
            found_end = True
            break
        prompt_lines.append(line)
    elif line.strip() == start_marker:
        capturing = True

if not capturing or not found_end or not prompt_lines:
    raise SystemExit("failed to extract REVIEW_PROMPT heredoc from helix-concerns demo")

expected_prompt = "\n".join(prompt_lines)
prompt_line_set = {line.strip() for line in prompt_lines}
expected_hash = hashlib.sha256(expected_prompt.encode("utf-8")).hexdigest()[:16]
fixture_path = fixture_dir / f"{expected_hash}.json"

if not fixture_path.is_file():
    raise SystemExit(
        f"missing fixture for extracted review prompt hash: {fixture_path.name}"
    )

with fixture_path.open(encoding="utf-8") as fh:
    payload = json.load(fh)

prompt = payload.get("prompt")
prompt_hash = payload.get("prompt_hash")
prompt_len = payload.get("prompt_len")

if prompt != expected_prompt:
    raise SystemExit("fixture prompt text does not match the demo REVIEW_PROMPT body")
if prompt_hash != expected_hash:
    raise SystemExit("fixture prompt_hash does not match the demo REVIEW_PROMPT hash")
if prompt_len != len(expected_prompt):
    raise SystemExit("fixture prompt_len does not match the demo REVIEW_PROMPT length")
if hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16] != expected_hash:
    raise SystemExit("fixture prompt hash is not the SHA-256 truncation of the prompt text")
if expected_command not in prompt_line_set:
    raise SystemExit("REVIEW_PROMPT body does not include the labeled review-finding command")
if stale_command in prompt_line_set:
    raise SystemExit("REVIEW_PROMPT body still includes the stale unlabeled review-finding command")
PYEOF
}

expected_command='ddx bead create "drift: <description>" --type task --labels helix,phase:build,review-finding,area:testing'
stale_command='ddx bead create "drift: <description>" --type task --labels helix,phase:build,review-finding'

[[ ! -e "$repo_root/docs/demos/helix-concerns/agent-dictionary/e049bf7ab8d7b559.json" ]] \
  || fail "stale helix-concerns replay fixture should be removed after prompt hash changes"

assert_fixture_matches_demo_prompt "$demo_script" "$fixture_dir" "$expected_command" "$stale_command"

printf 'validated demo fixtures\n'
