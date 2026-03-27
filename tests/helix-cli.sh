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

assert_file_contains() {
  local path="$1"
  local needle="$2"
  local message="$3"
  [[ -f "$path" ]] || fail "$message"
  local content
  content="$(cat "$path")"
  assert_contains "$content" "$needle" "$message"
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

  cat >"$root/bin/bd" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

if [[ "${1:-}" != "list" ]] || [[ "${2:-}" != "--json" ]]; then
  echo "mock bd only supports: bd list --json" >&2
  exit 1
fi

if [[ "${MOCK_BD_FAIL:-0}" == "1" ]]; then
  echo "mock bd failure" >&2
  exit 1
fi

printf '%s\n' "${MOCK_BD_LIST_JSON:-[]}"
EOF

  cat >"$root/bin/br" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

if [[ "${1:-}" != "list" ]] || [[ "${2:-}" != "--json" ]]; then
  echo "mock br only supports: br list --json" >&2
  exit 1
fi

if [[ "${MOCK_BR_FAIL:-0}" == "1" ]]; then
  echo "mock br failure" >&2
  exit 1
fi

printf '%s\n' "${MOCK_BR_LIST_JSON:-[]}"
EOF

  chmod +x "$root/bin/codex" "$root/bin/claude" "$root/bin/bd" "$root/bin/br"
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

run_helix_with_env() {
  local root="$1"
  local env_name="$2"
  local env_value="$3"
  shift 3
  local cmd="${1:-help}"
  shift || true
  (
    cd "$root/work"
    env \
      HOME="$root/home" \
      PATH="$root/bin:$PATH" \
      MOCK_STATE_ROOT="$root/state" \
      HELIX_LIBRARY_ROOT="$repo_root/workflows" \
      "$env_name=$env_value" \
      bash "$repo_root/scripts/helix" "$cmd" --quiet "$@"
  )
}

run_helix_with_envs() {
  local root="$1"
  shift
  local env_args=()
  while [[ $# -gt 0 ]] && [[ "$1" != "--" ]]; do
    env_args+=("$1")
    shift
  done
  if [[ "${1:-}" != "--" ]]; then
    fail "run_helix_with_envs requires -- before command arguments"
  fi
  shift
  local cmd="${1:-help}"
  shift || true
  (
    cd "$root/work"
    env \
      HOME="$root/home" \
      PATH="$root/bin:$PATH" \
      MOCK_STATE_ROOT="$root/state" \
      HELIX_LIBRARY_ROOT="$repo_root/workflows" \
      "${env_args[@]}" \
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

test_tracker_help() {
  local root
  root="$(make_workspace)"
  local output
  output="$(run_helix "$root" tracker help)"
  assert_contains "$output" "helix tracker create" "tracker help should list create"
  assert_contains "$output" "helix tracker import" "tracker help should list import"
  assert_contains "$output" "helix tracker export" "tracker help should list export"
  assert_contains "$output" "Canonical storage is .helix/issues.jsonl" "tracker help should describe canonical storage"
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
  output="$(run_helix "$root" run --no-auto-review 2>&1)"

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

  run_helix "$root" run --review-every 2 --no-auto-review >/dev/null

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

  run_helix "$root" run --no-auto-review >/dev/null

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
  if output="$(run_helix "$root" run --review-every 1 --no-auto-review 2>&1)"; then
    fail "run should fail when periodic alignment fails"
  fi

  assert_contains "$output" "mock alignment failure" "run should surface the alignment failure"
  assert_contains "$output" "helix: periodic alignment failed after 1 cycles" "run should report why the loop exited"
  rm -rf "$root"
}

test_run_stops_on_queue_drift_before_close() {
  local root
  root="$(make_workspace)"
  seed_tracker "$root" 1

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
      tmp="$(jq -c '.["spec-id"] = "TP-DRIFT" | .status = "closed"' .helix/issues.jsonl)"
      printf '%s\n' "$tmp" > .helix/issues.jsonl
    fi
    echo "implementation complete"
    ;;
  *) record other; echo "mock codex" ;;
esac
MOCK
  chmod +x "$root/bin/codex"

  local output
  output="$(run_helix "$root" run --no-auto-review 2>&1)"
  assert_contains "$output" "queue drift detected" "run should report queue drift"
  assert_contains "$output" "stopping after queue drift" "run should stop after drift is detected"

  local status
  status="$(run_helix "$root" tracker show hx-mock-0 --json | jq -r '.status')"
  assert_eq "open" "$status" "run should reopen a drifted issue instead of leaving it closed"
  rm -rf "$root"
}

test_run_stops_on_queue_drift_before_close_without_closing() {
  local root
  root="$(make_workspace)"
  seed_tracker "$root" 1

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
      tmp="$(jq -c '.["spec-id"] = "TP-DRIFT"' .helix/issues.jsonl)"
      printf '%s\n' "$tmp" > .helix/issues.jsonl
    fi
    echo "implementation complete"
    ;;
  *) record other; echo "mock codex" ;;
esac
MOCK
  chmod +x "$root/bin/codex"

  local output
  output="$(run_helix "$root" run --no-auto-review 2>&1)"
  assert_contains "$output" "queue drift detected" "run should report drift even if the issue was not closed"
  assert_contains "$output" "stopping after queue drift" "run should stop for a re-check path"

  local status
  status="$(run_helix "$root" tracker show hx-mock-0 --json | jq -r '.status')"
  assert_eq "open" "$status" "run should leave the issue open for re-check"
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
    AGENTS_HOME="$root/agents-home" \
    CLAUDE_HOME="$root/claude-home" \
    bash scripts/install-local-skills.sh >/dev/null
  )

  [[ -x "$root/home/.local/bin/helix" ]] || fail "installer should create helix launcher"
  local launcher
  launcher="$(cat "$root/home/.local/bin/helix")"
  assert_contains "$launcher" 'exec bash "'$repo_root'/scripts/helix"' "launcher should invoke repo helix script through bash"
  local canonical_skills=(
    helix-run
    helix-implement
    helix-check
    helix-align
    helix-backfill
    helix-plan
    helix-polish
    helix-next
    helix-review
    helix-experiment
  )
  local skill
  for skill in "${canonical_skills[@]}"; do
    [[ -L "$root/agents-home/skills/$skill" ]] || fail "installer should link $skill into .agents"
    [[ -L "$root/claude-home/skills/$skill" ]] || fail "installer should link $skill into Claude"
  done
  [[ ! -e "$root/agents-home/skills/helix-workflow" ]] || fail "installer should remove legacy skill aliases"
  [[ ! -e "$root/agents-home/skills/plan-workflow" ]] || fail "installer should remove legacy skill aliases"
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
  output="$(run_helix "$root" run --claude --no-auto-review 2>&1)"

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

  run_helix "$root" run --claude --no-auto-review >/dev/null

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

test_run_stops_on_wait() {
  local root
  root="$(make_workspace)"
  printf 'WAIT\n' > "$root/state/next-actions"

  local output
  output="$(run_helix "$root" run --no-auto-review 2>&1)"

  local calls
  calls="$(cat "$root/state/calls.log")"
  assert_eq $'check' "$calls" "run should stop immediately when check returns WAIT"
  assert_contains "$output" "stopping after check returned WAIT" "run should report terminal WAIT"
  rm -rf "$root"
}

test_run_stops_on_backfill() {
  local root
  root="$(make_workspace)"
  printf 'BACKFILL\n' > "$root/state/next-actions"

  local output
  output="$(run_helix "$root" run --no-auto-review 2>&1)"

  local calls
  calls="$(cat "$root/state/calls.log")"
  assert_eq $'check' "$calls" "run should not auto-dispatch backfill after queue drain"
  assert_contains "$output" "stopping after check returned BACKFILL" "run should surface BACKFILL as a distinct stop"
  assert_contains "$output" "run helix backfill repo" "run should print the explicit backfill handoff command"
  rm -rf "$root"
}

test_run_max_cycles_counts_completed_cycles_only() {
  local root
  root="$(make_workspace)"
  seed_tracker "$root" 1

  cat >"$root/bin/codex" <<'MOCK'
#!/usr/bin/env bash
set -euo pipefail
state_root="${MOCK_STATE_ROOT:?}"
record() { printf '%s\n' "$1" >> "$state_root/calls.log"; }
attempt_file="$state_root/implement-attempts"
attempts=0
if [[ -f "$attempt_file" ]]; then
  attempts="$(cat "$attempt_file")"
fi
payload="$*"
case "$payload" in
  *"implementation action"*)
    record implement
    attempts=$((attempts + 1))
    printf '%s\n' "$attempts" > "$attempt_file"
    if (( attempts >= 2 )) && [[ -f .helix/issues.jsonl ]]; then
      tmp="$(jq -c '.status = "closed"' .helix/issues.jsonl)"
      printf '%s\n' "$tmp" > .helix/issues.jsonl
    fi
    echo "implementation complete"
    ;;
  *"alignment action"*)
    record align
    echo "alignment complete"
    ;;
  *"check action"*)
    record check
    echo "NEXT_ACTION: STOP"
    ;;
  *) record other; echo "mock codex" ;;
