#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
test_count=0

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

assert_eq() {
  local expected="$1"
  local actual="$2"
  local message="$3"
  if [[ "$expected" != "$actual" ]]; then
    printf 'expected:\n%s\nactual:\n%s\n' "$expected" "$actual" >&2
    fail "$message"
  fi
}

assert_contains() {
  local haystack="$1"
  local needle="$2"
  local message="$3"
  if [[ "$haystack" != *"$needle"* ]]; then
    printf 'missing substring: %s\nin:\n%s\n' "$needle" "$haystack" >&2
    fail "$message"
  fi
}

assert_file_exists() {
  local path="$1"
  local message="$2"
  [[ -f "$path" ]] || fail "$message"
}

assert_fails() {
  local message="$1"
  shift
  if "$@"; then
    fail "$message"
  fi
}

make_mock_bin() {
  local root="$1"
  mkdir -p "$root/bin" "$root/state"

  cat >"$root/bin/codex" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

state_root="${MOCK_STATE_ROOT:?}"

if [[ "$*" != *"--dangerously-bypass-approvals-and-sandbox"* ]]; then
  echo "mock codex expected --dangerously-bypass-approvals-and-sandbox" >&2
  exit 1
fi

if [[ "$*" != *"--progress-cursor"* ]]; then
  echo "mock codex expected --progress-cursor" >&2
  exit 1
fi

payload="$*"
mode="${MOCK_BACKFILL_MODE:-complete}"

record() {
  printf '%s\n' "$1" >> "$state_root/calls.log"
}

next_action() {
  local file="$state_root/next-actions"
  if [[ ! -s "$file" ]]; then
    echo STOP
    return
  fi
  head -n1 "$file"
  tail -n +2 "$file" > "$file.tmp" || true
  mv "$file.tmp" "$file"
}

case "$payload" in
  *"implementation action"*)
    record implement
    echo "implementation complete"
    ;;
  *"check action"*)
    record check
    action="$(next_action)"
    printf 'NEXT_ACTION: %s\n' "$action"
    echo "Recommended Command: mock"
    ;;
  *"alignment action"*)
    if [[ "${MOCK_ALIGN_FAIL:-0}" == "1" ]]; then
      echo "mock alignment failure" >&2
      exit 1
    fi
    record align
    echo "alignment complete"
    ;;
  *"backfill action"*)
    record backfill
    case "$mode" in
      complete)
        mkdir -p docs/helix/06-iterate/backfill-reports
        report="docs/helix/06-iterate/backfill-reports/BF-2099-01-01-repo.md"
        printf '# mock backfill report\n' > "$report"
        echo "Backfill Metadata"
        echo "BACKFILL_STATUS: COMPLETE"
        echo "BACKFILL_REPORT: $report"
        echo "RESEARCH_EPIC: hx-mock-backfill"
        ;;
      guidance)
        mkdir -p docs/helix/06-iterate/backfill-reports
        report="docs/helix/06-iterate/backfill-reports/BF-2099-01-01-guidance.md"
        printf '# mock guidance report\n' > "$report"
        echo "Backfill Metadata"
        echo "BACKFILL_STATUS: GUIDANCE_NEEDED"
        echo "BACKFILL_REPORT: $report"
        echo "RESEARCH_EPIC: hx-mock-backfill"
        ;;
      missing-report)
        echo "Backfill Metadata"
        echo "BACKFILL_STATUS: COMPLETE"
        echo "RESEARCH_EPIC: hx-mock-backfill"
        ;;
      blocked)
        mkdir -p docs/helix/06-iterate/backfill-reports
        report="docs/helix/06-iterate/backfill-reports/BF-2099-01-01-blocked.md"
        printf '# mock blocked report\n' > "$report"
        echo "Backfill Metadata"
        echo "BACKFILL_STATUS: BLOCKED"
        echo "BACKFILL_REPORT: $report"
        echo "RESEARCH_EPIC: hx-mock-backfill"
        ;;
      *)
        echo "unsupported mock backfill mode: $mode" >&2
        exit 1
        ;;
    esac
    ;;
  *"plan action"*)
    record plan
    echo "PLAN_STATUS: CONVERGED"
    echo "PLAN_DOCUMENT: docs/helix/02-design/plan-2099-01-01-repo.md"
    echo "PLAN_ROUNDS: 5"
    ;;
  *"polish action"*)
    record polish
    echo "POLISH_STATUS: CONVERGED"
    echo "POLISH_ROUNDS: 4"
    echo "ISSUES_MODIFIED: 3"
    echo "ISSUES_CREATED: 1"
    echo "ISSUES_MERGED: 2"
    ;;
  *"fresh-eyes review"*)
    record review
    echo "REVIEW_STATUS: CLEAN"
    echo "ISSUES_COUNT: 0"
    ;;
  *"experiment action"*)
    record experiment
    echo "EXPERIMENT_STATUS: ITERATION_COMPLETE"
    echo "EXPERIMENT_ITERATIONS: 1"
    echo "EXPERIMENT_KEPT: 0"
    echo "EXPERIMENT_BEST: test_runtime=4.2s (-0.0% vs baseline)"
    echo "EXPERIMENT_CONFIDENCE: 0.0"
    ;;
  *)
    record other
    echo "mock codex"
    ;;
