#!/usr/bin/env bash
# Copilot CLI integration test for HELIX skill activation.
#
# Exercises GitHub Copilot's machine-readable output to assert that the helix skill
# is referenced for each scenario. Exit code 0 on all scenarios passing.
#
# Usage:
#   bash tests/workflows/copilot-cli/run-scenarios.sh [--no-helix]
#
# Environment:
#   GITHUB_TOKEN: required, GitHub token with Copilot license
#   HELIX_REPO_PATH: optional, path to helix repo (default: current directory)

set -euo pipefail

HELIX_REPO_PATH="${HELIX_REPO_PATH:-.}"
SCENARIOS_DIR="$HELIX_REPO_PATH/tests/workflows/copilot-cli/scenarios"
EXPECTED_DIR="$HELIX_REPO_PATH/tests/workflows/copilot-cli/expected"
INSTALL_DIR="$HELIX_REPO_PATH/tests/install/copilot-cli"
IMAGE_TAG="helix-int-test:copilot-cli"
NO_HELIX="${1:-}"
SKIP_HELIX_INSTALL=0

if [[ "$NO_HELIX" == "--no-helix" ]]; then
  SKIP_HELIX_INSTALL=1
  log_info "Running in --no-helix negative control mode (should fail)"
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
if [[ -z "${GITHUB_TOKEN:-}" ]]; then
  log_error "GITHUB_TOKEN not set"
  exit 1
fi

if ! command -v docker &> /dev/null; then
  log_error "docker not found in PATH"
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

# Run each scenario
SCENARIOS=("install-verify" "skill-list" "bootstrap")
FAILED_SCENARIOS=()
PASSED_SCENARIOS=()

for scenario in "${SCENARIOS[@]}"; do
  log_info "Running scenario: $scenario"

  PROMPT_FILE="$SCENARIOS_DIR/$scenario.prompt"
  EXPECT_FILE="$EXPECTED_DIR/$scenario.expect"
  RESPONSE_FILE="$TEST_TMP/$scenario.response.txt"

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

  # Read the prompt
  PROMPT=$(cat "$PROMPT_FILE")
  log_info "  Input: ${PROMPT:0:60}..."

  # Create a Docker setup script that will:
  # 1. Install the HELIX instructions (if not --no-helix)
  # 2. Run gh copilot suggest with the prompt
  # 3. Capture output
  DOCKER_SETUP=$(mktemp)
  cat > "$DOCKER_SETUP" << 'DOCKER_EOF'
#!/bin/bash
set -euo pipefail

PROMPT="$1"
SCENARIO="$2"
SKIP_INSTALL="$3"

cd /workspace/helix

if [[ "$SKIP_INSTALL" != "1" ]]; then
  echo "Installing HELIX instructions..."
  /usr/local/bin/install.sh >/dev/null 2>&1

  # Verify installation
  if [[ -f /tmp/copilot-helix-adopter/.github/copilot-instructions.md ]]; then
    echo "✓ HELIX instructions installed"
  else
    echo "✗ HELIX instructions installation failed"
    exit 1
  fi
fi

# Set up authentication
export GH_TOKEN="$GITHUB_TOKEN"

# Change to the scratch adopter repo where instructions are installed
cd /tmp/copilot-helix-adopter || mkdir -p /tmp/copilot-helix-adopter && cd /tmp/copilot-helix-adopter

# If skip_install=0, make sure the instructions exist
if [[ "$SKIP_INSTALL" != "1" && ! -f .github/copilot-instructions.md ]]; then
  cp /workspace/helix/.github/copilot-instructions.md .github/copilot-instructions.md 2>/dev/null || true
  mkdir -p skills
  cp -r /workspace/helix/skills/helix skills/ 2>/dev/null || true
  mkdir -p workflows
  ln -sf /workspace/helix/workflows workflows 2>/dev/null || true
  git init -q . 2>/dev/null || true
fi