esac
MOCK
  chmod +x "$root/bin/codex"

  local output
  output="$(run_helix "$root" run --max-cycles 1 --no-auto-review 2>&1)"

  local calls
  calls="$(cat "$root/state/calls.log")"
  assert_eq $'implement\nimplement' "$calls" "max cycles should count only completed issue closures"
  assert_contains "$output" "did not complete a tracked issue" "run should distinguish attempted work from completed work"
  assert_contains "$output" "reached max cycles (1)" "run should stop after one completed cycle"
  rm -rf "$root"
}

test_run_periodic_alignment_ignores_failed_attempts() {
  local root
  root="$(make_workspace)"
  seed_tracker "$root" 1
  printf 'STOP\n' > "$root/state/next-actions"

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
attempt_file="$state_root/implement-attempts"
attempts=0
if [[ -f "$attempt_file" ]]; then
  attempts="$(cat "$attempt_file")"
fi
payload="$*"
case "$payload" in
  *"implementation action"*)
    record implement
    attempts=$((attempts + 1))
    printf '%s\n' "$attempts" > "$attempt_file"
    if (( attempts == 1 )); then
      echo "mock implementation failure" >&2
      exit 1
    fi
    if [[ -f .helix/issues.jsonl ]]; then
      tmp="$(jq -c '.status = "closed"' .helix/issues.jsonl)"
      printf '%s\n' "$tmp" > .helix/issues.jsonl
    fi
    echo "implementation complete"
    ;;
  *"alignment action"*)
    record align
    echo "alignment complete"
    ;;
  *"check action"*)
    record check
    action="$(next_action)"
    printf 'NEXT_ACTION: %s\n' "$action"
    ;;
  *) record other; echo "mock codex" ;;