esac
EOF

  cat >"$root/bin/claude" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

state_root="${MOCK_STATE_ROOT:?}"

if [[ "$*" != *"--dangerously-skip-permissions"* ]]; then
  echo "mock claude expected --dangerously-skip-permissions" >&2
  exit 1
fi

if [[ "$*" != *"--no-session-persistence"* ]]; then
  echo "mock claude expected --no-session-persistence" >&2
  exit 1
fi

if [[ "${MOCK_CLAUDE_SLEEP:-0}" -gt 0 ]]; then
  sleep "$MOCK_CLAUDE_SLEEP" &
  wait $!
  exit 0
fi

stdin_payload=""
if ! [[ -t 0 ]]; then
  stdin_payload="$(cat)"
fi
payload="$* $stdin_payload"
mode="${MOCK_BACKFILL_MODE:-complete}"

record() {
  printf '%s\n' "$1" >> "$state_root/calls.log"
}

next_action() {
  local file="$state_root/next-actions"
  if [[ ! -s "$file" ]]; then
    echo STOP
    return
  fi
  head -n1 "$file"
  tail -n +2 "$file" > "$file.tmp" || true
  mv "$file.tmp" "$file"
}

case "$payload" in
  *"implementation action"*)
    record implement
    echo "implementation complete"
    ;;
  *"check action"*)
    record check
    action="$(next_action)"
    printf 'NEXT_ACTION: %s\n' "$action"
    echo "Recommended Command: mock"
    ;;
  *"alignment action"*)
    if [[ "${MOCK_ALIGN_FAIL:-0}" == "1" ]]; then
      echo "mock alignment failure" >&2
      exit 1
    fi
    record align
    echo "alignment complete"
    ;;
  *"backfill action"*)
    record backfill
    case "$mode" in
      complete)
        mkdir -p docs/helix/06-iterate/backfill-reports
        report="docs/helix/06-iterate/backfill-reports/BF-2099-01-01-repo.md"
        printf '# mock backfill report\n' > "$report"
        echo "Backfill Metadata"
        echo "BACKFILL_STATUS: COMPLETE"
        echo "BACKFILL_REPORT: $report"
        echo "RESEARCH_EPIC: hx-mock-backfill"
        ;;
      *)
        echo "unsupported mock backfill mode: $mode" >&2
        exit 1
        ;;
    esac
    ;;
  *"plan action"*)
    record plan
    echo "PLAN_STATUS: CONVERGED"
    echo "PLAN_DOCUMENT: docs/helix/02-design/plan-2099-01-01-repo.md"
    echo "PLAN_ROUNDS: 5"
    ;;
  *"polish action"*)
    record polish
    echo "POLISH_STATUS: CONVERGED"
    echo "POLISH_ROUNDS: 4"
    echo "ISSUES_MODIFIED: 3"
    echo "ISSUES_CREATED: 1"
    echo "ISSUES_MERGED: 2"
    ;;
  *"fresh-eyes review"*)
    record review
    echo "REVIEW_STATUS: CLEAN"
    echo "ISSUES_COUNT: 0"
    ;;
  *"experiment action"*)
    record experiment
    echo "EXPERIMENT_STATUS: ITERATION_COMPLETE"
    echo "EXPERIMENT_ITERATIONS: 1"
    echo "EXPERIMENT_KEPT: 0"
    echo "EXPERIMENT_BEST: test_runtime=4.2s (-0.0% vs baseline)"
    echo "EXPERIMENT_CONFIDENCE: 0.0"
    ;;
  *)
    record other
    echo "mock claude"
    ;;
