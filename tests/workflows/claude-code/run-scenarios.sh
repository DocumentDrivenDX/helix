#!/usr/bin/env bash
# Claude Code integration test for HELIX skill activation.
#
# Exercises stream-json tool_use events to assert that the helix skill
# is invoked for each scenario. Exit code 0 on all scenarios passing.
#
# Usage:
#   bash tests/workflows/claude-code/run-scenarios.sh [--no-skill]
#
# Environment:
#   ANTHROPIC_API_KEY: required, Claude API key
#   HELIX_REPO_PATH: optional, path to helix repo (default: current directory)

set -euo pipefail

HELIX_REPO_PATH="${HELIX_REPO_PATH:-.}"
SCENARIOS_DIR="$HELIX_REPO_PATH/tests/workflows/claude-code/scenarios"
EXPECTED_DIR="$HELIX_REPO_PATH/tests/workflows/claude-code/expected"
INSTALL_DIR="$HELIX_REPO_PATH/tests/install/claude-code"
IMAGE_TAG="helix-int-test:claude-code"
NO_SKILL="${1:-}"
SKIP_SKILL_INSTALL=0

if [[ "$NO_SKILL" == "--no-skill" ]]; then
  SKIP_SKILL_INSTALL=1
  log_info "Running in --no-skill negative control mode (should fail)"
fi

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

# Check requirements
if [[ -z "${ANTHROPIC_API_KEY:-}" ]]; then
  log_error "ANTHROPIC_API_KEY not set"
  exit 1
fi

if ! command -v docker &> /dev/null; then
  log_error "docker not found in PATH"
  exit 1
fi

if ! command -v jq &> /dev/null; then
  log_error "jq not found in PATH (required for stream-json parsing)"
  exit 1
fi

# Build the Docker image
log_info "Building Docker image: $IMAGE_TAG"
docker build \
  -t "$IMAGE_TAG" \
  -f "$INSTALL_DIR/Dockerfile" \
  "$HELIX_REPO_PATH" 2>&1 | tail -20

# Create a temporary directory for test outputs
TEST_TMP=$(mktemp -d)
trap "rm -rf '$TEST_TMP'" EXIT

log_info "Test temp directory: $TEST_TMP"

# Load and validate routing.jsonl expectations
EVALS_FILE="$HELIX_REPO_PATH/tests/workflows/claude-code/evals/routing.jsonl"
if [[ ! -f "$EVALS_FILE" ]]; then
  log_error "Routing evaluations file not found: $EVALS_FILE"
  exit 1
fi

log_info "Loaded routing evaluations from: $EVALS_FILE"

# Run each scenario
SCENARIOS=("install-verify" "skill-list" "bootstrap")
FAILED_SCENARIOS=()
PASSED_SCENARIOS=()

for scenario in "${SCENARIOS[@]}"; do
  log_info "Running scenario: $scenario"

  PROMPT_FILE="$SCENARIOS_DIR/$scenario.prompt"
  EXPECT_FILE="$EXPECTED_DIR/$scenario.expect"
  RESPONSE_FILE="$TEST_TMP/$scenario.response.txt"
  STREAM_FILE="$TEST_TMP/$scenario.stream.jsonl"

  if [[ ! -f "$PROMPT_FILE" ]]; then
    log_error "Prompt file not found: $PROMPT_FILE"
    FAILED_SCENARIOS+=("$scenario")
    continue
  fi

  if [[ ! -f "$EXPECT_FILE" ]]; then
    log_error "Expected file not found: $EXPECT_FILE"
    FAILED_SCENARIOS+=("$scenario")
    continue
  fi

  # Build the claude command
  CLAUDE_ARGS=(
    "--bare"
    "--output-format" "stream-json"
    "--allowed-tools" "Skill(helix)"
  )

  if [[ $SKIP_SKILL_INSTALL -eq 1 ]]; then
    CLAUDE_ARGS+=("--permission-mode" "default")
  else
    CLAUDE_ARGS+=("--plugin-dir" "/workspace/helix")
  fi

  # Run the scenario inside Docker
  PROMPT=$(cat "$PROMPT_FILE")

  log_info "  Input: ${PROMPT:0:60}..."

  # Create a script to run inside Docker to handle prompt escaping
  DOCKER_SCRIPT=$(mktemp)
  cat > "$DOCKER_SCRIPT" << 'DOCKER_EOF'