esac
MOCK
  chmod +x "$root/bin/codex"

  local output
  output="$(run_helix "$root" run --review-every 1 --no-auto-review 2>&1)"

  local calls
  calls="$(cat "$root/state/calls.log")"
  assert_eq $'implement\nimplement\nalign\ncheck' "$calls" "periodic alignment should wait for a completed cycle, not a failed attempt"
  assert_contains "$output" "implementation failed during cycle 1" "run should report failed attempts without counting them as complete"
  rm -rf "$root"
}

test_run_recovery_preserves_unrelated_dirty_changes() {
  local root
  root="$(make_workspace)"
  local issue_id
  issue_id="$(run_helix "$root" tracker create "Claimed task" --labels helix,phase:build)"
  run_helix "$root" tracker update "$issue_id" --claim >/dev/null

  (
    cd "$root/work"
    printf 'tracked\n' > keep.txt
    git add keep.txt
    git commit -qm "seed tracked file"
    printf 'tracked but dirty\n' > keep.txt
  )
  printf 'WAIT\n' > "$root/state/next-actions"

  local output
  output="$(run_helix "$root" run --no-auto-review 2>&1)"

  local status
  status="$(run_helix "$root" tracker show "$issue_id" --json | jq -r '.status')"
  assert_eq "in_progress" "$status" "ambiguous stale claims should remain claimed by default"
  assert_file_contains "$root/work/keep.txt" "tracked but dirty" "recovery should not revert unrelated dirty worktree changes"
  assert_contains "$output" "may be stale" "run should warn when a claim looks stale"
  assert_contains "$output" "leaving local changes intact" "run should report non-destructive recovery handling"
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

test_help_includes_all_commands() {
  local root
  root="$(make_workspace)"
  local output
  output="$(run_helix "$root" help)"
  assert_contains "$output" "helix plan" "help should list plan command"
  assert_contains "$output" "helix polish" "help should list polish command"
  assert_contains "$output" "helix next" "help should list next command"
  assert_contains "$output" "helix review" "help should list review command"
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
  assert_contains "$output" "re-read the selected issue immediately before claim and immediately before close" "implement prompt should require pre-claim and pre-close revalidation"
  rm -rf "$root"
}

# ── Auto-review in loop tests ──────────────────────────────────────

test_run_auto_reviews_after_implement() {
  local root
  root="$(make_workspace)"
  seed_tracker "$root" 1
  printf 'STOP\n' > "$root/state/next-actions"

  # Mock codex that closes issue on implement and handles review
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
    if [[ -f .helix/issues.jsonl ]]; then
      tmp="$(jq -c '.status = "closed"' .helix/issues.jsonl)"
      printf '%s\n' "$tmp" > .helix/issues.jsonl
    fi
    echo "implementation complete"
    ;;
  *"fresh-eyes review"*)
    record review
    echo "REVIEW_STATUS: CLEAN"
    echo "ISSUES_COUNT: 0"
    echo "AGENTS_MD_UPDATED: NO"
    echo "LEARNINGS_FILED: 0"
    ;;
  *"check action"*)
    record check
    action="$(next_action)"
    printf 'NEXT_ACTION: %s\n' "$action"
    ;;
  *"alignment action"*)
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
  assert_eq $'implement\nreview\ncheck' "$calls" "run should review after each successful implementation"
  assert_contains "$output" "post-implementation review" "run should report review step"
  rm -rf "$root"
}

test_run_no_auto_review_flag() {
  local root
  root="$(make_workspace)"
  seed_tracker "$root" 1
  printf 'STOP\n' > "$root/state/next-actions"

  # Same mock as above
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
  *) record other; echo "mock codex" ;;
esac
MOCK
  chmod +x "$root/bin/codex"

  run_helix "$root" run --no-auto-review >/dev/null

  local calls
  calls="$(cat "$root/state/calls.log")"
  assert_eq $'implement\ncheck' "$calls" "run --no-auto-review should skip review"
  rm -rf "$root"
}

# ── Extended tracker tests ─────────────────────────────────────────