esac
EOF

  chmod +x "$root/bin/codex" "$root/bin/claude"
}

make_workspace() {
  local root
  root="$(mktemp -d)"
  mkdir -p "$root/work"
  make_mock_bin "$root"
  (
    cd "$root/work"
    git init -q
  )
  echo "$root"
}

# Seed the built-in tracker with ready issues for loop tests
seed_tracker() {
  local root="$1"
  local count="${2:-0}"
  local work_dir="$root/work"
  mkdir -p "$work_dir/.helix"
  local i
  for ((i = 0; i < count; i++)); do
    printf '{"id":"hx-mock-%d","title":"mock issue %d","type":"task","status":"open","priority":2,"labels":["helix"],"parent":"","spec-id":"","description":"","design":"","acceptance":"","deps":[],"assignee":"","notes":"","created":"2099-01-01T00:00:00Z","updated":"2099-01-01T00:00:00Z"}\n' "$i" "$i"
  done > "$work_dir/.helix/issues.jsonl"
}

# Close all tracker issues (simulates agent completing work)
close_all_issues() {
  local work_dir="$1/work"
  if [[ -f "$work_dir/.helix/issues.jsonl" ]]; then
    local tmp
    tmp="$(jq -c '.status = "closed"' "$work_dir/.helix/issues.jsonl")"
    printf '%s\n' "$tmp" > "$work_dir/.helix/issues.jsonl"
  fi
}

run_helix() {
  local root="$1"
  shift
  local cmd="${1:-help}"
  shift || true
  (
    cd "$root/work"
    HOME="$root/home" \
    PATH="$root/bin:$PATH" \
    MOCK_STATE_ROOT="$root/state" \
    HELIX_LIBRARY_ROOT="$repo_root/workflows" \
    bash "$repo_root/scripts/helix" "$cmd" --quiet "$@"
  )
}

# ── Tracker unit tests ──────────────────────────────────────────────

test_tracker_create_and_show() {
  local root
  root="$(make_workspace)"
  local id
  id="$(run_helix "$root" tracker create "Test issue" --type task --labels helix,phase:build)"
  [[ -n "$id" ]] || fail "tracker create should return an ID"

  local output
  output="$(run_helix "$root" tracker show "$id")"
  assert_contains "$output" "Test issue" "show should display title"
  assert_contains "$output" "helix" "show should display labels"
  rm -rf "$root"
}

test_tracker_ready_and_blocked() {
  local root
  root="$(make_workspace)"
  local id1 id2
  id1="$(run_helix "$root" tracker create "First")"
  id2="$(run_helix "$root" tracker create "Second")"
  run_helix "$root" tracker dep add "$id2" "$id1" >/dev/null

  local ready_count
  ready_count="$(run_helix "$root" tracker ready --json | jq 'length')"
  assert_eq "1" "$ready_count" "only unblocked issue should be ready"

  local blocked_count
  blocked_count="$(run_helix "$root" tracker blocked --json | jq 'length')"
  assert_eq "1" "$blocked_count" "blocked issue should show as blocked"

  run_helix "$root" tracker close "$id1" >/dev/null
  ready_count="$(run_helix "$root" tracker ready --json | jq 'length')"
  assert_eq "1" "$ready_count" "previously blocked issue should become ready after dep closes"

  local ready_id
  ready_id="$(run_helix "$root" tracker ready --json | jq -r '.[0].id')"
  assert_eq "$id2" "$ready_id" "the unblocked issue should be the second one"
  rm -rf "$root"
}

test_tracker_update_and_claim() {
  local root
  root="$(make_workspace)"
  local id
  id="$(run_helix "$root" tracker create "Claim me")"

  run_helix "$root" tracker update "$id" --claim >/dev/null
  local status
  status="$(run_helix "$root" tracker show "$id" --json | jq -r '.status')"
  assert_eq "in_progress" "$status" "claim should set status to in_progress"

  local assignee
  assignee="$(run_helix "$root" tracker show "$id" --json | jq -r '.assignee')"
  assert_eq "helix" "$assignee" "claim should set assignee to helix"
  rm -rf "$root"
}

test_tracker_status() {
  local root
  root="$(make_workspace)"
  run_helix "$root" tracker create "One" >/dev/null
  run_helix "$root" tracker create "Two" >/dev/null

  local output
  output="$(run_helix "$root" tracker status)"
  assert_contains "$output" "2 issues" "status should show total count"
  assert_contains "$output" "2 open" "status should show open count"
  rm -rf "$root"
}