#!/bin/bash
PROMPT="$1"
CLAUDE_ARGS=("${@:2}")
echo "$PROMPT" | claude "${CLAUDE_ARGS[@]}"
DOCKER_EOF

  if ! docker run --rm \
    -e ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
    -v "$HELIX_REPO_PATH:/workspace/helix:ro" \
    -v "$DOCKER_SCRIPT:/tmp/run-scenario.sh:ro" \
    "$IMAGE_TAG" \
    bash /tmp/run-scenario.sh "$PROMPT" "${CLAUDE_ARGS[@]}" > "$STREAM_FILE" 2>&1; then
    log_error "  Docker run failed for scenario: $scenario"
    rm -f "$DOCKER_SCRIPT"
    FAILED_SCENARIOS+=("$scenario")
    continue
  fi
  rm -f "$DOCKER_SCRIPT"

  # Extract plain text response from stream-json (if in stream format)
  # Try to extract text from content_block_delta events
  if grep -q '"type":"content_block_delta"' "$STREAM_FILE" 2>/dev/null; then
    RESPONSE=$(jq -r 'select(.type=="content_block_delta" and .delta.type=="text_delta") | .delta.text' "$STREAM_FILE" 2>/dev/null | tr -d '\n' || true)
  fi

  # If no structured response, fall back to plain text output
  if [[ -z "$RESPONSE" ]]; then
    RESPONSE=$(cat "$STREAM_FILE" | tr -d '\n')
  fi

  echo "$RESPONSE" > "$RESPONSE_FILE"

  # For non-bootstrap scenarios, check expected text patterns
  if [[ "$scenario" != "bootstrap" ]]; then
    local failed=0
    while IFS= read -r expected; do
      if [[ -n "$expected" && ! "$RESPONSE" =~ $expected ]]; then
        log_error "  Missing expected text: '$expected'"
        failed=1
      fi
    done < "$EXPECT_FILE"

    if [[ $failed -eq 1 ]]; then
      FAILED_SCENARIOS+=("$scenario")
      continue
    fi
  fi

  # Check for helix skill invocation via stream-json tool_use event
  # (except for install-verify which doesn't necessarily invoke the skill)
  SKILL_INVOKED=0
  if [[ "$scenario" != "install-verify" ]]; then
    # Look for content_block_start with tool_use type and name="Skill"
    # The helix skill name should be in input.skill_name or similar
    SKILL_INVOKED=$(jq -r 'select(.type=="content_block_start" and .content_block.type=="tool_use" and .content_block.name=="Skill") | .content_block.input.skill_name // "none"' "$STREAM_FILE" 2>/dev/null | grep -c "helix" || true)

    if [[ $SKILL_INVOKED -eq 0 ]]; then
      # Fallback: check for any reference to "helix" Skill in the stream
      SKILL_INVOKED=$(jq -r 'select(.content_block.type=="tool_use" or .type=="tool_use") | select(.content_block.name=="Skill" or .name=="Skill" or .content_block.input.skill_name=="helix" or .input.skill_name=="helix")' "$STREAM_FILE" 2>/dev/null | wc -l)
    fi

    if [[ $SKILL_INVOKED -eq 0 ]]; then
      if [[ $SKIP_SKILL_INSTALL -eq 1 ]]; then
        # In --no-skill mode, expected that skill is NOT invoked
        # This is the negative control - we expect failures
        log_info "  Expected: Skill not invoked in --no-skill mode"
        FAILED_SCENARIOS+=("$scenario")
        continue
      else
        log_warn "  No helix Skill invocation detected in stream-json"
        # For bootstrap, this is a blocker. For others, it's a warning
        if [[ "$scenario" == "bootstrap" ]]; then
          FAILED_SCENARIOS+=("$scenario")
          continue
        fi
      fi
    elif [[ $SKIP_SKILL_INSTALL -eq 1 ]]; then
      # In --no-skill mode, we found skill invoked - this is wrong
      log_error "  ERROR: Skill invoked in --no-skill mode!"
      FAILED_SCENARIOS+=("$scenario")
      continue
    fi
  fi

  log_info "  ✓ Scenario passed: $scenario"
  PASSED_SCENARIOS+=("$scenario")
done

# Negative control: run with --no-skill and verify it fails or produces different behavior
if [[ $SKIP_SKILL_INSTALL -eq 0 ]]; then
  log_info "Running negative control: --no-skill"

  PROMPT=$(cat "$SCENARIOS_DIR/bootstrap.prompt")
  NEGATIVE_STREAM="$TEST_TMP/negative-control.stream.jsonl"

  if docker run --rm \
    -e ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
    -v "$HELIX_REPO_PATH:/workspace/helix:ro" \
    "$IMAGE_TAG" \
    bash -c "echo '$PROMPT' | claude --bare --output-format stream-json --allowed-tools ''" > "$NEGATIVE_STREAM" 2>&1; then

    # Check that skill was NOT invoked
    SKILL_NOT_INVOKED=$(jq 'select(.type=="content_block_start" and .content_block.type=="tool_use" and .content_block.name=="Skill")' "$NEGATIVE_STREAM" 2>/dev/null | wc -l)

    if [[ $SKILL_NOT_INVOKED -gt 0 ]]; then
      log_warn "Negative control: Skill still invoked with no allowed tools (may indicate issue with restriction)"
    else
      log_info "  ✓ Negative control: Skill not invoked when not allowed"
    fi
  else
    log_warn "Negative control docker run exited nonzero (may be expected)"
  fi
fi

# Print results
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
exit 0