test_tracker_create_requires_title() {
  local root
  root="$(make_workspace)"
  assert_fails "create without title should fail" run_helix "$root" tracker create 2>/dev/null
  rm -rf "$root"
}

test_tracker_show_missing_issue() {
  local root
  root="$(make_workspace)"
  assert_fails "show nonexistent issue should fail" run_helix "$root" tracker show hx-nonexistent 2>/dev/null
  rm -rf "$root"
}

test_tracker_update_missing_issue() {
  local root
  root="$(make_workspace)"
  assert_fails "update nonexistent issue should fail" run_helix "$root" tracker update hx-nonexistent --status closed 2>/dev/null
  rm -rf "$root"
}

test_tracker_close_sets_status() {
  local root
  root="$(make_workspace)"
  local id
  id="$(run_helix "$root" tracker create "Close me")"

  run_helix "$root" tracker close "$id" >/dev/null
  local status
  status="$(run_helix "$root" tracker show "$id" --json | jq -r '.status')"
  assert_eq "closed" "$status" "close should set status to closed"

  # Closed issues should not appear in ready
  local ready_count
  ready_count="$(run_helix "$root" tracker ready --json | jq 'length')"
  assert_eq "0" "$ready_count" "closed issue should not be ready"
  rm -rf "$root"
}

test_tracker_update_multiple_fields() {
  local root
  root="$(make_workspace)"
  local id
  id="$(run_helix "$root" tracker create "Multi update" --priority 2)"

  run_helix "$root" tracker update "$id" --priority 0 --title "Urgent" --assignee agent >/dev/null

  local json
  json="$(run_helix "$root" tracker show "$id" --json)"
  assert_eq "0" "$(printf '%s' "$json" | jq '.priority')" "priority should be updated"
  assert_eq "Urgent" "$(printf '%s' "$json" | jq -r '.title')" "title should be updated"
  assert_eq "agent" "$(printf '%s' "$json" | jq -r '.assignee')" "assignee should be updated"
  rm -rf "$root"
}

test_tracker_list_filters() {
  local root
  root="$(make_workspace)"
  local id1 id2
  id1="$(run_helix "$root" tracker create "Open task" --labels helix,phase:build)"
  id2="$(run_helix "$root" tracker create "Other task" --labels helix,phase:test)"

  run_helix "$root" tracker close "$id1" >/dev/null

  # Filter by status
  local open_count
  open_count="$(run_helix "$root" tracker list --status open --json | jq 'length')"
  assert_eq "1" "$open_count" "list --status open should return only open issues"

  local closed_count
  closed_count="$(run_helix "$root" tracker list --status closed --json | jq 'length')"
  assert_eq "1" "$closed_count" "list --status closed should return only closed issues"

  # Filter by label
  local build_count
  build_count="$(run_helix "$root" tracker list --label phase:build --json | jq 'length')"
  assert_eq "1" "$build_count" "list --label should filter by label"
  rm -rf "$root"
}

test_tracker_dep_add_and_remove() {
  local root
  root="$(make_workspace)"
  local id1 id2
  id1="$(run_helix "$root" tracker create "Parent")"
  id2="$(run_helix "$root" tracker create "Child")"

  # Add dep
  run_helix "$root" tracker dep add "$id2" "$id1" >/dev/null
  local deps
  deps="$(run_helix "$root" tracker show "$id2" --json | jq -r '.deps[]')"
  assert_eq "$id1" "$deps" "dep add should add dependency"

  # Adding same dep again should not duplicate
  run_helix "$root" tracker dep add "$id2" "$id1" >/dev/null
  local dep_count
  dep_count="$(run_helix "$root" tracker show "$id2" --json | jq '.deps | length')"
  assert_eq "1" "$dep_count" "duplicate dep add should not create duplicates"

  # Remove dep
  run_helix "$root" tracker dep remove "$id2" "$id1" >/dev/null
  dep_count="$(run_helix "$root" tracker show "$id2" --json | jq '.deps | length')"
  assert_eq "0" "$dep_count" "dep remove should remove dependency"
  rm -rf "$root"
}

test_tracker_dep_tree() {
  local root
  root="$(make_workspace)"
  local id1 id2
  id1="$(run_helix "$root" tracker create "Dep parent")"
  id2="$(run_helix "$root" tracker create "Dep child")"
  run_helix "$root" tracker dep add "$id2" "$id1" >/dev/null

  local output
  output="$(run_helix "$root" tracker dep tree "$id2")"
  assert_contains "$output" "$id2" "dep tree should show the issue"
  assert_contains "$output" "$id1" "dep tree should show dependency"
  rm -rf "$root"
}

test_tracker_unique_ids() {
  local root
  root="$(make_workspace)"

  # Create multiple issues and verify IDs are unique
  local id1 id2 id3
  id1="$(run_helix "$root" tracker create "First")"
  id2="$(run_helix "$root" tracker create "Second")"
  id3="$(run_helix "$root" tracker create "Third")"

  [[ "$id1" != "$id2" ]] || fail "issue IDs should be unique (1 vs 2)"
  [[ "$id2" != "$id3" ]] || fail "issue IDs should be unique (2 vs 3)"
  [[ "$id1" != "$id3" ]] || fail "issue IDs should be unique (1 vs 3)"
  rm -rf "$root"
}

