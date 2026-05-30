#!/usr/bin/env bash
# Databricks Genie Code integration test for HELIX skill activation.
#
# Exercises Playwright to drive headless Chromium against a Databricks workspace,
# testing HELIX skill invocation via DOM signals and response content validation.
# Captures webm recordings and per-prompt JSON event logs.
#
# Exit code 0 on all scenarios passing.
#
# Usage:
#   bash tests/workflows/genie/run-scenarios.sh [--no-skill]
#
# Environment:
#   DATABRICKS_HOST: workspace host (e.g., https://adb-xxx.azuredatabricks.net)
#   DATABRICKS_WORKSPACE_URL: full workspace URL (e.g., https://adb-xxx.azuredatabricks.net/?o=123)
#   DBAUTH_COOKIE_PATH: path to file containing DBAUTH session cookie value
#   HELIX_REPO_PATH: optional, path to helix repo (default: current directory)

set -euo pipefail

HELIX_REPO_PATH="${HELIX_REPO_PATH:-.}"
SCENARIOS_DIR="$HELIX_REPO_PATH/tests/workflows/genie/scenarios"
EXPECTED_DIR="$HELIX_REPO_PATH/tests/workflows/genie/expected"
EVALS_FILE="$HELIX_REPO_PATH/tests/workflows/genie/evals/routing.jsonl"
RECORDINGS_DIR="$HELIX_REPO_PATH/tests/workflows/genie/recordings"
DRIVER_SCRIPT="$HELIX_REPO_PATH/tests/workflows/genie/genie-playwright-driver.py"

NO_SKILL="${1:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
  echo -e "${GREEN}→${NC} $*"
}

log_error() {
  echo -e "${RED}✗${NC} $*" >&2
}

log_warn() {
  echo -e "${YELLOW}!${NC} $*"
}

# Check required environment
if [[ -z "${DATABRICKS_HOST:-}" ]]; then
  log_error "DATABRICKS_HOST not set (e.g., https://adb-xxx.azuredatabricks.net)"
  exit 1
fi

if [[ -z "${DATABRICKS_WORKSPACE_URL:-}" ]]; then
  log_error "DATABRICKS_WORKSPACE_URL not set (e.g., https://adb-xxx.azuredatabricks.net/?o=123)"
  exit 1
fi

if [[ -z "${DBAUTH_COOKIE_PATH:-}" ]]; then
  log_error "DBAUTH_COOKIE_PATH not set (path to DBAUTH session cookie file)"
  exit 1
fi

if [[ ! -f "$DBAUTH_COOKIE_PATH" ]]; then
  log_error "DBAUTH cookie file not found: $DBAUTH_COOKIE_PATH"
  exit 1
fi

# Check dependencies
if ! command -v python3 &> /dev/null; then
  log_error "python3 not found in PATH"
  exit 1
fi

if ! python3 -c "import playwright" 2>/dev/null; then
  log_error "Playwright not installed (run: pip install playwright && playwright install chromium)"
  exit 1
fi

if ! python3 -c "import playwright" 2>/dev/null; then
  log_error "Playwright install incomplete; run: playwright install chromium"
  exit 1
fi

log_info "Genie Code HELIX workflow integration test"
log_info "==========================================="
log_info "Workspace: $DATABRICKS_HOST"
log_info "Workspace URL: $DATABRICKS_WORKSPACE_URL"
log_info "DBAUTH cookie: $DBAUTH_COOKIE_PATH"

# Validate evals file
if [[ ! -f "$EVALS_FILE" ]]; then
  log_error "Routing evaluations file not found: $EVALS_FILE"
  exit 1
fi
log_info "Loaded routing evaluations from: $EVALS_FILE"

# Create recordings directory
mkdir -p "$RECORDINGS_DIR"

# Run scenarios
SCENARIOS=("install-verify" "skill-list" "bootstrap")
FAILED_SCENARIOS=()
PASSED_SCENARIOS=()

log_info ""
log_info "Running scenarios..."
log_info ""

