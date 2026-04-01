#!/usr/bin/env bash
# HELIX Quickstart Demo — scripted asciinema recording
#
# This script drives a full HELIX cycle on a tiny Node.js project:
#   1. Setup: init repo, init tracker, install ddx skills
#   2. Seed: one prompt creates the PRD
#   3. Queue: set up issues for the planning + build chain
#   4. Execute: drain the queue — one issue at a time
#   5. Verify: tests pass, app runs
#   6. Review: /review critically reviews all work products
#   7. Triage: /triage identifies gaps and creates follow-up issues
#   8. Experiment: metric-driven optimization iteration on test runtime
#
# Every artifact is created by Claude. Issues drive the work.
#
# Usage:
#   docker run --rm \
#     -v ~/.claude.json:/root/.claude.json:ro \
#     -v ~/.claude:/root/.claude:ro \
#     -v $(pwd):/ddx-library:ro \
#     -v $(pwd)/docs/demos/helix-quickstart/recordings:/recordings \
#     helix-demo
#
set -euo pipefail

RECORDING_FILE="/recordings/helix-quickstart-$(date +%Y%m%d-%H%M%S).cast"
MAX_RETRIES=3
COOLDOWN=8  # generous gap between API calls to avoid rate limits
DEMO_LIBRARY_ROOT="${DEMO_LIBRARY_ROOT:-/ddx-library}"

narrate() {
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "  $1"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  sleep 2
}

run() {
  echo "$ $*"
  "$@"
  echo ""
  sleep 1
}

show_file() {
  local file="$1"
  local lines="${2:-20}"
  echo "── $file ──"
  head -n "$lines" "$file" 2>/dev/null || echo "(file not found)"
  echo "..."
  echo ""
  sleep 2
}