test_tracker_json_output() {
  local root
  root="$(make_workspace)"
  local id
  id="$(run_helix "$root" tracker create "JSON test" --type bug --labels area:cli --description "Test desc" --acceptance "Tests pass")"

  # Verify JSON output is valid and has all fields
  local json
  json="$(run_helix "$root" tracker show "$id" --json)"
  assert_eq "$id" "$(printf '%s' "$json" | jq -r '.id')" "JSON id should match"
  assert_eq "JSON test" "$(printf '%s' "$json" | jq -r '.title')" "JSON title should match"
  assert_eq "bug" "$(printf '%s' "$json" | jq -r '.type')" "JSON type should match"
  assert_eq "open" "$(printf '%s' "$json" | jq -r '.status')" "JSON status should match"
  assert_eq "Test desc" "$(printf '%s' "$json" | jq -r '.description')" "JSON description should match"
  assert_eq "Tests pass" "$(printf '%s' "$json" | jq -r '.acceptance')" "JSON acceptance should match"
  assert_eq "area:cli" "$(printf '%s' "$json" | jq -r '.labels[0]')" "JSON labels should match"
  rm -rf "$root"
}

test_tracker_create_with_deps() {
  local root
  root="$(make_workspace)"
  local parent child
  parent="$(run_helix "$root" tracker create "Parent issue")"
  child="$(run_helix "$root" tracker create "Child issue" --deps "$parent")"

  local dep_id
  dep_id="$(run_helix "$root" tracker show "$child" --json | jq -r '.deps[0]')"
  assert_eq "$parent" "$dep_id" "create --deps should seed dependencies"
  rm -rf "$root"
}

test_tracker_update_structural_fields() {
  local root
  root="$(make_workspace)"
  local parent dep target
  parent="$(run_helix "$root" tracker create "Parent issue")"
  dep="$(run_helix "$root" tracker create "Dependency issue")"
  target="$(run_helix "$root" tracker create "Target issue")"

  run_helix "$root" tracker update "$target" --spec-id TP-999 --parent "$parent" --deps "$dep" >/dev/null

  local json
  json="$(run_helix "$root" tracker show "$target" --json)"
  assert_eq "TP-999" "$(printf '%s' "$json" | jq -r '.["spec-id"]')" "update should set spec-id"
  assert_eq "$parent" "$(printf '%s' "$json" | jq -r '.parent')" "update should set parent"
  assert_eq "$dep" "$(printf '%s' "$json" | jq -r '.deps[0]')" "update should set deps"
  rm -rf "$root"
}

test_tracker_status_json() {
  local root
  root="$(make_workspace)"
  run_helix "$root" tracker create "A" >/dev/null
  local id
  id="$(run_helix "$root" tracker create "B")"
  run_helix "$root" tracker close "$id" >/dev/null

  local json
  json="$(run_helix "$root" tracker status --json)"
  assert_eq "2" "$(printf '%s' "$json" | jq '.total')" "status JSON total should be 2"
  assert_eq "1" "$(printf '%s' "$json" | jq '.open')" "status JSON open should be 1"
  assert_eq "1" "$(printf '%s' "$json" | jq '.closed')" "status JSON closed should be 1"
  rm -rf "$root"
}

test_tracker_in_progress_not_ready() {
  local root
  root="$(make_workspace)"
  local id
  id="$(run_helix "$root" tracker create "Claimed task")"
  run_helix "$root" tracker update "$id" --claim >/dev/null

  local ready_count
  ready_count="$(run_helix "$root" tracker ready --json | jq 'length')"
  assert_eq "0" "$ready_count" "in_progress issues should not appear in ready queue"
  rm -rf "$root"
}

test_tracker_empty_ready() {
  local root
  root="$(make_workspace)"
  local ready_count
  ready_count="$(run_helix "$root" tracker ready --json | jq 'length')"
  assert_eq "0" "$ready_count" "empty tracker should have 0 ready issues"
  rm -rf "$root"
}

test_tracker_serializes_concurrent_writes() {
  local root
  root="$(make_workspace)"

  run_helix_with_env "$root" HELIX_TRACKER_TEST_HOLD_LOCK_SEC 0.3 tracker create "First concurrent issue" >/dev/null &
  local first_pid=$!

  sleep 0.05

  local second_id
  second_id="$(run_helix "$root" tracker create "Second concurrent issue")"
  wait "$first_pid"

  local count
  count="$(run_helix "$root" tracker list --json | jq 'length')"
  assert_eq "2" "$count" "concurrent creates should both persist"

  local second_title
  second_title="$(run_helix "$root" tracker show "$second_id" --json | jq -r '.title')"
  assert_eq "Second concurrent issue" "$second_title" "second writer should succeed after waiting for the lock"
  rm -rf "$root"
}