# ── CLI integration tests ───────────────────────────────────────────

test_help() {
  local root
  root="$(make_workspace)"
  local output
  output="$(run_helix "$root" help)"
  assert_contains "$output" "helix run" "help should list run command"
  assert_contains "$output" "--review-every" "help should list review option"
  assert_contains "$output" "tracker" "help should list tracker command"
  rm -rf "$root"
}

test_check_dry_run() {
  local root
  root="$(make_workspace)"
  local output
  output="$(run_helix "$root" check --dry-run repo)"
  assert_contains "$output" "codex --dangerously-bypass-approvals-and-sandbox exec --progress-cursor -C" "dry-run should print codex command"
  assert_contains "$output" "actions/check.md" "dry-run should reference check action"
  rm -rf "$root"
}

test_backfill_dry_run() {
  local root
  root="$(make_workspace)"
  local output
  output="$(run_helix "$root" backfill --dry-run repo)"
  assert_contains "$output" "actions/backfill-helix-docs.md" "backfill dry-run should reference backfill action"
  assert_contains "$output" "This is a writable live session" "backfill dry-run should assert writable live execution"
  assert_contains "$output" "BACKFILL_STATUS" "backfill dry-run should require machine-readable trailer"
  rm -rf "$root"
}

test_run_stops_after_queue_drains() {
  local root
  root="$(make_workspace)"
  seed_tracker "$root" 2
  printf 'STOP\n' > "$root/state/next-actions"

  # The mock agent's implement call doesn't close issues, so we need to
  # close them after each implement call. We'll seed with 1 issue and
  # have the mock close it by manipulating the tracker file.
  seed_tracker "$root" 1

  # Override codex to also close the issue after implementing
  cat >"$root/bin/codex" <<'MOCK'
#!/usr/bin/env bash
set -euo pipefail
state_root="${MOCK_STATE_ROOT:?}"
record() { printf '%s\n' "$1" >> "$state_root/calls.log"; }
next_action() {
  local file="$state_root/next-actions"
  if [[ ! -s "$file" ]]; then echo STOP; return; fi
  head -n1 "$file"
  tail -n +2 "$file" > "$file.tmp" || true
  mv "$file.tmp" "$file"
}
payload="$*"
case "$payload" in
  *"implementation action"*)
    record implement
    # Close all open issues to simulate completing work
    if [[ -f .helix/issues.jsonl ]]; then
      tmp="$(jq -c '.status = "closed"' .helix/issues.jsonl)"
      printf '%s\n' "$tmp" > .helix/issues.jsonl
    fi
    echo "implementation complete"
    ;;
  *"check action"*)
    record check
    action="$(next_action)"
    printf 'NEXT_ACTION: %s\n' "$action"
    ;;
  *"alignment action"*)
    if [[ "${MOCK_ALIGN_FAIL:-0}" == "1" ]]; then
      echo "mock alignment failure" >&2; exit 1
    fi
    record align
    echo "alignment complete"
    ;;
  *) record other; echo "mock codex" ;;
esac
MOCK
  chmod +x "$root/bin/codex"

  local output
  output="$(run_helix "$root" run 2>&1)"

  local calls
  calls="$(cat "$root/state/calls.log")"
  assert_eq $'implement\ncheck' "$calls" "run should implement until drained, then check"
  assert_contains "$output" "helix: stopping after check returned STOP" "run should report why it stopped"
  rm -rf "$root"
}

test_run_periodic_alignment() {
  local root
  root="$(make_workspace)"
  seed_tracker "$root" 2
  printf 'STOP\n' > "$root/state/next-actions"

  # Mock agent that closes one issue per implement call
  cat >"$root/bin/codex" <<'MOCK'
#!/usr/bin/env bash
set -euo pipefail
state_root="${MOCK_STATE_ROOT:?}"
record() { printf '%s\n' "$1" >> "$state_root/calls.log"; }
next_action() {
  local file="$state_root/next-actions"
  if [[ ! -s "$file" ]]; then echo STOP; return; fi
  head -n1 "$file"
  tail -n +2 "$file" > "$file.tmp" || true
  mv "$file.tmp" "$file"
}
payload="$*"
case "$payload" in
  *"implementation action"*)
    record implement
    # Close first open issue
    if [[ -f .helix/issues.jsonl ]]; then
      first_open="$(jq -r 'select(.status == "open") | .id' .helix/issues.jsonl | head -1)"
      if [[ -n "$first_open" ]]; then
        tmp="$(jq -c "if .id == \"$first_open\" then .status = \"closed\" else . end" .helix/issues.jsonl)"
        printf '%s\n' "$tmp" > .helix/issues.jsonl
      fi
    fi
    echo "implementation complete"
    ;;
  *"check action"*)
    record check
    action="$(next_action)"
    printf 'NEXT_ACTION: %s\n' "$action"
    ;;
  *"alignment action"*)
    if [[ "${MOCK_ALIGN_FAIL:-0}" == "1" ]]; then
      echo "mock alignment failure" >&2; exit 1
    fi
    record align
    echo "alignment complete"
    ;;
  *) record other; echo "mock codex" ;;