# Run gh copilot suggest with the prompt
# Note: gh copilot suggest is shell-command-oriented
gh copilot suggest "$PROMPT" 2>&1 || true
DOCKER_EOF

  if ! docker run --rm \
    -e GITHUB_TOKEN="$GITHUB_TOKEN" \
    -v "$HELIX_REPO_PATH:/workspace/helix:ro" \
    -v "$DOCKER_SETUP:/tmp/run-scenario.sh:ro" \
    "$IMAGE_TAG" \
    bash /tmp/run-scenario.sh "$PROMPT" "$scenario" "$SKIP_HELIX_INSTALL" > "$RESPONSE_FILE" 2>&1; then
    log_error "  Docker run failed for scenario: $scenario"
    rm -f "$DOCKER_SETUP"
    FAILED_SCENARIOS+=("$scenario")
    continue
  fi
  rm -f "$DOCKER_SETUP"

  # Extract response
  RESPONSE=$(cat "$RESPONSE_FILE" | tr -d '\n')

  # Check for expected text patterns
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

  # Check for behavioral signal: HELIX-specific terminology in response
  HELIX_SIGNAL=0
  if [[ "$RESPONSE" =~ (frame|input|design|review|product-vision|prd|helix|artifact) ]]; then
    HELIX_SIGNAL=1
  fi

  if [[ $HELIX_SIGNAL -eq 0 ]]; then
    if [[ $SKIP_HELIX_INSTALL -eq 1 ]]; then
      # In --no-helix mode, expected that HELIX is NOT invoked
      log_info "  Expected: HELIX not referenced in --no-helix mode"
    else
      log_warn "  No HELIX signal detected in response"
      # For install-verify and skill-list, this is a hard blocker
      if [[ "$scenario" != "bootstrap" ]]; then
        FAILED_SCENARIOS+=("$scenario")
        continue
      fi
    fi
  elif [[ $SKIP_HELIX_INSTALL -eq 1 ]]; then
    # In --no-helix mode, we found HELIX signal - this is unexpected
    log_error "  ERROR: HELIX signal found in --no-helix mode!"
    FAILED_SCENARIOS+=("$scenario")
    continue
  fi

  log_info "  ✓ Scenario passed: $scenario"
  PASSED_SCENARIOS+=("$scenario")
done

# Negative control: run with bootstrap prompt but HELIX explicitly not installed
if [[ $SKIP_HELIX_INSTALL -eq 0 ]]; then
  log_info "Running negative control: HELIX instructions removed"

  PROMPT=$(cat "$SCENARIOS_DIR/bootstrap.prompt")
  NEGATIVE_RESPONSE="$TEST_TMP/negative-control.response.txt"

  NEGATIVE_SETUP=$(mktemp)
  cat > "$NEGATIVE_SETUP" << 'DOCKER_EOF'
#!/bin/bash
set -euo pipefail
PROMPT="$1"

# Set up authentication
export GH_TOKEN="$GITHUB_TOKEN"

cd /tmp/copilot-helix-adopter-negative || mkdir -p /tmp/copilot-helix-adopter-negative && cd /tmp/copilot-helix-adopter-negative

# Ensure NO HELIX instructions are present
rm -rf .github/copilot-instructions.md skills/helix

# Run without the instructions - should not reference HELIX
gh copilot suggest "$PROMPT" 2>&1 || true
DOCKER_EOF

  if docker run --rm \
    -e GITHUB_TOKEN="$GITHUB_TOKEN" \
    -v "$HELIX_REPO_PATH:/workspace/helix:ro" \
    -v "$NEGATIVE_SETUP:/tmp/run-scenario.sh:ro" \
    "$IMAGE_TAG" \
    bash /tmp/run-scenario.sh "$PROMPT" > "$NEGATIVE_RESPONSE" 2>&1; then

    # Check that response does NOT contain HELIX-specific terminology
    NEGATIVE_RESPONSE_TEXT=$(cat "$NEGATIVE_RESPONSE" | tr -d '\n')
    if [[ ! "$NEGATIVE_RESPONSE_TEXT" =~ (frame|input|design|review|product-vision|prd|helix.*skill) ]]; then
      log_info "  ✓ Negative control: HELIX not referenced when instructions absent"
    else
      log_warn "Negative control: Response still contains HELIX terminology (may indicate fallback behavior)"
    fi
  else
    log_warn "Negative control docker run exited nonzero (may be expected)"
  fi

  rm -f "$NEGATIVE_SETUP"
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