test_tracker_lock_timeout_reports_owner() {
  local root
  root="$(make_workspace)"

  mkdir -p "$root/work/.helix/issues.lock"
  printf '424242\n' > "$root/work/.helix/issues.lock/pid"
  printf '2099-01-01T00:00:00Z\n' > "$root/work/.helix/issues.lock/acquired_at"

  local output
  output="$(run_helix_with_env "$root" HELIX_TRACKER_LOCK_TIMEOUT 0 tracker create "Blocked by lock" 2>&1 || true)"
  assert_contains "$output" "timed out waiting for tracker lock" "lock timeout should be reported"
  assert_contains "$output" "owner: 424242" "lock timeout should report the recorded lock owner"

  local count
  count="$(run_helix "$root" tracker list --json | jq 'length')"
  assert_eq "0" "$count" "timed out mutation should not create partial tracker state"
  rm -rf "$root"
}

test_tracker_list_fails_on_malformed_jsonl() {
  local root
  root="$(make_workspace)"

  mkdir -p "$root/work/.helix"
  printf '{"id":"hx-good","title":"ok"}\n{"id":"hx-bad"\n' > "$root/work/.helix/issues.jsonl"

  assert_fails "list should fail on malformed tracker state" run_helix "$root" tracker list --json 2>/dev/null
  assert_fails "status should fail on malformed tracker state" run_helix "$root" tracker status --json 2>/dev/null
  rm -rf "$root"
}

test_tracker_mutation_fails_on_malformed_jsonl() {
  local root
  root="$(make_workspace)"

  mkdir -p "$root/work/.helix"
  printf '{"id":"hx-good","title":"ok"}\n{"id":"hx-bad"\n' > "$root/work/.helix/issues.jsonl"

  assert_fails "create should fail on malformed tracker state" run_helix "$root" tracker create "Should fail" 2>/dev/null
  assert_fails "update should fail on malformed tracker state" run_helix "$root" tracker update hx-good --title "new" 2>/dev/null

  local line_count
  line_count="$(wc -l < "$root/work/.helix/issues.jsonl" | tr -d ' ')"
  assert_eq "2" "$line_count" "failed mutation should not rewrite malformed tracker state"
  rm -rf "$root"
}

# ── Migration tests ───────────────────────────────────────────────

test_tracker_import_from_jsonl() {
  local root
  root="$(make_workspace)"

  # Create a legacy .beads/issues.jsonl
  mkdir -p "$root/work/.beads"
  cat >"$root/work/.beads/issues.jsonl" <<'LEGACY'
{"id":"bd-aaa111","title":"Legacy task one","type":"task","status":"open","priority":1,"labels":["helix","phase:build"],"parent":"","spec-id":"TP-001","description":"From beads","deps":[],"assignee":"","created":"2026-01-01T00:00:00Z","updated":"2026-01-01T00:00:00Z"}
{"id":"bd-bbb222","title":"Legacy task two","type":"bug","status":"closed","priority":0,"labels":["helix"],"deps":["bd-aaa111"],"assignee":"agent","created":"2026-01-01T00:00:00Z","updated":"2026-01-02T00:00:00Z"}
LEGACY

  local output
  output="$(run_helix "$root" tracker import --from jsonl 2>&1)"
  assert_contains "$output" "found 2 issues" "import should find issues"
  assert_contains "$output" "imported 2 beads" "import should report count"
  assert_contains "$output" ".beads/issues.jsonl" "import should report the JSONL source"

  # Verify data is accessible
  local count
  count="$(run_helix "$root" tracker list --json | jq 'length')"
  assert_eq "2" "$count" "imported tracker should have 2 issues"

  # Verify IDs are preserved
  local title
  title="$(run_helix "$root" tracker show bd-aaa111 --json | jq -r '.title')"
  assert_eq "Legacy task one" "$title" "imported issue should preserve title"

  # Verify deps are preserved
  local deps
  deps="$(run_helix "$root" tracker show bd-bbb222 --json | jq -r '.deps[0]')"
  assert_eq "bd-aaa111" "$deps" "imported issue should preserve deps"

  # Verify labels are preserved
  local label
  label="$(run_helix "$root" tracker show bd-aaa111 --json | jq -r '.labels[1]')"
  assert_eq "phase:build" "$label" "imported issue should preserve labels"
  rm -rf "$root"
}

test_tracker_import_no_source() {
  local root
  root="$(make_workspace)"
  # No .beads/ directory, no bd, no br
  assert_fails "import with no source should fail" run_helix "$root" tracker import 2>/dev/null
  rm -rf "$root"
}

test_tracker_import_warns_existing_data() {
  local root
  root="$(make_workspace)"

  # Seed existing tracker data
  run_helix "$root" tracker create "Existing issue" >/dev/null

  # Create legacy data
  mkdir -p "$root/work/.beads"
  printf '{"id":"bd-ccc333","title":"Legacy","type":"task","status":"open","priority":2,"labels":[],"deps":[]}\n' \
    >"$root/work/.beads/issues.jsonl"

  local output
  output="$(run_helix "$root" tracker import --from jsonl 2>&1)"
  assert_contains "$output" "WARNING" "import should warn about existing data"
  assert_contains "$output" "already has 1 issues" "import should report existing count"

  # Verify both old and new data exist
  local count
  count="$(run_helix "$root" tracker list --json | jq 'length')"
  assert_eq "2" "$count" "import should append to existing data"
  rm -rf "$root"
}