esac
MOCK
  chmod +x "$root/bin/codex"

  run_helix "$root" run --review-every 2 >/dev/null

  local calls
  calls="$(cat "$root/state/calls.log")"
  assert_eq $'implement\nimplement\nalign\ncheck' "$calls" "periodic alignment should run after configured cycles"
  rm -rf "$root"
}

test_run_auto_aligns_once() {
  local root
  root="$(make_workspace)"
  # No issues — queue is empty from the start
  printf 'ALIGN\nSTOP\n' > "$root/state/next-actions"

  run_helix "$root" run >/dev/null

  local calls
  calls="$(cat "$root/state/calls.log")"
  assert_eq $'check\nalign\ncheck' "$calls" "run should auto-align once when check returns ALIGN"
  rm -rf "$root"
}

test_run_reports_periodic_alignment_failure() {
  local root
  root="$(make_workspace)"
  seed_tracker "$root" 1

  # Mock that closes issue on implement
  cat >"$root/bin/codex" <<'MOCK'
#!/usr/bin/env bash
set -euo pipefail
state_root="${MOCK_STATE_ROOT:?}"
record() { printf '%s\n' "$1" >> "$state_root/calls.log"; }
payload="$*"
case "$payload" in
  *"implementation action"*)
    record implement
    if [[ -f .helix/issues.jsonl ]]; then
      tmp="$(jq -c '.status = "closed"' .helix/issues.jsonl)"
      printf '%s\n' "$tmp" > .helix/issues.jsonl
    fi
    echo "implementation complete"
    ;;
  *"alignment action"*)
    echo "mock alignment failure" >&2; exit 1
    ;;
  *) record other; echo "mock codex" ;;
esac
MOCK
  chmod +x "$root/bin/codex"

  local output
  if output="$(run_helix "$root" run --review-every 1 2>&1)"; then
    fail "run should fail when periodic alignment fails"
  fi

  assert_contains "$output" "mock alignment failure" "run should surface the alignment failure"
  assert_contains "$output" "helix: periodic alignment failed after 1 cycles" "run should report why the loop exited"
  rm -rf "$root"
}

run_backfill_missing_report() {
  local root="$1"
  MOCK_BACKFILL_MODE=missing-report run_helix "$root" backfill repo >/dev/null
}

test_backfill_requires_report_marker() {
  local root
  root="$(make_workspace)"
  assert_fails "backfill should fail when the trailer omits BACKFILL_REPORT" \
    run_backfill_missing_report "$root"
  rm -rf "$root"
}

test_backfill_creates_report() {
  local root
  root="$(make_workspace)"
  local output
  output="$(run_helix "$root" backfill repo)"
  assert_contains "$output" "BACKFILL_STATUS: COMPLETE" "backfill should report completion"
  assert_file_exists "$root/work/docs/helix/06-iterate/backfill-reports/BF-2099-01-01-repo.md" "backfill should create the declared report"
  local calls
  calls="$(cat "$root/state/calls.log")"
  assert_eq $'backfill' "$calls" "backfill should invoke the backfill action once"
  rm -rf "$root"
}

test_installer_creates_launcher() {
  local root
  root="$(make_workspace)"
  (
    cd "$repo_root"
    HOME="$root/home" \
    CODEX_HOME="$root/codex-home" \
    CLAUDE_HOME="$root/claude-home" \
    bash scripts/install-local-skills.sh >/dev/null
  )

  [[ -x "$root/home/.local/bin/helix" ]] || fail "installer should create helix launcher"
  local launcher
  launcher="$(cat "$root/home/.local/bin/helix")"
  assert_contains "$launcher" 'exec bash "'$repo_root'/scripts/helix"' "launcher should invoke repo helix script through bash"
  rm -rf "$root"
}