# Run claude -p with prompt visible. Output is captured but printed after.
# Retries on failure with file-change detection.
claude_run() {
  local prompt=""
  if [[ $# -gt 0 ]]; then
    prompt="$*"
  else
    prompt="$(cat)"
  fi

  # Show the command the viewer would type
  echo '$ claude -p "'"${prompt}"'"'
  echo ""

  local attempt output
  for attempt in $(seq 1 "$MAX_RETRIES"); do
    touch /tmp/claude_ts
    output=$(printf '%s' "$prompt" | claude -p --no-session-persistence 2>/dev/null) || true

    if [[ -n "$output" && "$output" != "Execution error" ]]; then
      break
    fi
    # Check if files were created despite error
    local new_files
    new_files=$(find . -not -path './.git/*' -not -path './.helix/*' -newer /tmp/claude_ts 2>/dev/null | wc -l || echo 0)
    if [[ "$new_files" -gt 0 ]]; then
      break
    fi
    if [[ $attempt -lt $MAX_RETRIES ]]; then
      echo "  (retrying $attempt/$MAX_RETRIES...)"
      sleep $((attempt * 3))
    fi
  done

  # Show output
  if [[ -n "$output" && "$output" != "Execution error" ]]; then
    printf '%s\n' "$output"
  fi

  echo ""
  sleep "$COOLDOWN"
}

# Execute an issue: show it, run claude, close it
execute_issue() {
  local issue_id="$1"
  local title
  title=$(helix tracker show "$issue_id" --json 2>/dev/null | jq -r '.title // empty' 2>/dev/null || echo "")

  echo "▶ Issue $issue_id"
  if [[ -n "$title" ]]; then
    echo "  $title"
  fi
  echo ""

  claude_run "$title Read existing artifacts under docs/helix/ for context. When done, close the issue: helix tracker close $issue_id"
}

require_file() {
  local file="$1"
  local label="${2:-$file}"
  if [[ ! -f "$file" ]]; then
    echo "FAIL: $label not found — aborting"
    exit 1
  fi
  echo "  ✓ $label exists"
}

assert_output() {
  local actual="$1"
  local expected="$2"
  local label="$3"
  if [[ "$actual" == *"$expected"* ]]; then
    echo "  ✓ $label — got $expected"
  else
    echo "FAIL: $label — expected '$expected', got '$actual'"
    exit 1
  fi
}

setup_demo_workspace() {
  mkdir -p .agents .claude
  cp -rf "$DEMO_LIBRARY_ROOT/.agents/skills" .agents/
  cat > .claude/settings.json <<'SETTINGS'
{
  "permissions": {
    "allow": ["Bash(*)", "Read(*)", "Write(*)", "Edit(*)"]
  }
}
SETTINGS
}

demo_body() {
  # ── ACT 1: Setup ──────────────────────────────────────────
  narrate "ACT 1: Project Setup"

  run git init hello-helix
  cd hello-helix
  run helix tracker init

  setup_demo_workspace
  echo "HELIX skills installed: $(ls .agents/skills/ | tr '\n' ' ')"
  echo ""
  sleep 2

  # ── ACT 2: Seed the project ─────────────────────────────
  narrate "ACT 2: Seed the Project"

  claude_run 'Write a PRD for "hello-helix", a Node.js CLI that converts temperatures. Features: convert --to-celsius <temp> and convert --to-fahrenheit <temp>, output with one decimal place. Write to docs/helix/01-frame/prd.md. Keep it short.'
  require_file docs/helix/01-frame/prd.md "the PRD"
  show_file docs/helix/01-frame/prd.md

  # ── ACT 3: Build the work queue ─────────────────────────
  narrate "ACT 3: Build the Work Queue"

  echo "Creating issues for the HELIX chain..."
  echo ""

  B1=$(helix tracker create "Write user story US-001 from the PRD. Acceptance criteria: convert --to-celsius 212 prints 100.0, convert --to-fahrenheit 0 prints 32.0. Write to docs/helix/01-frame/user-stories/US-001-temperature-conversion.md" \
    --type task --priority 1 --labels helix,phase:frame)

  B2=$(helix tracker create "Write technical design TD-001: single bin/convert.js exporting toFahrenheit(c) and toCelsius(f), CLI via process.argv, toFixed(1) output. Write to docs/helix/02-design/technical-designs/TD-001-temperature-conversion.md" \
    --type task --priority 1 --labels helix,phase:design)

  B3=$(helix tracker create "Write test plan TP-001 and failing tests. Create package.json with node --test, and tests/convert.test.js requiring ../bin/convert.js for toFahrenheit(0)===32, toCelsius(212)===100, toCelsius(98.6)~=37. Do NOT create bin/convert.js." \
    --type task --priority 1 --labels helix,phase:test)

  B4=$(helix tracker create "Implement bin/convert.js per the technical design. Export toFahrenheit(c) and toCelsius(f). Add CLI with --to-celsius and --to-fahrenheit flags, toFixed(1) output. Run npm test — all tests must pass." \
    --type task --priority 1 --labels helix,phase:build)

  echo ""
  run helix tracker list
  sleep 2

  # ── ACT 4: Drain the queue ─────────────────────────────
  narrate "ACT 4: Execute Issues"

  execute_issue "$B1"
  require_file docs/helix/01-frame/user-stories/US-001-temperature-conversion.md "user story"
  show_file docs/helix/01-frame/user-stories/US-001-temperature-conversion.md

  execute_issue "$B2"
  require_file docs/helix/02-design/technical-designs/TD-001-temperature-conversion.md "tech design"
  show_file docs/helix/02-design/technical-designs/TD-001-temperature-conversion.md

  execute_issue "$B3"
  # Ensure package.json exists for npm test
  [[ -f package.json ]] || echo '{"name":"hello-helix","version":"0.1.0","scripts":{"test":"node --test"}}' > package.json
  require_file tests/convert.test.js "tests"
  show_file tests/convert.test.js 25

  echo "Red phase — tests should fail:"
  npm test 2>&1 || true
  echo ""
  sleep 2

  execute_issue "$B4"
  show_file bin/convert.js 25

  # ── ACT 5: Verify ──────────────────────────────────────
  narrate "ACT 5: Verify"

  echo "Tests:"
  npm test 2>&1 || { echo "FAIL: npm test failed — aborting"; exit 1; }
  echo "  ✓ all tests pass"
  echo ""
  sleep 2

  require_file bin/convert.js "implementation"

  echo "App — checking acceptance criteria:"
  local out
  out=$(node bin/convert.js --to-celsius 212)
  assert_output "$out" "100.0" "212°F → Celsius"

  out=$(node bin/convert.js --to-fahrenheit 0)
  assert_output "$out" "32.0" "0°C → Fahrenheit"

  out=$(node bin/convert.js --to-celsius 98.6)
  assert_output "$out" "37.0" "98.6°F → Celsius"

  echo ""
  sleep 2

  # Commit
  git add -A
  git commit -m "feat: temperature conversion CLI via HELIX" --allow-empty || true

  echo ""
  run helix tracker list --all
  sleep 2

  # ── ACT 6: Review ──────────────────────────────────────
  narrate "ACT 6: Review"

  claude_run "Review all artifacts and code in this project for errors, omissions, and mischaracterizations. Check docs/helix/ specs, tests/convert.test.js, and bin/convert.js. Does the implementation match the specs? Are acceptance criteria covered? Be concise — bullet points."
  sleep 2

  # ── ACT 7: Triage ──────────────────────────────────────
  narrate "ACT 7: Triage"

  claude_run "Read tests/convert.test.js and bin/convert.js. List gaps: which error paths have no tests? Which edge cases are untested? Which acceptance criteria lack integration tests? Numbered list, one line each."

  echo ""
  echo "Creating follow-up issues from triage..."
  run helix tracker create "Add CLI integration tests for acceptance criteria" --type task --priority 2
  run helix tracker create "Add error-path tests (missing flag, bad input)" --type task --priority 2
  run helix tracker create "Add edge-case tests (negative temps, -40 crossover)" --type task --priority 3

  echo ""
  echo "Final queue:"
  run helix tracker list --all
  sleep 2

  # ── ACT 8: Experiment ──────────────────────────────────
  narrate "ACT 8: Experiment"

  echo "Creating an iterate issue for test-runtime optimization..."
  echo ""
  B_EXP=$(helix tracker create "Optimize test suite startup time — reduce wall-clock time of npm test" \
    --type task --priority 2 --labels helix,phase:iterate)
  echo "  Experiment issue: $B_EXP"
  echo ""
  sleep 2

  # Create the metric definition
  mkdir -p docs/helix/06-iterate/metrics
  cat > docs/helix/06-iterate/metrics/test-runtime.yaml <<'METRIC_DEF'
name: test-runtime
description: Wall-clock time for the full test suite (npm test)
unit: seconds
direction: lower
command: |
  start=$(date +%s%N)
  npm test >/dev/null 2>&1
  end=$(date +%s%N)
  elapsed=$(echo "scale=3; ($end - $start) / 1000000000" | bc)
  echo "METRIC test-runtime=$elapsed"
tolerance: 10%
labels:
  area: testing
  phase: iterate
METRIC_DEF
  echo "── docs/helix/06-iterate/metrics/test-runtime.yaml ──"
  cat docs/helix/06-iterate/metrics/test-runtime.yaml
  echo ""
  sleep 2

  git add docs/helix/06-iterate/metrics/test-runtime.yaml
  git commit -m "docs: add test-runtime metric definition" --allow-empty || true
  sleep 1

  # Run the experiment via Claude — setup + one iteration
  claude_run <<'EXPERIMENT_PROMPT'
You are running one experiment iteration to optimize test suite startup time.

Issue: use helix tracker to find the open phase:iterate issue and claim it with helix tracker update <id> --claim.

Steps:
1. Create branch experiment/test-runtime
2. Add session gitignore entries (autoresearch.md, autoresearch.sh, autoresearch.jsonl, experiments/) and commit
3. Create autoresearch.sh that measures npm test wall-clock time and prints METRIC test-runtime=<seconds>. Make it executable.
4. Run ./autoresearch.sh to get baseline
5. Create autoresearch.jsonl with a config line and the baseline result
6. Look at tests/convert.test.js and try ONE optimization to reduce startup time (e.g., reduce redundant requires, simplify test structure, or use a faster assertion pattern). Only modify tests/convert.test.js.
7. Run npm test to verify tests still pass
8. Run ./autoresearch.sh to measure after
9. Log the result to autoresearch.jsonl
10. If improved, commit the change. If not, revert tests/convert.test.js.

Keep it simple — this is a demo. Print a short summary at the end.
Metric definition: docs/helix/06-iterate/metrics/test-runtime.yaml
EXPERIMENT_PROMPT

  # Show the JSONL log
  if [[ -f autoresearch.jsonl ]]; then
    echo "── autoresearch.jsonl (experiment log) ──"
    cat autoresearch.jsonl
    echo ""
    sleep 2
  fi

  # Show final issue status
  echo ""
  echo "Experiment issue status:"
  run helix tracker show "$B_EXP"
  sleep 2

  # Clean up experiment branch
  local current_branch
  current_branch=$(git branch --show-current)
  if [[ "$current_branch" == experiment/* ]]; then
    git checkout main 2>/dev/null || git checkout - 2>/dev/null || true
  fi
  rm -f autoresearch.md autoresearch.sh autoresearch.jsonl
  rm -rf experiments/
  git branch -D experiment/test-runtime 2>/dev/null || true

  narrate "Demo complete!"
  echo ""
  echo "What you just saw:"
  echo "  1. One prompt seeded the PRD"
  echo "  2. Issues defined the work queue"
  echo "  3. Each issue executed in phase order: story -> design -> tests -> code"
  echo "  4. Tests pass, app runs, acceptance criteria verified"
  echo "  5. Review found gaps, triage created follow-up issues"
  echo "  6. Experiment optimized test runtime with metric-driven iteration"
  echo ""
  echo "One seed. Issues drive. HELIX delivers."
  echo ""
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  if [[ -d /recordings && "${HELIX_DEMO_RECORDING:-0}" != "1" ]]; then
    echo "Recording to $RECORDING_FILE"
    HELIX_DEMO_RECORDING=1 asciinema rec \
      -c "bash /usr/local/bin/demo.sh" \
      --title "HELIX Quickstart: Temperature Converter" \
      --cols 100 --rows 30 \
      "$RECORDING_FILE"
    echo "Recording saved: $RECORDING_FILE"
  else
    demo_body
  fi
fi