for scenario in "${SCENARIOS[@]}"; do
  log_info "Scenario: $scenario"

  PROMPT_FILE="$SCENARIOS_DIR/$scenario.prompt"
  EXPECT_FILE="$EXPECTED_DIR/$scenario.expect"

  if [[ ! -f "$PROMPT_FILE" ]]; then
    log_error "  Prompt file not found: $PROMPT_FILE"
    FAILED_SCENARIOS+=("$scenario")
    continue
  fi

  if [[ ! -f "$EXPECT_FILE" ]]; then
    log_error "  Expected file not found: $EXPECT_FILE"
    FAILED_SCENARIOS+=("$scenario")
    continue
  fi

  # Read and log the prompt
  PROMPT=$(cat "$PROMPT_FILE")
  log_info "  Input: ${PROMPT:0:60}..."

  # Run the Playwright driver
  DRIVER_ARGS=(
    "--workspace-url" "$DATABRICKS_WORKSPACE_URL"
    "--dbauth-cookie" "$DBAUTH_COOKIE_PATH"
    "--repo-root" "$HELIX_REPO_PATH"
  )

  if [[ "$NO_SKILL" == "--no-skill" ]]; then
    DRIVER_ARGS+=("--no-skill")
    log_info "  (negative control mode)"
  fi

  if python3 "$DRIVER_SCRIPT" "${DRIVER_ARGS[@]}" 2>&1 | tee -a /tmp/genie-test-$scenario.log; then
    log_info "  ✓ Scenario passed: $scenario"
    PASSED_SCENARIOS+=("$scenario")
  else
    log_error "  Scenario failed: $scenario (see /tmp/genie-test-$scenario.log)"
    FAILED_SCENARIOS+=("$scenario")
  fi
done

# Report results
echo
log_info "Test Results"
log_info "============"
log_info "Passed: ${#PASSED_SCENARIOS[@]}/${#SCENARIOS[@]}"
for scenario in "${PASSED_SCENARIOS[@]}"; do
  echo -e "  ${GREEN}✓${NC} $scenario"
done

if [[ ${#FAILED_SCENARIOS[@]} -gt 0 ]]; then
  echo
  log_error "Failed: ${#FAILED_SCENARIOS[@]}/${#SCENARIOS[@]}"
  for scenario in "${FAILED_SCENARIOS[@]}"; do
    echo -e "  ${RED}✗${NC} $scenario"
  done
  exit 1
fi

log_info "All scenarios passed"

# Aggregate per-scenario events into single INT-GN-events.json
log_info ""
log_info "Aggregating events..."

# Create combined events file
COMBINED_EVENTS_FILE="$RECORDINGS_DIR/INT-GN-events.json"
python3 << 'PYTHON_EOF'
import json
import glob
from pathlib import Path
from datetime import datetime

recordings_dir = Path("'"$RECORDINGS_DIR"'")
event_files = sorted(glob.glob(str(recordings_dir / "*-events.json")))

combined_events = {
    "test_run": "INT-GN",
    "timestamp": datetime.now().isoformat(),
    "scenarios": []
}

for event_file in event_files:
    try:
        with open(event_file, 'r') as f:
            scenario_data = json.load(f)
        combined_events["scenarios"].append(scenario_data)
    except Exception as e:
        print(f"Warning: could not load {event_file}: {e}")

# Write combined events
with open('"$COMBINED_EVENTS_FILE"', 'w') as f:
    json.dump(combined_events, f, indent=2)

print(f"Wrote combined events to {Path('"$COMBINED_EVENTS_FILE"').name}")
PYTHON_EOF

# Check for recordings
log_info ""
log_info "Recordings and events:"

# List any webm files created by Playwright
if ls "$RECORDINGS_DIR"/*.webm > /dev/null 2>&1; then
  log_info "  Video: $RECORDINGS_DIR/*.webm (created by Playwright)"
else
  log_warn "  Video not found (Playwright may need recording flag enabled)"
fi

if [[ -f "$COMBINED_EVENTS_FILE" ]]; then
  log_info "  Combined events: $(basename "$COMBINED_EVENTS_FILE")"
else
  log_warn "  Combined events file not created"
fi

exit 0