test_claude_run_stops_after_queue_drains() {
  local root
  root="$(make_workspace)"
  seed_tracker "$root" 1
  printf 'STOP\n' > "$root/state/next-actions"

  # Mock claude that closes issues
  cat >"$root/bin/claude" <<'MOCK'
#!/usr/bin/env bash
set -euo pipefail
state_root="${MOCK_STATE_ROOT:?}"
stdin_payload=""
if ! [[ -t 0 ]]; then stdin_payload="$(cat)"; fi
payload="$* $stdin_payload"
record() { printf '%s\n' "$1" >> "$state_root/calls.log"; }
next_action() {
  local file="$state_root/next-actions"
  if [[ ! -s "$file" ]]; then echo STOP; return; fi
  head -n1 "$file"
  tail -n +2 "$file" > "$file.tmp" || true
  mv "$file.tmp" "$file"
}
case "$payload" in
  *"implementation action"*)
    record implement
    if [[ -f .helix/issues.jsonl ]]; then
      tmp="$(jq -c '.status = "closed"' .helix/issues.jsonl)"
      printf '%s\n' "$tmp" > .helix/issues.jsonl
    fi
    echo "implementation complete"
    ;;
  *"check action"*)
    record check
    action="$(next_action)"
    printf 'NEXT_ACTION: %s\n' "$action"
    ;;
  *"alignment action"*)
    record align; echo "alignment complete" ;;
  *) record other; echo "mock claude" ;;
esac
MOCK
  chmod +x "$root/bin/claude"

  local output
  output="$(run_helix "$root" run --claude 2>&1)"

  local calls
  calls="$(cat "$root/state/calls.log")"
  assert_eq $'implement\ncheck' "$calls" "claude run should implement until drained, then check"
  assert_contains "$output" "helix: stopping after check returned STOP" "claude run should report why it stopped"
  rm -rf "$root"
}

test_claude_run_auto_aligns() {
  local root
  root="$(make_workspace)"
  printf 'ALIGN\nSTOP\n' > "$root/state/next-actions"

  run_helix "$root" run --claude >/dev/null

  local calls
  calls="$(cat "$root/state/calls.log")"
  assert_eq $'check\nalign\ncheck' "$calls" "claude run should auto-align when check returns ALIGN"
  rm -rf "$root"
}

test_claude_check_dry_run() {
  local root
  root="$(make_workspace)"
  local output
  output="$(run_helix "$root" check --claude --dry-run repo)"
  assert_contains "$output" "claude -p --permission-mode bypassPermissions" "claude dry-run should print claude command"
  assert_contains "$output" "check action" "claude dry-run should reference check action"
  rm -rf "$root"
}

test_run_auto_unblock_on_wait() {
  local root
  root="$(make_workspace)"
  # First check returns WAIT, unblock attempt runs, second check returns STOP
  printf 'WAIT\nSTOP\n' > "$root/state/next-actions"

  local output
  output="$(run_helix "$root" run 2>&1)"

  local calls
  calls="$(cat "$root/state/calls.log")"
  assert_eq $'check\nimplement\ncheck' "$calls" "run should attempt implementation when check returns WAIT, then re-check"
  assert_contains "$output" "attempting to unblock" "run should report unblock attempt"
  rm -rf "$root"
}

test_run_no_auto_unblock_flag() {
  local root
  root="$(make_workspace)"
  printf 'WAIT\n' > "$root/state/next-actions"

  local output
  output="$(run_helix "$root" run --no-auto-unblock 2>&1)"

  local calls
  calls="$(cat "$root/state/calls.log")"
  assert_eq $'check' "$calls" "run --no-auto-unblock should not attempt implementation on WAIT"
  assert_contains "$output" "stopping after check returned WAIT" "run should stop on WAIT with --no-auto-unblock"
  rm -rf "$root"
}