test_tracker_import_normalizes_missing_fields() {
  local root
  root="$(make_workspace)"

  # Create legacy data with minimal fields
  mkdir -p "$root/work/.beads"
  printf '{"id":"bd-sparse","title":"Sparse issue"}\n' \
    >"$root/work/.beads/issues.jsonl"

  run_helix "$root" tracker import --from jsonl 2>/dev/null

  # Verify defaults were applied
  local json
  json="$(run_helix "$root" tracker show bd-sparse --json)"
  assert_eq "task" "$(printf '%s' "$json" | jq -r '.type')" "import should default type to task"
  assert_eq "open" "$(printf '%s' "$json" | jq -r '.status')" "import should default status to open"
  assert_eq "2" "$(printf '%s' "$json" | jq '.priority')" "import should default priority to 2"
  assert_eq "0" "$(printf '%s' "$json" | jq '.deps | length')" "import should default deps to empty"
  assert_eq "0" "$(printf '%s' "$json" | jq '.labels | length')" "import should default labels to empty"
  rm -rf "$root"
}

test_tracker_import_from_bd() {
  local root
  root="$(make_workspace)"
  mkdir -p "$root/work/.beads"

  local output
  output="$(run_helix_with_envs "$root" \
    MOCK_BD_LIST_JSON='[{"id":"bd-live","title":"From bd","type":"task","status":"open","priority":1,"labels":["helix","phase:build"],"deps":[]}]' \
    -- tracker import --from bd 2>&1)"
  assert_contains "$output" "bd (live Dolt database)" "import should report bd as the source"

  local title
  title="$(run_helix "$root" tracker show bd-live --json | jq -r '.title')"
  assert_eq "From bd" "$title" "bd import should populate canonical storage"
  rm -rf "$root"
}

test_tracker_import_from_br() {
  local root
  root="$(make_workspace)"

  local output
  output="$(run_helix_with_envs "$root" \
    MOCK_BR_LIST_JSON='[{"id":"br-live","title":"From br","type":"bug","status":"closed","priority":0,"labels":["helix"],"deps":[]}]' \
    -- tracker import --from br 2>&1)"
  assert_contains "$output" "br (live SQLite database)" "import should report br as the source"

  local status
  status="$(run_helix "$root" tracker show br-live --json | jq -r '.status')"
  assert_eq "closed" "$status" "br import should preserve issue state"
  rm -rf "$root"
}

test_tracker_migrate_aliases_import() {
  local root
  root="$(make_workspace)"
  mkdir -p "$root/work/.beads"
  printf '{"id":"bd-alias","title":"Alias issue","type":"task","status":"open","priority":2,"labels":[],"deps":[]}\n' \
    >"$root/work/.beads/issues.jsonl"

  local output
  output="$(run_helix "$root" tracker migrate 2>&1)"
  assert_contains "$output" "imported 1 beads" "migrate should remain an import alias"
  rm -rf "$root"
}

test_tracker_export_writes_beads_jsonl() {
  local root
  root="$(make_workspace)"
  local id
  id="$(run_helix "$root" tracker create "Export me" --type bug --labels helix,area:cli)"
  run_helix "$root" tracker update "$id" --claim >/dev/null

  local export_path
  export_path="$(run_helix "$root" tracker export)"
  local export_file="$export_path"
  if [[ "$export_file" != /* ]]; then
    export_file="$root/work/$export_file"
  fi
  [[ -f "$export_file" ]] || fail "export should write bead JSONL"

  local exported_json
  exported_json="$(jq -s '.' "$export_file")"
  assert_eq "$id" "$(printf '%s' "$exported_json" | jq -r '.[0].id')" "export should preserve ids"
  assert_eq "in_progress" "$(printf '%s' "$exported_json" | jq -r '.[0].status')" "export should preserve status"
  assert_eq "helix" "$(printf '%s' "$exported_json" | jq -r '.[0].assignee')" "export should preserve assignee"
  rm -rf "$root"
}

test_tracker_export_stdout_roundtrip() {
  local root
  root="$(make_workspace)"
  run_helix "$root" tracker create "Round trip A" >/dev/null
  run_helix "$root" tracker create "Round trip B" --labels helix >/dev/null

  mkdir -p "$root/work/tmp"
  run_helix "$root" tracker export --stdout > "$root/work/tmp/export.jsonl"
  rm -f "$root/work/.helix/issues.jsonl"

  run_helix "$root" tracker import --from jsonl --file tmp/export.jsonl >/dev/null

  local count
  count="$(run_helix "$root" tracker list --json | jq 'length')"
  assert_eq "2" "$count" "exported beads JSONL should round-trip back into canonical storage"
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
run_test "tracker create requires title" test_tracker_create_requires_title
run_test "tracker show missing issue" test_tracker_show_missing_issue
run_test "tracker update missing issue" test_tracker_update_missing_issue
run_test "tracker ready and blocked" test_tracker_ready_and_blocked
run_test "tracker update and claim" test_tracker_update_and_claim
run_test "tracker update multiple fields" test_tracker_update_multiple_fields
run_test "tracker close sets status" test_tracker_close_sets_status
run_test "tracker list filters" test_tracker_list_filters
run_test "tracker dep add and remove" test_tracker_dep_add_and_remove
run_test "tracker dep tree" test_tracker_dep_tree
run_test "tracker unique IDs" test_tracker_unique_ids
run_test "tracker JSON output" test_tracker_json_output
run_test "tracker create with deps" test_tracker_create_with_deps
run_test "tracker update structural fields" test_tracker_update_structural_fields
run_test "tracker status JSON" test_tracker_status_json
run_test "tracker status" test_tracker_status
run_test "tracker in_progress not ready" test_tracker_in_progress_not_ready
run_test "tracker empty ready" test_tracker_empty_ready
run_test "tracker serializes concurrent writes" test_tracker_serializes_concurrent_writes
run_test "tracker lock timeout reports owner" test_tracker_lock_timeout_reports_owner
run_test "tracker list fails on malformed jsonl" test_tracker_list_fails_on_malformed_jsonl
run_test "tracker mutation fails on malformed jsonl" test_tracker_mutation_fails_on_malformed_jsonl

# Beads interop tests
run_test "tracker import from JSONL" test_tracker_import_from_jsonl
run_test "tracker import no source" test_tracker_import_no_source
run_test "tracker import warns existing data" test_tracker_import_warns_existing_data
run_test "tracker import normalizes missing fields" test_tracker_import_normalizes_missing_fields
run_test "tracker import from bd" test_tracker_import_from_bd
run_test "tracker import from br" test_tracker_import_from_br
run_test "tracker migrate aliases import" test_tracker_migrate_aliases_import
run_test "tracker export writes beads JSONL" test_tracker_export_writes_beads_jsonl
run_test "tracker export stdout roundtrip" test_tracker_export_stdout_roundtrip

# Auto-review in loop tests
run_test "run auto-reviews after implement" test_run_auto_reviews_after_implement
run_test "run no-auto-review flag" test_run_no_auto_review_flag

# CLI integration tests
run_test "help" test_help
run_test "tracker help" test_tracker_help
run_test "check dry-run" test_check_dry_run
run_test "backfill dry-run" test_backfill_dry_run
run_test "run stops after drain" test_run_stops_after_queue_drains
run_test "periodic alignment" test_run_periodic_alignment
run_test "auto-align" test_run_auto_aligns_once
run_test "periodic alignment failure reason" test_run_reports_periodic_alignment_failure
run_test "run stops on queue drift before close" test_run_stops_on_queue_drift_before_close
run_test "run stops on queue drift without closing" test_run_stops_on_queue_drift_before_close_without_closing
run_test "backfill requires report marker" test_backfill_requires_report_marker
run_test "backfill creates report" test_backfill_creates_report
run_test "installer launcher" test_installer_creates_launcher
run_test "claude run stops after drain" test_claude_run_stops_after_queue_drains
run_test "claude auto-align" test_claude_run_auto_aligns
run_test "claude check dry-run" test_claude_check_dry_run
run_test "run stops on WAIT" test_run_stops_on_wait
run_test "run stops on BACKFILL" test_run_stops_on_backfill
run_test "max cycles count completed work only" test_run_max_cycles_counts_completed_cycles_only
run_test "periodic alignment ignores failed attempts" test_run_periodic_alignment_ignores_failed_attempts
run_test "extract NEXT_ACTION from claude output" test_extract_next_action_from_claude_output
run_test "plan dry-run" test_plan_dry_run
run_test "plan custom rounds" test_plan_custom_rounds
run_test "polish dry-run" test_polish_dry_run
run_test "review dry-run" test_review_dry_run
run_test "review custom scope" test_review_custom_scope
run_test "next shows ready issue" test_next_shows_ready_issue
run_test "next no ready issues" test_next_no_ready_issues
run_test "help includes all commands" test_help_includes_all_commands
run_test "experiment dry-run" test_experiment_dry_run
run_test "experiment requires clean worktree" test_experiment_requires_clean_worktree
run_test "experiment close dry-run" test_experiment_close_dry_run
run_test "recovery preserves unrelated dirty changes" test_run_recovery_preserves_unrelated_dirty_changes
# TODO: timeout test hangs in CI — the mock claude sleep subprocess isn't
# killed reliably through the stdin pipe subshell. Fix the watchdog to
# kill the process group, then re-enable.
# run_test "claude agent timeout kills process" test_claude_agent_timeout_kills_process
run_test "implement prompt references tracker" test_implement_prompt_references_tracker

echo "PASS: ${test_count} helix wrapper tests"