test_extract_next_action_from_claude_output() {
  extract_next_action() {
    local stripped
    stripped="$(printf '%s\n' "$1" | sed 's/[*`]//g')"
    local result
    result="$(printf '%s\n' "$stripped" | grep -oE 'NEXT_ACTION: *(IMPLEMENT|ALIGN|BACKFILL|WAIT|GUIDANCE|STOP)' | head -n1 | sed 's/^NEXT_ACTION: *//')"
    printf '%s' "$result"
  }

  local result
  result="$(extract_next_action "## Queue Health
NEXT_ACTION: IMPLEMENT
Target issue: hx-mock-1")"
  assert_eq "IMPLEMENT" "$result" "extract plain NEXT_ACTION"

  result="$(extract_next_action "**NEXT_ACTION: WAIT**")"
  assert_eq "WAIT" "$result" "extract bold-wrapped NEXT_ACTION"

  result="$(extract_next_action '`NEXT_ACTION: STOP`')"
  assert_eq "STOP" "$result" "extract backtick-wrapped NEXT_ACTION"

  result="$(extract_next_action '**NEXT_ACTION:** GUIDANCE')"
  assert_eq "GUIDANCE" "$result" "extract bold-key NEXT_ACTION"

  result="$(extract_next_action 'NEXT_ACTION: **ALIGN**')"
  assert_eq "ALIGN" "$result" "extract bold-value NEXT_ACTION"

  result="$(extract_next_action 'Some preamble
\`NEXT_ACTION: BACKFILL\`
Some epilogue')"
  assert_eq "BACKFILL" "$result" "extract code-inline NEXT_ACTION"
}

test_plan_dry_run() {
  local root
  root="$(make_workspace)"
  local output
  output="$(run_helix "$root" plan --dry-run repo)"
  assert_contains "$output" "actions/plan.md" "plan dry-run should reference plan action"
  assert_contains "$output" "Plan scope: repo" "plan dry-run should include scope"
  assert_contains "$output" "Refinement rounds: 5" "plan dry-run should include default rounds"
  rm -rf "$root"
}

test_plan_custom_rounds() {
  local root
  root="$(make_workspace)"
  local output
  output="$(run_helix "$root" plan --dry-run --rounds 8 auth)"
  assert_contains "$output" "Refinement rounds: 8" "plan should accept custom rounds"
  assert_contains "$output" "Plan scope: auth" "plan should accept scope argument"
  rm -rf "$root"
}

test_polish_dry_run() {
  local root
  root="$(make_workspace)"
  local output
  output="$(run_helix "$root" polish --dry-run)"
  assert_contains "$output" "actions/polish.md" "polish dry-run should reference polish action"
  assert_contains "$output" "Maximum refinement rounds: 6" "polish dry-run should include default rounds"
  rm -rf "$root"
}

test_review_dry_run() {
  local root
  root="$(make_workspace)"
  local output
  output="$(run_helix "$root" review --dry-run)"
  assert_contains "$output" "actions/fresh-eyes-review.md" "review dry-run should reference fresh-eyes action"
  assert_contains "$output" "Review scope: last-commit" "review dry-run should default to last-commit"
  rm -rf "$root"
}

test_review_custom_scope() {
  local root
  root="$(make_workspace)"
  local output
  output="$(run_helix "$root" review --dry-run src/auth/)"
  assert_contains "$output" "Review scope: src/auth/" "review should accept custom scope"
  rm -rf "$root"
}

test_next_shows_ready_issue() {
  local root
  root="$(make_workspace)"
  seed_tracker "$root" 1

  local output
  output="$(run_helix "$root" next 2>&1)"
  assert_contains "$output" "hx-mock-0" "next should show first ready issue ID"
  rm -rf "$root"
}

test_next_no_ready_issues() {
  local root
  root="$(make_workspace)"

  local output
  output="$(run_helix "$root" next 2>&1)"
  assert_contains "$output" "no ready issues" "next should report when no issues are ready"
  rm -rf "$root"
}

test_spawn_without_ntm() {
  local root
  root="$(make_workspace)"

  local output
  output="$(run_helix "$root" spawn 2>&1)" || true
  assert_contains "$output" "ntm not found" "spawn should report ntm absence"
  rm -rf "$root"
}

test_help_includes_all_commands() {
  local root
  root="$(make_workspace)"
  local output
  output="$(run_helix "$root" help)"
  assert_contains "$output" "helix plan" "help should list plan command"
  assert_contains "$output" "helix polish" "help should list polish command"
  assert_contains "$output" "helix next" "help should list next command"
  assert_contains "$output" "helix review" "help should list review command"
  assert_contains "$output" "helix spawn" "help should list spawn command"
  assert_contains "$output" "helix experiment" "help should list experiment command"
  assert_contains "$output" "helix tracker" "help should list tracker command"
  rm -rf "$root"
}

test_experiment_dry_run() {
  local root
  root="$(make_workspace)"
  local output
  output="$(run_helix "$root" experiment --dry-run)"
  assert_contains "$output" "actions/experiment.md" "experiment dry-run should reference experiment action"
  assert_contains "$output" "Experiment target" "experiment dry-run should include experiment target"
  rm -rf "$root"
}

test_experiment_requires_clean_worktree() {
  local root
  root="$(make_workspace)"
  echo dirty > "$root/work/dirty.txt" && cd "$root/work" && git add dirty.txt

  local output
  if output="$(run_helix "$root" experiment 2>&1)"; then
    fail "experiment should fail with uncommitted changes"
  fi

  local found=0
  if [[ "$output" == *"uncommitted changes"* ]] || [[ "$output" == *"please commit"* ]]; then
    found=1
  fi
  [[ "$found" -eq 1 ]] || fail "experiment should mention uncommitted changes or please commit"
  rm -rf "$root"
}

test_experiment_close_dry_run() {
  local root
  root="$(make_workspace)"
  local output
  output="$(run_helix "$root" experiment --dry-run --close)"
  assert_contains "$output" "CLOSE SESSION" "experiment close dry-run should include CLOSE SESSION"
  rm -rf "$root"
}

test_claude_agent_timeout_kills_process() {
  local root
  root="$(make_workspace)"
  seed_tracker "$root" 1

  local output
  if output="$(HELIX_AGENT_TIMEOUT=1 MOCK_CLAUDE_SLEEP=30 run_helix "$root" run --claude 2>&1)"; then
    fail "claude run should fail when agent times out"
  fi

  assert_contains "$output" "agent timeout after" "run should report agent timeout"
  assert_contains "$output" "killing" "run should report killing the agent"
  rm -rf "$root"
}

test_implement_prompt_references_tracker() {
  local root
  root="$(make_workspace)"
  local output
  output="$(run_helix "$root" implement --dry-run)"
  assert_contains "$output" "helix tracker" "implement prompt should reference helix tracker"
  assert_contains "$output" "issues.jsonl" "implement prompt should reference JSONL file"
  rm -rf "$root"
}

# ── Run all tests ──────────────────────────────────────────────────

run_test() {
  local name="$1"
  shift
  "$@"
  test_count=$((test_count + 1))
  echo "ok - $name"
}

# Tracker unit tests
run_test "tracker create and show" test_tracker_create_and_show
run_test "tracker ready and blocked" test_tracker_ready_and_blocked
run_test "tracker update and claim" test_tracker_update_and_claim
run_test "tracker status" test_tracker_status

# CLI integration tests
run_test "help" test_help
run_test "check dry-run" test_check_dry_run
run_test "backfill dry-run" test_backfill_dry_run
run_test "run stops after drain" test_run_stops_after_queue_drains
run_test "periodic alignment" test_run_periodic_alignment
run_test "auto-align" test_run_auto_aligns_once
run_test "periodic alignment failure reason" test_run_reports_periodic_alignment_failure
run_test "backfill requires report marker" test_backfill_requires_report_marker
run_test "backfill creates report" test_backfill_creates_report
run_test "installer launcher" test_installer_creates_launcher
run_test "claude run stops after drain" test_claude_run_stops_after_queue_drains
run_test "claude auto-align" test_claude_run_auto_aligns
run_test "claude check dry-run" test_claude_check_dry_run
run_test "auto-unblock on WAIT" test_run_auto_unblock_on_wait
run_test "no-auto-unblock flag" test_run_no_auto_unblock_flag
run_test "extract NEXT_ACTION from claude output" test_extract_next_action_from_claude_output
run_test "plan dry-run" test_plan_dry_run
run_test "plan custom rounds" test_plan_custom_rounds
run_test "polish dry-run" test_polish_dry_run
run_test "review dry-run" test_review_dry_run
run_test "review custom scope" test_review_custom_scope
run_test "next shows ready issue" test_next_shows_ready_issue
run_test "next no ready issues" test_next_no_ready_issues
run_test "spawn without ntm" test_spawn_without_ntm
run_test "help includes all commands" test_help_includes_all_commands
run_test "experiment dry-run" test_experiment_dry_run
run_test "experiment requires clean worktree" test_experiment_requires_clean_worktree
run_test "experiment close dry-run" test_experiment_close_dry_run
run_test "claude agent timeout kills process" test_claude_agent_timeout_kills_process
run_test "implement prompt references tracker" test_implement_prompt_references_tracker

echo "PASS: ${test_count} helix wrapper tests"
